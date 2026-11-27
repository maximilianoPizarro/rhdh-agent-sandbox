---
layout: default
title: Upgrade to 0.2.0 (RHDH 2.1)
permalink: /upgrade-0.2.0/
---

# Upgrade to chart 0.2.0 (RHDH 2.1)

The last **0.1.x** line is frozen as git tag / GitHub Release **[v0.1.11](https://github.com/maximilianoPizarro/rhdh-agent-sandbox/releases/tag/v0.1.11)** (RHDH 1.10.3).

## Breaking changes

- Subchart **redhat-developer-hub 2.1.0** (Intelligent Assistant replaces Lightspeed UI path `/lightspeed` → `/intelligent-assistant`).
- Helm values remap: `rhdh.global.clusterRouterBase` → **`rhdh.openshift.clusterRouterBase`**.
- Embedded PostgreSQL is **18** — cannot reuse a 1.x PG15 PVC.
- Default chat model is in-namespace **`local-cpu`** InferenceService (llama.cpp), not sandbox-shared-models granite/qwen.
- Kubernetes MCP uses the **public** `quay.io/maximilianopizarro/openshift-mcp-server` image (or set `mcp.kubernetes.enabled=false`).

## Fresh install (required on Developer Sandbox)

```bash
# Preserve LiteMaaS key
oc get secret litemaas-credentials -o yaml > /tmp/litemaas-backup.yaml || true

helm uninstall rhdh-agent -n "$(oc project -q)"
# pre-delete hook removes chart PVCs; if any remain:
oc delete pvc data-rhdh-agent-sandbox-postgresql-0 --ignore-not-found
oc delete pvc -l app.kubernetes.io/name=developer-hub --ignore-not-found

helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set rhdh.openshift.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --set secrets.litemaasApiKey="<your-key>"   # optional
```

Wait for Hub and the CPU model:

```bash
oc wait --for=condition=available deploy/rhdh-agent-developer-hub --timeout=600s
oc wait --for=condition=Ready inferenceservice/local-cpu --timeout=600s
```

Open Intelligent Assistant and chat with **local-cpu**. Check OpenShift AI → Models for the InferenceService.

## Branding

Set `hub.title` / `hub.branding.theme.*` in values (mirrored under `rhdh.appConfig.app`) or override:

```bash
--set rhdh.appConfig.app.title='My Hub' \
--set rhdh.appConfig.app.branding.theme.light.primaryColor='#0066CC'
```
