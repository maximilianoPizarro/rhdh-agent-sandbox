# Minimal metadata materialized by Deploy Agent golden path (source lives under language/ subdirs).
# Runtime image is built via BuildConfig; agent-applier deploys from ImageStream.

# ${{ values.name }}
Agent: ${{ values.name }}
Language: ${{ values.language }}
Framework: ${{ values.framework }}
Model: ${{ values.model }}
Type: ${{ values.agentType }}

## Specification

${{ values.agentSpec }}

## Pipeline

1. Scaffolder generates real framework source (`python/` | `nodejs/` | `quarkus/`).
2. Component annotations set `rhdh-agent-sandbox.io/build=true`.
3. Agent-applier materializes source, starts Binary BuildConfig, deploys ImageStream tag.

## Verify

```bash
oc get bc/${{ values.name }}
oc logs -f bc/${{ values.name }}
oc get deploy/${{ values.name }}
oc logs deploy/${{ values.name }}
```

## Open in DevSpaces

https://workspaces.openshift.com/#https://github.com/maximilianoPizarro/rhdh-agent-sandbox/tree/main/files/templates/skeletons/deploy-agent/${{ values.language }}

## Red Hat agentic skills

https://www.redhat.com/en/agentic-skills
