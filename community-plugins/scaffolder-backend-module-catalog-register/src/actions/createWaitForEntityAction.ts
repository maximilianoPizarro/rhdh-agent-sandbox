import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import type { CatalogService } from '@backstage/plugin-catalog-node';

const ACTION_ID = 'catalog:wait-for-entity';
const DEFAULT_LOCATION_REF = 'location:default/registered-catalog-entities';

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function createWaitForEntityAction(options: { catalog: CatalogService }) {
  const { catalog } = options;

  return createTemplateAction({
    id: ACTION_ID,
    description:
      'Waits until a catalog entity is visible via the in-process catalog client.',
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
      const name = ctx.input.name;
      const kind = (ctx.input.kind ?? 'component').toLowerCase();
      const namespace = ctx.input.namespace ?? 'default';
      const timeoutSeconds = ctx.input.timeoutSeconds ?? 120;
      const timeoutMs = timeoutSeconds * 1000;
      const pollMs = (ctx.input.pollIntervalSeconds ?? 5) * 1000;
      const entityRef = `${kind}:${namespace}/${name}`;
      const credentials = await ctx.getInitiatorCredentials();
      const start = Date.now();
      let attempts = 0;

      ctx.logger.info(
        `Waiting for ${entityRef} via catalog client (timeout ${timeoutSeconds}s)`,
      );

      while (Date.now() - start < timeoutMs) {
        attempts += 1;
        const elapsedSeconds = Math.round((Date.now() - start) / 1000);

        try {
          const entity = await catalog.getEntityByRef(entityRef, {
            credentials,
          });
          if (entity) {
            ctx.logger.info(
              `Entity became visible in catalog: ${entityRef} after ${elapsedSeconds}s`,
            );
            ctx.output('entityRef', entityRef);
            return;
          }
        } catch (error) {
          ctx.logger.warn(
            `Catalog lookup for ${entityRef} failed (will retry): ${errorMessage(error)}`,
          );
        }

        // Heartbeat keeps the scaffolder event stream from looking idle.
        ctx.logger.info(
          `Still waiting for ${entityRef} (${elapsedSeconds}s, attempt ${attempts})`,
        );

        if (attempts % 2 === 0) {
          try {
            await catalog.refreshEntity(DEFAULT_LOCATION_REF, { credentials });
          } catch (error) {
            ctx.logger.warn(
              `Catalog refresh of ${DEFAULT_LOCATION_REF} failed: ${errorMessage(error)}`,
            );
          }
        }

        await sleep(pollMs);
      }

      throw new Error(
        `Timed out waiting for catalog entity ${entityRef} after ${timeoutSeconds}s`,
      );
    },
  });
}
