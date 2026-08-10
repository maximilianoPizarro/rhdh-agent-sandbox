# AI capabilities

What this Sandbox chart demonstrates **today** (Guest Hub + DevSpaces AI).

## Capability map

| Capability | Delivery |
|---|---|
| Multi-model chat | Lightspeed → LiteLLM → Granite / Qwen |
| In-Hub MCP chat | MCP Chat plugin → LiteLLM + mcp-actions |
| Knowledge in Hub | TechDocs + catalog entities |
| Saved prompts | Catalog `Resource` (`type: prompt`) + `docs/prompts/` in scaffolds |
| Skills | Catalog `Resource` (`type: skill`) + `.continue/skills/` in scaffolds |
| MCP tools from Hub | mcp-actions-backend + software-catalog / TechDocs MCP extras |
| OpenShift / K8s MCP | Chart-deployed MCP servers (Lightspeed + DevSpaces) |
| MCP discovery | Catalog `Resource` (`type: mcp-server`) in ConfigMap |
| Agent-friendly IDE | Devfile + Continue → LiteLLM Route in DevSpaces |
| Golden Path agents | Deploy Agent template → catalog Component + Deployment/Service (no git push) |
| Sample agent Components | `sample-{python,nodejs,quarkus}-agent` with Open in DevSpaces |

## Community AI plugins (Backstage)

These are real [Backstage community plugins](https://backstage.io/plugins) loaded as RHDH 1.10 **dynamic plugins** from `ghcr.io/redhat-developer/rhdh-plugin-export-overlays` (source: [backstage/community-plugins](https://github.com/backstage/community-plugins) / Backstage core).

| Plugin | OCI package (tag) | Role |
|---|---|---|
| MCP Actions Backend | `backstage-plugin-mcp-actions-backend:bs_1.49.4__0.1.11` | Streamable HTTP MCP server at `/api/mcp-actions/v1` |
| Software Catalog MCP extras | `…software-catalog-mcp-extras:bs_1.49.4__0.2.2` | Catalog tools for mcp-actions |
| TechDocs MCP extras | `…techdocs-mcp-extras:bs_1.49.4__0.2.3` | TechDocs tools for mcp-actions |
| MCP Chat (frontend) | `backstage-community-plugin-mcp-chat:bs_1.49.4__0.6.0` | Hub UI tab at `/mcp-chat` |
| MCP Chat (backend) | `backstage-community-plugin-mcp-chat-backend:bs_1.49.4__0.8.0` | Chat API → LiteLLM + MCP servers |

After install, open **MCP Chat** in the Hub sidebar. Provider defaults to LiteLLM (`granite`). MCP Chat connects to OpenShift MCP, Kubernetes MCP, and Hub mcp-actions (catalog / TechDocs extras). External MCP clients (Cursor, Continue) can call `https://<hub-route>/api/mcp-actions/v1` with the `mcp-token` from the chart secret.

### Tool calling limitation

Shared Granite / Qwen behind Sandbox oauth-proxy do **not** support `tool_choice` / function calling:

- MCP Chat + LiteLLM: chat works; the model will not autonomously call MCP tools (you can still browse tools in the UI).
- MCP Chat + your own OpenAI / Claude / Gemini key: full agentic tool use.
- MCP Actions Backend: always usable from clients that bring their own model.

### Evaluated and not included

| Plugin | Why skipped |
|---|---|
| Agent Forge | Inactive in the plugin directory; needs external CAIPE platform |
| Roadie RAG AI | Reference-only; needs PGVector and is minimally maintained |
| AWS Generative AI | Experimental; LangGraph + Bedrock dependency chain |

## Discover in Catalog (Guest)

1. Sign in as **Guest**.  
2. Open **Catalog**.  
3. Filter by tags or types:

| Filter | What you should see |
|---|---|
| tag `mcp` / type `mcp-server` | OpenShift and Kubernetes MCP entities |
| tag `skill` / type `skill` | e.g. DevSpaces AI, OpenShift MCP, Lightspeed RAG |
| tag `prompt` / type `prompt` | Triage namespace, explain catalog, scaffold DevSpaces |
| Templates | Deploy Agent (Golden Path), DevSpaces AI Workspace, AI service skeleton |
| tag `agent` | Sample + golden-path agent Components |
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
| Quay community packs | Optional OCI asset bundles for Continue/skills (not in the Hub image). **Not** loaded as RHDH dynamic plugins. |
| Cursor Remote SSH / proxy | Out of the primary demo path (see [optional note](devspaces-cursor.md)). |
| Public MCP Routes | OpenShift/K8s MCP stay ClusterIP; Hub MCP Actions is on the Hub Route (token-gated). |
| RBAC / `permission.enabled: true` | Off for Guest demo. |
