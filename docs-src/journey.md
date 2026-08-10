# Golden Path journey

<p class="muted">End-to-end walkthrough of the three Golden Paths: Deploy Agent, DevSpaces AI Workspace, and AI Service with MCP wiring.</p>

<div class="journey-carousel" id="journey-carousel" role="region" aria-roledescription="carousel" aria-label="Golden Path journey" tabindex="0">
<div class="journey-viewport" id="journey-viewport">

<figure class="journey-slide is-active" data-slide="0" role="group" aria-roledescription="slide" aria-label="1 of 10">
<img src="../assets/screenshots/hub-home.png" alt="Developer Hub home page with Welcome back greeting" />
<figcaption>
<span class="slide-num">Step 01</span>
<strong>Developer Hub home</strong>
<span class="desc">Login as Guest and land on the home page. Explore, Learn, and Self-service cards are ready.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="1" role="group" aria-roledescription="slide" aria-label="2 of 10" hidden>
<img src="../assets/screenshots/templates-all-3.png" alt="Self-service page showing 3 Golden Path templates" />
<figcaption>
<span class="slide-num">Step 02</span>
<strong>Three Golden Paths</strong>
<span class="desc">Three templates available: Agent-friendly DevSpaces AI Workspace, AI Service with MCP wiring, and Deploy Agent (Golden Path).</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="2" role="group" aria-roledescription="slide" aria-label="3 of 10" hidden>
<img src="../assets/screenshots/deploy-agent-form.png" alt="Deploy Agent form with agent name, owner, language and specification fields" />
<figcaption>
<span class="slide-num">Step 03</span>
<strong>Deploy Agent — form</strong>
<span class="desc">Fill agent name, owner, language (Python/Node.js/Quarkus), agent spec, and model. Framework is resolved deterministically.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="3" role="group" aria-roledescription="slide" aria-label="4 of 10" hidden>
<img src="../assets/screenshots/deploy-agent-success.png" alt="All 5 steps completed successfully with green checkmarks" />
<figcaption>
<span class="slide-num">Step 04</span>
<strong>Deploy Agent — success</strong>
<span class="desc">All steps green: skeleton materialized, runtime manifests applied, Component registered. The agent-applier creates the Deployment + Service automatically.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="4" role="group" aria-roledescription="slide" aria-label="5 of 10" hidden>
<img src="../assets/screenshots/devspaces-form.png" alt="DevSpaces AI Workspace form with name, owner and stack fields" />
<figcaption>
<span class="slide-num">Step 05</span>
<strong>DevSpaces Workspace — form</strong>
<span class="desc">Choose a name, owner, and stack (nodejs/python/quarkus). This scaffolds a browser IDE workspace with Devfile + Continue AI config.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="5" role="group" aria-roledescription="slide" aria-label="6 of 10" hidden>
<img src="../assets/screenshots/devspaces-review.png" alt="DevSpaces template review showing all parameters" />
<figcaption>
<span class="slide-num">Step 06</span>
<strong>DevSpaces Workspace — review</strong>
<span class="desc">Review the parameters before creation: Description, Stack, Name and Owner are confirmed.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="6" role="group" aria-roledescription="slide" aria-label="7 of 10" hidden>
<img src="../assets/screenshots/devspaces-success.png" alt="DevSpaces template executed successfully with both steps green" />
<figcaption>
<span class="slide-num">Step 07</span>
<strong>DevSpaces Workspace — success</strong>
<span class="desc">Fetch skeleton + Publish instructions complete. Next steps guide you to push to Git, open in DevSpaces, and wire Continue to LiteLLM.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="7" role="group" aria-roledescription="slide" aria-label="8 of 10" hidden>
<img src="../assets/screenshots/ai-service-form.png" alt="AI Service with MCP wiring form with name, owner and model fields" />
<figcaption>
<span class="slide-num">Step 08</span>
<strong>AI Service with MCP — form</strong>
<span class="desc">Name your service, pick an owner, and select the default LLM model (granite or qwen3) via LiteLLM proxy.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="8" role="group" aria-roledescription="slide" aria-label="9 of 10" hidden>
<img src="../assets/screenshots/ai-service-review.png" alt="AI Service review page showing granite model, name and owner" />
<figcaption>
<span class="slide-num">Step 09</span>
<strong>AI Service with MCP — review</strong>
<span class="desc">Confirm model (granite), service name, and owner before scaffolding the AI service with MCP wiring.</span>
</figcaption>
</figure>

<figure class="journey-slide" data-slide="9" role="group" aria-roledescription="slide" aria-label="10 of 10" hidden>
<img src="../assets/screenshots/ai-service-success.png" alt="AI Service template executed successfully showing Connect to Lightspeed output" />
<figcaption>
<span class="slide-num">Step 10</span>
<strong>AI Service with MCP — success</strong>
<span class="desc">Skeleton fetched and logged. "Connect to Lightspeed" output tells you how to point clients at the LiteLLM route and register MCP servers.</span>
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
<span class="journey-status" id="journey-status" aria-live="polite">1 / 10</span>
</div>
</div>

## The three Golden Paths

| Template | What it does | Steps |
|----------|-------------|-------|
| **Deploy Agent** | Creates a namespace-scoped agent Pod (Deployment + Service) without git push. Framework chosen from language. | fetch skeleton → fetch runtime → catalog:write → agent-applier creates K8s resources |
| **DevSpaces AI Workspace** | Scaffolds a repository with Devfile, Continue→LiteLLM config, and AI skills for browser IDE. | fetch skeleton from GitHub → log next steps |
| **AI Service with MCP wiring** | Scaffolds a service with catalog Component/API entities for MCP and Lightspeed integration. | fetch skeleton from GitHub → log next actions |

## What happens behind the scenes

1. **Resolve framework** — `python` → LangGraph, `nodejs` → LangChain.js, `quarkus` → LangChain4j
2. **Materialize skeleton** — `fetch:template` downloads files from GitHub repository
3. **Materialize runtime** — language-specific Deployment + Service manifests (Deploy Agent only)
4. **Write Component** — `catalog:write` registers the entity directly in the Hub catalog
5. **Agent-applier** — watches for `managed-agent` annotations and creates/updates K8s resources

## Verify

```bash
# Deploy Agent — check the deployed pod
oc get deploy/<agent-name>
oc logs deploy/<agent-name>
curl -s http://<agent-name>:8080/health | jq .

# DevSpaces — push and open workspace
git push && open DevSpaces factory URL

# AI Service — point clients at LiteLLM
curl -s https://<litellm-route>/v1/models -H "Authorization: Bearer $KEY"
```
