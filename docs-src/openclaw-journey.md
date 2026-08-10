---
title: OpenClaw journey
carousel: true
---

# OpenClaw + Qwen Tool Calling journey

<p class="muted">Step-by-step guide to provision OpenClaw from sandbox.redhat.com, connect it to a private Qwen model with tool calling, and use it alongside Developer Hub agents.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="OpenClaw configuration journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 7">
<img src="{{ '/assets/screenshots/sandbox-catalog.png' | relative_url }}" alt="Developer Sandbox catalog showing OpenShift, OpenShift AI, Dev Spaces, Ansible, OpenShift Virtualization, and OpenClaw cards" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Developer Sandbox catalog</strong>
<span class="desc">Log into sandbox.redhat.com. The catalog shows all available services. Scroll down to find the OpenClaw card with its red crab icon.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 7" hidden>
<img src="{{ '/assets/screenshots/sandbox-openclaw-card.png' | relative_url }}" alt="OpenClaw card with features: personal AI assistant, bring your own LLM keys, full workspace access, Kubernetes-native" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>OpenClaw card</strong>
<span class="desc">OpenClaw: personal AI assistant running on your cluster. Bring your own LLM API keys (OpenAI, Anthropic, Google, etc.). Click <strong>Provision</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 7" hidden>
<img src="{{ '/assets/screenshots/openclaw-provision-modal.png' | relative_url }}" alt="Provision OpenClaw instance modal with New credential section and AI provider dropdown" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Provision modal</strong>
<span class="desc">The provision dialog asks for AI provider credentials. Click the dropdown to choose from Primary (Google, Anthropic, OpenAI, xAI), Advanced (OpenRouter, Vertex AI), or <strong>Custom / Self-Hosted</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 7" hidden>
<img src="{{ '/assets/screenshots/openclaw-providers.png' | relative_url }}" alt="Dropdown showing Primary providers (Google Gemini, Anthropic Claude, OpenAI, xAI), Advanced (OpenRouter, Vertex AI), and Custom / Self-Hosted" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Select Custom / Self-Hosted</strong>
<span class="desc">For a private Qwen model served via LiteLLM/LiteMaaS, select <strong>Custom / Self-Hosted</strong> under the Custom section. This unlocks the endpoint URL and model fields.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 7" hidden>
<img src="{{ '/assets/screenshots/openclaw-provision-filled.png' | relative_url }}" alt="Completed provision form showing LiteMaaS endpoint URL, OpenAI Completions format, masked API key, Qwen3.6-35B-A3B model name, and display name" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>Configure Qwen + LiteMaaS</strong>
<span class="desc">Fill: <strong>Endpoint URL</strong> = your LiteMaaS /v1 endpoint, <strong>API Format</strong> = OpenAI Completions, <strong>API Key</strong> = your bearer token (never commit to git!), <strong>Model Name</strong> = Qwen3.6-35B-A3B, <strong>Display Name</strong> = friendly label. Click <strong>Provision</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 7" hidden>
<img src="{{ '/assets/screenshots/openclaw-chat-qwen.png' | relative_url }}" alt="OpenClaw chat interface showing tool calling with kubectl, powered by Qwen3.6-35B-A3B" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>OpenClaw chat with tool calling</strong>
<span class="desc">OpenClaw is live! Ask it to inspect your namespace — it uses Qwen's tool calling to execute kubectl, read logs, and analyze deployments. The model indicator shows &ldquo;Qwen 3.6 35B-A3B (Tool Calling)&rdquo;.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 7" hidden>
<img src="{{ '/assets/screenshots/openclaw-devhub-integration.png' | relative_url }}" alt="Split view of Developer Hub catalog and OpenClaw deploying an agent via Golden Path template" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>OpenClaw + Developer Hub</strong>
<span class="desc">OpenClaw works alongside Developer Hub: invoke the scaffolder API to deploy agents via Golden Path templates, check catalog entries, and manage the full agent lifecycle — all from one AI-powered interface.</span>
</figcaption>
</figure>

</div>
<div class="journey-controls">
<div class="journey-nav">
<button type="button" class="journey-btn" id="journey-prev" aria-label="Previous slide">&#8592; Prev</button>
<button type="button" class="journey-btn" id="journey-next" aria-label="Next slide">Next &#8594;</button>
<button type="button" class="journey-btn" id="journey-fs" aria-label="Toggle fullscreen" aria-pressed="false">Fullscreen</button>
</div>
<div class="journey-dots" id="journey-dots" role="tablist" aria-label="Slide picker"></div>
<span class="journey-status" id="journey-status" aria-live="polite">1 / 7</span>
</div>
</div>

## Architecture overview

![OpenClaw integration architecture]({{ '/assets/screenshots/openclaw-architecture.png' | relative_url }})

OpenClaw connects to a **private Qwen3.6-35B-A3B** model via the **LiteMaaS** OpenAI-compatible API. Unlike shared Sandbox models (Granite / Qwen via chart LiteLLM), the LiteMaaS endpoint **supports tool calling** (`tool_choice=auto`), enabling OpenClaw's full agentic loop.

| Component | Role |
|---|---|
| **sandbox.redhat.com** | Provision OpenClaw instance with your credentials |
| **LiteMaaS** | Red Hat AI Services hosted LLM gateway (OpenAI Completions API) |
| **Qwen3.6-35B-A3B** | Private model with function/tool calling support |
| **OpenClaw Pod** | Kubernetes-native AI assistant running in your namespace |
| **Developer Hub** | Catalog, Lightspeed, Golden Paths — OpenClaw can orchestrate these |
| **DevSpaces** | Browser IDE connected to LiteLLM for AI-assisted coding |

## Security: never commit API keys

> **Warning: API key handling**
>
> Your LiteMaaS API key (`sk-...`) is stored as a Kubernetes Secret by the sandbox provisioner. **Never** commit it to git, values.yaml, or ConfigMaps.

The provision form securely stores the key in a Secret that only the OpenClaw pod can mount. To rotate:

1. Delete the OpenClaw instance from sandbox.redhat.com
2. Re-provision with the new key
3. Or patch the Secret directly: `oc patch secret openclaw-credentials -p '{"data":{"api-key":"<base64-new-key>"}}'`

## Using OpenClaw with agents

Once provisioned, OpenClaw can:

- **Inspect deployments**: `kubectl get deployments` via tool calling
- **Read agent logs**: `kubectl logs deployment/triage-agent`
- **Deploy new agents**: invoke the Developer Hub scaffolder API
- **Debug issues**: analyze pod events, check resource limits, inspect routes
- **Manage lifecycle**: scale deployments, update ConfigMaps, restart pods

### Example: deploy an agent via OpenClaw

```
You: Deploy a new python agent called security-scanner using the Golden Path template

OpenClaw: I'll help you deploy security-scanner using the Golden Path template.
  > Executing tool: POST /api/scaffolder/v2/tasks
  > Template: deploy-agent-golden-path
  > Parameters: name=security-scanner, language=python, owner=platform-team
  
  ✓ Skeleton materialized
  ✓ Runtime manifests applied
  ✓ Component registered in catalog
  
  security-scanner is now running in your namespace.
```

## See also

- [OpenClaw (setup reference)]({{ '/openclaw/' | relative_url }}) — full configuration guide
- [Architecture]({{ '/architecture/' | relative_url }}) — overall stack diagram
- [Golden Path journey]({{ '/journey/' | relative_url }}) — the three Golden Paths in action
- [Lightspeed & models]({{ '/lightspeed-models/' | relative_url }}) — why shared models drop `tool_choice`
