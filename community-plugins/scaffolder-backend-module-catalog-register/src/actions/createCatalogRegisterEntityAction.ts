import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import type { CatalogService } from '@backstage/plugin-catalog-node';
import { stringifyEntityRef, type Entity } from '@backstage/catalog-model';
import fs from 'fs-extra';
import path from 'node:path';
import yaml from 'yaml';

const ACTION_ID = 'catalog:register-entity';

type Options = {
  catalog: CatalogService;
  registeredRoot: string;
  techdocsAgentTemplate: string;
};

function substituteAgentDocs(
  templateDir: string,
  targetDir: string,
  values: Record<string, string>,
) {
  const replaceInFile = (filePath: string) => {
    if (!fs.existsSync(filePath)) {
      return;
    }
    let content = fs.readFileSync(filePath, 'utf8');
    for (const [key, val] of Object.entries(values)) {
      content = content.replaceAll(`{{${key}}}`, val);
    }
    fs.writeFileSync(filePath, content);
  };

  fs.copySync(templateDir, targetDir);
  const docsDir = path.join(targetDir, 'docs');
  if (fs.existsSync(docsDir)) {
    for (const entry of fs.readdirSync(docsDir, { withFileTypes: true })) {
      const full = path.join(docsDir, entry.name);
      if (entry.isFile()) {
        replaceInFile(full);
      }
    }
  }
  replaceInFile(path.join(targetDir, 'mkdocs.yml'));
}

export function createCatalogRegisterEntityAction(options: Options) {
  const { catalog, registeredRoot, techdocsAgentTemplate } = options;

  return createTemplateAction({
    id: ACTION_ID,
    description:
      'Registers a catalog entity from inline YAML and optional per-agent TechDocs.',
    schema: {
      input: {
        entity: z =>
          z
            .record(z.any())
            .describe('Catalog entity object (Component, API, etc.)'),
        techdocs: z =>
          z
            .object({
              enabled: z.boolean().optional(),
              values: z.record(z.string()).optional(),
            })
            .optional(),
      },
      output: {
        entityRef: z => z.string().describe('Registered entity reference'),
        catalogInfoPath: z =>
          z.string().describe('Path to persisted catalog-info.yaml'),
      },
    },
    async handler(ctx) {
      const entity = ctx.input.entity as Entity;
      const name = entity.metadata?.name;
      const kind = (entity.kind ?? 'Component').toLowerCase();

      if (!name) {
        throw new Error('entity.metadata.name is required');
      }

      const entityDir = path.join(registeredRoot, kind, name);
      await fs.ensureDir(entityDir);
      const catalogInfoPath = path.join(entityDir, 'catalog-info.yaml');
      await fs.writeFile(catalogInfoPath, yaml.stringify(entity));

      const techdocsValues = ctx.input.techdocs?.values ?? {};
      const techdocsEnabled =
        ctx.input.techdocs?.enabled ??
        entity.metadata?.annotations?.['rhdh-agent-sandbox.io/managed-agent'] ===
          'true';

      if (techdocsEnabled && (await fs.pathExists(techdocsAgentTemplate))) {
        const agentDocsDir = path.join(
          registeredRoot,
          'techdocs',
          'agents',
          name,
        );
        substituteAgentDocs(techdocsAgentTemplate, agentDocsDir, {
          name,
          agentSpec:
            techdocsValues.agentSpec ??
            String(entity.metadata?.description ?? ''),
          language:
            techdocsValues.language ??
            String(
              entity.metadata?.annotations?.['rhdh-agent-sandbox.io/language'] ??
                '',
            ),
          framework:
            techdocsValues.framework ??
            String(
              entity.metadata?.annotations?.[
                'rhdh-agent-sandbox.io/framework'
              ] ?? '',
            ),
          model:
            techdocsValues.model ??
            String(
              entity.metadata?.annotations?.['rhdh-agent-sandbox.io/model'] ??
                '',
            ),
          agentType:
            techdocsValues.agentType ??
            String(
              entity.metadata?.annotations?.[
                'rhdh-agent-sandbox.io/agent-type'
              ] ?? '',
            ),
        });

        entity.metadata = entity.metadata ?? {};
        entity.metadata.annotations = entity.metadata.annotations ?? {};
        entity.metadata.annotations['backstage.io/techdocs-ref'] =
          `dir:${agentDocsDir}`;
        await fs.writeFile(catalogInfoPath, yaml.stringify(entity));
      }

      const locationTarget = `file:${catalogInfoPath}`;
      ctx.logger.info(`Registering catalog location ${locationTarget}`);

      const result = await catalog.addLocation(
        {
          type: 'file',
          target: locationTarget,
          onConflict: 'refresh',
        },
        { credentials: await ctx.getInitiatorCredentials() },
      );

      const registered =
        result.entities.find(e => e.metadata.name === name) ?? result.entities[0];

      if (!registered) {
        throw new Error(`Failed to register entity ${name}`);
      }

      ctx.output('entityRef', stringifyEntityRef(registered));
      ctx.output('catalogInfoPath', catalogInfoPath);
    },
  });
}
