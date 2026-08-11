---
layout: default
title: Architecture
permalink: /architecture/
---


![Architecture overview](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/architecture-overview.png)

## Components

| Component | Delivery | Network |
|-----------|----------|---------|
| Red Hat Developer Hub 1.10.3 | Helm subchart | Route `*-developer-hub` |
| LiteLLM | Chart Deployment | ClusterIP + Route |
| OpenShift MCP | Chart Deployment | ClusterIP `:8080` |
| Kubernetes MCP | Chart Deployment | ClusterIP `:8085` |
| agent-applier | Chart Deployment | Polls catalog → builds agents |
| AI catalog | ConfigMap | `/opt/app-root/src/catalog` |

## Inference path

```text
Guest → Lightspeed UI → lightspeed-core → LiteLLM → shared Granite/Qwen
Guest → MCP Chat → LiteLLM (litemaas-qwen) → MCP tools
```

## Tokens

| Secret key | Consumer | Refresh |
|------------|----------|---------|
| `model-api-key` | LiteLLM → shared models | `oc whoami -t` (~24h) |
| `litellm-master-key` | Lightspeed, Continue | Chart-generated |
| `mcp-token` | MCP Actions, applier | Chart-generated |

## Golden Path flow

![Golden Path](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/golden-path-deploy-agent.png)

1. Scaffolder registers Component (`catalog:register-entity` via pending ConfigMap)
2. agent-applier creates BuildConfig + Deployment
3. Hub shows **Topology** (Kubernetes plugin) and **TechDocs** for the agent

![Agent Topology tab](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/agent-topology-preview.png)

## MCP tools flow

![MCP tools flow](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/mcp-tools-flow.png)

## Skills ↔ MCP APIs

![Skills catalog map](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/skills-catalog-map.png)
