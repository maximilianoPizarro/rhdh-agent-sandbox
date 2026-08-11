---
layout: default
title: Agent-friendly Developer Hub
permalink: /
---


![Install overview](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/install-one-command.png)

This demo deploys **Red Hat Developer Hub 1.10** with Lightspeed, LiteLLM, MCP tools, Golden Paths, and DevSpaces AI on **OpenShift Developer Sandbox**.

## Who is this for?

| Identity | What you do |
|----------|-------------|
| **Hub Guest** | Browse catalog, run Golden Paths, use Lightspeed and MCP Chat — no OpenShift token |
| **Sandbox user (`oc`)** | Install the chart, refresh tokens, open DevSpaces workspaces |

## What you get

- **Developer Hub** — catalog, scaffolder, TechDocs, Topology, Lightspeed
- **LiteLLM** — Granite, Qwen, LiteMaaS Qwen (tool calling)
- **MCP servers** — OpenShift + Kubernetes (namespace-scoped)
- **Golden Paths** — Deploy Agent, DevSpaces AI, AI Service with MCP wiring

## Recommended path

1. [Quickstart](quickstart.md) — Helm install
2. [Golden Paths](golden-paths.md) — create an agent
3. [Demo script](demo-script.md) — 10-minute walkthrough

See [Architecture](architecture.md) for tokens, networking, and component map.
