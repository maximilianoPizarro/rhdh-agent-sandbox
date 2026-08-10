---
title: Hub tool calling journey
carousel: true
---

# Hub tool calling journey (Lightspeed + MCP Chat)

<p class="muted">Evidence that Guest Hub AI can call Kubernetes/OpenShift MCP tools with LiteMaaS Qwen (<code>litemaas-qwen</code>). Shared Granite/Qwen stay chat-only.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="Hub tool calling journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 5">
<img src="{{ '/assets/screenshots/lightspeed-toolcall-result.png' | relative_url }}" alt="Lightspeed chat showing Tool response chips for pods_list and pods_log with litemaas-qwen" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Lightspeed — tool rounds</strong>
<span class="desc">Open Lightspeed, select <code>litemaas-qwen</code>, ask to list pods and check sample agents. The UI shows Tool response chips (<code>pods_list</code>, <code>pods_list_in_namespace</code>, <code>pods_log</code>).</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 5" hidden>
<img src="{{ '/assets/screenshots/lightspeed-toolcall-summary.png' | relative_url }}" alt="Lightspeed summary confirming sample-python, nodejs, and quarkus agents Running with health 200" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>Lightspeed — action result</strong>
<span class="desc">Final answer cites real pod names and <code>/health</code> 200 lines for sample-python-agent, sample-nodejs-agent, and sample-quarkus-agent.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 5" hidden>
<img src="{{ '/assets/screenshots/mcp-chat-home.png' | relative_url }}" alt="MCP Chat landing page with Catalog, Namespace pods, and TechDocs suggested prompts" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>MCP Chat — start</strong>
<span class="desc">Sidebar <strong>MCP Chat</strong> offers suggested prompts (Catalog, Namespace pods, TechDocs) wired to the same LiteLLM + MCP servers.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 5" hidden>
<img src="{{ '/assets/screenshots/mcp-chat-toolcall-config.png' | relative_url }}" alt="MCP Chat status panel showing Connected provider litemaas-qwen and OpenShift plus Kubernetes MCP servers" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>MCP Chat — connected</strong>
<span class="desc">Status shows Provider Connected, model <code>litemaas-qwen</code>, OpenShift MCP (19 tools) and Kubernetes MCP (23 tools) enabled.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 5" hidden>
<img src="{{ '/assets/screenshots/mcp-chat-toolcall-result.png' | relative_url }}" alt="MCP Chat reply listing three Running sample agent pods with Tools used pods_list_in_namespace" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>MCP Chat — tool result</strong>
<span class="desc">Ask for <code>pods_list_in_namespace</code> in your Sandbox namespace. Reply lists the three sample-*-agent pods and shows <strong>Tools used (1) pods_list_in_namespace</strong>.</span>
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
<span class="journey-status" id="journey-status" aria-live="polite">1 / 5</span>
</div>
</div>

## Models

| Alias | Tools | Use for |
|---|---|---|
| `granite` / `qwen3` | Dropped by LiteLLM | Everyday Hub chat |
| `litemaas-qwen` → LiteMaaS `Qwen3.6-35B-A3B` | ON | Lightspeed + MCP Chat tool demos |

Store the LiteMaaS key only in cluster Secret `litemaas-credentials` (never in git). See [Lightspeed & models]({{ '/lightspeed-models/' | relative_url }}).

## Related journeys

- [Golden Path journey]({{ '/journey/' | relative_url }}) — Deploy Agent / DevSpaces / AI Service templates  
- [OpenClaw journey]({{ '/openclaw-journey/' | relative_url }}) — Sandbox OpenClaw + LiteMaaS kubectl tools  

## DevSpaces Continue Secret

The chart also creates `rhdh-agent-sandbox-continue` for Che Code Continue → LiteLLM (chat models). Devfile `wire-continue` consumes it:

![Continue Secret keys LITELLM_API_BASE and LITELLM_API_KEY]({{ '/assets/screenshots/devspaces-continue-secret.png' | relative_url }})
