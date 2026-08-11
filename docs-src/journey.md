---
title: Golden Path journey
carousel: true
---

# Golden Path journey

<p class="muted">End-to-end walkthrough of the three Golden Paths: Deploy Agent, DevSpaces AI Workspace, and AI Service with MCP wiring. Install the chart first via the <a href="{{ '/install-journey/' | relative_url }}">Helm install journey</a>.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="Golden Path journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 12">
<img src="{{ '/assets/screenshots/hub-home.png' | relative_url }}" alt="Developer Hub home page with Welcome back greeting" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Developer Hub home</strong>
<span class="desc">After <a href="{{ '/install-journey/' | relative_url }}">Helm install</a>, sign in as <strong>Guest</strong>. Explore, Learn, and Self-service cards are ready.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 12" hidden>
<img src="{{ '/assets/screenshots/self-service-templates.png' | relative_url }}" alt="Self-service page showing 3 Golden Path templates" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>Three Golden Paths</strong>
<span class="desc">Create → <strong>Deploy Agent</strong>, <strong>Agent-friendly DevSpaces AI Workspace</strong>, or <strong>AI Service with MCP wiring</strong>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 12" hidden>
<img src="{{ '/assets/screenshots/deploy-agent-form.png' | relative_url }}" alt="Deploy Agent form with agent name, owner, language, agent type and specification fields" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Deploy Agent — form</strong>
<span class="desc">Name, owner, language (Python/Node.js/Quarkus), <code>agentType</code>, <code>agentSpec</code>, and LiteLLM model. Framework is mapped deterministically.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 12" hidden>
<img src="{{ '/assets/screenshots/deploy-agent-success.png' | relative_url }}" alt="Deploy Agent template completed with green checkmarks" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Deploy Agent — success</strong>
<span class="desc">Four green steps: resolve framework → fetch skeleton → <code>catalog:write</code> with <code>build=true</code> → applier hint. No git push.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 12" hidden>
<img src="{{ '/assets/screenshots/deploy-agent-build.png' | relative_url }}" alt="Terminal showing BuildConfig and Deployment for a user-created agent" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>Deploy Agent — build + pod</strong>
<span class="desc">agent-applier creates ImageStream + BuildConfig, runs a binary Docker build from chart skeleton sources, then deploys the image. Verify with <code>oc get bc</code> and <code>/health</code>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 12" hidden>
<img src="{{ '/assets/screenshots/catalog-component-detail.png' | relative_url }}" alt="Catalog component detail for a golden-path agent with build annotations" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>Catalog — your agent Component</strong>
<span class="desc">Component with <code>managed-agent=true</code>, <code>build=true</code>, language/framework annotations, and optional DevSpaces factory link.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 12" hidden>
<img src="{{ '/assets/screenshots/devspaces-form.png' | relative_url }}" alt="DevSpaces AI Workspace form with name, owner, agent language and model" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>DevSpaces — form</strong>
<span class="desc">Choose workspace name, owner, <strong>agent language</strong> (Python / Node.js / Quarkus), and default Continue model.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 12" hidden>
<img src="{{ '/assets/screenshots/devspaces-success.png' | relative_url }}" alt="DevSpaces template success with three green steps" />
<figcaption>
<span class="slide-num">Step 08</span>
<strong>DevSpaces — success</strong>
<span class="desc">Three steps green. Component registered with <code>managed-devworkspace=true</code>. agent-applier creates a <strong>started</strong> DevWorkspace — no push-to-git.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="8" role="group" aria-roledescription="slide" aria-label="9 of 12" hidden>
<img src="{{ '/assets/screenshots/devspaces-dashboard-workspaces.png' | relative_url }}" alt="DevSpaces dashboard listing workspaces" />
<figcaption>
<span class="slide-num">Step 09</span>
<strong>DevSpaces — open workspace</strong>
<span class="desc">Open the DevSpaces dashboard, select your workspace, and start coding. Continue wires to LiteLLM on postStart. Deeper IDE flow: <a href="{{ '/devspaces-journey/' | relative_url }}">DevSpaces journey</a>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="9" role="group" aria-roledescription="slide" aria-label="10 of 12" hidden>
<img src="{{ '/assets/screenshots/ai-service-form.png' | relative_url }}" alt="AI Service with MCP wiring form" />
<figcaption>
<span class="slide-num">Step 10</span>
<strong>AI Service with MCP — form</strong>
<span class="desc">Name, owner, and default LiteLLM model. The service will call in-cluster Kubernetes and OpenShift MCP servers.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="10" role="group" aria-roledescription="slide" aria-label="11 of 12" hidden>
<img src="{{ '/assets/screenshots/ai-service-success.png' | relative_url }}" alt="AI Service template success showing MCP wiring output" />
<figcaption>
<span class="slide-num">Step 11</span>
<strong>AI Service — success</strong>
<span class="desc">Component registered with <code>managed-ai-service=true</code>. agent-applier deploys an HTTP service with <code>GET /mcp/smoke</code>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="11" role="group" aria-roledescription="slide" aria-label="12 of 12" hidden>
<img src="{{ '/assets/screenshots/ai-service-mcp-smoke.png' | relative_url }}" alt="curl output from /mcp/smoke showing k8s_mcp and openshift_mcp ok" />
<figcaption>
<span class="slide-num">Step 12</span>
<strong>AI Service — MCP smoke</strong>
<span class="desc"><code>curl http://&lt;name&gt;:8080/mcp/smoke</code> calls <code>pods_list_in_namespace</code> (k8s-mcp) and <code>monitorDeployments</code> (openshift-mcp). Hub MCP Chat demos: <a href="{{ '/tool-calling-journey/' | relative_url }}">tool calling journey</a>.</span>
</figcaption>
</figure>

</div>
<div class="journey-controls">
<div class="journey-nav">
<button type="button" class="journey-btn" id="journey-prev" aria-label="Previous slide">← Prev</button>
<button type="button" class="journey-btn" id="journey-next" aria-label="Next slide">Next →</button>
<button type="button" class="journey-btn" id="journey-fs" aria-label="Toggle fullscreen" aria-pressed="false">Fullscreen</button>
</div>
<div class="journey-dots" id="journey-dots" role="tablist" aria-label="Slide picker"></div>
<span class="journey-status" id="journey-status" aria-live="polite">1 / 12</span>
</div>
</div>

## The three Golden Paths

| Template | What it does | Steps |
|----------|-------------|-------|
| **Deploy Agent** | Generates real LangGraph / LangChain.js / LangChain4j source, BuildConfig-compiles, and deploys without git push. | resolve → fetch → `catalog:write` (`build=true`) → applier builds + deploys |
| **DevSpaces AI Workspace** | Creates a started DevWorkspace with Continue→LiteLLM for the selected agent language. | `catalog:write` (`managed-devworkspace=true`) → applier creates DevWorkspace |
| **AI Service with MCP wiring** | Deploys a small HTTP service that smoke-calls Kubernetes + OpenShift MCP (`/mcp/smoke`). | `catalog:write` (`managed-ai-service=true`) → applier deploys Service |

## Verify

```bash
# Deploy Agent — watch build then pod
oc get bc/<agent-name>
oc logs -f bc/<agent-name>
oc get deploy/<agent-name>
curl -s http://<agent-name>:8080/health

# DevSpaces — open started workspace (no git push)
oc get dw <workspace-name>
# Open DevSpaces dashboard → Open workspace

# AI Service — MCP smoke
oc run curl-smoke --rm -i --restart=Never --image=registry.access.redhat.com/ubi9/ubi-minimal:latest -- \
  curl -s http://<service-name>:8080/mcp/smoke
```
