# Kubernetes MCP Server

Official OpenShift/Kubernetes MCP server for CRUD and Helm helpers in the current namespace.

| Property | Value |
|----------|-------|
| Transport | HTTP |
| In-cluster URL | `http://rhdh-agent-sandbox-k8s-mcp:8085/mcp` |

## Tools (examples)

- `pods_list_in_namespace`
- `events_list`
- `helm_list`

## Skills

Kubernetes MCP shares namespace-scoped rules with OpenShift MCP — see [skills/openshift-mcp.md](skills/openshift-mcp.md).
