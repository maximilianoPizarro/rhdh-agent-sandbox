# Quickstart

Install on **OpenShift Developer Sandbox** with a single Helm release. Chart source lives at the **repository root**. GitHub Pages serves the **`/docs`** folder, which holds the Helm repo (`index.yaml`, `artifacthub-repo.yml`, packaged `.tgz`).

!!! warning "Replace `<your-sandbox>` before running"
    Both install methods use the placeholder `apps.<your-sandbox>.openshiftapps.com`. Replace it with your cluster's apps domain **before** you copy-paste.
    If `oc get ingresses.config.openshift.io cluster` is Forbidden, take any Route host and drop the first DNS label (example: `my-app-ns.apps.rm2.thpm.p1.openshiftapps.com` → `apps.rm2.thpm.p1.openshiftapps.com`).

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

!!! warning "Model token TTL ~24 h"
    `secrets.modelApiKey` uses your Sandbox oauth-proxy token, which expires in **~24 hours**. When Lightspeed or LiteLLM returns **401**, refresh the secret and restart LiteLLM:

    ```bash
    oc set data secret/rhdh-agent-sandbox-secrets \
      --from-literal=model-api-key="$(oc whoami -t)"
    oc rollout restart deploy/rhdh-agent-litellm
    ```

!!! info "Expected resources and time"
    First install pulls large images (RHDH ~1.5 GB, LiteLLM ~500 MB). **Expect 5–10 minutes** on Developer Sandbox.
    Approximate quota: Hub pod (**1 CPU / 2.5 Gi**), LiteLLM pod (**0.5 CPU / 512 Mi**), plus one DevSpaces workspace if you follow the full demo.

## Confirm

```bash
oc get route | grep developer-hub
oc get pods
```

Sign in as **Guest**. Next: [Golden Paths](golden-paths.md) (deploy an agent) and [Verify](verify.md).

## Notes (not install steps)

| Topic | Detail |
|---|---|
| Prerequisites | `oc` logged in, `helm` 3.14+, Sandbox quota available |
| RHDH dependency | Declared in `Chart.yaml`; bump version there when upgrading Developer Hub |
| Single values file | All Sandbox defaults live in root `values.yaml` |
