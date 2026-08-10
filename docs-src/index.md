---
layout: home
title: Home
permalink: /
---

# Agent-friendly Developer Hub on Developer Sandbox

Umbrella Helm chart that deploys **Red Hat Developer Hub 1.10.3** on **OpenShift Developer Sandbox** with a working agent loop: Lightspeed → LiteLLM → shared Granite/Qwen (chat) or LiteMaaS Qwen (tool calling), plus MCP tools, Golden Paths, and DevSpaces AI workspaces.

![One-command install]({{ '/assets/diagrams/install-one-command.png' | relative_url }})

## What you get

<div class="card-grid" markdown="0">
<div class="card">
<h3>Developer Hub</h3>
<p>Guest login, catalog, scaffolder, TechDocs, and Lightspeed UI — all in one portal.</p>
</div>
<div class="card">
<h3>LiteLLM Gateway</h3>
<p>OpenAI-compatible proxy to shared Granite &amp; Qwen models via sandbox-shared-models.</p>
</div>
<div class="card">
<h3>MCP Servers</h3>
<p>OpenShift + Kubernetes tools (namespace-scoped) for Lightspeed AI interactions.</p>
</div>
<div class="card">
<h3>Golden Paths</h3>
<p>Deploy Agent → Pod + Component + Open in DevSpaces — no git push required.</p>
</div>
<div class="card">
<h3>DevSpaces AI</h3>
<p>Browser IDE (Che Code + Continue) connected to the LiteLLM Route, with Hub MCP Actions over the Hub Route. <a href="{{ '/devspaces-journey/' | relative_url }}">See the journey</a>.</p>
</div>
<div class="card">
<h3>AI Catalog</h3>
<p>Skills, prompts, MCP entities, and software templates mounted via ConfigMaps.</p>
</div>
<div class="card">
<h3>Hub tool calling</h3>
<p>Lightspeed + MCP Chat with <code>litemaas-qwen</code> call real Kubernetes tools. <a href="{{ '/tool-calling-journey/' | relative_url }}">See the journey</a>.</p>
</div>
<div class="card">
<h3>OpenClaw + Qwen</h3>
<p>Personal AI assistant with <strong>tool calling</strong> via LiteMaaS Qwen3.6-35B-A3B. <a href="{{ '/openclaw-journey/' | relative_url }}">See the journey</a>.</p>
</div>
</div>

## Two identities (important)

| Who | What they do |
|---|---|
| **Hub Guest** | Signs into Developer Hub only. Uses Lightspeed + catalog. No OpenShift token. |
| **OpenShift Sandbox user** (`oc` / console) | Refreshes `model-api-key`, starts DevSpaces workspaces, reads `litellm-master-key`. |

Guest Hub ≠ DevSpaces login. The chart prepares Devfiles and IDE config; the Sandbox user opens the workspace.

## Recommended path

1. [Quickstart]({{ '/quickstart/' | relative_url }}) — single `helm upgrade --install`  
2. [Verify the install]({{ '/verify/' | relative_url }}) — confirm Hub, LiteLLM, routes  
3. [Golden Paths]({{ '/golden-paths/' | relative_url }}) — deploy an agent Pod from the catalog  
4. [Agents]({{ '/agents/' | relative_url }}) — Hub Guest, agent Pods, DevSpaces loops  
5. [DevSpaces journey]({{ '/devspaces-journey/' | relative_url }}) — Continue → LiteLLM + Hub MCP from the IDE  
6. [DevSpaces AI]({{ '/devspaces-ai/' | relative_url }}) — reference for Devfile / Secret wiring  
7. [Demo script]({{ '/demo-script/' | relative_url }}) — guided ~10 minute walkthrough  

Deeper reading: [Architecture]({{ '/architecture/' | relative_url }}), [Lightspeed & models]({{ '/lightspeed-models/' | relative_url }}), [AI capabilities]({{ '/ai-capabilities/' | relative_url }}), [OpenClaw]({{ '/openclaw/' | relative_url }}), [Troubleshooting]({{ '/troubleshooting/' | relative_url }}), [Community packs]({{ '/community-plugins-quay/' | relative_url }}).

## Beyond Sandbox (production)

This chart proves an agent loop on Developer Sandbox. For a managed OpenShift cluster, harden identity, secrets, gateway control, token budgets, AI safety, and CI/CD with Connectivity Link, RHBK, Vault + External Secrets, OpenShift AI Guardrails, Trusted Software Supply Chain, and `TokenRateLimitPolicy`.

See **[Production considerations]({{ '/production-considerations/' | relative_url }})** under Operations (recommendations + official docs links — not installed by this chart).

## Install

One `helm upgrade --install` deploys everything. Two options: clone the repo or add the Pages Helm repo. See **[Quickstart]({{ '/quickstart/' | relative_url }})** for full commands, prerequisites, and post-install checks.

## Source

[github.com/maximilianopizarro/rhdh-agent-sandbox](https://github.com/maximilianopizarro/rhdh-agent-sandbox)
