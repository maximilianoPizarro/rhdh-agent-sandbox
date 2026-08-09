# ${{ values.name | default "ai-service-service" }}

Agent-friendly workspace for OpenShift DevSpaces (browser IDE + Continue → LiteLLM).

## Open in DevSpaces

1. Push this repo (or use a DevSpaces factory URL / import from Git).
2. Create a workspace from `devfile.yaml` in OpenShift DevSpaces.
3. Wire Continue to LiteLLM:

```bash
export LITELLM_API_BASE="https://$(oc get route -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')/v1"
export LITELLM_API_KEY="$(oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.litellm-master-key}' | base64 -d)"
# then run Devfile command wire-continue, or edit .continue/config.json
```

Models: `granite` (default), `qwen3`.

## Skills and prompts

- Skills: `.continue/skills/`
- Prompts: `docs/prompts/`
- Discover the same assets in Developer Hub Catalog (tags `skill` / `prompt`) while logged in as **Guest**.

## Hub agent loop

Use Developer Hub Lightspeed (guest) for MCP tool-calling against the namespace. This workspace uses LiteLLM for code assistance only.
