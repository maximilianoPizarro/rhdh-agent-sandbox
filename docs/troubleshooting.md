# Troubleshooting

## LiteLLM 401 to shared models

Refresh the Sandbox token:

```bash
oc set env secret/rhdh-agent-sandbox-secrets model-api-key="$(oc whoami -t)"
oc rollout restart deploy -l app.kubernetes.io/component=litellm
```

## RHDH Route host wrong

Set the correct apps domain:

```bash
helm upgrade rhdh-agent . -f values-sandbox.yaml \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --reuse-values
```

## Pods Pending / quota

Disable optional pieces:

```bash
--set mcp.kubernetes.enabled=false \
--set litellm.route.enabled=false
```

Lower RHDH memory in `values-sandbox.yaml` if needed.

## Guest login missing

Confirm `auth.environment: development` and `auth.providers.guest.dangerouslyAllowOutsideDevelopment: true` in `values-sandbox.yaml`, then `helm upgrade` and restart the Hub deployment. Guest is demo-only; set `auth.environment: production` to hide it.

## Hub readiness 503 / GitHub catalog provider

If logs show `Either organization or app must be specified`, disable the GitHub catalog module (default in `values-sandbox.yaml`) or set `catalog.providers.github` with an org/app. Sandbox demo uses URL catalog locations instead.

## Hub readiness 503 / postgres auth or missing `BACKEND_SECRET`

Helm **replaces** `upstream.backstage.extraEnvVars` arrays. Keep both chart defaults when overriding:

- `BACKEND_SECRET` → `rhdh-agent-sandbox-secrets` / `backend-secret`
- `POSTGRESQL_ADMIN_PASSWORD` → `rhdh-agent-postgresql` / `postgres-password`

See `values-sandbox.yaml`. Without them you get `password authentication failed for user "postgres"` or `Missing required config value at 'backend.auth.externalAccess[0].options.secret'`.

```bash
helm upgrade rhdh-agent . -f values-sandbox.yaml \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com
oc rollout status deploy/rhdh-agent-developer-hub
```

## Catalog entities missing

Ensure the GitHub repo is public (URL locations) or apply/sync ConfigMap `rhdh-agent-sandbox-catalog` contents into a catalog location RHDH can read.

## MCP permission errors

MCP ServiceAccount only has **namespace** Role access. Cluster-scoped tools will fail by design on Developer Sandbox.
