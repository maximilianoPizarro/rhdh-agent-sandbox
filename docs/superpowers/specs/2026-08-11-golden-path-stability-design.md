# Golden Path Stability + Plugin Tabs + Tekton Deploy

**Date:** 2026-08-11  
**Status:** Draft for review  
**Approach:** B — layered reliability (root-cause + hardening), performance-first split

## Problem summary

Browser E2E of the three create Golden Paths exposed systemic instability and weak Component UX:

| Symptom | Root cause (evidence) |
|--------|------------------------|
| Deploy Agent build Complete but no Deployment/Service | `imagestream_has_image()` checks `tag.items` on ImageStreamTag (always empty); applier loops `waiting_for_image build_result=skipped` |
| Applier poll blocked / slow | Binary build wait lives inside applier cycle; concurrent agents starve AI/DevSpaces work |
| `catalog:wait-for-entity` fails at 120s | Catalog ingest slower than timeout; AI/DevSpaces tasks failed verify even though entities appeared later |
| OwnerPicker blocks browser submit | Expects entity object, not plain string |
| Warning `group:default/developers` missing | Group entity not present / not ingested |
| Component tabs underused | Missing `kubernetes-namespace`, weak API/dependsOn wiring; no real CI surface |
| Remove Golden Paths unreliable | Partial K8s cleanup; catalog entity can linger → applier recreates; no Tekton/PipelineRun cleanup planned |

## Goals (done = C)

1. Three create Golden Paths end `completed` with real runtime.
2. Deploy Agent: Tekton PipelineRun Succeeded + Deployment 1/1.
3. AI Service: `/mcp/smoke` OK; API + Dependencies populated.
4. DevSpaces: DevWorkspace Running.
5. Component shows useful **Topology**, **Kubernetes/CI via Tekton resources**, **API**, **Dependencies** (no broken Docs).
6. Three remove Golden Paths actually delete runtime + catalog so applier does not recreate.
7. Docs screenshots + reproducible E2E checklist updated.

## Non-goals (this pass)

- Live Red Hat Security MCP inside Hub (SSO browser).
- GitHub Actions CI plugin.
- Moving AI Service / DevSpaces builds into Tekton (they stay on applier for speed).

## Architecture decision

**Performance split**

- **Deploy Agent (heavy):** OpenShift BuildConfig binary path moves into a **Tekton Pipeline**. Applier only ensures Pipeline exists and starts an idempotent PipelineRun (keyed by agent-spec hash), then returns. No in-loop image wait.
- **AI Service + DevSpaces (light):** Remain on agent-applier (~one poll cycle). Keeps create latency low.
- **Remove:** Extended to delete Pipeline/PipelineRun/TaskRun + BC/IS (legacy) + Deploy/Service/DevWorkspace + registered catalog key + **catalog entity** so reconciliation cannot resurrect workloads.

```text
[Scaffolder create] → pending CM → applier registers entity
                         │
         ┌───────────────┼──────────────────┐
         ▼               ▼                  ▼
   managed-agent    managed-ai         managed-dw
   trigger Tekton   deploy HTTP svc    create DevWorkspace
   PipelineRun      (applier)          (applier)
         │
         ▼
   Tasks: materialize → buildah → deploy → verify
```

## Workstreams

### 1) Applier reliability (still required)

- Fix image detection if any legacy path remains: use `ImageStreamTag.image` or `ImageStream.status.tags[].items`.
- After Tekton cutover for agents: remove / short-circuit `start_binary_build` wait path for `managed-agent`; implement `ensure_pipeline` + `start_pipelinerun_if_needed`.
- Keep AI/DevSpaces ensure paths; do not block them on agent builds.
- Structured logs: `pipelinerun_started`, `pipelinerun_unchanged`, `image_ready` (if retained), `deploy_ensured`.

### 2) Tekton Pipeline for Deploy Agent

Namespace-scoped resources (Helm templates):

- `Pipeline` `deploy-agent` (or release-prefixed name)
- Tasks:
  1. **materialize** — skeleton + agentSpec into workspace (from ConfigMap/chart assets or params)
  2. **build** — Buildah → push `image-registry.../<ns>/<name>:latest`
  3. **deploy** — apply Deployment + Service (same labels as today)
  4. **verify** — wait for rollout ready (short timeout)
