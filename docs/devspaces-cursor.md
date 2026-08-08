# DevSpaces + Cursor

## Goal

Give developers a remote workspace close to an agent-friendly IDE loop:

1. Scaffold or open a repo with a Devfile (Hub Software Template or `files/devfiles/devfile.yaml`).
2. Start the workspace in **OpenShift DevSpaces** (available on Developer Sandbox).
3. Connect **Cursor** using Remote SSH / DevSpaces tooling.
4. Use Hub Skills, Prompts, and MCP tools while coding.

## Template

Use **Agent-friendly DevSpaces Workspace** from Developer Hub Create.

It generates:

- `devfile.yaml`
- `catalog-info.yaml`
- README with Cursor connection notes

## Cursor tips

- Install Remote SSH (and DevSpaces-related extensions if prompted).
- Keep cluster mutations namespace-scoped (Sandbox RBAC).
- Install skills from Catalog Resources tagged `skill` into `.cursor/skills/`.
- Prefer saved prompts tagged `prompt` for repeatable agent tasks.

## MCP from the workspace

From inside the cluster network, MCP services are reachable at:

- `http://rhdh-agent-sandbox-mcp:8080/mcp`
- `http://rhdh-agent-sandbox-k8s-mcp:8085/mcp`

(Release name prefix may vary if you change `fullnameOverride` / release name.)
