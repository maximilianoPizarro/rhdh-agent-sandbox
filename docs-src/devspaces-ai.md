# DevSpaces AI (browser IDE)

Run **OpenShift DevSpaces** with in-browser AI (**Che Code** + **Continue**) against this chart’s **LiteLLM Route** (Granite / Qwen).

!!! info "Identity"
    Hub **Guest** is only for Developer Hub. DevSpaces is started by your **OpenShift Sandbox user**. The chart prepares Devfiles and `.continue/` config; it does not open DevSpaces as Guest.

## Prerequisites

- Chart installed and [verified](verify.md) (LiteLLM Route returns models).  
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

Inside the workspace terminal (or before start via env):

```bash
export LITELLM_API_BASE="https://$(oc get route -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')/v1"
export LITELLM_API_KEY="$(oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.litellm-master-key}' | base64 -d)"
```

Then either:

- Run the Devfile command **`wire-continue`**, or  
- Edit `.continue/config.json` with `apiBase` = `$LITELLM_API_BASE`, `apiKey` = `$LITELLM_API_KEY`, models `granite` / `qwen3`.

Open the **Continue** sidebar in Che Code and send a short chat.

!!! tip
    Use **`litellm-master-key`**, not your OpenShift user token. The user token is only for LiteLLM → shared models (`model-api-key`).

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
