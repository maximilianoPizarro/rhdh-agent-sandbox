---
layout: default
title: Quickstart
permalink: /quickstart/
---


## Prerequisites

- `oc login` to Developer Sandbox
- Helm 3.14+
- **Quota budget:** chart baseline is ~525m CPU / ~2.2Gi memory requests plus **6Gi PVC** (5Gi dynamic-plugins + 1Gi Postgres). Leave headroom before Golden Path agents or DevSpaces (~512Mi request / 3Gi limit per workspace).

## Install

From the Helm repo (reproducible chart tag):

```bash
helm repo add rhdh-agent https://maximilianopizarro.github.io/rhdh-agent-sandbox
helm repo update
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox --version 0.1.6 \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

Wait for Hub **2/2** (first pull can take 5–10 minutes):

```bash
oc wait --for=condition=available deploy/rhdh-agent-developer-hub -n "$(oc project -q)" --timeout=600s
```

Or from a git clone of this chart:

```bash
export MODEL_API_KEY=$(oc whoami -t)
helm dependency update
helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

OpenShift Console **Helm** form: set **Cluster Router Base** (required), OpenShift token, and LiteMaaS key. Leave Git revision empty to pin `v` + chart version (e.g. `v0.1.6`).

## Verify

```bash
oc get pods -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc get route -l app.kubernetes.io/part-of=rhdh-agent-sandbox
```

Open the Developer Hub route and sign in as **Guest**.

Refresh `model-api-key` only if Lightspeed or LiteLLM chat returns **401** (~24h token TTL):

```bash
oc patch secret/rhdh-agent-sandbox-secrets --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm
```

## Next steps

- Hub → **Create** → **Deploy Agent (Golden Path)**
- DevSpaces workspaces are created **stopped** — start from Dev Spaces after Create
- Open the new Component → **Topology** and **Documentation** tabs (Topology fills in after the BuildConfig Deployment is Ready; no git push)

## Reinstall from zero

`helm uninstall` runs a **pre-delete hook** that removes Golden Path workloads, pending catalog ConfigMaps, and chart PVCs (keeps `litemaas-credentials` and unlabeled apps like legacy demos).

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
helm repo update
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox --version 0.1.6 \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m --wait=false
```

See [Troubleshooting — Reinstall]({{ '/troubleshooting/' | relative_url }}) if Hub returns 503 or pods stay Pending.
