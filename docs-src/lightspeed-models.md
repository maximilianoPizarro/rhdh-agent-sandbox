# Lightspeed and models

## Model aliases

LiteLLM exposes OpenAI-compatible endpoints:

| LiteLLM alias | Upstream InferenceService |
|---|---|
| `granite` | `isvc-granite-31-8b-fp8` in `sandbox-shared-models` |
| `qwen3` | `isvc-qwen3-8b-fp8` in `sandbox-shared-models` |

In the Lightspeed UI / llama-stack, models appear as **`vllm/granite`** and **`vllm/qwen3`**. Hub `lightspeed.servers` in `values.yaml` uses those ids.

## How Hub Lightspeed is wired

1. **Secret** `rhdh-agent-sandbox-secrets` (mounted into `lightspeed-core` via `envFrom`):

   | Key | Value |
   |---|---|
   | `ENABLE_VLLM` | `true` |
   | `VLLM_URL` | `http://rhdh-agent-sandbox-litellm:4000/v1` |
   | `VLLM_API_KEY` | LiteLLM master key |
   | `VLLM_TLS_VERIFY` | `false` |

2. **Do not set `ENABLE_OPENAI`**. That provider targets api.openai.com and will break model refresh with a 401 on a LiteLLM-shaped key.

3. **appConfig** (`values.yaml` → `rhdh.upstream.backstage.appConfig.lightspeed`):

   - `servers`: `vllm/granite`, `vllm/qwen3` → LiteLLM Service URL  
   - `mcpServers`: `mcp-integration-tools` with `${MCP_TOKEN}`  

4. **lightspeed-stack** ConfigMap (chart) points MCP integration tools at `http://localhost:7007/api/mcp-actions/v1`.

!!! note "Guest users never paste tokens"
    Operators refresh `model-api-key`. Guests only use the Hub UI.

## LiteLLM behaviour on Sandbox

Shared Granite/Qwen reject `tool_choice=auto` (they are not started with `--enable-auto-tool-choice`). The chart sets:

- `supports_function_calling: false`
- `additional_drop_params` for `tool_choice` / `tools` / …

Without that, Lightspeed returns HTTP 200 with an empty stream and `Error while obtaining answer` in `lightspeed-core` logs.

## DevSpaces Continue

Continue uses the **LiteLLM Route** (public) + `litellm-master-key`, models `granite` / `qwen3`. See [DevSpaces AI](devspaces-ai.md).

## Refresh model token (~24h)

```bash
oc patch secret/rhdh-agent-sandbox-secrets --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm
```

## Test from your laptop

```bash
ROUTE=$(oc get route -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')
KEY=$(oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.litellm-master-key}' | base64 -d)

curl -sk "https://${ROUTE}/v1/models" -H "Authorization: Bearer ${KEY}"

curl -sk "https://${ROUTE}/v1/chat/completions" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"granite","messages":[{"role":"user","content":"Say hi"}],"max_tokens":16}'
```

Full checklist: [Verify the install](verify.md).
