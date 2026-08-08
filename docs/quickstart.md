# Quickstart (Developer Sandbox)

## Prerequisites

- `oc` logged into Developer Sandbox
- `helm` 3.14+
- Namespace with enough quota for RHDH + Postgres + LiteLLM + MCP

## Install

```bash
git clone https://github.com/maximilianoPizarro/rhdh-agent-sandbox.git
cd rhdh-agent-sandbox

helm dependency update

export NAMESPACE=$(oc project -q)
export MODEL_API_KEY=$(oc whoami -t)
export APPS_DOMAIN=apps.rm2.thpm.p1.openshiftapps.com   # adjust to your sandbox

helm upgrade --install rhdh-agent . \
  --namespace "${NAMESPACE}" \
  -f values-sandbox.yaml \
  --set secrets.modelApiKey="${MODEL_API_KEY}" \
  --set rhdh.global.clusterRouterBase="${APPS_DOMAIN}" \
  --timeout 20m \
  --wait=false
```

## Verify

```bash
oc get pods,route,svc -n "${NAMESPACE}"
oc get secret rhdh-agent-sandbox-secrets -n "${NAMESPACE}"
```

Open the Developer Hub Route (name typically contains `developer-hub`).

On the login page, choose **Enter** / **Guest** — the sandbox profile enables anonymous guest access with the permission framework disabled so the demo user can use catalog, scaffolder, TechDocs, Lightspeed, and related UI without an IdP.

## Refresh model token

Sandbox model services sit behind oauth-proxy. Tokens expire (~24h):

```bash
oc set env secret/rhdh-agent-sandbox-secrets model-api-key="$(oc whoami -t)" -n "${NAMESPACE}"
oc rollout restart deploy -l app.kubernetes.io/component=litellm -n "${NAMESPACE}"
```
