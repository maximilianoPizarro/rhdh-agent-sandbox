---
title: Agents
---

# Agents

Three related loops on Developer Sandbox. Prefer [Golden Paths]({{ '/golden-paths/' | relative_url }}) to create a new agent Pod + catalog Component from **real** LangGraph / LangChain.js / LangChain4j source.

## 1. Hub Guest (in-cluster)

| Surface | Path |
|---|---|
| Lightspeed | Guest UI → lightspeed-core → LiteLLM Service → Granite/Qwen |
| MCP Chat | Guest UI → LiteLLM + MCP servers (tools limited without model function-calling) |
| Catalog | Skills, prompts, MCP entities, **Deploy Agent** template, sample agent Components |

Guest has **no** OpenShift token. Agent Deployments and builds are created by chart RBAC (samples + agent-applier), not by the Guest’s kubeconfig.

## 2. Agent Pod (Golden Path / samples)

### Golden Path (build=true)

- Scaffolder generates framework source; agent-applier starts a **Binary BuildConfig**.
- Image: `image-registry.openshift-image-registry.svc:5000/<ns>/<name>:latest`
- Env: `AGENT_SPEC`, `AGENT_TYPE`, `MODEL`, LiteLLM credentials
- Endpoints: `/health`, `/`, `/v1/chat` (plus `/v1/graph` or `/v1/runtime` per language)
- Service: **ClusterIP only**

```bash
oc get bc,is,deploy,svc -l app.kubernetes.io/component=agent
oc logs -f bc/<name>
oc logs deploy/<name>
```

### Legacy samples

Pre-installed `sample-*-agent` Deployments were removed. Create agents only via the Deploy Agent golden path (`build=true`).

## 3. DevSpaces (OpenShift user)

Factory links open language skeletons:

`https://workspaces.openshift.com/#https://github.com/maximilianoPizarro/rhdh-agent-sandbox/tree/main/files/templates/skeletons/deploy-agent/<language>`

Wire Continue to the LiteLLM **Route** with `litellm-master-key` (see [DevSpaces AI]({{ '/devspaces-ai/' | relative_url }})).

Official [Red Hat agentic skills](https://www.redhat.com/en/agentic-skills) (CVE, lifecycle, diagnostics, support severity) are available in the catalog and can be installed into IDE skill directories.

## Identity cheat sheet

| Actor | Token / power |
|---|---|
| Hub Guest | Catalog + Lightspeed + scaffolder register (no cluster admin) |
| Agent Pod SA / applier | Namespace create/update Deployment, Service, BuildConfig, ImageStream; start builds |
| OpenShift Sandbox user | `model-api-key` refresh, DevSpaces start, read secrets |
