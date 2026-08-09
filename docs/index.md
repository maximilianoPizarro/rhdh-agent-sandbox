# Agent-friendly Developer Hub on Developer Sandbox

Umbrella Helm chart that deploys **Red Hat Developer Hub 1.10** on **OpenShift Developer Sandbox** with a working agent loop: Lightspeed → LiteLLM → shared Granite/Qwen, plus MCP tools and DevSpaces AI workspaces.

## What you get

| Piece | Role |
|---|---|
| **Developer Hub** | Guest login, catalog, scaffolder, TechDocs, Lightspeed UI |
| **LiteLLM** | OpenAI-compatible gateway to `sandbox-shared-models` (Granite / Qwen) |
| **MCP servers** | OpenShift + Kubernetes tools (namespace-scoped) for Lightspeed |
| **AI catalog** | Skills, prompts, MCP entities, software templates (ConfigMap mount) |
| **DevSpaces AI** | Browser IDE (Che Code + Continue) talking to the LiteLLM Route |

## Two identities (important)

| Who | What they do |
|---|---|
| **Hub Guest** | Signs into Developer Hub only. Uses Lightspeed + catalog. No OpenShift token. |
| **OpenShift Sandbox user** (`oc` / console) | Refreshes `model-api-key`, starts DevSpaces workspaces, reads `litellm-master-key`. |

Guest Hub ≠ DevSpaces login. The chart prepares Devfiles and IDE config; the Sandbox user opens the workspace.

## Recommended path

1. [Quickstart](quickstart.md) — install the chart  
2. [Verify the install](verify.md) — confirm Hub, LiteLLM, Lightspeed  
3. [Demo script](demo-script.md) — ~10 minute walkthrough  
4. [DevSpaces AI](devspaces-ai.md) — browser IDE with Continue  

Deeper reading: [Architecture](architecture.md), [Lightspeed & models](lightspeed-models.md), [Troubleshooting](troubleshooting.md).

## Single values file

This chart is **Developer Sandbox only**. Configuration lives in one `values.yaml` (no separate sandbox overlay). Override at install time with `--set` for your apps domain and model token.

```bash
helm upgrade --install rhdh-agent . \
  -n "$(oc project -q)" \
  --set secrets.modelApiKey="$(oc whoami -t)" \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com
```

## Source

[github.com/maximilianoPizarro/rhdh-agent-sandbox](https://github.com/maximilianoPizarro/rhdh-agent-sandbox)
