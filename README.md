# rhdh-agent-sandbox

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maximilianopizarro.github.io/rhdh-agent-sandbox/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Agent-friendly **Red Hat Developer Hub** umbrella Helm chart for **OpenShift Developer Sandbox**.

It wires:

- Developer Hub 1.10.3 (Lightspeed, TechDocs, Kubernetes/Topology)
- **LiteLLM** → Granite / Qwen in `sandbox-shared-models`
- **MCP** servers (OpenShift + Kubernetes) with namespace RBAC
- AI **Skills / Prompts / MCP catalog** (ConfigMap mount)
- **DevSpaces AI** Devfiles + Software Templates (Continue → LiteLLM in the browser IDE)
- Guest login for Hub demos (`permission.enabled: false`)

## Quick install

```bash
helm dependency update
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

Single `values.yaml` — this chart is Sandbox-only (no overlay file).

## Documentation

**https://maximilianopizarro.github.io/rhdh-agent-sandbox/**

| Page | Content |
|---|---|
| [Quickstart](docs/quickstart.md) | Install step by step |
| [Verify](docs/verify.md) | Post-install checks (LiteLLM, Lightspeed, catalog) |
| [Demo script](docs/demo-script.md) | ~10 minute Hub + DevSpaces walkthrough |
| [Architecture](docs/architecture.md) | Components, tokens, MCP |
| [OpenClaw](docs/openclaw.md) | Optional Sandbox-provisioned assistant wiring |
| [Troubleshooting](docs/troubleshooting.md) | Common failures |

## Repository layout

```text
Chart.yaml / values.yaml / templates/   # umbrella chart (Sandbox-only)
files/catalog|templates|devfiles        # Hub catalog + scaffolder assets
community-plugins/                      # optional Quay asset packs (Podman CI)
docs/                                   # GitHub Pages (MkDocs)
.github/workflows/                      # CI for charts, pages, Quay
```

## License

Apache-2.0
