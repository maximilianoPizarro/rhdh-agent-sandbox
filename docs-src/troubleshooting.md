---
title: Troubleshooting
---

# Troubleshooting

## LiteLLM 401 to shared models

Symptoms: `/v1/models` works with the master key, but chat returns 401 / upstream auth errors; or chat worked yesterday and fails today.

```bash
oc patch secret/rhdh-agent-sandbox-secrets --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy -l app.kubernetes.io/component=litellm
```

Confirm the LiteLLM pod picked up the new key (`oc exec … -- env | grep MODEL_API_KEY`).

## Lightspeed chat empty / “Error while processing query”

Check sidecar logs:

```bash
HUB=$(oc get pods -o name | grep developer-hub | head -1 | sed 's|pod/||')
oc logs "$HUB" -c lightspeed-core --tail=100
```

| Cause | Fix |
|---|---|
| `tool_choice=auto` / BadRequest from Granite | Chart must set `supports_function_calling: false` + drop tool params in LiteLLM ConfigMap. Re-upgrade chart. |
| `Incorrect API key` / OpenAI provider | Remove `ENABLE_OPENAI` / `OPENAI_*` from the secret. Only `ENABLE_VLLM=true` + `VLLM_URL` → LiteLLM. |
| `model-api-key` is `replace-me` | Patch token (above) and restart LiteLLM. Helm preserves the key when you pass `--set secrets.modelApiKey=…` or when the existing secret already has a real value. |
| Wrong model id | Use provider `vllm` + model `granite` (UI: `vllm/granite`). |

## LiteLLM OOMKilled / CrashLoopBackOff

LiteLLM needs more than 512Mi. Defaults in `values.yaml` request 512Mi / limit **1536Mi**. If the live Deployment still shows 512Mi limit, upgrade the chart or:

```bash
oc set resources deploy/rhdh-agent-sandbox-litellm \
  --requests=cpu=50m,memory=512Mi \
  --limits=cpu=500m,memory=1536Mi
```

## RHDH Route host wrong

```bash
helm upgrade rhdh-agent . \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --reuse-values
```

## Pods Pending / quota

```bash
oc describe resourcequota
```

Mitigations:

```bash
helm upgrade rhdh-agent . \
  --reuse-values \
  --set mcp.kubernetes.enabled=false
```

Stop DevSpaces workspaces. Lower Hub memory in `values.yaml` if needed.

## Guest login missing

Confirm in `values.yaml`:

- `auth.environment: development`  
- `auth.providers.guest.dangerouslyAllowOutsideDevelopment: true`  
- `permission.enabled: false`  

Then `helm upgrade` and restart the Hub Deployment.

## Hub readiness 503 / GitHub catalog provider

Logs: `Either organization or app must be specified`.

GitHub catalog/scaffolder modules are **disabled** in `values.yaml`. Catalog loads from the ConfigMap **file** location. Do not re-enable GitHub modules without org/app config.

## Hub readiness 503 / postgres or BACKEND_SECRET

Helm **replaces** `extraEnvVars` arrays. Keep:

| Env | Secret / key |
|---|---|
| `BACKEND_SECRET` | `rhdh-agent-sandbox-secrets` / `backend-secret` |
| `MCP_TOKEN` | `rhdh-agent-sandbox-secrets` / `mcp-token` |
| `POSTGRESQL_ADMIN_PASSWORD` | `rhdh-agent-postgresql` / `postgres-password` |

Same for `extraVolumes` / `extraVolumeMounts`: keep RHDH dynamic-plugins defaults **plus** the catalog ConfigMap mount.

```bash
helm upgrade rhdh-agent . \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com
oc rollout status deploy/rhdh-agent-developer-hub
```

## Catalog entities missing

```bash
oc exec deploy/rhdh-agent-developer-hub -c backstage-backend -- ls /opt/app-root/src/catalog
```

If empty, check ConfigMap `rhdh-agent-sandbox-catalog` and Hub volume mount `rhdh-agent-catalog`.

## DevSpaces Continue cannot reach models

