# DevSpaces AI workspace

## When to use
Coding inside OpenShift DevSpaces (Che Code) with Continue pointed at the sandbox LiteLLM gateway.

## Steps
1. Start the workspace from this repo's `devfile.yaml` in OpenShift DevSpaces.
2. In the browser IDE, open Continue.
3. Set `LITELLM_API_BASE` to the LiteLLM Route (`…/v1`) and `LITELLM_API_KEY` from secret `rhdh-agent-sandbox-secrets` key `litellm-master-key`.
4. Run the Devfile command `wire-continue` (or edit `.continue/config.json`).
5. Models: `granite` (default) or `qwen3`.
6. Use Hub guest login for Lightspeed + MCP catalog tools; this workspace talks to LiteLLM for code assistance.
