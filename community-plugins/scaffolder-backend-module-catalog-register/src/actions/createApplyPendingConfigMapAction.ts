import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import type { CatalogService } from '@backstage/plugin-catalog-node';
import fs from 'fs-extra';
import https from 'node:https';
import path from 'node:path';
import yaml from 'yaml';

const ACTION_ID = 'catalog:apply-pending-configmap';
const SA_TOKEN = '/var/run/secrets/kubernetes.io/serviceaccount/token';
const SA_CA = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt';
const SA_NS = '/var/run/secrets/kubernetes.io/serviceaccount/namespace';
const K8S_HOST = 'kubernetes.default.svc';

type K8sResponse = { status: number; body: string };

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

const IMMEDIATE_INGEST_DIR = '/tmp/scaffolder-immediate';

export function createApplyPendingConfigMapAction(options: {
  catalog: CatalogService;
}) {
  const { catalog } = options;

  return createTemplateAction({
    id: ACTION_ID,
    description:
      'Applies a pending catalog entity ConfigMap manifest from the scaffolder workspace.',
    schema: {
      input: {
        manifestPath: z =>
          z
            .string()
            .optional()
            .describe(
              'Workspace-relative path to the ConfigMap YAML (default: kubernetes/configmap.yaml)',
            ),
        namespace: z =>
          z
            .string()
            .optional()
            .describe('Target namespace (defaults to pod service account namespace)'),
      },
      output: {
        configMapName: z => z.string().describe('Applied ConfigMap name'),
      },
    },
    async handler(ctx) {
      const manifestPath =
        ctx.input.manifestPath ?? 'kubernetes/configmap.yaml';
      const absPath = path.resolve(ctx.workspacePath, manifestPath);

      if (!(await fs.pathExists(absPath))) {
        throw new Error(`ConfigMap manifest not found at ${manifestPath}`);
      }

      const raw = await fs.readFile(absPath, 'utf8');
      const doc = yaml.parse(raw) as {
        apiVersion?: string;
        kind?: string;
        metadata?: { name?: string; namespace?: string; labels?: Record<string, string> };
        data?: Record<string, string>;
        labels?: Record<string, string>;
      };

      if (doc.kind !== 'ConfigMap') {
        throw new Error(`Expected kind ConfigMap, got ${doc.kind ?? 'unknown'}`);
      }

      const name = doc.metadata?.name;
      if (!name) {
        throw new Error('ConfigMap metadata.name is required');
      }

      const namespace = readNamespace(
        doc.metadata?.namespace ?? ctx.input.namespace,
      );

      const payload = {
        apiVersion: 'v1',
        kind: 'ConfigMap',
        metadata: {
          name,
          namespace,
          labels: doc.metadata?.labels ?? doc.labels,
        },
        data: doc.data ?? {},
      };

      const getPath = `/api/v1/namespaces/${namespace}/configmaps/${name}`;
      const existing = await k8sRequest('GET', getPath);

      let result: K8sResponse;
      if (existing.status === 200) {
        result = await k8sRequest(
          'PATCH',
          getPath,
          payload,
          'application/merge-patch+json',
        );
      } else if (existing.status === 404) {
        result = await k8sRequest(
          'POST',
          `/api/v1/namespaces/${namespace}/configmaps`,
          payload,
        );
      } else {
        throw new Error(
          `Failed to read ConfigMap ${name}: HTTP ${existing.status} ${existing.body}`,
        );
      }

      if (result.status < 200 || result.status >= 300) {
        throw new Error(
          `Failed to apply ConfigMap ${name}: HTTP ${result.status} ${result.body}`,
        );
      }

      ctx.logger.info(`Applied pending catalog ConfigMap ${namespace}/${name}`);
      ctx.output('configMapName', name);

      const pendingName = name.replace(/^pending-entity-/, '');
      const router = (process.env.CLUSTER_ROUTER_BASE ?? '').trim();
      const agentBase = router
        ? `https://${pendingName}-${namespace}.${router}`
        : `http://${pendingName}:8080`;
      const entityYaml = (payload.data?.['entity.yaml'] ?? '')
        .replaceAll('__RELEASE_NAMESPACE__', namespace)
        .replaceAll('__AGENT_BASE_URL__', agentBase);
      if (!entityYaml.trim()) {
        ctx.logger.warn(
          `ConfigMap ${name} has no entity.yaml; skipping immediate catalog ingest`,
        );
        return;
      }

      try {
        await fs.ensureDir(IMMEDIATE_INGEST_DIR);
        const ingestPath = path.join(IMMEDIATE_INGEST_DIR, `${name}.yaml`);
        await fs.writeFile(ingestPath, entityYaml);
        const location = await catalog.addLocation(
          {
            type: 'file',
            target: ingestPath,
            onConflict: 'refresh',
          },
          { credentials: await ctx.getInitiatorCredentials() },
        );
        const ingested = (location.entities ?? [])
          .map(
            entity =>
              `${entity.kind}:${entity.metadata?.namespace ?? 'default'}/${entity.metadata?.name}`,
          )
          .join(', ');
        ctx.logger.info(
          `Ingested pending entities immediately (${ingested || 'none returned'}) from ${ingestPath}`,
        );
      } catch (error) {
        ctx.logger.warn(
          `Immediate catalog ingest failed; wait-for-entity will poll the registered ConfigMap: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    },
  });
}
