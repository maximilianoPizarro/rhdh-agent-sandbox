---
layout: default
title: Interactive demo
permalink: /demo-script/
arcade: true
content_class: content--wide
---


<div class="arcade-embed" role="region" aria-label="Interactive demo" tabindex="0">
  <div class="arcade-embed__frame">
    <iframe
      src="https://app.arcade.software/share/3eNsUpTwG1SiGKP9kvgI?embed"
      title="Demo Agentic IA Developer Sandbox"
      loading="lazy"
      allow="fullscreen"
      allowfullscreen
    ></iframe>
  </div>
  <div class="arcade-embed__toolbar">
    <button type="button" class="arcade-embed__fs" data-arcade-fs aria-label="Toggle fullscreen" aria-pressed="false">Fullscreen</button>
    <span class="arcade-embed__hint">Esc to exit</span>
    <a href="https://app.arcade.software/share/3eNsUpTwG1SiGKP9kvgI" class="arcade-embed__open" target="_blank" rel="noopener">Open in Arcade</a>
  </div>
</div>

Watch the walkthrough above without a cluster, or follow the live script below.

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
