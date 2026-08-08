# Lightspeed and models

LiteLLM exposes OpenAI-compatible endpoints inside the namespace and routes to:

| Alias | Upstream InferenceService |
|---|---|
| `granite` | `isvc-granite-31-8b-fp8` in `sandbox-shared-models` |
| `qwen3` | `isvc-qwen3-8b-fp8` in `sandbox-shared-models` |

Lightspeed is configured to use the LiteLLM Service via the shared secret `rhdh-agent-sandbox-secrets` (`VLLM_URL` / `OPENAI_*` keys).

MCP servers registered in LiteLLM config:

- OpenShift MCP Quarkus service
- Kubernetes MCP service

Test LiteLLM (after Route is ready):

```bash
ROUTE=$(oc get route -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')
KEY=$(oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.litellm-master-key}' | base64 -d)
curl -sS "https://${ROUTE}/v1/models" -H "Authorization: Bearer ${KEY}"
```