If the picker says **No models configured**, Continue 2 is reading an empty `~/.continue/config.yaml` — see [Continue shows no models](#devspaces-continue-shows-no-models--no-mcp-servers).

Otherwise:

1. LiteLLM **Route** up?  
2. Continue `apiBase` ends with `/v1`?  
3. API key = `litellm-master-key` (not OpenShift token)?  
4. Shared models token fresh if LiteLLM itself 401s upstream?

## MCP permission errors

Namespace Role only. Cluster-scoped tools fail by design. Stay inside the user project.

## OpenClaw cannot use tools with shared models

OpenClaw provisioned from sandbox.redhat.com needs **LiteMaaS Qwen** (or an external vendor key) for agentic tool use. Shared Granite/Qwen via this chart’s LiteLLM reject `tool_choice` / function calling — the chart intentionally drops those params so Lightspeed stays stable. Pointing OpenClaw only at LiteLLM is chat-only. Keep `agents.defaults.sandbox.mode: "off"` on Developer Sandbox (no Docker daemon). See [OpenClaw]({{ '/openclaw/' | relative_url }}).

## OpenClaw MCP probe fails against Hub (403 / 405)

| Symptom | Cause | Fix |
|---|---|---|
| `Proxy response (403)` | Hub Route host not on claw-proxy allowlist | Declare Hub MCP on the **Claw CR** (`spec.mcpServers` + credential). Operator regenerates proxy routes. Manual `openclaw mcp add` alone is not enough on Sandbox. |
| `Non-200 status code (405)` with `transport: sse` | RHDH MCP Actions expects streamable HTTP | Set `transport: streamable-http` on `spec.mcpServers.hub-mcp-actions` |
| ClusterIP Hub Service timeout from `*-claw` | Cross-namespace NetworkPolicy | Use the **public Hub Route** (allowlisted via Claw CR), not `*.svc` |

Verify: `oc exec -n <claw-ns> deploy/claw -c gateway -- openclaw mcp probe` → `hub-mcp-actions: 4 tools`.

## MCP Chat loads but tools never fire

Default provider is LiteLLM → Granite. Shared models do not support function calling, so chat replies without tool invocations. Browse tools in the MCP Chat sidebar to confirm servers are connected. For agentic calls, set `mcpChat.providers` to openai/claude/gemini with your own API key (Secret + env). See [AI capabilities]({{ '/ai-capabilities/' | relative_url }}).

If **Backstage MCP Actions** shows disconnected at startup, that is an init race (mcp-chat connects before `/api/mcp-actions/v1` is registered). OpenShift/Kubernetes MCP servers are listed first and should connect. Re-open MCP Chat or restart the Hub pod after warm-up; external clients can still call the Hub Route MCP endpoint with `mcp-token`.

## MCP / community OCI plugins fail to install

Init container `install-dynamic-plugins` must pull from `ghcr.io/redhat-developer/rhdh-plugin-export-overlays`. Check:

```bash
oc logs deploy/rhdh-agent-developer-hub -c install-dynamic-plugins | grep -iE 'mcp-chat|mcp-actions|Successfully installed|ERROR|denied'
```

Confirm the tag matches RHDH 1.10 / Backstage `1.49.4` (`bs_1.49.4__…`) and the cluster can reach ghcr.io.

## Stale secret keys after upgrade

If old `ENABLE_OPENAI` keys linger, replace the secret data (chart uses `data:` so Helm merge can drop keys) or:

```bash
# after a good helm upgrade, confirm keys:
oc get secret rhdh-agent-sandbox-secrets -o json | python -c "import json,sys; print(sorted(json.load(sys.stdin)['data']))"
```

You should **not** see `ENABLE_OPENAI` / `OPENAI_API_KEY`. Then restart Hub so `lightspeed-core` reloads envFrom.

## DevSpaces: “has not received an IDE URL”

The dashboard can show **Running** while **Open IDE** fails with *The workspace has not received an IDE URL in the last 20 seconds*.

Golden Path workspaces are created by **agent-applier**, not the Dev Spaces dashboard. The `che.eclipse.org/che-editor` annotation does not inject Che Code. The DevWorkspace needs `spec.contributions` pointing at the chart DevWorkspaceTemplate `rhdh-agent-sandbox-che-code` (endpoint 3100 → `status.mainUrl`).

New workspaces get this after a chart upgrade. For an existing workspace:

```bash
DWT=$(oc get dwt -o name | grep che-code | head -1 | sed 's|.*/||')
oc patch dw <workspace> --type=merge \
  -p "{\"spec\":{\"contributions\":[{\"name\":\"editor\",\"kubernetes\":{\"name\":\"${DWT}\"}}]}}"
oc patch dw <workspace> --type=merge -p '{"spec":{"started":false}}'
oc patch dw <workspace> --type=merge -p '{"spec":{"started":true}}'
oc get dw <workspace> -o jsonpath='{.status.phase} {.status.mainUrl}{"\n"}'
```

Then reopen the workspace from the Dev Spaces dashboard.

## DevSpaces: Continue shows no models / no MCP servers

Continue **2.x** reads **`~/.continue/config.yaml`** (home directory), not project `.continue/config.json`. The left CHAT panel is Continue — keep the extension.

```bash
POD=$(oc get pod -l controller.devfile.io/devworkspace_name=<workspace> -o jsonpath='{.items[0].metadata.name}')
oc exec "$POD" -c tools -- python3 /opt/rhdh-agent-sandbox/wire-continue.py
```

Reload the Che Code window. You should see Granite / Qwen3 / LiteMaaS Qwen and MCP server `hub-mcp-actions` (4 catalog/TechDocs tools).

**“New MCP server” / Connection closed:** Continue 2 writes `.continue/mcpServers/new-mcp-server.yaml` with a placeholder `npx -y <your-mcp-server>`. Toggle it **off** or delete that file — `wire-continue` now removes it. It is not a Hub or Red Hat server.

**Chat vs Agent:** Continue disables tools in Chat. Switch to **Agent** or **Plan** (`Ctrl+Alt+I` then the mode picker) before asking for MCP.

**Red Hat Security MCP:** Continue 2 cannot complete Customer Portal SSO against `127.0.0.1:3334` from Che Simple Browser (`code-redirect-*` → Express `Cannot GET /`). That is **not** a missing git push or a workspace regenerate.

`wire-continue` starts an SSO helper UI on a public HTTPS Route. Red Hat `mcp-client` only allows `http://127.0.0.1:3334/oauth/callback` (DCR echoes other URIs but authorize returns `redirect_uri not allowed`). Open the helper, click **Conectar con Red Hat**, then **paste** the failed `127.0.0.1:3334` URL back into the helper.

Do this:

1. Close any Simple Browser tab that shows `Cannot GET /` (that is `code-redirect`, not the helper).
2. Open the **HTTPS** helper URL printed by `auth-rh-security-mcp` (or the dedicated `*-rh-oauth` Route). Do not use Che `code-redirect` or `http://` on the default `http-8080` endpoint — that Route is not TLS unless the Devfile sets `secure: true`.
3. Click **Conectar con Red Hat**, grant access on Customer Portal, wait to land back on the helper.
4. Continue Tools → **red-hat-security** off/on, **Agent** or **Plan** mode.

Until the official MCP accepts the token (`initialize` 200, scope `api.graphql`), Continue may show one setup tool (`redhat_security_connect`) instead of `Connection closed`. Cursor still uses repo `.mcp.json` (`type: http`).

No Helm upgrade is required for an already-running workspace: copy/start the helper in the tools container. Do **not** change ConfigMap `*-wire-continue` just to pick this up — that ConfigMap is watched and restarts DevWorkspaces.

## Topology tab is empty after Deploy Agent

No git push is required. Golden Path registers a catalog ConfigMap; `agent-applier` binary-builds from the chart skeleton and creates the Deployment.

Topology stays empty until that Deployment exists. Quarkus images often take 2–4 minutes. Refresh the Component page after:

```bash
oc get build,deploy,svc <name>
```

`Complete` + `deploy/<name> 1/1` means Topology should show the workload (`app.kubernetes.io/name=<name>` in this namespace).

## API Definition / Swagger Execute shows no response

The catalog OpenAPI used to list `/invoke` and `/mcp/tools`, which the agent does not implement. Try-it-out also had no `servers` URL, so Execute called the **Hub** origin and hung (Cancel, empty Responses).

Real endpoints: `GET /`, `GET /health`, `GET /v1/runtime`, `POST /v1/chat`. The applier now creates a Route and CORS so Swagger can call the agent. Recreate the Component or refresh the API entity after upgrade.

Until then:

```bash
oc create route edge <name> --service=<name> --insecure-policy=Redirect
oc exec deploy/<name> -- curl -sS http://127.0.0.1:8080/health
```

## Scaffolder Verify step shows “Network error”

The verify action (`catalog:wait-for-entity`) often keeps running in Hub after the browser drops the task event-stream. OpenShift Routes default to a **30s** timeout; catalog ingest via ConfigMap mount can take ~60–90s.

The chart sets `haproxy.router.openshift.io/timeout: 5m` on the Hub Route. Confirm:

```bash
oc annotate route rhdh-agent-developer-hub \
  haproxy.router.openshift.io/timeout=5m --overwrite
```

Then open **Catalog** and search for the Component name. If it is there, the task actually succeeded — reload the task page. Plugin 0.1.2+ ingests the entity immediately (no ConfigMap-mount wait) and polls the in-process catalog client instead of `localhost:7007`.

## Reinstall (Helm only)

Prefer `helm upgrade --install` with a fresh `oc whoami -t`. That preserves chart secrets and the Postgres PVC.

To uninstall and install again:

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
oc delete pvc data-rhdh-agent-postgresql-0 --ignore-not-found
export MODEL_API_KEY=$(oc whoami -t)
helm dependency update
helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

Then [Verify the install]({{ '/verify/' | relative_url }}).

`helm uninstall` does not always remove everything in the namespace:

| Left after uninstall | Symptom on next install |
|---|---|
| PVC `rhdh-agent-postgresql` | Hub 503 — new password vs old volume |
| Golden Path Deploy/BC/IS | Pods Pending (quota) |
| DevWorkspaces | Same quota; Continue Secret is gone |
| Pending catalog ConfigMaps | agent-applier may recreate old agents |
