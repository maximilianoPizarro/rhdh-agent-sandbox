---
title: Quickstart
---

# Quickstart

Install on **OpenShift Developer Sandbox** with a single Helm release. Chart source lives at the **repository root**. GitHub Pages serves the **`/docs`** folder, which holds the Helm repo (`index.yaml`, `artifacthub-repo.yml`, packaged `.tgz`).

## Prerequisites

| Requirement | Detail |
|---|---|
| `oc` CLI | Logged in to Developer Sandbox (`oc login`) |
| `helm` | 3.14 or newer |
| Sandbox quota | At least **1.5 CPU / 3 Gi** free (Hub + LiteLLM + MCP) |

> **Warning: Replace `<your-sandbox>` before running**
>
> Both install methods use the placeholder `apps.<your-sandbox>.openshiftapps.com`. Replace it with your cluster's apps domain **before** you copy-paste.
> If `oc get ingresses.config.openshift.io cluster` is Forbidden, take any Route host and drop the first DNS label (example: `my-app-ns.apps.rm2.thpm.p1.openshiftapps.com` → `apps.rm2.thpm.p1.openshiftapps.com`).

## Install from clone

```bash
git clone https://github.com/maximilianopizarro/rhdh-agent-sandbox.git
cd rhdh-agent-sandbox

helm dependency update
helm upgrade --install rhdh-agent . \
  --namespace "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m \
  --wait=false
```

`helm dependency update` downloads **Red Hat Developer Hub** (`redhat-developer-hub` 1.10.3 from `charts.openshift.io`) into local `charts/` only. That subchart is **not** committed to git.

## Install from Pages Helm repo

```bash
helm repo add rhdh-agent-sandbox https://maximilianopizarro.github.io/rhdh-agent-sandbox
helm repo update
helm upgrade --install rhdh-agent rhdh-agent-sandbox/rhdh-agent-sandbox \
  --namespace "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --timeout 20m \
  --wait=false
```

## What to expect

First install pulls large images (RHDH ~1.5 GB, LiteLLM ~500 MB). **Expect 5–10 minutes** on Developer Sandbox before everything is Ready.

| Phase | Typical time | What you'll see |
|---|---|---|
| Helm release created | Instant | `release "rhdh-agent" … installed` |
| Image pulls | 3–7 min | Pods in `ContainerCreating` / `Init:0/1` — **this is normal** |
| LiteLLM ready | ~1 min after pull | `rhdh-agent-litellm-*` shows `1/1 Running` |
| Hub ready (2 containers) | 2–4 min after pull | `rhdh-agent-developer-hub-*` shows `2/2 Running` |
| MCP servers ready | ~30 s after pull | `rhdh-agent-*-mcp-*` pods show `1/1 Running` |

> **Tip: Normal vs. not normal**
>
> **Normal:** pods in `ContainerCreating` for several minutes, `0/1` or `1/2` while init containers run, occasional `CrashLoopBackOff` on Hub if PostgreSQL isn't ready yet (self-heals).
> **Not normal:** pods stuck in `Pending` for >5 min (quota issue — run `oc describe resourcequota`), or `ImagePullBackOff` (network/registry issue).

## Confirm

```bash
oc get pods
oc get route | grep -E 'developer-hub|litellm'
```

Expected output (names will vary):

```
NAME                                          READY   STATUS    RESTARTS   AGE
rhdh-agent-developer-hub-<hash>               2/2     Running   0          6m
rhdh-agent-litellm-<hash>                     1/1     Running   0          5m
rhdh-agent-sandbox-kubernetes-mcp-<hash>      1/1     Running   0          5m
rhdh-agent-sandbox-openshift-mcp-<hash>       1/1     Running   0          5m
...
```

Sign in as **Guest**. Next: [Golden Paths]({{ '/golden-paths/' | relative_url }}) (deploy an agent) and [Verify]({{ '/verify/' | relative_url }}).

## Token refresh (when chat returns 401)

`secrets.modelApiKey` uses your Sandbox oauth-proxy token, which expires in **~24 hours**. When Lightspeed or LiteLLM returns **401**, refresh the secret and restart LiteLLM:

```bash
oc set data secret/rhdh-agent-sandbox-secrets \
  --from-literal=model-api-key="$(oc whoami -t)"
oc rollout restart deploy/rhdh-agent-litellm
```

If the problem persists, see [Troubleshooting — LiteLLM 401]({{ '/troubleshooting/' | relative_url }}#litellm-401-to-shared-models).

## Notes

| Topic | Detail |
|---|---|
| RHDH dependency | Declared in `Chart.yaml`; bump version there when upgrading Developer Hub |
| Single values file | All Sandbox defaults live in root `values.yaml` |
