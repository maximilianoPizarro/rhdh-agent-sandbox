# rhdh-agent-sandbox

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/rhdh-agent-sandbox)](https://artifacthub.io/packages/helm/rhdh-agent-sandbox/rhdh-agent-sandbox)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maximilianopizarro.github.io/rhdh-agent-sandbox/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Agent-friendly Red Hat Developer Hub** on **OpenShift Developer Sandbox** — an umbrella Helm chart that deploys a fully wired AI developer platform in a single command.

Docs site: **https://maximilianopizarro.github.io/rhdh-agent-sandbox/** (Jekyll → GitHub Pages; share preview `1200×630` OG image).

## What you get

| Component | Description |
|---|---|
| **Red Hat Developer Hub** (RHDH 1.10) | Backstage portal with Guest + GitHub login, Lightspeed, MCP Chat, TechDocs, Kubernetes plugin |
| **LiteLLM Proxy** | OpenAI-compatible gateway to Sandbox shared models (**Granite**, **Qwen3**) |
| **OpenShift + Kubernetes MCP** | Namespace-scoped tools for Lightspeed / MCP Chat (ClusterIP) |
| **Backstage MCP Actions** | Software Catalog + TechDocs tools on Hub Route `/api/mcp-actions/v1` |
| **Agent Applier + samples** | Catalog-driven Deployments; Python/LangGraph, Node.js, Quarkus stubs with structured logs |
| **Golden Path Templates** | Deploy Agent, DevSpaces AI Workspace, AI Service with MCP |
| **DevSpaces + Continue** | Preinstalled Continue → LiteLLM; optional Hub MCP from the IDE |
| **OpenClaw (optional)** | Provisioned from sandbox.redhat.com (separate `*-claw` ns); wire Hub MCP via Claw CR |

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

Search for **rhdh-agent-sandbox** on [artifacthub.io](https://artifacthub.io/packages/helm/rhdh-agent-sandbox/rhdh-agent-sandbox).

## Configuration

### Required parameters

| Parameter | Description |
|---|---|
| `secrets.modelApiKey` | OpenShift token for sandbox-shared-models oauth-proxy. Run `oc whoami -t`. Refreshes every ~24h. |
| `rhdh.global.clusterRouterBase` | Cluster apps domain (e.g. `apps.rm2.thpm.p1.openshiftapps.com`) |

### Key optional parameters

| Parameter | Default | Description |
|---|---|---|
| `litellm.enabled` | `true` | Deploy the LiteLLM proxy |
| `mcp.enabled` | `true` | Deploy OpenShift/Kubernetes MCP servers |
| `catalog.enabled` | `true` | Mount AI catalog ConfigMap |
| `agents.enabled` | `true` | Sample agents + applier |
| `agents.logLevel` / `agents.applier.logLevel` | `INFO` | Structured UTC logs |
| `rhdh.enabled` | `true` | Deploy Red Hat Developer Hub |

Full form: [`values.yaml`](values.yaml) + [`values.schema.json`](values.schema.json) (OpenShift Console Helm form).

## Architecture (summary)

```text
Hub Guest ──► Developer Hub (Lightspeed / MCP Chat / Catalog / Scaffolder)
                 │
                 ├─► LiteLLM ──► sandbox-shared-models (Granite/Qwen chat)
                 ├─► LiteMaaS Qwen (tool calling demos)
                 └─► ClusterIP OpenShift/K8s MCP

Sandbox user ──► DevSpaces Che Code + Continue ──► LiteLLM Route
                 └─► Hub Route MCP Actions (catalog/TechDocs)

Sandbox user ──► OpenClaw (*-claw ns, LiteMaaS Qwen)
                 ├─► kubectl into *-dev
                 └─► Hub MCP Actions (Claw CR mcpServers + claw-proxy allowlist)
```

## Token refresh

```bash
oc patch secret/rhdh-agent-sandbox-secrets -n "$(oc project -q)" --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm
```

## Post-install verification

```bash
oc get route -l app.kubernetes.io/name=developer-hub -o jsonpath='{.items[0].spec.host}'
oc get pods -l app.kubernetes.io/instance=rhdh-agent
curl -sk "https://$(oc get route rhdh-agent-sandbox-litellm -o jsonpath='{.spec.host}')/health"
```

## Documentation

| Page | Content |
|---|---|
| [Quickstart](https://maximilianopizarro.github.io/rhdh-agent-sandbox/quickstart/) | Install |
| [Verify](https://maximilianopizarro.github.io/rhdh-agent-sandbox/verify/) | Health checks |
| [Golden Path journey](https://maximilianopizarro.github.io/rhdh-agent-sandbox/journey/) | Deploy Agent carousel |
| [Hub tool calling journey](https://maximilianopizarro.github.io/rhdh-agent-sandbox/tool-calling-journey/) | Lightspeed + MCP Chat tools |
| [DevSpaces journey](https://maximilianopizarro.github.io/rhdh-agent-sandbox/devspaces-journey/) | Continue chat + Hub MCP from IDE |
| [OpenClaw](https://maximilianopizarro.github.io/rhdh-agent-sandbox/openclaw/) | LiteMaaS + **Hub MCP via Claw CR** |
| [OpenClaw journey](https://maximilianopizarro.github.io/rhdh-agent-sandbox/openclaw-journey/) | Provision carousel |
| [Architecture](https://maximilianopizarro.github.io/rhdh-agent-sandbox/architecture/) | Components & tokens |
| [Troubleshooting](https://maximilianopizarro.github.io/rhdh-agent-sandbox/troubleshooting/) | Common failures |

Source for Pages is **`docs-src/`** (Jekyll + PatternFly). CI builds into `docs/` on `main`.

## OpenClaw ↔ Hub MCP

OpenClaw is **not** a Developer Hub plugin. Wire Hub MCP from the Claw custom resource (`spec.mcpServers` + `credentialRef`, transport `streamable-http`). See [OpenClaw docs page](https://maximilianopizarro.github.io/rhdh-agent-sandbox/openclaw/).

## Uninstall

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
