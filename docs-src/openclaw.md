---
title: OpenClaw (optional)
---

# OpenClaw (optional)

OpenClaw is a **personal AI assistant** you provision from [sandbox.redhat.com](https://sandbox.redhat.com) — not from this Helm chart. It runs in your Developer Sandbox namespace with a managed lifecycle.

This page explains how OpenClaw relates to the RHDH agent stack and how to wire it safely.

> **New: OpenClaw + Qwen Tool Calling journey**
>
> See the [OpenClaw journey]({{ '/openclaw-journey/' | relative_url }}) for a step-by-step visual guide to provisioning OpenClaw with a private Qwen3.6-35B-A3B model (with tool calling) via LiteMaaS.

## Role in the architecture

OpenClaw is a **third AI client**, alongside Hub Lightspeed and DevSpaces Continue. It does **not** replace the chart's MCP servers.

| Client | How you get it | Typical model path |
|---|---|---|
| Lightspeed | Chart (Hub sidecar) | LiteLLM → shared Granite/Qwen |
| Continue (DevSpaces AI) | Chart Devfiles + Sandbox DevSpaces | LiteLLM Route + `litellm-master-key` |
| **OpenClaw** | Provision on sandbox.redhat.com | **LiteMaaS Qwen** (tool calling) or external vendor key |

![OpenClaw in the agent stack]({{ '/assets/diagrams/openclaw-architecture.png' | relative_url }})

## Prerequisites

| Requirement | Notes |
|---|---|
| OpenClaw provisioned | Card on sandbox.redhat.com → **Provision** |
| LiteMaaS API key | Bearer token for `litemaas.rhoai.rh-aiservices-bu.com` (recommended for tool calling) |
| This chart installed | Optional for OpenClaw itself; needed only if you also want LiteLLM chat fallback |
| Quota headroom | OpenClaw adds its own Deployment + PVC; stop unused DevSpaces workspaces first |

## Recommended path: LiteMaaS Qwen with tool calling

The **LiteMaaS** gateway (`litemaas.rhoai.rh-aiservices-bu.com`) serves **Qwen3.6-35B-A3B** — a model that **supports function/tool calling** (`tool_choice=auto`). This is the recommended path for OpenClaw on Developer Sandbox because:

- Full agentic capabilities (exec, read, write, kubectl)
- OpenAI Completions API compatible
- No need for external vendor keys (Anthropic, OpenAI, etc.)

### Provision via sandbox.redhat.com

1. Go to [sandbox.redhat.com](https://sandbox.redhat.com) and click **Provision** on the OpenClaw card
2. Select **Custom / Self-Hosted** as the AI provider
3. Fill the form:

| Field | Value |
|---|---|
| **Endpoint URL** | `https://litemaas.rhoai.rh-aiservices-bu.com/v1` |
| **API Format** | OpenAI Completions |
| **API Key** | Your LiteMaaS bearer token (`sk-...`) |
| **Model Name** | `Qwen3.6-35B-A3B` |
| **Display Name** | `Qwen 3.6 35B-A3B (Tool Calling)` |

4. Click **Provision** — OpenClaw deploys as a pod in your namespace

> **Warning: Never commit API keys**
>
> The LiteMaaS API key is stored securely as a Kubernetes Secret by the provisioner. Never add it to git, values.yaml, or ConfigMaps.

### Verify with curl

```bash
curl -X POST https://litemaas.rhoai.rh-aiservices-bu.com/v1/chat/completions \
  -H "Authorization: Bearer $LITEMAAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B",
    "messages": [
      {"role": "user", "content": "Hello, world!"}
    ]
  }'
```

See the [OpenClaw journey carousel]({{ '/openclaw-journey/' | relative_url }}) for the full visual walkthrough.

## Alternative: external vendor API key

If you prefer a commercial provider, shared Sandbox models (Granite / Qwen) **do not** support function calling (`tool_choice=auto`). OpenClaw's agent loop needs tool calls, so **bring your own provider key**.

Configure OpenClaw (Control UI or `~/.openclaw/openclaw.json`) with your provider:

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-5" },
      sandbox: { mode: "off" },
    },
  },
  env: {
    ANTHROPIC_API_KEY: "sk-ant-...",
  },
}
```

Use OpenClaw's onboard / Control UI **Config** tab if you prefer a form over raw JSON5. Follow [OpenClaw configuration](https://docs.openclaw.ai/) for the exact provider fields for your vendor.

> **Tip: Sandbox tool sandboxing**
>
> OpenClaw can sandbox tools with Docker (`agents.defaults.sandbox.mode: non-main|all`). Developer Sandbox does **not** expose a Docker socket or privileged DinD. Keep `sandbox.mode: "off"` so tools run inside the OpenClaw pod under the provisioned ServiceAccount.

## Optional: LiteLLM as chat-only custom provider

You can point OpenClaw at this chart's LiteLLM Route for **chat without tools** (same Granite/Qwen aliases as Continue).

1. Get the Route and master key:

```bash
export NAMESPACE=$(oc project -q)
oc get route -n "${NAMESPACE}" | grep litellm
export LITELLM_KEY=$(oc get secret rhdh-agent-sandbox-secrets -n "${NAMESPACE}" \
  -o jsonpath='{.data.litellm-master-key}' | base64 -d)
```

2. Example custom provider (adjust host to your Route):

```json5
{
  models: {
    mode: "merge",
    providers: {
      "sandbox-litellm": {
        baseUrl: "https://rhdh-agent-sandbox-litellm-<namespace>.apps.<cluster>/v1",
        apiKey: "${LITELLM_MASTER_KEY}",
        api: "openai-completions",
        models: [
          { id: "granite", name: "Granite (Sandbox)", reasoning: false, input: ["text"] },
          { id: "qwen3", name: "Qwen3 (Sandbox)", reasoning: false, input: ["text"] },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "sandbox-litellm/granite" },
      sandbox: { mode: "off" },
    },
  },
}
```

> **Warning: Chat-only with shared models**
>
> With Granite/Qwen via LiteLLM, OpenClaw will **not** get reliable tool calls. Use this path only for plain Q&A. For agentic work (code, shell, multi-step tools), use LiteMaaS Qwen or an external API key.

## What this chart does *not* do

- Does **not** deploy OpenClaw (no `openclaw:` block in `values.yaml`).
- Does **not** create OpenClaw Secrets or Routes.
- Does **not** expose public MCP Routes — Lightspeed still uses ClusterIP MCP only. OpenClaw on Sandbox should not require opening MCP to the internet.

## Identity reminder

| Identity | OpenClaw |
|---|---|
| Hub Guest | No access to OpenClaw provisioning or cluster secrets |
| OpenShift Sandbox user | Provisions OpenClaw, supplies LLM keys, may read `litellm-master-key` for chat-only wiring |

## See also

- [OpenClaw journey]({{ '/openclaw-journey/' | relative_url }}) — visual carousel walkthrough
- [Architecture]({{ '/architecture/' | relative_url }}) — full stack diagram  
- [Lightspeed & models]({{ '/lightspeed-models/' | relative_url }}) — why shared models drop `tool_choice`  
- [Troubleshooting]({{ '/troubleshooting/' | relative_url }}) — OpenClaw + shared models  
- [OpenClaw docs](https://docs.openclaw.ai/) — upstream gateway / config reference  