- `PipelineRun` params: `name`, `language`, `framework`, `model`, `agentType`, `agentSpec`, `image`
- Idempotency: annotation/label `rhdh-agent-sandbox.io/spec-hash`; skip new run if Succeeded run with same hash exists and Deployment healthy.
- RBAC: Pipeline SA can create builds/deployments/imagestreams in namespace; Hub/applier SA can create PipelineRuns.

Catalog annotations on Component:

- `backstage.io/kubernetes-label-selector: app.kubernetes.io/name=<name>`
- `backstage.io/kubernetes-namespace: <release-ns>`
- Tekton-related labels on PipelineRun/Deploy so Topology/Kubernetes show pipeline + workload.

### 3) Catalog wait + register path

- Raise `catalog:wait-for-entity` `timeoutSeconds` to ~300 on create templates.
- After `catalog:apply-pending-configmap`, trigger catalog refresh (location or registered entities) before/during wait.
- Clearer timeout errors (last HTTP status/body).
- Ensure pending entity YAML always includes `kubernetes-namespace`.

### 4) Component plugin tabs

| Tab | How |
|-----|-----|
| Topology / Kubernetes | Namespace + label selector; labels on Deploy/Service/PipelineRun/IS |
| API | `dependsOn` MCP APIs; AI Service `providesApis` with small HTTP/MCP smoke API entity |
| Dependencies | Real `Group` `developers` + `system: agent-sandbox` + dependsOn |
| Docs | No `techdocs-ref` on golden-path entities |
| CI | Tekton PipelineRuns visible via Kubernetes/Topology (no new CI plugin this pass) |

### 5) Owner / Group / OwnerPicker

- Ship `Group` `default/developers` in catalog ConfigMap.
- Template defaults: owner prefilled to `group:default/developers`.
- Prefer OwnerPicker options that resolve without browser object quirks (default + optional EntityPicker fix / string fallback documented for API).

### 6) Remove Golden Paths (must work)

Hardening `catalog:remove-entity`:

1. Delete pending CM + patch registered-catalog key (existing).
2. Delete Deploy + Service (existing).
3. Delete DevWorkspace when annotated (existing).
4. **New:** Delete Tekton `PipelineRun`s labeled for the agent; optional shared Pipeline left in place.
5. **New:** Delete legacy BuildConfig/ImageStream/Builds if present.
6. **New:** Delete catalog entity via Catalog API (`DELETE` by-uid or location refresh that drops orphan) so applier cannot see it and recreate.
7. Refresh catalog; optional short `wait-until-absent`.
8. RBAC: add `tekton.dev` PipelineRuns (and related) delete/list to hub-scaffolder Role.
9. Remove templates: confirm step that logs remaining resources or fails if Deploy still present.

Anti-recreate rule: **never leave Component in catalog if runtime was deleted.**

### 7) Validation + docs

- E2E checklist (create ×3, remove ×3) with expected task status and `oc` probes.
- Refresh screenshots: forms, tasks, Topology (with Tekton), API/Dependencies, smoke, remove success.
- Update `scripts/render-ocp-terminal-screenshots.py` for `gp-browser-*` / PipelineRun commands.

## Success criteria checklist

- [ ] `deploy-agent` task completed; PipelineRun Succeeded; Deployment 1/1; Topology shows resources
- [ ] `ai-service-with-mcp` completed; `/mcp/smoke` both MCP tools ok; API tab has provides/depends
- [ ] `agent-friendly-devspaces-workspace` completed; DevWorkspace Running
- [ ] Remove templates for all three leave zero Deploy/Service/DW/PR for that name and no catalog Component
- [ ] Applier poll cycles stay short while an agent PipelineRun is running (no multi-minute `building` block)
- [ ] No `group:default/developers` missing warning on new Components
- [ ] Docs screenshots + E2E checklist committed

## Risks

- Developer Sandbox Tekton operator availability / SCC for Buildah — verify early; fallback keep BC path behind flag if Pipeline cannot run.
- Catalog delete permissions for Hub token — validate MCP_TOKEN can delete entities or use location-only drop.
- Dynamic plugin image rebuild needed for remove/wait action changes.

## Implementation order (for later plan)

1. Fix remove + Group entity (stops recreate loops)  
2. Catalog annotations + wait timeouts (tabs + create green)  
3. Tekton Pipeline + applier trigger (performance)  
4. API relations for AI/Deploy  
5. E2E + screenshots + checklist  
