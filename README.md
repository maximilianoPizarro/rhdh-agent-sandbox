# rhdh-agent-sandbox

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/rhdh-agent-sandbox)](https://artifacthub.io/packages/search?repo=rhdh-agent-sandbox)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maximilianoPizarro.github.io/rhdh-agent-sandbox/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Agent-friendly **Red Hat Developer Hub** umbrella Helm chart for **OpenShift Developer Sandbox**.

It wires:

- Developer Hub 1.10 (Lightspeed, TechDocs, Kubernetes/Topology, GitHub modules)
- **LiteLLM** → Granite / Qwen in `sandbox-shared-models`
- **MCP** servers (OpenShift + Kubernetes) with namespace RBAC
- AI **Skills / Prompts / MCP catalog** entities
- **DevSpaces** Devfiles + Software Templates for **Cursor** remote workflows
- Community AI asset packs published to **GHCR** (`ghcr.io/maximilianoPizarro/rhdh-agent-sandbox/*`)

## Quick install

```bash
helm dependency update
export MODEL_API_KEY=$(oc whoami -t)
helm upgrade --install rhdh-agent . \
  -n "$(oc project -q)" \
  -f values-sandbox.yaml \
  --set secrets.modelApiKey="$MODEL_API_KEY" \
  --set rhdh.global.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com
```

Full guide: [docs/quickstart.md](docs/quickstart.md)

## Repository layout

```text
Chart.yaml / values*.yaml / templates/   # umbrella chart
files/catalog|templates|devfiles         # Hub catalog + scaffolder assets
community-plugins/                       # GHCR asset packs + build script
docs/                                    # GitHub Pages (MkDocs)
.github/workflows/                       # CI for charts, pages, GHCR
```

## Documentation

https://maximilianoPizarro.github.io/rhdh-agent-sandbox/

## License

Apache-2.0
