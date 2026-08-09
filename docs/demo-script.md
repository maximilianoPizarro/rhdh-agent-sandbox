# Demo script (~10 minutes)

Audience: show an **agent loop** on Developer Sandbox — Guest Hub + Lightspeed, then DevSpaces AI.

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

Optional deep check: [Verify the install](verify.md).

!!! tip "Quota"
    Keep at most **one** modest DevSpaces workspace while Hub + LiteLLM + MCP are running.

## Part A — Hub agent loop (Guest) — ~5 min

1. Open the Developer Hub Route → **Enter as Guest**.  
2. **Catalog** → filter tag `mcp` → open OpenShift / Kubernetes MCP entities. Mention namespace-scoped RBAC.  
3. Filter `skill` / `prompt` → open the DevSpaces AI skill and a triage / catalog prompt.  
4. Open **Lightspeed** → select **vllm/granite** (or granite).  
5. Ask:

   > List pods in this namespace and summarize anything that looks unhealthy. Prefer read-only tools.

6. Talking points while it runs:

   - Guest has **no** OpenShift token; models are wired by the operator.  
   - Inference path: Lightspeed → LiteLLM Service → shared Granite.  
   - MCP tools are ClusterIP-only from Hub.  
   - `permission.enabled: false` is deliberate for this demo.

## Part B — DevSpaces AI (OpenShift user) — ~5 min

1. In Hub, open Create / Templates → **Agent-friendly DevSpaces AI Workspace** (or clone this repo / use `files/devfiles/devfile.yaml`).  
2. Guest scaffolder ends in local/log steps — push or import the generated files yourself if needed.  
3. In **OpenShift DevSpaces**, start a workspace from `devfile.yaml`.  
4. In Che Code, open **Continue** and point it at the LiteLLM Route:

   ```bash
   export LITELLM_API_BASE="https://$(oc get route -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')/v1"
   export LITELLM_API_KEY="$(oc get secret rhdh-agent-sandbox-secrets -o jsonpath='{.data.litellm-master-key}' | base64 -d)"
   # Devfile command wire-continue, or edit .continue/config.json
   ```

5. Chat: *“Explain the Devfile and how granite is reached via LiteLLM.”*  
6. Show `.continue/skills/` and `docs/prompts/` — same names as Hub catalog.

Full IDE steps: [DevSpaces AI](devspaces-ai.md).

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
