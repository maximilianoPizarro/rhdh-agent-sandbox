# Quickstart

## Prerequisites

- `oc login` to Developer Sandbox
- Helm 3.14+
- ~1.5 CPU / 3 Gi quota free

## Install

```bash
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com
```

## Verify

```bash
oc get pods -l app.kubernetes.io/part-of=rhdh-agent-sandbox
oc get route -l app.kubernetes.io/part-of=rhdh-agent-sandbox
```

Open the Developer Hub route and sign in as **Guest**.

## Next steps

- Hub → **Create** → **Deploy Agent (Golden Path)**
- Open the new Component → **Topology** and **Documentation** tabs
