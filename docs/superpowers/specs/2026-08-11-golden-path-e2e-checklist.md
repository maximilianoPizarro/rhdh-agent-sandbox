# Golden Path E2E Checklist

**Date:** 2026-08-11  
**Spec:** [golden-path-stability-design.md](./2026-08-11-golden-path-stability-design.md)  
**Plan:** [golden-path-stability.md](../plans/2026-08-11-golden-path-stability.md)

Set `NS` to the release namespace and `NAME` to the workload name used in each run.

```bash
export NS=<release-namespace>
```

---

## Create — Deploy Agent

- [ ] Scaffolder task `deploy-agent` **completed** (no failed steps)
- [ ] PipelineRun Succeeded: `oc get pipelinerun -n $NS -l app.kubernetes.io/name=$NAME -o jsonpath='{.items[0].status.conditions[?(@.type=="Succeeded")].status}'` → `True`
- [ ] Deployment ready: `oc get deploy -n $NS -l app.kubernetes.io/name=$NAME -o jsonpath='{.items[0].status.readyReplicas}'` → `1`
- [ ] Service exists: `oc get svc -n $NS -l app.kubernetes.io/name=$NAME`
- [ ] Component **Topology** shows PipelineRun + Deployment/Service
- [ ] Component **API** tab lists MCP dependencies (`dependsOn`)
- [ ] Component **Dependencies** tab shows `group:default/developers` and `system:agent-sandbox` (no missing-group warning)

---

## Create — AI Service

- [ ] Scaffolder task `ai-service-with-mcp` **completed**
- [ ] Deployment ready: `oc get deploy -n $NS -l app.kubernetes.io/name=$NAME -o jsonpath='{.items[0].status.readyReplicas}'` → `1`
- [ ] `/mcp/smoke` OK (both MCP tools): `curl -sf "https://<route>/$NAME/mcp/smoke"` (or port-forward + local curl)
- [ ] Component **API** tab shows `providesApis` + `dependsOn`
- [ ] Component **Topology** shows Deployment/Service
- [ ] Component **Dependencies** tab populated

---

## Create — DevSpaces

- [ ] Scaffolder task `agent-friendly-devspaces-workspace` **completed**
- [ ] DevWorkspace Running: `oc get devworkspace -n $NS -l app.kubernetes.io/name=$NAME -o jsonpath='{.items[0].status.phase}'` → `Running`
- [ ] Component **Topology** shows DevWorkspace
- [ ] Component **Dependencies** tab populated

---

## Applier performance (during agent build)

While a Deploy Agent PipelineRun is **Pending/Running**:

- [ ] Applier logs show short poll cycles (no multi-minute `building` / `waiting_for_image` block)
- [ ] AI Service or DevSpaces create can still progress in parallel (applier not starved)

```bash
oc logs -n $NS deploy/<release>-agent-applier --tail=50 | grep -E 'poll|pipelinerun_started|building'
```

---

## Remove — all three Golden Paths

Run remove template for each created workload (`$NAME` = deploy-agent, ai-service, devspaces names).

- [ ] Remove task **completed** for Deploy Agent
- [ ] Remove task **completed** for AI Service
- [ ] Remove task **completed** for DevSpaces
- [ ] No runtime left (all three names):

```bash
for n in <agent-name> <ai-name> <dw-name>; do
  echo "=== $n ==="
  oc get deploy,svc,devworkspace,pipelinerun,buildconfig,imagestream -n $NS -l app.kubernetes.io/name=$n 2>/dev/null
done
```

- [ ] No catalog Component remains:

```bash
curl -sf -H "Authorization: Bearer $MCP_TOKEN" \
  "https://<hub>/api/catalog/entities/by-name/component/default/<name>" \
  && echo "STILL PRESENT — FAIL" || echo "absent OK"
```

- [ ] Applier does **not** recreate workloads after remove (wait one poll cycle, re-run `oc get` above)

---

## Pass criteria

All checkboxes above checked → Golden Path stability E2E **pass**.
