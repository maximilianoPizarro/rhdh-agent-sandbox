# Architecture

```text
Cursor (local)
    | Remote SSH
DevSpaces workspace
    ^
Developer Hub (RHDH)
    |-- Lightspeed ---- LiteLLM ---- sandbox-shared-models (Granite / Qwen)
    |-- MCP Actions (catalog / techdocs)
    |-- OpenShift MCP + Kubernetes MCP (namespace RBAC)
    '-- Catalog: Skills / Prompts / MCP server entities
```

## Helm pieces

| Component | Source |
|---|---|
| RHDH 1.10 | dependency `redhat-developer-hub` |
| LiteLLM | chart templates |
| MCP servers | chart templates (images from existing MCP builds) |
| AI catalog | ConfigMap + GitHub locations + GHCR catalog index |
| DevSpaces | Devfiles + Software Templates (operator assumed available on Sandbox) |
