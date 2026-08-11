---
layout: default
title: Golden Paths
permalink: /golden-paths/
---


Three self-service templates ship with this chart:

## Deploy Agent

Generate a real LangGraph / LangChain.js / LangChain4j agent, BuildConfig-compile, and deploy without git push.

- Registers a catalog Component with `managed-agent=true` and `build=true`
- agent-applier builds from chart skeleton sources
- Component page: **Topology** + per-agent **Documentation**

## DevSpaces AI Workspace

Creates a started DevWorkspace with Continue → LiteLLM for the selected language.

## AI Service with MCP wiring

Deploys a small HTTP service with `/mcp/smoke` calling Kubernetes + OpenShift MCP.

![Deploy Agent](https://maximilianopizarro.github.io/rhdh-agent-sandbox/assets/diagrams/golden-path-deploy-agent.png)

Run from Hub → **Create** → pick a template → follow the task log.
