# rhdh-agent-sandbox

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maximilianopizarro.github.io/rhdh-agent-sandbox/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Agent-friendly **Red Hat Developer Hub** on **OpenShift Developer Sandbox**.

- Chart source: **repository root** (`Chart.yaml`, `values.yaml`, `templates/`, `files/`)
- Markdown source: **`docs-src/`** (MkDocs builds into `docs/`)
- GitHub Pages: **`/docs`** on `main` (Settings → Deploy from branch)
- In `docs/`: built HTML site + Helm repo (`index.yaml`, `artifacthub-repo.yml`, `.tgz`)
- Developer Hub: Helm **dependency** `redhat-developer-hub` from `https://charts.openshift.io/` (`helm dependency update`; not vendored under `/charts` in git)

## Install

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

From the Pages Helm repo (no clone of chart source):

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

## Docs

**https://maximilianopizarro.github.io/rhdh-agent-sandbox/**

| Page | Content |
|---|---|
| [Quickstart](docs-src/quickstart.md) | Clone or install from Pages Helm repo |
| [Golden Paths](docs-src/golden-paths.md) | Deploy agents without git push |
| [Agents](docs-src/agents.md) | Hub / Pod / DevSpaces agent loops |
| [Architecture](docs-src/architecture.md) | Components and tokens |
| [Verify](docs-src/verify.md) | Post-install checks |

## Layout

```text
Chart.yaml            # umbrella + dependency: redhat-developer-hub
values.yaml
templates/
files/                # catalog, scaffolder skeletons, agent-runtimes
docs-src/             # Markdown source (MkDocs input)
docs/                 # Built site (MkDocs output) + Helm repo — served by Pages
  index.yaml          # Helm repository index
  artifacthub-repo.yml
  rhdh-agent-sandbox-*.tgz
community-plugins/
.github/workflows/    # lint + refresh docs/*.tgz / index.yaml on main
```

## License

Apache-2.0
