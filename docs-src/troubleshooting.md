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
