# rhdh-agent-sandbox

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/rhdh-agent-sandbox)](https://artifacthub.io/packages/helm/rhdh-agent-sandbox/rhdh-agent-sandbox)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maximilianopizarro.github.io/rhdh-agent-sandbox/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Agent-friendly Red Hat Developer Hub** on **OpenShift Developer Sandbox** — an umbrella Helm chart that deploys a fully wired AI developer platform in a single command.

## What you get

| Component | Description |
|---|---|
| **Red Hat Developer Hub** (RHDH 1.10) | Backstage-based portal with Guest + GitHub login, Lightspeed AI assistant, MCP Chat, TechDocs, and Kubernetes plugin |
| **LiteLLM Proxy** | OpenAI-compatible gateway routing to Sandbox shared models (**Granite 3.1 8B**, **Qwen3 8B**) |
| **OpenShift MCP Server** (Quarkus) | Streamable-HTTP MCP server for cluster introspection — deployments, pods, logs, health checks |
| **Kubernetes MCP Server** | MCP server for namespace-scoped Kubernetes operations — pods, helm, resources, exec |
| **Backstage MCP Actions** | Software Catalog + TechDocs exposed as MCP tools for Lightspeed and external agents |
| **Agent Applier** | Reconciler that creates Deployment + Service from `managed-agent` catalog annotations |
| **Sample Agents** | Pre-deployed Python/LangGraph, Node.js/LangChain.js, and Quarkus/LangChain4j agents |
| **Golden Path Templates** | Self-service scaffolder for "Deploy Agent", "DevSpaces AI Workspace", and "AI Service with MCP" |
| **DevSpaces Integration** | Devfiles + Continue → LiteLLM config for browser-based AI coding |

## Prerequisites

- **OpenShift Developer Sandbox** (free tier) — or any OpenShift ≥ 4.14 cluster
- `oc` CLI logged in (`oc login`)
- `helm` ≥ 3.14

## Quick start

### From source (development)

```bash
git clone https://github.com/maximilianoPizarro/rhdh-agent-sandbox.git
cd rhdh-agent-sandbox

helm dependency update
helm upgrade --install rhdh-agent . \
  --namespace "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

### From Helm repository (production)

```bash
helm repo add rhdh-agent https://maximilianopizarro.github.io/rhdh-agent-sandbox
helm repo update

helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox \
  --namespace "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

### From Artifact Hub

Search for **rhdh-agent-sandbox** on [artifacthub.io](https://artifacthub.io/packages/helm/rhdh-agent-sandbox/rhdh-agent-sandbox) and follow the install instructions.

## Configuration

### Required parameters

| Parameter | Description |
|---|---|
| `secrets.modelApiKey` | OpenShift token for sandbox-shared-models oauth-proxy. Run `oc whoami -t`. Refreshes every ~24h. |
| `rhdh.global.clusterRouterBase` | Your cluster apps domain (e.g. `apps.rm2.thpm.p1.openshiftapps.com`) |

### Key optional parameters

| Parameter | Default | Description |
|---|---|---|
| `litellm.enabled` | `true` | Deploy the LiteLLM proxy |
| `litellm.models` | Granite + Qwen3 | Inference backends (name, modelId, apiBase) |
| `litellm.defaultModel` | `granite` | Default model alias |
| `mcp.enabled` | `true` | Deploy MCP servers |
| `mcp.quarkus.enabled` | `true` | OpenShift MCP server (Quarkus) |
| `mcp.kubernetes.enabled` | `true` | Kubernetes MCP server |
| `catalog.enabled` | `true` | Mount AI catalog ConfigMap |
| `agents.enabled` | `true` | Deploy sample agents + applier |
| `agents.applier.enabled` | `true` | Catalog-driven agent reconciler |
| `agents.hubRbac.enabled` | `true` | Namespace RBAC for scaffolder |
| `agents.samples` | 3 agents | Pre-created agent Deployments |
| `rhdh.enabled` | `true` | Deploy Red Hat Developer Hub |

The chart ships a `values.schema.json` that renders a form in the **OpenShift Console → Helm → Install** workflow.

See the full [`values.yaml`](values.yaml) for all configurable fields.

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│  OpenShift Developer Sandbox namespace                          │
│                                                                 │
│  ┌──────────────────┐    ┌───────────────┐   ┌──────────────┐  │
│  │  Developer Hub   │◄──►│  LiteLLM      │──►│ Granite/Qwen │  │
│  │  (Backstage)     │    │  Proxy :4000  │   │ shared-models│  │
│  │  • Lightspeed    │    └───────────────┘   └──────────────┘  │
│  │  • MCP Chat      │                                          │
│  │  • Catalog       │    ┌───────────────┐                     │
│  │  • Scaffolder    │◄──►│  OpenShift    │                     │
│  │  • TechDocs      │    │  MCP :8080    │                     │
│  │  • K8s Plugin    │    └───────────────┘                     │
│  └────────┬─────────┘                                          │
│           │              ┌───────────────┐                     │
│           │              │  Kubernetes   │                     │
│           └─────────────►│  MCP :8085    │                     │
│                          └───────────────┘                     │
│  ┌──────────────────────────────────────┐                      │
│  │  Agent Pods (Golden Path)            │                      │
│  │  • sample-python-agent  (LangGraph)  │                      │
│  │  • sample-nodejs-agent  (LangChain)  │                      │
│  │  • sample-quarkus-agent (LangChain4j)│                      │
│  │  • agent-applier (reconciler)        │                      │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

## Golden Paths (Self-service Templates)

| Template | Description |
|---|---|
| **Deploy Agent** | Create a namespace-scoped agent Pod. Picks framework from language (Python→LangGraph, Node.js→LangChain.js, Quarkus→LangChain4j). No git push needed. |
| **Agent-friendly DevSpaces AI Workspace** | Scaffolds a repo with Devfile, Continue→LiteLLM config, and skills for browser-based AI coding. |
| **AI Service with MCP wiring** | Scaffolds a small service + catalog Component/API entities for MCP and Lightspeed. |

## Token refresh

The Sandbox shared-models token expires every ~24h. To refresh:

```bash
oc patch secret/rhdh-agent-sandbox-secrets -n "$(oc project -q)" --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm
```

## Post-install verification

```bash
# Hub route
oc get route -l app.kubernetes.io/name=developer-hub -o jsonpath='{.items[0].spec.host}'

# All pods running
oc get pods -l app.kubernetes.io/instance=rhdh-agent

# LiteLLM health
curl -s "$(oc get route rhdh-agent-sandbox-litellm -o jsonpath='{.spec.host}')/health"

# MCP servers
oc logs deploy/rhdh-agent-sandbox-mcp --tail=5
oc logs deploy/rhdh-agent-sandbox-k8s-mcp --tail=5
```

## Repository layout

```text
Chart.yaml                # Umbrella chart + redhat-developer-hub dependency
values.yaml               # All configurable parameters
values.schema.json        # JSON Schema for OpenShift Console form
templates/                # Helm templates (Deployments, Services, ConfigMaps, RBAC)
files/                    # Catalog entities, scaffolder skeletons, agent runtimes
  catalog/                # Software Templates + sample-agents + catalog wiring
  templates/              # Scaffolder skeletons (deploy-agent, ai-service, devspaces)
  dynamic-plugins.yaml    # RHDH dynamic plugin configuration
  lightspeed-stack.yaml   # Lightspeed → MCP server wiring
docs-src/                 # MkDocs markdown source
docs/                     # Built MkDocs HTML + Helm repo artifacts (GitHub Pages)
community-plugins/        # OCI asset pack build scripts
.github/workflows/        # CI: lint, package, rebuild Pages
```

## Documentation

Full documentation at **https://maximilianopizarro.github.io/rhdh-agent-sandbox/**

| Page | Content |
|---|---|
| [Quickstart](https://maximilianopizarro.github.io/rhdh-agent-sandbox/quickstart/) | Install guide |
| [Golden Paths](https://maximilianopizarro.github.io/rhdh-agent-sandbox/golden-paths/) | Deploy agents without git push |
| [Architecture](https://maximilianopizarro.github.io/rhdh-agent-sandbox/architecture/) | Components, tokens, flows |
| [Agents](https://maximilianopizarro.github.io/rhdh-agent-sandbox/agents/) | Hub / Pod / DevSpaces agent loops |
| [AI Capabilities](https://maximilianopizarro.github.io/rhdh-agent-sandbox/ai-capabilities/) | Lightspeed, MCP, models |
| [DevSpaces AI](https://maximilianopizarro.github.io/rhdh-agent-sandbox/devspaces-ai/) | Browser IDE + Continue |
| [Verify](https://maximilianopizarro.github.io/rhdh-agent-sandbox/verify/) | Post-install checks |
| [Troubleshooting](https://maximilianopizarro.github.io/rhdh-agent-sandbox/troubleshooting/) | Common issues |

## Uninstall

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
