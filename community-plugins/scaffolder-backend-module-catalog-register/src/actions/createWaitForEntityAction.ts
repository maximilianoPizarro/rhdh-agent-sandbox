import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import http from 'node:http';
import https from 'node:https';
import { URL } from 'node:url';

const ACTION_ID = 'catalog:wait-for-entity';

type HttpResponse = { status: number; body: string };

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function httpRequest(
  url: string,
  token: string,
  options: { method?: string; body?: unknown } = {},
): Promise<HttpResponse> {
  const { method = 'GET', body } = options;
  const parsed = new URL(url);
  const client = parsed.protocol === 'https:' ? https : http;
  const payload = body === undefined ? undefined : JSON.stringify(body);

  return new Promise((resolve, reject) => {
    const req = client.request(
      {
        protocol: parsed.protocol,
        hostname: parsed.hostname,
        port: parsed.port,
        path: `${parsed.pathname}${parsed.search}`,
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
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
        res.on('end', () => {
          resolve({
            status: res.statusCode ?? 0,
            body: Buffer.concat(chunks).toString('utf8'),
          });
        });
      },
    );
    req.on('error', reject);
    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

export function createWaitForEntityAction() {
  return createTemplateAction({
    id: ACTION_ID,
    description:
      'Waits until a catalog entity is visible via the Backstage catalog API.',
    schema: {
      input: {
        name: z => z.string().describe('Entity name'),
        kind: z =>
          z
            .string()
            .optional()
            .describe('Entity kind (default: component)'),
        namespace: z =>
          z
            .string()
            .optional()
            .describe('Entity namespace (default: default)'),
        timeoutSeconds: z =>
          z
            .number()
            .optional()
            .describe('Maximum time to wait in seconds (default: 120)'),
        pollIntervalSeconds: z =>
          z
            .number()
            .optional()
            .describe('Polling interval in seconds (default: 5)'),
      },
      output: {
        entityRef: z => z.string().describe('Resolved entity reference'),
      },
    },
    async handler(ctx) {
      const token = process.env.MCP_TOKEN?.trim();
      if (!token) {
        throw new Error(
          'MCP_TOKEN env var is required for catalog:wait-for-entity',
        );
      }

      const baseUrl = (
        process.env.BACKSTAGE_BACKEND_URL ?? 'http://localhost:7007'
      ).replace(/\/+$/, '');
      const name = ctx.input.name;
      const kind = (ctx.input.kind ?? 'component').toLowerCase();
      const namespace = ctx.input.namespace ?? 'default';
      const timeoutMs = (ctx.input.timeoutSeconds ?? 120) * 1000;
      const pollMs = (ctx.input.pollIntervalSeconds ?? 5) * 1000;
      const entityRef = `${kind}:${namespace}/${name}`;
      const url = `${baseUrl}/api/catalog/entities/by-name/${encodeURIComponent(kind)}/${encodeURIComponent(namespace)}/${encodeURIComponent(name)}`;

      const refreshUrl = `${baseUrl}/api/catalog/refresh`;
      const catalogLocationRef = 'location:default/rhdh-agent-sandbox-catalog';
      const start = Date.now();
      let notFoundCount = 0;

      while (Date.now() - start < timeoutMs) {
        const response = await httpRequest(url, token);

        if (response.status === 200) {
          ctx.logger.info(`Entity became visible in catalog: ${entityRef}`);
          ctx.output('entityRef', entityRef);
          return;
        }

        if (response.status !== 404) {
          throw new Error(
            `Failed while waiting for ${entityRef}: HTTP ${response.status} ${response.body}`,
          );
        }

        notFoundCount += 1;
        if (notFoundCount % 3 === 0) {
          try {
            const refresh = await httpRequest(refreshUrl, token, {
              method: 'POST',
              body: { entityRef: catalogLocationRef },
            });
            if (![200, 202].includes(refresh.status)) {
              ctx.logger.warn(
                `Catalog refresh failed while waiting for ${entityRef}: HTTP ${refresh.status} ${refresh.body}`,
              );
            }
          } catch (error) {
            ctx.logger.warn(
              `Catalog refresh failed while waiting for ${entityRef}: ${error}`,
            );
          }
        }

        await sleep(pollMs);
      }

      throw new Error(
        `Timed out waiting for catalog entity ${entityRef} after ${ctx.input.timeoutSeconds ?? 120}s`,
      );
    },
  });
}
