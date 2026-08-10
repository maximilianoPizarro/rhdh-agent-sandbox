# Agent-friendly Developer Hub on Developer Sandbox

Umbrella Helm chart that deploys **Red Hat Developer Hub 1.10.3** on **OpenShift Developer Sandbox** with a working agent loop: Lightspeed → LiteLLM → shared Granite/Qwen, plus MCP tools, Golden Paths, and DevSpaces AI workspaces.

![One-command install](assets/diagrams/install-one-command.png)

## What you get

| Piece | Role |
|---|---|
| **Developer Hub** | Guest login, catalog, scaffolder, TechDocs, Lightspeed UI |
| **LiteLLM** | OpenAI-compatible gateway to `sandbox-shared-models` (Granite / Qwen) |
| **MCP servers** | OpenShift + Kubernetes tools (namespace-scoped) for Lightspeed |
| **Golden Paths** | Deploy Agent → Pod + Component + Open in DevSpaces (no git push) |
| **AI catalog** | Skills, prompts, MCP entities, software templates (ConfigMap mount) |
| **DevSpaces AI** | Browser IDE (Che Code + Continue) talking to the LiteLLM Route |
| **OpenClaw** (optional) | Personal assistant from sandbox.redhat.com; bring your own LLM keys |

## Two identities (important)

| Who | What they do |
|---|---|
| **Hub Guest** | Signs into Developer Hub only. Uses Lightspeed + catalog. No OpenShift token. |
| **OpenShift Sandbox user** (`oc` / console) | Refreshes `model-api-key`, starts DevSpaces workspaces, reads `litellm-master-key`. |

Guest Hub ≠ DevSpaces login. The chart prepares Devfiles and IDE config; the Sandbox user opens the workspace.

## Recommended path

1. [Quickstart](quickstart.md) — single `helm upgrade --install`  
2. [Verify the install](verify.md) — confirm Hub, LiteLLM, routes  
3. [Golden Paths](golden-paths.md) — deploy an agent Pod from the catalog  
4. [Agents](agents.md) — Hub Guest, agent Pods, DevSpaces loops  
5. [DevSpaces AI](devspaces-ai.md) — browser IDE with Continue → LiteLLM  
6. [Demo script](demo-script.md) — guided ~10 minute walkthrough  

Deeper reading: [Architecture](architecture.md), [Lightspeed & models](lightspeed-models.md), [AI capabilities](ai-capabilities.md), [OpenClaw](openclaw.md), [Troubleshooting](troubleshooting.md), [Community packs](community-plugins-quay.md).

## Install

One `helm upgrade --install` deploys everything. Two options: clone the repo or add the Pages Helm repo. See **[Quickstart](quickstart.md)** for full commands, prerequisites, and post-install checks.

## Source

[github.com/maximilianopizarro/rhdh-agent-sandbox](https://github.com/maximilianopizarro/rhdh-agent-sandbox)
