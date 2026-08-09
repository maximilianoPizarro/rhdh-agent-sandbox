# AI capabilities

What this Sandbox chart demonstrates **today** (Guest Hub + DevSpaces AI).

## Capability map

| Capability | Delivery |
|---|---|
| Multi-model chat | Lightspeed → LiteLLM → Granite / Qwen |
| Knowledge in Hub | TechDocs + catalog entities |
| Saved prompts | Catalog `Resource` (`type: prompt`) + `docs/prompts/` in scaffolds |
| Skills | Catalog `Resource` (`type: skill`) + `.continue/skills/` in scaffolds |
| MCP tools from Hub | RHDH mcp-actions + OpenShift MCP + Kubernetes MCP |
| MCP discovery | Catalog `Resource` (`type: mcp-server`) in ConfigMap |
| Agent-friendly IDE | Devfile + Continue → LiteLLM Route in DevSpaces |

## Discover in Catalog (Guest)

1. Sign in as **Guest**.  
2. Open **Catalog**.  
3. Filter by tags or types:

| Filter | What you should see |
|---|---|
| tag `mcp` / type `mcp-server` | OpenShift and Kubernetes MCP entities |
| tag `skill` / type `skill` | e.g. DevSpaces AI, OpenShift MCP, Lightspeed RAG |
| tag `prompt` / type `prompt` | Triage namespace, explain catalog, scaffold DevSpaces |
| Templates | Agent-friendly DevSpaces AI Workspace, AI service skeleton |
| Groups | `developers`, `guests` |

Entities are loaded from the **ConfigMap mount** (`/opt/app-root/src/catalog`), not from a live GitHub poll.

## Skills and prompts in repos

Software Templates and shared skeletons embed IDE assets:

| Path | Purpose |
|---|---|
| `.continue/config.json` | Models → LiteLLM |
| `.continue/skills/*/SKILL.md` | Agent skills for Continue |
| `docs/prompts/*.md` | Saved prompts aligned with catalog annotations |
| `devfile.yaml` | DevSpaces workspace definition |

Catalog annotations point at these stable paths so Hub and the IDE tell the same story.

## MCP scope

- Tools run with a ServiceAccount limited to the **user namespace**.  
- Cluster-scoped operations fail by design on Developer Sandbox.  
- Prefer list/get before mutate; Lightspeed system prompt reinforces that.

## What is not claimed

| Topic | Reality |
|---|---|
| GHCR community packs | Optional asset bundles for Continue/skills. **Not** loaded as RHDH dynamic plugins. |
| Cursor Remote SSH / proxy | Out of the primary demo path (see [optional note](devspaces-cursor.md)). |
| Public MCP Routes | Not exposed; Hub uses ClusterIP. |
| RBAC / `permission.enabled: true` | Off for Guest demo. |
