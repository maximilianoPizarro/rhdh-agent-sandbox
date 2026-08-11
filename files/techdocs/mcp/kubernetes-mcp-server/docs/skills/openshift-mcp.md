# OpenShift MCP tool-calling

## When to use
Namespace-scoped diagnostics and changes through MCP tools on Developer Sandbox.

## Rules
- Prefer list/get before mutate.
- Stay inside the current namespace (Sandbox has no cluster-admin).
- Summarize risk before create/update/delete.
- Refresh `model-api-key` daily (`oc whoami -t`) when LiteLLM calls shared models fail with 401.
