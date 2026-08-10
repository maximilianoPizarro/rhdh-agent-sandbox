---
title: DevSpaces journey
carousel: true
---

# DevSpaces + Continue AI journey

<p class="muted">Open OpenShift Dev Spaces from the Developer Sandbox, send a real <strong>Continue</strong> chat to this chart’s LiteLLM Route, and show an MCP <strong>tool action → catalog reaction</strong> from the IDE over the public Hub Route.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="DevSpaces Continue journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 9">
<img src="{{ '/assets/screenshots/devspaces-dashboard-workspaces.png' | relative_url }}" alt="Dev Spaces dashboard listing workspaces including rhdh-agent-ai-demo" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Dev Spaces dashboard</strong>
<span class="desc">Open Dev Spaces as your <strong>OpenShift Sandbox user</strong> (not Hub Guest). The Workspaces list shows existing IDEs; only one workspace can run at a time on Sandbox.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-create-workspace.png' | relative_url }}" alt="Create Workspace page with Git URL pointing at rhdh-agent-sandbox files/devfiles" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>Create from chart Devfile</strong>
<span class="desc">Import from Git using <code>…/rhdh-agent-sandbox/tree/main/files/devfiles</code> (or clone the full repo). Prefer Create &amp; Open so Che Code is injected. Alternative: Hub template <strong>Agent-friendly DevSpaces AI Workspace</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-secret.png' | relative_url }}" alt="OpenShift Secret rhdh-agent-sandbox-continue with LITELLM_API_BASE and LITELLM_API_KEY" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Chart Continue Secret</strong>
<span class="desc">The Helm chart creates Secret <code>rhdh-agent-sandbox-continue</code> with <code>LITELLM_API_BASE</code> (LiteLLM Route <code>/v1</code>) and <code>LITELLM_API_KEY</code> (<code>litellm-master-key</code>). Never commit those values to git.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-ide-home.png' | relative_url }}" alt="Che Code IDE opened on rhdh-agent-sandbox with explorer and chat sidebars" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Open Che Code</strong>
<span class="desc">When the workspace is Running, Open IDE loads Che Code on the repo (or Devfile project). Trust the workspace so extensions and tasks can activate.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-trust-workspace.png' | relative_url }}" alt="Workspace Trust dialog comparing Trusted Workspace vs Restricted Mode" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>Trust the workspace</strong>
<span class="desc">Restricted Mode disables extensions. Click <strong>Trust</strong> so Continue and recommended extensions can run.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-ready.png' | relative_url }}" alt="Continue sidebar with Granite (LiteLLM) model selected in Che Code" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>Continue wired to LiteLLM</strong>
<span class="desc">Continue is <strong>preinstalled</strong> (Devfile downloads the OpenVSX linux-x64 <code>.vsix</code> into <code>/tmp/continue.vsix</code>). Run <code>wire-continue</code> so Continue v2 writes <code>~/.continue/config.yaml</code> with <code>granite</code> / <code>qwen3</code> → LiteLLM. Select <strong>Granite (LiteLLM)</strong> (ignore the optional OpenAI/Anthropic/Gemini Connect panel).</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-chat.png' | relative_url }}" alt="Continue chat showing user query Reply with exactly DevSpaces Continue OK and Granite LiteLLM reply" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>Continue query → model reply</strong>
<span class="desc">In the Continue sidebar, ask: <em>Reply with exactly: DevSpaces Continue OK</em>. Granite answers via LiteLLM Route <code>/v1</code>. This is the chat loop the journey must show — not only model selection.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-mcp-action.png' | relative_url }}" alt="Continue showing MCP tool query-catalog-entities and reply listing sample agent components beside smoke markdown" />
<figcaption>
<span class="slide-num">Step 08</span>
<strong>MCP action → catalog reaction</strong>
<span class="desc">With Hub MCP wired in <code>mcpServers</code>, ask Continue to list Components tagged <code>agent</code>. Action: <code>software-catalog-mcp-extras.query-catalog-entities</code>. Reaction: sample-python / nodejs / quarkus agents from the Hub catalog (same entities as the smoke markdown on the right).</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="8" role="group" aria-roledescription="slide" aria-label="9 of 9" hidden>
<img src="{{ '/assets/screenshots/mcp-chat-toolcall-result.png' | relative_url }}" alt="Hub MCP Chat showing Kubernetes tool call results for pods in namespace" />
<figcaption>
<span class="slide-num">Step 09</span>
<strong>Cluster MCP stays in Hub</strong>
<span class="desc">OpenShift/Kubernetes MCP services are <strong>ClusterIP only</strong> — not reachable from DevSpaces. For K8s tool demos with <code>litemaas-qwen</code>, use Hub <a href="{{ '/tool-calling-journey/' | relative_url }}">Lightspeed / MCP Chat</a>. Stop the workspace when finished to free Sandbox quota.</span>
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
<span class="journey-status" id="journey-status" aria-live="polite">1 / 9</span>
</div>
</div>

## What this journey proves

| Path | Endpoint | Auth | From DevSpaces? |
|---|---|---|---|
| Continue **query → reply** | LiteLLM Route `/v1` | `rhdh-agent-sandbox-continue` | Yes (Step 07) |
| Continue **MCP action → reaction** | Hub Route `/api/mcp-actions/v1` | `mcp-token` | Yes (Step 08 catalog tools) |
| OpenShift / K8s MCP | ClusterIP services | Hub Lightspeed | No — use Hub MCP Chat |

Shared Sandbox models via LiteLLM drop tool calling for Continue chat models. Catalog/TechDocs MCP actions still work from the IDE over the Hub Route. Full K8s tool rounds stay on Hub with `litemaas-qwen` or OpenClaw + LiteMaaS.

## Wire Continue (v2) + optional Hub MCP

Devfile command `wire-continue` loads the Continue Secret and writes:

1. `~/.continue/config.yaml` — Continue **2.x** (models + optional `mcpServers`)
2. Workspace `.continue/config.json` — placeholders only (safe to commit; no live keys)

Example MCP block (token from Secret, not from git):

```yaml
mcpServers:
  - name: hub-mcp-actions
    type: sse
    url: https://<hub-route>/api/mcp-actions/v1
    requestOptions:
      headers:
        Authorization: Bearer <mcp-token>
```

```bash
oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.mcp-token}' | base64 -d
```

### Try the same prompts

**Continue chat (Step 07):**

> Reply with exactly: DevSpaces Continue OK

**MCP action (Step 08):**

> Use Hub MCP to list sample agent Components tagged agent.

Expected reaction names: `sample-python-agent`, `sample-nodejs-agent`, `sample-quarkus-agent`.

## Stop when done

```bash
oc patch dw rhdh-agent-ai-demo --type=merge -p '{"spec":{"started":false}}'
```

Or **Stop** in the Dev Spaces UI.

## Related

- Reference: [DevSpaces AI]({{ '/devspaces-ai/' | relative_url }})
- Hub tools: [Hub tool calling journey]({{ '/tool-calling-journey/' | relative_url }})
- OpenClaw: [OpenClaw journey]({{ '/openclaw-journey/' | relative_url }})
