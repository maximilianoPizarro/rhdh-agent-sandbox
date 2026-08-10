---
title: DevSpaces journey
carousel: true
---

# DevSpaces + Continue AI journey

<p class="muted">In the browser IDE, <strong>Continue</strong> is the AI client. It talks to this chart in <strong>two separate paths</strong>: chat completions (LiteLLM) and optional Hub catalog tools (MCP Actions). Cluster Kubernetes tools stay on Hub — not in DevSpaces.</p>

## Mental model: AI chat ≠ MCP tools

Continue does **not** send chat messages through MCP. Chat and tools use different endpoints and secrets:

```text
Che Code + Continue (DevSpaces workspace)
 │
 ├── Path A — AI chat / edit (Steps 06–07)
 │     Continue  ──litellm-master-key──►  LiteLLM Route /v1
 │                                         └──► Granite or Qwen (shared models)
 │
 └── Path B — Hub MCP tools (Step 08, optional)
       Continue  ──mcp-token──►  Hub Route /api/mcp-actions/v1
                                   └──► catalog / TechDocs tools only
```

| | Path A — AI | Path B — Hub MCP |
|---|---|---|
| **What you prove** | Model replies in the Continue sidebar | Tool call lists catalog Components |
| **Endpoint** | LiteLLM Route `/v1` | Hub Route `/api/mcp-actions/v1` |
| **Auth** | Secret `rhdh-agent-sandbox-continue` (`LITELLM_API_*`) | `mcp-token` from `rhdh-agent-sandbox-secrets` |
| **Wired by** | `wire-continue` → `models:` in `~/.continue/config.yaml` | Same command → `mcpServers: hub-mcp-actions` when Hub Route + token exist |
| **Not available** | Native function-calling on shared Granite/Qwen | OpenShift/Kubernetes MCP (ClusterIP only — Step 09) |

**How it feels in the IDE:** you type in Continue. Path A always answers as a model. Path B only runs when you ask for catalog/TechDocs and Continue invokes an MCP tool (you should see a tool name such as `query-catalog-entities`, then a reaction with entity names).

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
<strong>Path A credentials (Continue Secret)</strong>
<span class="desc">The Helm chart creates Secret <code>rhdh-agent-sandbox-continue</code> with <code>LITELLM_API_BASE</code> (LiteLLM Route <code>/v1</code>) and <code>LITELLM_API_KEY</code> (<code>litellm-master-key</code>). That is <strong>only for AI chat</strong>. Hub MCP uses a different key (<code>mcp-token</code>). Never commit either value to git.</span>
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
<strong>Wire Continue (Path A + optional Path B)</strong>
<span class="desc">Continue is <strong>preinstalled</strong> (OpenVSX <code>.vsix</code> → <code>/tmp/continue.vsix</code>). Run Devfile command <code>wire-continue</code>: it writes <code>~/.continue/config.yaml</code> with <code>models:</code> → LiteLLM (Path A) and, if Hub Route + <code>mcp-token</code> exist, <code>mcpServers: hub-mcp-actions</code> (Path B). Select <strong>Granite (LiteLLM)</strong> — ignore the optional vendor Connect panel.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-chat.png' | relative_url }}" alt="Continue chat showing user query Reply with exactly DevSpaces Continue OK and Granite LiteLLM reply" />
<figcaption>
<span class="slide-num">Step 07 — Path A</span>
<strong>AI chat: query → model reply</strong>
<span class="desc"><strong>No MCP here.</strong> In Continue, ask: <em>Reply with exactly: DevSpaces Continue OK</em>. Continue posts to LiteLLM Route <code>/v1</code>; Granite answers. If you only see a model picker and no reply, Path A is not proven yet.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 9" hidden>
<img src="{{ '/assets/screenshots/devspaces-continue-mcp-action.png' | relative_url }}" alt="Continue showing MCP tool query-catalog-entities and reply listing sample agent components beside smoke markdown" />
<figcaption>
<span class="slide-num">Step 08 — Path B</span>
<strong>Hub MCP: tool action → catalog reaction</strong>
<span class="desc"><strong>Still in Continue, but a different network hop.</strong> Ask to list Components tagged <code>agent</code>. Continue calls Hub MCP Actions over the Hub Route. Action: <code>software-catalog-mcp-extras.query-catalog-entities</code>. Reaction: sample-python / nodejs / quarkus agents (same entities as the smoke markdown). This is catalog/TechDocs MCP — not Kubernetes.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="8" role="group" aria-roledescription="slide" aria-label="9 of 9" hidden>
<img src="{{ '/assets/screenshots/mcp-chat-toolcall-result.png' | relative_url }}" alt="Hub MCP Chat showing Kubernetes tool call results for pods in namespace" />
<figcaption>
<span class="slide-num">Step 09 — not DevSpaces</span>
<strong>Cluster MCP stays in Hub</strong>
<span class="desc">OpenShift/Kubernetes MCP services are <strong>ClusterIP only</strong> — Continue in DevSpaces cannot reach them. For K8s tool demos with <code>litemaas-qwen</code>, leave the IDE and use Hub <a href="{{ '/tool-calling-journey/' | relative_url }}">Lightspeed / MCP Chat</a>. Stop the DevSpaces workspace when finished to free Sandbox quota.</span>
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
| **A** Continue chat → reply | LiteLLM Route `/v1` | `rhdh-agent-sandbox-continue` | Yes (Step 07) |
| **B** Continue MCP → catalog | Hub Route `/api/mcp-actions/v1` | `mcp-token` | Yes (Step 08) |
| Cluster OpenShift / K8s MCP | ClusterIP services | Hub Lightspeed | **No** — Hub MCP Chat only |

Shared Sandbox models via LiteLLM do **not** do native function-calling for Continue chat. Path B still works because Continue talks to Hub MCP Actions as an MCP **client** (tools are on Hub). Full K8s tool rounds stay on Hub with `litemaas-qwen`, or OpenClaw + LiteMaaS.

## Wire Continue (v2): both paths in one command

Devfile command `wire-continue` loads secrets and writes:

1. `~/.continue/config.yaml` — Continue **2.x** live config (`models` + optional `mcpServers`)
2. Workspace `.continue/config.json` — placeholders only (safe to commit; no live keys)

Example Path B block (token from Secret, not from git):

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

**Path A — AI chat (Step 07):**

> Reply with exactly: DevSpaces Continue OK

**Path B — Hub MCP (Step 08):**

> Use Hub MCP to list sample agent Components tagged agent.

Expected reaction names: `sample-python-agent`, `sample-nodejs-agent`, `sample-quarkus-agent`.

## Stop when done

```bash
oc patch dw rhdh-agent-ai-demo --type=merge -p '{"spec":{"started":false}}'
```

Or **Stop** in the Dev Spaces UI.

## Related

- Reference: [DevSpaces AI]({{ '/devspaces-ai/' | relative_url }})
- Hub K8s tools: [Hub tool calling journey]({{ '/tool-calling-journey/' | relative_url }})
- OpenClaw: [OpenClaw journey]({{ '/openclaw-journey/' | relative_url }})
