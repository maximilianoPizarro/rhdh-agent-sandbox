import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import fs from 'fs-extra';
import http from 'node:http';
import https from 'node:https';
const ACTION_ID = 'catalog:remove-entity';
const SA_TOKEN = '/var/run/secrets/kubernetes.io/serviceaccount/token';
const SA_CA = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt';
const SA_NS = '/var/run/secrets/kubernetes.io/serviceaccount/namespace';
const K8S_HOST = 'kubernetes.default.svc';
const CATALOG_NAMESPACE = 'default';

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

function backstageRequest(
  method: 'GET' | 'POST' | 'DELETE',
  pathname: string,
  body?: unknown,
): Promise<HttpResponse> {
  const backendUrl = process.env.BACKSTAGE_BACKEND_URL ?? 'http://localhost:7007';
  const token = process.env.MCP_TOKEN?.trim();
  if (!token) {
    return Promise.resolve({
      status: 0,
      body: 'MCP_TOKEN env var not configured',
    });
  }
  const target = new URL(pathname, backendUrl);
  const payload = body === undefined ? undefined : JSON.stringify(body);
  const client = target.protocol === 'https:' ? https : http;

  return new Promise((resolve, reject) => {
    const req = client.request(
      {
        protocol: target.protocol,
        hostname: target.hostname,
        port: target.port,
        path: `${target.pathname}${target.search}`,
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json, text/event-stream',
          ...(payload
            ? {
                'Content-Type': 'application/json',
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

async function deleteIfExists(path: string): Promise<void> {
  const result = await k8sRequest('DELETE', path);
  if (![200, 202, 404].includes(result.status)) {
    throw new Error(`DELETE ${path} failed: HTTP ${result.status} ${result.body}`);
  }
}

async function deleteLabeledTekton(
  namespace: string,
  name: string,
  resource: 'pipelineruns' | 'taskruns',
): Promise<void> {
  const labelSelector = encodeURIComponent(`app.kubernetes.io/name=${name}`);
  const listPath = `/apis/tekton.dev/v1/namespaces/${namespace}/${resource}?labelSelector=${labelSelector}`;
  const listResult = await k8sRequest('GET', listPath);

  if (listResult.status === 404) {
    return;
  }
  if (listResult.status !== 200) {
    throw new Error(
      `Failed to list ${resource} for ${name}: HTTP ${listResult.status} ${listResult.body}`,
    );
  }

  const list = JSON.parse(listResult.body) as {
    items?: Array<{ metadata?: { name?: string } }>;
  };

  for (const item of list.items ?? []) {
    const runName = item.metadata?.name;
    if (!runName) {
      continue;
    }
    await deleteIfExists(
      `/apis/tekton.dev/v1/namespaces/${namespace}/${resource}/${runName}`,
    );
  }
}

async function deletePipelineRuns(namespace: string, name: string): Promise<void> {
  await deleteLabeledTekton(namespace, name, 'pipelineruns');
  await deleteLabeledTekton(namespace, name, 'taskruns');
}

async function deleteCatalogEntity(
  kind: string,
  name: string,
  logger: { info: (msg: string) => void; warn: (msg: string) => void },
): Promise<void> {
  const byNamePath = `/api/catalog/entities/by-name/${encodeURIComponent(kind)}/${encodeURIComponent(CATALOG_NAMESPACE)}/${encodeURIComponent(name)}`;
  const getResult = await backstageRequest('GET', byNamePath);

  if (getResult.status === 0) {
    logger.warn(
      'MCP_TOKEN not configured; skipping catalog entity deletion by uid',
    );
    return;
  }

  if (getResult.status === 404) {
    logger.info(
      `Catalog entity ${kind}:${CATALOG_NAMESPACE}/${name} not found; skipping delete`,
    );
    return;
  }

  if (getResult.status !== 200) {
    logger.warn(
      `Failed to look up catalog entity ${kind}:${CATALOG_NAMESPACE}/${name}: HTTP ${getResult.status} ${getResult.body}`,
    );
    return;
  }

  const entity = JSON.parse(getResult.body) as { metadata?: { uid?: string } };
  const uid = entity.metadata?.uid;
  if (!uid) {
    throw new Error(
      `Catalog entity ${kind}:${CATALOG_NAMESPACE}/${name} is missing metadata.uid`,
    );
  }

  const deleteResult = await backstageRequest(
    'DELETE',
    `/api/catalog/entities/by-uid/${encodeURIComponent(uid)}`,
  );

  if (deleteResult.status === 404) {
    return;
  }

  if (![200, 202, 204].includes(deleteResult.status)) {
    throw new Error(
      `Failed to delete catalog entity by uid ${uid}: HTTP ${deleteResult.status} ${deleteResult.body}`,
    );
  }

  logger.info(`Deleted catalog entity ${kind}:${CATALOG_NAMESPACE}/${name} (uid ${uid})`);
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
      // Companion APIs: AI Service uses `${name}-http`; Deploy Agent uses `${name}-agent`.
      const companionApiKeys = [
        `api-${name}-http.yaml`,
        `api-${name}-agent.yaml`,
      ];

      await deleteIfExists(`/api/v1/namespaces/${namespace}/configmaps/${pendingName}`);
      ctx.logger.info(`Removed pending ConfigMap if present: ${namespace}/${pendingName}`);

      const existing = await k8sRequest(
        'GET',
        `/api/v1/namespaces/${namespace}/configmaps/${registeredCm}`,
      );

      if (existing.status === 200) {
        const cm = JSON.parse(existing.body) as { data?: Record<string, string> };
        const current = cm.data ?? {};
        // JSON merge-patch only deletes map keys when the value is null.
        const dataPatch: Record<string, null> = {};
        for (const k of [key, ...companionApiKeys]) {
          if (Object.prototype.hasOwnProperty.call(current, k)) {
            dataPatch[k] = null;
          }
        }
        if (Object.keys(dataPatch).length > 0) {
          const patch = await k8sRequest(
            'PATCH',
            `/api/v1/namespaces/${namespace}/configmaps/${registeredCm}`,
            { data: dataPatch },
            'application/merge-patch+json',
          );
          if (patch.status < 200 || patch.status >= 300) {
            throw new Error(
              `Failed to patch ${registeredCm}: HTTP ${patch.status} ${patch.body}`,
            );
          }
          ctx.logger.info(
            `Removed registered catalog keys: ${Object.keys(dataPatch).join(', ')}`,
          );
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
      await deleteIfExists(
        `/apis/build.openshift.io/v1/namespaces/${namespace}/buildconfigs/${name}`,
      );
      await deleteIfExists(
        `/apis/image.openshift.io/v1/namespaces/${namespace}/imagestreams/${name}`,
      );
      await deleteIfExists(
        `/apis/workspace.devfile.io/v1alpha2/namespaces/${namespace}/devworkspaces/${name}`,
      );

      // Per-agent Tekton runs only. Shared Pipeline {{fullname}}-deploy-agent stays.
      await deletePipelineRuns(namespace, name);
      ctx.logger.info(`Removed PipelineRuns labeled app.kubernetes.io/name=${name} if present`);

      await deleteCatalogEntity(kind, name, ctx.logger);
      await deleteCatalogEntity('api', `${name}-http`, ctx.logger);
      await deleteCatalogEntity('api', `${name}-agent`, ctx.logger);

      // Registered entities live under this Location (not the static chart catalog).
      const refreshTargets = [
        'location:default/registered-catalog-entities',
        'location:default/rhdh-agent-sandbox-catalog',
      ];
      for (const entityRef of refreshTargets) {
        const refresh = await backstageRequest('POST', '/api/catalog/refresh', {
          entityRef,
        });
        if (refresh.status && ![200, 202].includes(refresh.status)) {
          ctx.logger.warn(
            `Catalog refresh failed for ${entityRef}: HTTP ${refresh.status} ${refresh.body}`,
          );
        }
      }

      ctx.logger.info(`Removed catalog/runtime resources for ${kind}:${namespace}/${name}`);
      ctx.output('removed', true);
    },
  });
}
