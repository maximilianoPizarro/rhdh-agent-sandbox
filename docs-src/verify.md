---
title: Verify the install
---

# Verify the install

Run these checks after [Quickstart]({{ '/quickstart/' | relative_url }}). Adjust the namespace if needed.

```bash
export NAMESPACE=$(oc project -q)
```

## 1. Workloads Ready

```bash
oc get pods,deploy,route,svc -n "${NAMESPACE}" | grep -E 'rhdh-agent|NAME'
```

Expect:

- Hub Deployment available, pod **2/2**
- LiteLLM **1/1**
- Both MCP Deployments **1/1**
- `rhdh-agent-sandbox-agent-applier` **1/1**
- Routes for `developer-hub` and `litellm`
- Topology group **rhdh-agent** (see [Install journey]({{ '/install-journey/' | relative_url }}))

## 2. Secret shape (Lightspeed credentials)

```bash
oc get secret rhdh-agent-sandbox-secrets -n "${NAMESPACE}" -o json \
  | python -c "import json,sys,base64; d=json.load(sys.stdin)['data']; print(sorted(d.keys()))"
```

Required keys:

| Key | Purpose |
|---|---|
| `ENABLE_VLLM` | Must be `true` (enables Lightspeed vLLM provider) |
| `VLLM_URL` | `http://rhdh-agent-sandbox-litellm:4000/v1` |
| `VLLM_API_KEY` | Same value as `litellm-master-key` |
| `litellm-master-key` | Hub Lightspeed + DevSpaces Continue |
| `model-api-key` | OpenShift token for shared-model oauth-proxy |
| `mcp-token` | Static token for RHDH MCP actions |
| `backend-secret` | Hub backend auth |

> **Danger: Do not set ENABLE_OPENAI**
>
> That provider talks to api.openai.com. This chart only enables `ENABLE_VLLM` pointed at LiteLLM.

Confirm Lightspeed sidecar env:

```bash
HUB=$(oc get pods -n "${NAMESPACE}" -l app.kubernetes.io/name=developer-hub -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
# fallback name match
HUB=${HUB:-$(oc get pods -n "${NAMESPACE}" -o name | grep developer-hub | head -1 | sed 's|pod/||')}
oc exec -n "${NAMESPACE}" "${HUB}" -c lightspeed-core -- env | grep -E 'ENABLE_|VLLM_' | sort
```

## 3. LiteLLM Route (models + chat)

```bash
ROUTE=$(oc get route -n "${NAMESPACE}" -l app.kubernetes.io/component=litellm -o jsonpath='{.items[0].spec.host}')
KEY=$(oc get secret rhdh-agent-sandbox-secrets -n "${NAMESPACE}" -o jsonpath='{.data.litellm-master-key}' | base64 -d)

curl -sk "https://${ROUTE}/v1/models" -H "Authorization: Bearer ${KEY}"
```

Expect JSON with `"id":"granite"` and `"id":"qwen3"`.

Chat smoke:

```bash
curl -sk "https://${ROUTE}/v1/chat/completions" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"granite","messages":[{"role":"user","content":"Say hi in one word"}],"max_tokens":8}'
```

If you get **401** from upstream models, refresh `model-api-key` (see [Quickstart]({{ '/quickstart/' | relative_url }}) notes).

## 4. Hub HTTP + catalog mount

```bash
HUB_HOST=$(oc get route -n "${NAMESPACE}" -l app.kubernetes.io/name=developer-hub -o jsonpath='{.items[0].spec.host}' 2>/dev/null)
HUB_HOST=${HUB_HOST:-$(oc get route -n "${NAMESPACE}" | awk '/developer-hub/{print $2; exit}')}
curl -skI "https://${HUB_HOST}/" | head -5
```

Expect `HTTP/1.1 200`.

Catalog ConfigMap mount:

```bash
oc exec -n "${NAMESPACE}" "${HUB}" -c backstage-backend -- ls /opt/app-root/src/catalog
```

Expect at least: `all.yaml`, `skills.yaml`, `prompts.yaml`, `mcp-servers.yaml`, `template-deploy-agent.yaml`, `users.yaml`.

Scaffolder assets mount:

```bash
oc exec -n "${NAMESPACE}" "${HUB}" -c backstage-backend -- ls -R /opt/app-root/src/scaffolder-assets
```

## 5. Golden Path workloads (after Create templates)

```bash
# Deploy Agent (build=true)
oc get bc,deploy -l app.kubernetes.io/part-of=rhdh-agent-sandbox | grep -v agent-applier

# DevSpaces workspace
oc get dw

# AI Service MCP smoke
oc run curl-smoke --rm -i --restart=Never --image=registry.access.redhat.com/ubi9/ubi-minimal:latest -- \
  curl -s http://<ai-service-name>:8080/mcp/smoke
```

Expect agent-applier Running. Golden Path agents use BuildConfigs (`oc logs -f bc/<name>`) then Deployments from ImageStreams. AI Service `/mcp/smoke` should show `k8s_mcp.ok` and `openshift_mcp.ok`.

## 6. Lightspeed streaming query

From the Hub pod (sidecar):

```bash
oc exec -n "${NAMESPACE}" "${HUB}" -c lightspeed-core -- python -c '
import json, urllib.request
body=json.dumps({"query":"Say OK in one word.","model":"granite","provider":"vllm"}).encode()
req=urllib.request.Request(
  "http://127.0.0.1:8080/v1/streaming_query?user_id=user%3Adefault%2Fguest",
  data=body, headers={"Content-Type":"application/json"}, method="POST")
data=urllib.request.urlopen(req, timeout=90).read().decode()
assert "\"event\": \"error\"" not in data, data[:500]
print("Lightspeed OK")
print(data[:400])
'
```

In the UI: Guest → Lightspeed → select **vllm/granite** (or granite) → ask a short question. You should see streamed tokens, not an empty reply.

## 7. MCP services (cluster DNS)

```bash
oc get svc -n "${NAMESPACE}" | grep -E 'mcp|litellm'
```

Lightspeed reaches MCP over ClusterIP (no public MCP Routes). Namespace-scoped RBAC only.

## Checklist

- [ ] Hub pod 2/2, Route 200  
- [ ] LiteLLM `/v1/models` lists granite + qwen3  
- [ ] LiteLLM chat completion returns text  
- [ ] Secret has `ENABLE_VLLM=true` and **no** `ENABLE_OPENAI`  
- [ ] Catalog files visible under `/opt/app-root/src/catalog`  
- [ ] Scaffolder assets under `/opt/app-root/src/scaffolder-assets`  
- [ ] agent-applier Deployment Ready  
- [ ] Topology shows `rhdh-agent` group (Hub, LiteLLM, MCP, applier, PostgreSQL)  
- [ ] Lightspeed streaming_query returns tokens (no error event)  
- [ ] Guest login works without IdP  
- [ ] Catalog shows three Golden Path templates (no pre-installed sample agents)
If any step fails, see [Troubleshooting]({{ '/troubleshooting/' | relative_url }}).
