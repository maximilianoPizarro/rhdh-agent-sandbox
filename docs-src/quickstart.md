# Quickstart

Install on **OpenShift Developer Sandbox** with a single Helm release. Chart source lives at the **repository root**. GitHub Pages serves the **`/docs`** folder, which holds the Helm repo (`index.yaml`, `artifacthub-repo.yml`, packaged `.tgz`).

## Install from clone

```bash
git clone https://github.com/maximilianoPizarro/rhdh-agent-sandbox.git
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

!!! tip "Apps domain"
    Prefer the value already in `values.yaml` (`rhdh.global.clusterRouterBase`) when it matches your cluster.
    If you need to discover it and `oc get ingresses.config.openshift.io cluster` is Forbidden, take any Route host and drop the first DNS label (example: `my-app-ns.apps.rm2.thpm.p1.openshiftapps.com` → `apps.rm2.thpm.p1.openshiftapps.com`).

First install pulls large images (RHDH, LiteLLM). Expect several minutes.

## Confirm

```bash
oc get route | grep developer-hub
oc get pods
```

Sign in as **Guest**. Next: [Golden Paths](golden-paths.md) (deploy an agent) and [Verify](verify.md).

## Notes (not install steps)

| Topic | Detail |
|---|---|
| Prerequisites | `oc` logged in, `helm` 3.14+, Sandbox quota for Hub + LiteLLM + one DevSpaces workspace |
| Model token TTL | Sandbox oauth-proxy ~24h — refresh `model-api-key` on the chart secret and restart LiteLLM when chat 401s |
| RHDH dependency | Declared in `Chart.yaml`; bump version there when upgrading Developer Hub |
| Single values file | All Sandbox defaults live in root `values.yaml` |
