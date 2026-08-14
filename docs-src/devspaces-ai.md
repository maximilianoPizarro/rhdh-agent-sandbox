---
title: DevSpaces AI
---

# DevSpaces AI (browser IDE)

Run **OpenShift DevSpaces** with in-browser AI (**Che Code** + **Continue**) against this chart’s **LiteLLM Route** (Granite / Qwen).

> **Info: Identity**
>
> Hub **Guest** is only for Developer Hub. DevSpaces is started by your **OpenShift Sandbox user**. The chart prepares Devfiles and `.continue/` config; it does not open DevSpaces as Guest.

## Prerequisites

- Chart installed and [verified]({{ '/verify/' | relative_url }}) (LiteLLM Route returns models).  
- DevSpaces available on the cluster (true on Developer Sandbox).  
- Quota for ~200m CPU / 1Gi memory request (limits up to ~2 CPU / 3Gi). Stop other heavy workspaces first.

## Option A — From Hub template (recommended)

1. Guest → **Create** → **Agent-friendly DevSpaces AI Workspace**.  
2. Choose **workspace name**, **agent language** (Python / Node.js / Quarkus), and default Continue **model**.  
3. The scaffolder registers a catalog Component (`managed-devworkspace=true`).  
4. Within ~1 minute the **agent-applier** creates a **started** DevWorkspace with Continue → LiteLLM prewired (Secret `rhdh-agent-sandbox-continue`).  
5. Open [DevSpaces dashboard](https://workspaces.openshift.com/dashboard/#/workspaces) and open your workspace — **no git push**.

Fallback: Component link **Language factory URL** opens the same language skeleton Devfile via DevSpaces factory.

## Option B — From this repository

1. Use [`files/devfiles/devfile.yaml`](https://github.com/maximilianopizarro/rhdh-agent-sandbox/blob/main/files/devfiles/devfile.yaml) or a skeleton under `files/templates/skeletons/*/devfile.yaml`.  
2. Create a DevWorkspace that clones `https://github.com/maximilianopizarro/rhdh-agent-sandbox` (or your fork) and uses that Devfile.  
3. Start the workspace; wait until phase **Running**.

Example (adjust resources if needed):

```bash
oc apply -f - <<'EOF'
apiVersion: workspace.devfile.io/v1alpha2
kind: DevWorkspace
metadata:
  name: rhdh-agent-ai-demo
spec:
  routingClass: che
  started: true
  template:
    projects:
      - name: rhdh-agent-sandbox
        git:
          remotes:
            origin: https://github.com/maximilianopizarro/rhdh-agent-sandbox.git
          checkoutFrom:
            revision: main
    components:
      - name: tools
        container:
          image: quay.io/devfile/universal-developer-image:ubi9-latest
          memoryLimit: 3Gi
          memoryRequest: 1Gi
          cpuLimit: "2"
          cpuRequest: 200m
          mountSources: true
EOF

oc get dw rhdh-agent-ai-demo -w
```

## Wire Continue → LiteLLM

The Helm chart creates Secret **`rhdh-agent-sandbox-continue`** with:

| Key | Source |
|---|---|
| `LITELLM_API_BASE` | LiteLLM Route URL (`…/v1`) |
| `LITELLM_API_KEY` | `litellm-master-key` from `rhdh-agent-sandbox-secrets` |
| `HUB_MCP_URL` | Hub Route `/api/mcp-actions/v1` |
| `MCP_TOKEN` | `mcp-token` (when the chart Secret already exists) |

The left **CHAT / Agent** panel **is Continue 2**. Keep it. postStart runs Devfile **`wire-continue`**, which writes **`~/.continue/config.yaml`** (Continue 2.x live config: models + `red-hat-security` + `hub-mcp-actions`). Project `.continue/config.json` is placeholders only.

If the model picker says **No models configured**, reload the Che Code window (or re-run `wire-continue`). Continue 2 ignores project `config.json`.

Manual fallback:

```bash
export LITELLM_API_BASE="$(oc get secret rhdh-agent-sandbox-continue -o jsonpath='{.data.LITELLM_API_BASE}' | base64 -d)"
export LITELLM_API_KEY="$(oc get secret rhdh-agent-sandbox-continue -o jsonpath='{.data.LITELLM_API_KEY}' | base64 -d)"
```

Continue is **preinstalled** on workspace start (`DEFAULT_EXTENSIONS` + OpenVSX download; CLI fallback). Open the **Continue** sidebar in Che Code, select **Granite (LiteLLM)**, and send a short chat (for example `Reply with exactly: DevSpaces Continue OK`). Screenshots of the **query → reply** and Hub MCP **action → reaction** loop: [DevSpaces journey]({{ '/devspaces-journey/' | relative_url }}).

> **Tip**
>
> Use **`litellm-master-key`** (via the Continue Secret), not your OpenShift user token. The user token is only for LiteLLM → shared models (`model-api-key`). Hub tool demos use LiteMaaS via Lightspeed/MCP Chat — not Continue.

## What ships in skeletons

| Path | Purpose |
|---|---|
| `devfile.yaml` | UDI + modest resources + AI help commands |
| `.continue/config.json` | OpenAI-compatible models → LiteLLM |
| `.continue/skills/*` | DevSpaces AI, OpenShift MCP notes, Lightspeed RAG |
| `.vscode/extensions.json` | Recommends Continue |
| Devfile `DEFAULT_EXTENSIONS` + `download-continue-extension` | Preinstalls Continue from OpenVSX (linux-x64 `.vsix`) |
| `docs/prompts/*` | Prompts aligned with Hub catalog |

## AI and MCP from the IDE (two paths)

Continue is one sidebar (CHAT / Agent **is** Continue 2), three network paths:

| Path | Flow | Secret |
|---|---|---|
| **AI chat** | Continue → LiteLLM Route `/v1` → Granite/Qwen/LiteMaaS | `rhdh-agent-sandbox-continue` |
| **Hub MCP** | Continue → Hub Route `/api/mcp-actions/v1` → catalog/TechDocs | `mcp-token` |
| **Red Hat Security MCP** | Continue → `security-mcp.api.redhat.com` → CVEs/advisories | Customer Portal SSO (no Secret) |

OpenShift/Kubernetes MCP remain **ClusterIP** and are consumed from **Hub Lightspeed / MCP Chat**, not from the IDE. Screenshots and prompts: [DevSpaces journey]({{ '/devspaces-journey/' | relative_url }}).

> **Info: Continue v2**
>
> Continue 2.x stores live keys in `~/.continue/config.yaml` (local only). `wire-continue` also writes placeholder `.continue/config.json` in the repo tree — do not paste real keys into git.

## Stop when done

```bash
oc patch dw rhdh-agent-ai-demo --type=merge -p '{"spec":{"started":false}}'
```

Or use Stop in the DevSpaces UI. Freeing the workspace avoids quota pressure on Hub/LiteLLM.
