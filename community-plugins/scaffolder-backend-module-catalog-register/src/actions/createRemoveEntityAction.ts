import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import fs from 'fs-extra';
import http from 'node:http';
import https from 'node:https';
import yaml from 'yaml';

const ACTION_ID = 'catalog:remove-entity';
const SA_TOKEN = '/var/run/secrets/kubernetes.io/serviceaccount/token';
const SA_CA = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt';
const SA_NS = '/var/run/secrets/kubernetes.io/serviceaccount/namespace';
const K8S_HOST = 'kubernetes.default.svc';

type K8sResponse = { status: number; body: string };
type HttpResponse = { status: number; body: string };

function readNamespace(explicit?: string): string {
  if (explicit?.trim()) {
    return explicit.trim();
  }
  if (fs.existsSync(SA_NS)) {
    return fs.readFileSync(SA_NS, 'utf8').trim();
  }
  throw new Error(
    'namespace is required when not running in a Kubernetes pod',
  );
}

function k8sRequest(
  method: string,
  apiPath: string,
  body?: unknown,
  contentType = 'application/json',
): Promise<K8sResponse> {
  const token = fs.readFileSync(SA_TOKEN, 'utf8').trim();
  const ca = fs.readFileSync(SA_CA);
  const payload = body === undefined ? undefined : JSON.stringify(body);

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: K8S_HOST,
        path: apiPath,
        method,
        ca,
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
          ...(payload
            ? {
                'Content-Type': contentType,
                'Content-Length': Buffer.byteLength(payload),
              }
            : {}),
        },
      },
      res => {
        const chunks: Buffer[] = [];
        res.on('data', chunk => {
          chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
        });
        res.on('end', () =>
          resolve({
            status: res.statusCode ?? 0,
            body: Buffer.concat(chunks).toString('utf8'),
          }),
        );
      },
    );
    req.on('error', reject);
    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

function backstageRequest(pathname: string): Promise<HttpResponse> {
  const backendUrl = process.env.BACKSTAGE_BACKEND_URL ?? 'http://localhost:7007';
  const token = process.env.MCP_TOKEN?.trim();
  if (!token) {
    return Promise.resolve({
      status: 0,
      body: 'MCP_TOKEN env var not configured',
    });
  }
  const target = new URL(pathname, backendUrl);
  const client = target.protocol === 'https:' ? https : http;

  return new Promise((resolve, reject) => {
    const req = client.request(
      {
        protocol: target.protocol,
        hostname: target.hostname,
        port: target.port,
        path: `${target.pathname}${target.search}`,
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json, text/event-stream',
          'Content-Type': 'application/json',
          'Content-Length': 2,
        },
      },
      res => {
        const chunks: Buffer[] = [];
        res.on('data', chunk => {
          chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
        });
        res.on('end', () =>
          resolve({
            status: res.statusCode ?? 0,
            body: Buffer.concat(chunks).toString('utf8'),
          }),
        );
      },
    );
    req.on('error', reject);
    req.write('{}');
    req.end();
  });
}

async function deleteIfExists(path: string): Promise<void> {
  const result = await k8sRequest('DELETE', path);
  if (![200, 202, 404].includes(result.status)) {
    throw new Error(`DELETE ${path} failed: HTTP ${result.status} ${result.body}`);
  }
}

export function createRemoveEntityAction() {
  return createTemplateAction({
    id: ACTION_ID,
    description:
      'Removes a registered catalog entity and associated sandbox runtime resources.',
    schema: {
      input: {
        name: z => z.string().describe('Entity name to remove'),
        kind: z =>
          z
            .string()
            .optional()
            .describe('Entity kind (default: component)'),
        namespace: z =>
          z
            .string()
            .optional()
            .describe('Target namespace (defaults to pod namespace)'),
      },
      output: {
        removed: z => z.boolean().describe('True when removal completed'),
      },
    },
    async handler(ctx) {
      const name = ctx.input.name;
      const kind = (ctx.input.kind ?? 'component').toLowerCase();
      const namespace = readNamespace(ctx.input.namespace);
      const pendingName = `pending-entity-${name}`;
      const registeredCm =
        process.env.REGISTERED_CATALOG_CM ??
        'rhdh-agent-sandbox-registered-catalog';
      const key = `${kind}-${name}.yaml`;

      await deleteIfExists(`/api/v1/namespaces/${namespace}/configmaps/${pendingName}`);
      ctx.logger.info(`Removed pending ConfigMap if present: ${namespace}/${pendingName}`);

      const existing = await k8sRequest(
        'GET',
        `/api/v1/namespaces/${namespace}/configmaps/${registeredCm}`,
      );

      let annotations: Record<string, string> = {};
      if (existing.status === 200) {
        const cm = JSON.parse(existing.body) as { data?: Record<string, string> };
        const data = { ...(cm.data ?? {}) };
        const rawEntity = data[key];
        if (rawEntity) {
          const parsed = yaml.parse(rawEntity) as {
            metadata?: { annotations?: Record<string, string> };
          };
          annotations = parsed.metadata?.annotations ?? {};
          delete data[key];
          const patch = await k8sRequest(
            'PATCH',
            `/api/v1/namespaces/${namespace}/configmaps/${registeredCm}`,
            { data },
            'application/merge-patch+json',
          );
          if (patch.status < 200 || patch.status >= 300) {
            throw new Error(
              `Failed to patch ${registeredCm}: HTTP ${patch.status} ${patch.body}`,
            );
          }
        }
      } else if (existing.status !== 404) {
        throw new Error(
          `Failed to read ${registeredCm}: HTTP ${existing.status} ${existing.body}`,
        );
      }

      await deleteIfExists(
        `/apis/apps/v1/namespaces/${namespace}/deployments/${name}`,
      );
      await deleteIfExists(`/api/v1/namespaces/${namespace}/services/${name}`);

      const isManagedAgent =
        annotations['rhdh-agent-sandbox.io/managed-agent'] === 'true' ||
        (annotations['rhdh-agent-sandbox.io/build'] ?? '').toLowerCase() ===
          'true';
      if (isManagedAgent) {
        await deleteIfExists(
          `/apis/build.openshift.io/v1/namespaces/${namespace}/buildconfigs/${name}`,
        );
        await deleteIfExists(
          `/apis/image.openshift.io/v1/namespaces/${namespace}/imagestreams/${name}`,
        );
      }

      const isDevWorkspace =
        annotations['rhdh-agent-sandbox.io/managed-devworkspace'] === 'true';
      if (isDevWorkspace) {
        await deleteIfExists(
          `/apis/workspace.devfile.io/v1alpha2/namespaces/${namespace}/devworkspaces/${name}`,
        );
      }

      const refresh = await backstageRequest('/api/catalog/refresh');
      if (refresh.status && ![200, 202].includes(refresh.status)) {
        ctx.logger.warn(
          `Catalog refresh failed after removal: HTTP ${refresh.status} ${refresh.body}`,
        );
      }

      ctx.logger.info(`Removed catalog/runtime resources for ${kind}:${namespace}/${name}`);
      ctx.output('removed', true);
    },
  });
}
