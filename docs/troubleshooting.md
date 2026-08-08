# Troubleshooting

## LiteLLM 401 to shared models

Refresh the Sandbox token:

```bash
oc set env secret/rhdh-agent-sandbox-secrets model-api-key="$(oc whoami -t)"
oc rollout restart deploy -l app.kubernetes.io/component=litellm
```

## RHDH Route host wrong

Set the correct apps domain:

```bash
helm upgrade rhdh-agent . -f values-sandbox.yaml \
  --set rhdh.global.clusterRouterBase=apps.<your-sandbox>.openshiftapps.com \
  --reuse-values
```

## Pods Pending / quota

Disable optional pieces:

```bash
--set mcp.kubernetes.enabled=false \
--set litellm.route.enabled=false
```

Lower RHDH memory in `values-sandbox.yaml` if needed.

## Catalog entities missing

Ensure the GitHub repo is public (URL locations) or apply/sync ConfigMap `rhdh-agent-sandbox-catalog` contents into a catalog location RHDH can read.

## MCP permission errors

MCP ServiceAccount only has **namespace** Role access. Cluster-scoped tools will fail by design on Developer Sandbox.
