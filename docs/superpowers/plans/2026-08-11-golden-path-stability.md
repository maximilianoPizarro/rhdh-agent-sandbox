# Golden Path Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize create/remove Golden Paths, move Deploy Agent build+deploy to Tekton (free applier), and wire Component tabs (Topology/API/Dependencies).

**Architecture:** Performance split — Tekton Pipeline for managed agents; applier keeps AI Service + DevSpaces. Remove deletes catalog entity + Tekton runs + runtime so applier cannot recreate.

**Tech Stack:** Helm chart, agent-applier (Python in ConfigMap), scaffolder TS actions, Tekton `tekton.dev/v1`, Backstage catalog entities.

**Spec:** `docs/superpowers/specs/2026-08-11-golden-path-stability-design.md`

## Global Constraints

- Do not commit unless the user explicitly asks (session rule).
- Tekton only for Deploy Agent; AI/DevSpaces stay on applier.
- No new CI plugin; PipelineRuns visible via Kubernetes/Topology labels.
- Preserve existing template names and screenshot filenames when updating docs later.
- Hub SA for scaffolder is `default` (+ `*-developer-hub`); extend `templates/hub-scaffolder-rbac.yaml`.
- Namespace is always `.Release.Namespace`.
- Cluster has `tekton.dev/v1` Pipeline and PipelineRun.

## File map

| Area | Files |
|------|--------|
| Remove | `community-plugins/.../createRemoveEntityAction.ts`, `hub-scaffolder-rbac.yaml` |
| Group/catalog | `files/catalog/groups.yaml`, `files/catalog/all.yaml`, `templates/catalog-configmap.yaml` |
| Entity tabs | `files/templates/scaffolder/pending-catalog-entity*/kubernetes/configmap.yaml` |
| Waits | `files/catalog/template-deploy-agent.yaml`, `template-ai-service.yaml`, `template-devspaces-workspace.yaml` |
| Tekton | `templates/deploy-agent-pipeline.yaml` (new), RBAC |
| Applier | `templates/agent-applier.yaml` |
| Wait action | `createWaitForEntityAction.ts` |

---

### Task 1: Group entity + catalog wiring

**Files:**
- Create: `files/catalog/groups.yaml`
- Modify: `files/catalog/all.yaml`
- Modify: `templates/catalog-configmap.yaml`

- [ ] Add Group `developers` (`group:default/developers`) with member `user:default/guest`
- [ ] Add `./groups.yaml` to `all.yaml` targets
- [ ] Wire `groups.yaml` into `catalog-configmap.yaml` like `users.yaml`
- [ ] Do not commit

**Produces:** `group:default/developers` available to catalog.

---

### Task 2: Harden `catalog:remove-entity`

**Files:**
- Modify: `community-plugins/scaffolder-backend-module-catalog-register/src/actions/createRemoveEntityAction.ts`
- Modify: `templates/hub-scaffolder-rbac.yaml`

- [ ] List+delete PipelineRuns labeled `app.kubernetes.io/name=<name>`
- [ ] Always try delete BC/IS/Deploy/Service/DevWorkspace for name (404 OK)
- [ ] DELETE catalog entity by uid after GET by-name (MCP_TOKEN)
- [ ] Refresh `location:default/rhdh-agent-sandbox-catalog`
- [ ] RBAC: `tekton.dev` pipelineruns/taskruns get/list/watch/delete; pipelines get/list
- [ ] Do not commit

**Produces:** Remove leaves no runtime + no catalog Component.

---

### Task 3: Pending entity annotations + API relations + wait timeouts

**Files:**
- Modify pending entity configmaps under `files/templates/scaffolder/pending-catalog-entity*/`
- Modify create templates under `files/catalog/template-*.yaml`

- [ ] Deploy-agent pending: `dependsOn` MCP APIs; keep k8s label selector; applier still injects namespace
- [ ] AI pending: multi-doc YAML with API `${{ values.name }}-http` + Component `providesApis`
- [ ] DevSpaces pending: k8s label selector + `rhdh-agent-sandbox.io/managed-devworkspace: "true"`
- [ ] All create templates: `timeoutSeconds: 300` on wait-for-entity
- [ ] Do not commit

**Produces:** Topology/API/Dependencies usable; slower catalog OK.

---

### Task 4: Tekton Pipeline for Deploy Agent

**Files:**
- Create: `templates/deploy-agent-pipeline.yaml`
- Modify: `templates/hub-scaffolder-rbac.yaml` (create pipelineruns for default SA / applier)

- [ ] Pipeline `{{ fullname }}-deploy-agent` with params name/language/image/model/agent-type/agent-spec/namespace
- [ ] Tasks: materialize (from build-sources CM) → buildah build+push → deploy Deployment/Service → rollout verify
- [ ] Labels on created Deploy/PR: `app.kubernetes.io/name=$(params.name)`, `app.kubernetes.io/part-of={{ fullname }}`
- [ ] RoleBinding for `pipeline` SA with deploy/build/image rights in namespace
- [ ] Hub/applier can create PipelineRuns
- [ ] Do not commit

**Produces:** Pipeline installable via helm.

---

### Task 5: Applier triggers PipelineRun (non-blocking)

**Files:**
- Modify: `templates/agent-applier.yaml`

- [ ] Fix `imagestream_has_image` to use presence of `.image` on ImageStreamTag
- [ ] For managed-agent build=true: start/ensure PipelineRun with spec-hash; do not binary-build wait loop
- [ ] Return building only if PR Pending/Running; ensure deploy if PR Succeeded and deploy missing
- [ ] Do not commit

**Produces:** Fast applier polls during agent builds.

---

### Task 6: Wait-for-entity catalog refresh

**Files:**
- Modify: `createWaitForEntityAction.ts`

- [ ] Every 3rd 404 poll, POST `/api/catalog/refresh` with `entityRef: location:default/rhdh-agent-sandbox-catalog`
- [ ] Do not commit

---

### Task 7: E2E checklist

**Files:**
- Create: `docs/superpowers/specs/2026-08-11-golden-path-e2e-checklist.md`

- [ ] Create×3 / remove×3 checklist with oc/curl probes
- [ ] Do not commit

---

## Parallel waves

- **Wave A (parallel):** Tasks 1, 2, 3, 4
- **Wave B (after 4):** Task 5
- **Wave C (parallel with B):** Tasks 6, 7
