---
title: Golden Paths
---

# Golden Paths

Deploy namespace-scoped agents from Developer Hub **without git push**. The primary path is **Deploy Agent**: it generates **real** framework source, starts a **BuildConfig**, and deploys the resulting image.

![Deploy Agent Golden Path]({{ '/assets/diagrams/golden-path-deploy-agent.png' | relative_url }})

## Deploy Agent

| Field | Role |
|---|---|
| `name` | Deployment / Service / BuildConfig / ImageStream name |
| `owner` | Catalog owner (Group) |
| `language` | Selects framework skeleton + build |
| `agentType` | `tool-agent` / `chat-agent` / `rag-agent` (selects tools in generated code) |
| `agentSpec` | Injected as agent behaviour / system prompt |
| `model` | LiteLLM alias (`granite`, `qwen3`, or `litemaas-qwen`) |

### Framework map (fixed)

| language | default agentType | framework (real code) |
|---|---|---|
| python | tool-agent | **LangGraph** `StateGraph` + FastAPI |
| nodejs | tool-agent | **LangChain.js** `createReactAgent` |
| quarkus | tool-agent | **LangChain4j** `@RegisterAiService` |

No LLM chooses the framework — the scaffolder logs the map and stamps annotations. The **agent-applier** builds from chart source assets and deploys the ImageStream tag.

### What you get

1. **Generated source** for the selected framework (under `files/templates/skeletons/deploy-agent/<language>/`).
2. **Catalog Component** with `rhdh-agent-sandbox.io/managed-agent=true` and `rhdh-agent-sandbox.io/build=true`.
3. **BuildConfig + ImageStream** created/updated by the agent-applier; binary Docker build of the skeleton.
4. **Deployment + Service (ClusterIP)** using `image-registry.../<name>:latest`. Runtime talks to LiteLLM over Service DNS.

### Tools by agentType

| agentType | Tools in generated code |
|---|---|
| tool-agent | list pods, get deployment, Red Hat CVE lookup, product lifecycle |
| chat-agent | none (conversation only) |
| rag-agent | docs search hints + product lifecycle |

Red Hat security/lifecycle tools use public APIs; see also [Red Hat agentic skills](https://www.redhat.com/en/agentic-skills).

### Run it (Guest)

1. Hub → **Create** → **Deploy Agent (Golden Path)**.
2. Fill name, language, agentSpec, model → Create.
3. As OpenShift user:
   ```bash
   oc get bc/<name>
   oc logs -f bc/<name>
   oc get deploy/<name>
   oc logs deploy/<name>
   ```
4. Open the Component → **Open skeleton in DevSpaces**.

### Sample agents

Sample Deployments were removed from the chart. Use **Deploy Agent** to generate and build a real LangGraph / LangChain.js / LangChain4j agent.

## DevSpaces AI Workspace

Creates a **started** DevWorkspace (Continue → LiteLLM) for the language you select. No git push.

| Field | Role |
|---|---|
| `name` | DevWorkspace + catalog Component name |
| `owner` | Catalog owner (Group) |
| `language` | Skeleton / framework: python → LangGraph, nodejs → LangChain.js, quarkus → LangChain4j |
| `model` | Default Continue autocomplete/chat alias |

### What you get

1. Catalog Component with `rhdh-agent-sandbox.io/managed-devworkspace=true`.
2. **agent-applier** creates `DevWorkspace` (`started: true`, Che Code, Continue postStart).
3. Workspace clones this repo and materializes `files/templates/skeletons/<language>/` with Continue wired to the chart Continue Secret.

### Run it (Guest)

1. Hub → **Create** → **Agent-friendly DevSpaces AI Workspace**.
2. Pick language + model → Create.
3. Open [DevSpaces dashboard](https://workspaces.openshift.com/dashboard/#/workspaces) → open your workspace.

## AI Service with MCP wiring

Registers a Component and deploys a small HTTP service that **calls MCP for real**:

| Endpoint | Action |
|---|---|
| `GET /` | Service info + MCP URLs + LiteLLM model |
| `GET /mcp/smoke` | `pods_list_in_namespace` (k8s-mcp) + `monitorDeployments` (openshift-mcp) |

Catalog `dependsOn`: OpenShift MCP, Kubernetes MCP, Hub MCP Actions, **Red Hat Security MCP** (SSO via Cursor — Hub cannot complete browser OAuth).

## Related

- [Agents]({{ '/agents/' | relative_url }}) — Hub / Pod / DevSpaces loops  
- [Quickstart]({{ '/quickstart/' | relative_url }}) — install  
- [Architecture]({{ '/architecture/' | relative_url }}) — end-to-end picture  
