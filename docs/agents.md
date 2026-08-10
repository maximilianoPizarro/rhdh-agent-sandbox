# Agents

Three related loops on Developer Sandbox. Prefer [Golden Paths](golden-paths.md) to create a new agent Pod + catalog Component.

## 1. Hub Guest (in-cluster)

| Surface | Path |
|---|---|
| Lightspeed | Guest UI → lightspeed-core → LiteLLM Service → Granite/Qwen |
| MCP Chat | Guest UI → LiteLLM + MCP servers (tools limited without model function-calling) |
| Catalog | Skills, prompts, MCP entities, **Deploy Agent** template, sample agent Components |

Guest has **no** OpenShift token. Agent Deployments are created by chart RBAC (samples + agent-applier), not by the Guest’s kubeconfig.

## 2. Agent Pod (Golden Path / samples)

- Stub HTTP server (`/health`, `/v1/chat`) with `AGENT_SPEC`, `FRAMEWORK`, `MODEL`, LiteLLM env.
- Image: shared UBI Python runtime ConfigMap for Sandbox quota; framework is a label/intent (LangGraph / LangChain.js / LangChain4j).
- Service: **ClusterIP only**.
- Driven by Component annotations or Helm `agents.samples`.

```bash
oc get deploy,svc -l app.kubernetes.io/component=agent
oc logs deploy/sample-python-agent
```

## 3. DevSpaces (OpenShift user)

Factory links on sample / golden-path Components open:

`https://workspaces.openshift.com/#https://github.com/maximilianoPizarro/rhdh-agent-sandbox/tree/main/files/templates/skeletons/<language>`

Agent-oriented Devfiles also live under `files/devfiles/agents/`. Wire Continue to the LiteLLM **Route** with `litellm-master-key` (see [DevSpaces AI](devspaces-ai.md)).

Parallel path: use a DevSpaces catalog sample workspace if you do not have admin on `openshift-devspaces`.

## Identity cheat sheet

| Actor | Token / power |
|---|---|
| Hub Guest | Catalog + Lightspeed + scaffolder register (no cluster admin) |
| Agent Pod SA / applier | Namespace create/update Deployment, Service |
| OpenShift Sandbox user | `model-api-key` refresh, DevSpaces start, read secrets |
