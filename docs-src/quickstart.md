---
layout: default
title: Quickstart
permalink: /quickstart/
---


## Prerequisites

- `oc login` to Developer Sandbox
- Helm 3.14+
- ~1.5 CPU / 3 Gi quota free

## Install

From the Helm repo (reproducible chart tag):

```bash
helm repo add rhdh-agent https://maximilianopizarro.github.io/rhdh-agent-sandbox
helm repo update
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox --version 0.1.3 \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com
```

Or from a git clone of this chart:

```bash
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com
```

OpenShift Console **Helm** form: set Cluster Router Base, OpenShift token, and LiteMaaS key. Leave Git revision at `v0.1.3`.

## Verify

```bash
oc get pods -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc get route -l app.kubernetes.io/part-of=rhdh-agent-sandbox
```

Open the Developer Hub route and sign in as **Guest**.

## Next steps

- Hub → **Create** → **Deploy Agent (Golden Path)**
- Open the new Component → **Topology** and **Documentation** tabs (Topology fills in after the BuildConfig Deployment is Ready; no git push)

## Reinstall from zero

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
oc delete pvc data-rhdh-agent-postgresql-0 --ignore-not-found
helm dependency update
helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com \
  --timeout 20m --wait=false
```

See [Troubleshooting — Reinstall]({{ '/troubleshooting/' | relative_url }}) if Hub returns 503 or pods stay Pending.
