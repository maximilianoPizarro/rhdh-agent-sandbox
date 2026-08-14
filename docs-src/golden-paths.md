---
layout: default
title: Golden Paths
permalink: /golden-paths/
---


Three self-service templates ship with this chart:

## Deploy Agent

Generate a real LangGraph / LangChain.js / LangChain4j agent, BuildConfig-compile, and deploy without git push.

- Registers a catalog Component with `managed-agent=true` and `build=true`
- agentSpec may include colons (chart 0.1.11 quotes catalog YAML so Verify does not time out)
- agent-applier builds from chart skeleton sources
- Component page: **Topology** + per-agent **Documentation**
- Topology is empty until the BuildConfig finishes and the Deployment exists (no git push)

## DevSpaces AI Workspace

Creates a started DevWorkspace with Continue → LiteLLM for the selected language.

## AI Service with MCP wiring

Deploys a small HTTP service with `/mcp/smoke` calling Kubernetes + OpenShift MCP.

![Deploy Agent]({{ '/assets/diagrams/golden-path-deploy-agent.png' | relative_url }})

Run from Hub → **Create** → pick a template → follow the task log.

See the [Arcade demo](https://app.arcade.software/share/3eNsUpTwG1SiGKP9kvgI) for an end-to-end click-through of Deploy Agent, DevSpaces, and AI Service.
