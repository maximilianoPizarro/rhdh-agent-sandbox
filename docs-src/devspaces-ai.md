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

## Option A — From Hub template

1. Guest → **Create** → template **Agent-friendly DevSpaces AI Workspace**.  
2. Scaffolder steps are guest-safe (log / local). Export or push the generated tree to a git repo DevSpaces can clone, **or** copy files into an existing repo.  
3. In DevSpaces UI: create workspace from that repo’s `devfile.yaml`.

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

Inside the workspace terminal, run Devfile command **`wire-continue`**. It prefers env vars if set; otherwise it loads that Secret via `oc` and writes `.continue/config.json` (models `granite` / `qwen3`).

Manual fallback:

```bash
export LITELLM_API_BASE="$(oc get secret rhdh-agent-sandbox-continue -o jsonpath='{.data.LITELLM_API_BASE}' | base64 -d)"
export LITELLM_API_KEY="$(oc get secret rhdh-agent-sandbox-continue -o jsonpath='{.data.LITELLM_API_KEY}' | base64 -d)"
```

Open the **Continue** sidebar in Che Code and send a short chat.

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
| `docs/prompts/*` | Prompts aligned with Hub catalog |

## MCP from the IDE?

Not required for the demo. MCP ClusterIP services are consumed from **Hub Lightspeed**. The IDE path is Continue → LiteLLM Route → Granite/Qwen.

## Stop when done

```bash
oc patch dw rhdh-agent-ai-demo --type=merge -p '{"spec":{"started":false}}'
```

Or use Stop in the DevSpaces UI. Freeing the workspace avoids quota pressure on Hub/LiteLLM.
