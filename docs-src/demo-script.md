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
      src="https://app.arcade.software/share/TpWOUs1YMUqwoA0OxnzS?embed"
      title="Building Agentic AI in a Developer Sandbox"
      loading="lazy"
      allow="fullscreen"
      allowfullscreen
    ></iframe>
  </div>
  <div class="arcade-embed__toolbar">
    <button type="button" class="arcade-embed__fs" data-arcade-fs aria-label="Toggle fullscreen" aria-pressed="false">Fullscreen</button>
    <span class="arcade-embed__hint">Esc to exit</span>
    <a href="https://app.arcade.software/share/TpWOUs1YMUqwoA0OxnzS" class="arcade-embed__open" target="_blank" rel="noopener">Open in Arcade</a>
  </div>
</div>

Watch the walkthrough above without a cluster, or follow the live script below.

Interactive recording: **[Building Agentic AI in a Developer Sandbox](https://app.arcade.software/share/TpWOUs1YMUqwoA0OxnzS)** (Arcade).

Use **LiteMaaS Qwen** (`litemaas-qwen`) for any tool-calling step. Shared **Granite** is chat-only — Lightspeed/Continue will hallucinate CVEs if you leave it selected in Agent mode.

## Part A — Helm catalog install

1. OpenShift Console → **Developer** perspective → your Sandbox project
2. **+Add** → **Helm Chart** → search `rhdh-agent-sandbox` → **Install Helm Chart**
3. Release name `rhdh-agent`, chart **0.1.11**, Form view
4. Set **Cluster Router Base** and **OpenShift token (shared models)** (`oc whoami -t`). Leave **LiteMaaS API key** empty if Secret `litemaas-credentials` already exists
5. **Create** → wait until Topology group **rhdh-agent** is Ready (Hub 2/2, LiteLLM, MCP, applier, PostgreSQL)

## Part B — Hub agent loop (~5 min)

1. Open the Developer Hub Route → **Enter as Guest**
2. **Catalog** → filter `mcp` → browse MCP API entities and their **Documentation**
3. **Create** → **Deploy Agent (Golden Path)** (Python / LangGraph, `tool-agent`, model `granite`)
4. Open the new Component → **Topology** after the BuildConfig finishes (no git push)
5. **MCP Chat** → `litemaas-qwen` → ask for `pods_list_in_namespace` in this namespace

## Part C — DevSpaces + Red Hat Security MCP (~5 min)

1. **Create** → **Agent-friendly DevSpaces AI Workspace** (workspace starts **stopped**)
2. [Dev Spaces dashboard](https://workspaces.openshift.com/dashboard/#/workspaces) as the Sandbox user → **Start** → **Trust**
3. Continue → model **LiteMaaS Qwen (LiteLLM)** → **Agent** or **Plan** (not Chat)
4. Customer Portal SSO via the public **http-8080** helper (not Che `code-redirect`)
5. Ask `get_cve_by_id` for **CVE-2024-3094** (xz). Expect live tool chips, Red Hat severity — not NVD folklore
6. **Stop** the workspace when done to free quota

## Wrap-up

```bash
oc get bc,deploy -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc get dw
```
