---
layout: default
title: Demo script
permalink: /demo-script/
---


Interactive recording: **[Demo Agentic IA Developer Sandbox](https://app.arcade.software/share/3eNsUpTwG1SiGKP9kvgI)** (Arcade).

## Part A — Hub agent loop (~5 min)

1. Open Developer Hub → **Enter as Guest**
2. **Catalog** → filter `mcp` → browse MCP API entities and their **Documentation** (skills as markdown)
3. **Create** → run **Deploy Agent** Golden Path
4. Open the new Component → **Topology** tab
5. **Lightspeed** or **MCP Chat** → select `litemaas-qwen` → ask to list pods in namespace

## Part B — DevSpaces AI (~5 min)

1. **Create** → **Agent-friendly DevSpaces AI Workspace**
2. Open DevSpaces dashboard → open workspace
3. Continue chat → LiteLLM wired via chart Secret

## Wrap-up

```bash
oc get bc,deploy -l app.kubernetes.io/part-of=rhdh-agent-sandbox
```

Stop DevWorkspace when done to free quota.
