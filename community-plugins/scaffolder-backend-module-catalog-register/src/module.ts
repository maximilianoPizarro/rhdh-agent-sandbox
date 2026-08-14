import { createBackendModule } from '@backstage/backend-plugin-api';
import { catalogServiceRef } from '@backstage/plugin-catalog-node';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node';
import { createApplyPendingConfigMapAction } from './actions/createApplyPendingConfigMapAction';
import { createCatalogRegisterEntityAction } from './actions/createCatalogRegisterEntityAction';
import { createRemoveEntityAction } from './actions/createRemoveEntityAction';
import { createWaitForEntityAction } from './actions/createWaitForEntityAction';

export const catalogRegisterEntityModule = createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'catalog-register-entity',
  register(env) {
    env.registerInit({
      deps: {
        scaffolder: scaffolderActionsExtensionPoint,
        catalog: catalogServiceRef,
      },
      async init({ scaffolder, catalog }) {
        scaffolder.addActions(
          createApplyPendingConfigMapAction({ catalog }),
          createWaitForEntityAction({ catalog }),
          createRemoveEntityAction(),
          createCatalogRegisterEntityAction({
            catalog,
            registeredRoot:
              process.env.CATALOG_REGISTER_ROOT ??
              '/opt/app-root/src/scaffolder-registered',
            techdocsAgentTemplate:
              process.env.TECHDOCS_AGENT_TEMPLATE ??
              '/opt/app-root/src/techdocs/agents/_template',
          }),
        );
      },
    });
  },
});
