---
title: Install journey
carousel: true
---

# Helm install journey

<p class="muted">Install the chart on <strong>OpenShift Developer Sandbox</strong> with one Helm release. When pods are Ready, Topology shows the <code>rhdh-agent</code> application group — then sign in to Hub as Guest and run the <a href="{{ '/journey/' | relative_url }}">Golden Path journey</a>.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="Helm install journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 8">
<img src="{{ '/assets/diagrams/install-one-command.png' | relative_url }}" alt="Diagram: single helm upgrade installs Hub, LiteLLM, MCP, and applier" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Prerequisites</strong>
<span class="desc"><code>oc login</code> to Developer Sandbox, <code>helm</code> 3.14+, and ~1.5 CPU / 3 Gi quota free. Clone this repo or use the <a href="{{ '/quickstart/' | relative_url }}">Pages Helm repo</a>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 8" hidden>
<img src="{{ '/assets/screenshots/install-helm-command.png' | relative_url }}" alt="Terminal showing helm upgrade --install rhdh-agent" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>Helm install</strong>
<span class="desc">Run <code>helm dependency update</code> then <code>helm upgrade --install</code> with your Sandbox <code>clusterRouterBase</code> and <code>modelApiKey</code>. First pull takes 5–10 minutes.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 8" hidden>
<img src="{{ '/assets/screenshots/install-pods-ready.png' | relative_url }}" alt="oc get pods showing all rhdh-agent workloads Running" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Pods Ready</strong>
<span class="desc">Expect Hub <strong>2/2</strong>, LiteLLM, both MCP servers, agent-applier, and PostgreSQL <strong>Running</strong>. <code>ContainerCreating</code> during image pull is normal.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 8" hidden>
<img src="{{ '/assets/screenshots/install-routes.png' | relative_url }}" alt="oc get route for developer-hub and litellm" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Routes</strong>
<span class="desc">OpenShift creates Routes for <strong>developer-hub</strong> and <strong>litellm</strong>. DevSpaces and in-cluster MCP use ClusterIP only.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 8" hidden>
<img src="{{ '/assets/screenshots/topology-helm-ready.png' | relative_url }}" alt="OpenShift Topology: rhdh-agent group with postgresql, developer-hub, litellm, mcp, k8s-mcp, agent-applier" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>Topology — chart ready</strong>
<span class="desc">Application group <strong>rhdh-agent</strong>: PostgreSQL (SS), developer-hub, litellm, openshift-mcp, k8s-mcp, and agent-applier. No <code>sample-*-agent</code> pods — create agents via Golden Paths.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 8" hidden>
<img src="{{ '/assets/screenshots/install-model-token.png' | relative_url }}" alt="Terminal patching model-api-key and restarting litellm" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>Refresh model token</strong>
<span class="desc">Patch <code>model-api-key</code> with <code>oc whoami -t</code> (~24h TTL) and restart LiteLLM so shared Granite/Qwen models work. See <a href="{{ '/verify/' | relative_url }}">Verify</a>.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 8" hidden>
<img src="{{ '/assets/screenshots/hub-home.png' | relative_url }}" alt="Developer Hub home after Guest login" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>Guest login</strong>
<span class="desc">Open the Hub Route → sign in as <strong>Guest</strong>. Catalog, Lightspeed, MCP Chat, and Self-service templates are available.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 8" hidden>
<img src="{{ '/assets/screenshots/self-service-templates.png' | relative_url }}" alt="Self-service page with three Golden Path templates" />
<figcaption>
<span class="slide-num">Step 08</span>
<strong>Next: Golden Paths</strong>
<span class="desc">Create → <strong>Deploy Agent</strong>, <strong>DevSpaces AI Workspace</strong>, or <strong>AI Service with MCP wiring</strong>. Continue with the <a href="{{ '/journey/' | relative_url }}">Golden Path journey</a>.</span>
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
<span class="journey-status" id="journey-status" aria-live="polite">1 / 8</span>
</div>
</div>

## Quick commands

See [Quickstart]({{ '/quickstart/' | relative_url }}) for full install options (clone vs Pages Helm repo).

```bash
helm dependency update
helm upgrade --install rhdh-agent . \
  --namespace "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

Then [Verify the install]({{ '/verify/' | relative_url }}) and run the [Golden Path journey]({{ '/journey/' | relative_url }}).
