---
title: OpenClaw journey
carousel: true
---

# OpenClaw + Qwen Tool Calling journey

<p class="muted">Step-by-step guide to provision OpenClaw from sandbox.redhat.com, connect it to a private Qwen model with tool calling, and use it alongside Developer Hub agents.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="OpenClaw configuration journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 8">
<img src="{{ '/assets/screenshots/sandbox-catalog.png' | relative_url }}" alt="Developer Sandbox catalog showing OpenShift, OpenShift AI, Dev Spaces, Ansible, OpenShift Virtualization, and OpenClaw cards" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Developer Sandbox catalog</strong>
<span class="desc">Log into sandbox.redhat.com. The catalog shows all available services. Scroll down to find the OpenClaw card with its red crab icon.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 8" hidden>
<img src="{{ '/assets/screenshots/sandbox-openclaw-card.png' | relative_url }}" alt="OpenClaw card with features: personal AI assistant, bring your own LLM keys, full workspace access, Kubernetes-native" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>OpenClaw card</strong>
<span class="desc">OpenClaw: personal AI assistant running on your cluster. Bring your own LLM API keys (OpenAI, Anthropic, Google, etc.). Click <strong>Provision</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-provision-modal.png' | relative_url }}" alt="Provision OpenClaw instance modal with New credential section and AI provider dropdown" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Provision modal</strong>
<span class="desc">The provision dialog asks for AI provider credentials. Click the dropdown to choose from Primary (Google, Anthropic, OpenAI, xAI), Advanced (OpenRouter, Vertex AI), or <strong>Custom / Self-Hosted</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-providers.png' | relative_url }}" alt="Dropdown showing Primary providers (Google Gemini, Anthropic Claude, OpenAI, xAI), Advanced (OpenRouter, Vertex AI), and Custom / Self-Hosted" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Select Custom / Self-Hosted</strong>
<span class="desc">For a private Qwen model served via LiteLLM/LiteMaaS, select <strong>Custom / Self-Hosted</strong> under the Custom section. This unlocks the endpoint URL and model fields.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-provision-filled.png' | relative_url }}" alt="Completed provision form showing LiteMaaS endpoint URL, OpenAI Completions format, masked API key, Qwen3.6-35B-A3B model name, and display name" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>Configure Qwen + LiteMaaS</strong>
<span class="desc">Fill Endpoint URL (LiteMaaS /v1), API Format = OpenAI Completions, API Key (never commit to git), Model Name = Qwen3.6-35B-A3B, Display Name = friendly label. Then click Provision.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-ready.png' | relative_url }}" alt="OpenClaw instance provisioned modal with Launch button" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>Instance ready</strong>
<span class="desc">When provisioning finishes, Launch opens the OpenClaw Control UI (use the gateway token from Secret <code>claw-gateway-token</code> if pairing is required).</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-chat-qwen.png' | relative_url }}" alt="OpenClaw chat showing kubectl tool activity and sample agent Ready status with Qwen3.6-35B-A3B" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>OpenClaw chat with tool calling</strong>
<span class="desc">Ask OpenClaw to inspect namespaces with kubectl. Qwen runs real tool rounds and reports sample-*-agent Deployments/Pods as Ready in your Hub namespace.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 8" hidden>
<img src="{{ '/assets/screenshots/openclaw-devhub-integration.png' | relative_url }}" alt="Illustrative concept of OpenClaw beside Developer Hub catalog while deploying an agent" />
<figcaption>
<span class="slide-num">Step 08</span>
<strong>OpenClaw + Developer Hub</strong>
<span class="desc">Kubectl tools (Step 07) stay in-namespace. For <strong>Hub catalog / TechDocs MCP</strong>, declare <code>spec.mcpServers</code> on the Claw CR (<code>streamable-http</code> + Hub Route) — proven with <code>openclaw mcp probe</code> → 4 tools. Full scaffolder deploy-from-OpenClaw UI is still optional; Golden Paths remain in Hub Guest. Details: <a href="{{ '/openclaw/' | relative_url }}">OpenClaw setup</a>.</span>
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
<span class="journey-status" id="journey-status" aria-live="polite">1 / 8</span>
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
| **Developer Hub** | Catalog, Lightspeed, Golden Paths — complementary portal (Guest). Direct OpenClaw→scaffolder orchestration is not packaged yet |
| **DevSpaces** | Browser IDE connected to LiteLLM for AI-assisted coding |

## Security: never commit API keys

> **Warning: API key handling**
>
> Your LiteMaaS API key (`sk-...`) is stored as a Kubernetes Secret by the sandbox provisioner. **Never** commit it to git, values.yaml, or ConfigMaps.

The provision form securely stores the key in a Secret that only the OpenClaw pod can mount. To rotate:

1. Delete the OpenClaw instance from sandbox.redhat.com
2. Re-provision with the new key
3. Or patch the Secret directly: `oc patch secret openclaw-credentials -p '{"data":{"api-key":"<base64-new-key>"}}'`

## What is proven vs illustrative

| Capability | Status |
|---|---|
| Provision OpenClaw + LiteMaaS Qwen (tool calling) | **Proven** — Steps 01–06 |
| `kubectl` list Deployments/Pods in Hub namespace | **Proven** — Step 07 (real chat capture) |
| Split Hub catalog MCP from OpenClaw | **Proven via Claw CR** — `spec.mcpServers` + `openclaw mcp probe` (4 tools); see [OpenClaw]({{ '/openclaw/' | relative_url }}) |
| Deploy agents via Golden Path | **Proven in Hub Guest** — see [Golden Path journey]({{ '/journey/' | relative_url }}), not via OpenClaw scaffolder UI yet |

### Reproducing Step 07 (real)

1. Provision OpenClaw with LiteMaaS as in Steps 01–06.
2. Open Control UI with gateway token (`oc get secret claw-gateway-token -n <claw-ns> -o jsonpath='{.data.token}' | base64 -d`).
3. Approve device pairing if prompted (`openclaw devices approve …` inside the gateway pod).
4. Prompt: *Using kubectl, list Deployments and Pods in namespace &lt;your-dev-ns&gt;. Highlight sample-\*-agent Ready status.*

### Reproducing Golden Path deploy (Hub, not OpenClaw)

Use Guest → Self-service → **Deploy Agent (Golden Path)** and follow the [Golden Path journey]({{ '/journey/' | relative_url }}).

### What Step 08 would need to become a live capture

OpenClaw would need Hub Reachability + credentials (e.g. scaffolder/`mcp-token` or a service account that can call the Hub Route) and a deliberate prompt that posts a scaffolder task — that integration is **out of scope for this chart** today (OpenClaw is provisioned outside the umbrella chart).

## Using OpenClaw with the cluster (today)

Once provisioned with LiteMaaS Qwen, OpenClaw can typically:

- **Inspect deployments / pods** in namespaces its workspace kubeconfig allows (often your `*-dev` NS)
- **Read logs** with `kubectl logs`
- **Debug** events, describe resources, check readiness

Use Developer Hub Guest for catalog browse, Lightspeed/MCP Chat tool demos, and Golden Path scaffolding.

## See also

- [OpenClaw (setup reference)]({{ '/openclaw/' | relative_url }}) — full configuration guide
- [Architecture]({{ '/architecture/' | relative_url }}) — overall stack diagram
- [Golden Path journey]({{ '/journey/' | relative_url }}) — the three Golden Paths in action
- [Lightspeed & models]({{ '/lightspeed-models/' | relative_url }}) — why shared models drop `tool_choice`
