# Quickstart

Step-by-step install on **OpenShift Developer Sandbox**.

## 1. Prerequisites

| Requirement | Notes |
|---|---|
| `oc` logged into Sandbox | `oc whoami` and `oc project` succeed |
| `helm` 3.14+ | `helm version` |
| Quota headroom | Roughly: Hub ~1Gi, Postgres ~256Mi, LiteLLM ~512Mi request / 1.5Gi limit, MCP small. Leave room for one modest DevSpaces workspace (~200m / 1Gi). |
| DevSpaces Operator | Already available on Developer Sandbox (do not install) |

Discover your apps domain:

```bash
oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}{"\n"}'
# example: apps.rm2.thpm.p1.openshiftapps.com
```

## 2. Clone and pull chart dependencies

```bash
git clone https://github.com/maximilianoPizarro/rhdh-agent-sandbox.git
cd rhdh-agent-sandbox

helm dependency update
```

## 3. Install / upgrade

```bash
export NAMESPACE=$(oc project -q)
export MODEL_API_KEY=$(oc whoami -t)
export APPS_DOMAIN=$(oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}')

helm upgrade --install rhdh-agent . \
  --namespace "${NAMESPACE}" \
  --set secrets.modelApiKey="${MODEL_API_KEY}" \
  --set rhdh.global.clusterRouterBase="${APPS_DOMAIN}" \
  --timeout 20m \
  --wait=false
```

!!! tip "Single values file"
    All Sandbox defaults live in `values.yaml`. You only need `--set` for the model token and apps domain (if it differs from the default in the file).

First install pulls large images (RHDH, LiteLLM). Expect several minutes before pods are Ready.

## 4. Wait for pods

```bash
oc get pods -n "${NAMESPACE}" -w
```

Target state (names may include a release prefix):

| Pod / Deployment | Ready |
|---|---|
| `*-developer-hub-*` | `2/2` (backstage-backend + lightspeed-core) |
| `*-postgresql-0` | `1/1` |
| `*-litellm-*` | `1/1` |
| `*-mcp-*` and `*-k8s-mcp-*` | `1/1` |

```bash
oc rollout status deploy/rhdh-agent-developer-hub -n "${NAMESPACE}" --timeout=10m
oc rollout status deploy/rhdh-agent-sandbox-litellm -n "${NAMESPACE}" --timeout=5m
```

## 5. Open Developer Hub

```bash
oc get route -n "${NAMESPACE}" | grep developer-hub
```

1. Open the Hub Route URL in a browser.  
2. On the login page, choose **Enter** / **Guest**.  
3. Confirm you can open Catalog and the Lightspeed FAB / page.

Guest access is intentional for this demo (`auth.environment: development`, `permission.enabled: false`). No IdP required.

## 6. Refresh the model token later

Shared models sit behind oauth-proxy. The OpenShift user token in `model-api-key` expires about every **24 hours**:

```bash
oc patch secret/rhdh-agent-sandbox-secrets -n "${NAMESPACE}" --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm -n "${NAMESPACE}"
```

!!! warning
    Do not use `oc set env secret/...` — that command targets Deployments/Pods, not Secrets. Use `oc patch` as above.

## Next steps

- [Verify the install](verify.md) — curl LiteLLM, Lightspeed smoke, catalog mount  
- [Demo script](demo-script.md) — Hub MCP loop + DevSpaces AI  
- [Troubleshooting](troubleshooting.md) — common failures  
