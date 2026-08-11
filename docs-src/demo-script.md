---
title: Demo script
---

# Demo script (~10 minutes)

Audience: show an **agent loop** on Developer Sandbox — [Helm install]({{ '/install-journey/' | relative_url }}), Guest Hub + Golden Paths, then DevSpaces AI.

## Prep (OpenShift user / `oc`)

```bash
oc project   # *-dev namespace

# Refresh shared-model token (~24h TTL)
oc patch secret/rhdh-agent-sandbox-secrets --type=merge \
  -p "{\"stringData\":{\"model-api-key\":\"$(oc whoami -t)\"}}"
oc rollout restart deploy/rhdh-agent-sandbox-litellm

oc get pods,route | grep rhdh-agent
curl -skI "https://$(oc get route -l app.kubernetes.io/name=developer-hub -o jsonpath='{.items[0].spec.host}' 2>/dev/null || oc get route | awk '/developer-hub/{print $2; exit}')/" | head -1
```

Optional deep check: [Verify the install]({{ '/verify/' | relative_url }}).

> **Tip: Quota**
>
> Keep at most **one** modest DevSpaces workspace while Hub + LiteLLM + MCP are running.

## Part A — Hub agent loop (Guest) — ~5 min

1. Open the Developer Hub Route → **Enter as Guest**.  
2. **Catalog** → filter tag `mcp` → open OpenShift / Kubernetes MCP entities. Mention namespace-scoped RBAC.  
3. **Create** → run each Golden Path once (Deploy Agent, DevSpaces workspace, AI Service MCP) — see [Golden Path journey]({{ '/journey/' | relative_url }}).  
4. Filter `skill` / `prompt` → open Red Hat agentic skills and a triage prompt.  
5. Open **Lightspeed** or **MCP Chat** → select **litemaas-qwen** for tool demos ([tool calling journey]({{ '/tool-calling-journey/' | relative_url }})).  
6. Ask:

   > Use pods_list_in_namespace for this namespace and summarize pod status. Prefer read-only tools.

   - Guest has **no** OpenShift token; models are wired by the operator.  
   - Inference path: Lightspeed → LiteLLM Service → shared Granite.  
   - MCP tools are ClusterIP-only from Hub.  
   - Golden Path agents are ClusterIP Pods applied from catalog annotations (no git push).  
   - `permission.enabled: false` is deliberate for this demo.

## Part B — DevSpaces AI (OpenShift user) — ~5 min

1. Hub → **Create** → **Agent-friendly DevSpaces AI Workspace** (pick language + model).  
2. Wait ~1 minute for agent-applier to create a **started** DevWorkspace.  
3. Open **DevSpaces dashboard** → Open your workspace (no git push).  
4. In Che Code, open **Continue** — LiteLLM is wired on postStart via chart Secret.  
5. Chat: *“Explain the language skeleton and how granite is reached via LiteLLM.”*  
6. Show `.continue/skills/` and `docs/prompts/` — same names as Hub catalog.

Full IDE steps: [DevSpaces AI]({{ '/devspaces-ai/' | relative_url }}).

## Tokens (who needs what)

| Actor | Token |
|---|---|
| Hub Guest | None |
| Lightspeed → shared models | Operator refreshes `model-api-key` (`oc whoami -t`) |
| Continue in DevSpaces | `litellm-master-key` from `rhdh-agent-sandbox-secrets` |

## Wrap-up

1. Stop the DevSpaces workspace (`spec.started: false` or UI Stop) to free quota.  
2. Leave Hub + LiteLLM running if you will demo again the same day.  
3. Tomorrow: refresh `model-api-key` before the first Lightspeed question.
