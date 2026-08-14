# Quickstart

## Prerequisites

- `oc login` to Developer Sandbox
- Helm 3.14+
- **Quota budget:** ~525m CPU / ~2.2Gi memory requests plus 6Gi PVC before Golden Path agents or DevSpaces

## Install

From the Helm repo:

```bash
helm repo add rhdh-agent https://maximilianopizarro.github.io/rhdh-agent-sandbox
helm repo update
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox --version 0.1.11 \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com
```

## Verify

```bash
oc get pods -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc get route -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc wait --for=condition=available deploy/rhdh-agent-developer-hub -n "$(oc project -q)" --timeout=600s
```

Open the Developer Hub route and sign in as **Guest**.

## Next steps

- Hub → **Create** → **Deploy Agent (Golden Path)**
- DevSpaces workspaces start **stopped** — open from Dev Spaces after Create

## Reinstall from zero

`helm uninstall` runs a pre-delete hook (0.1.4+) that cleans Golden Path leftovers and chart PVCs.

```bash
helm uninstall rhdh-agent -n "$(oc project -q)"
helm repo update
helm upgrade --install rhdh-agent rhdh-agent/rhdh-agent-sandbox --version 0.1.11 \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com
```
