# Minimal skeleton materialized by Deploy Agent golden path (no git push).
# Runtime Pod is created by the chart agent-applier from Component annotations.

# ${{ values.name }}
Agent: ${{ values.name }}
Language: ${{ values.language }}
Framework: ${{ values.framework }}
Model: ${{ values.model }}
Type: ${{ values.agentType }}

## Specification

${{ values.agentSpec }}

## Cluster

The Hub agent-applier watches catalog Components annotated
`rhdh-agent-sandbox.io/managed-agent=true` and ensures Deployment + Service
in the release namespace (ClusterIP only, LiteLLM via Service DNS).

## Open in DevSpaces

https://workspaces.openshift.com/#https://github.com/maximilianoPizarro/rhdh-agent-sandbox/tree/main/files/templates/skeletons/${{ values.language }}
