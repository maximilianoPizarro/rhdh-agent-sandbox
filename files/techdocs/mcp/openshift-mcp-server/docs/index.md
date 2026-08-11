# OpenShift MCP Server

Namespace-scoped OpenShift operations for Lightspeed and AI agents.

| Property | Value |
|----------|-------|
| Transport | HTTP |
| In-cluster URL | `http://rhdh-agent-sandbox-mcp:8080/mcp` |
| Catalog entity | `api:default/openshift-mcp-server` |

## Tools (examples)

- `monitorDeployments` — rollout health in namespace
- `createDeployment` / `createService` — guarded mutations

## Agent skills

See [OpenShift MCP skill](skills/openshift-mcp.md) for tool-calling rules.
