# Runbook — {{name}}

## Watch build

```bash
oc get bc/{{name}}
oc logs -f bc/{{name}}
oc get is/{{name}}
```

## Watch rollout

```bash
oc get deploy/{{name}}
oc logs deploy/{{name}}
curl -s http://{{name}}:8080/health
```

## Troubleshooting

- Build pending: check namespace quota (`oc describe quota`)
- agent-applier logs: `oc logs deploy/rhdh-agent-sandbox-agent-applier --tail=50`
- Catalog missing: verify pending ConfigMap was registered (`oc get cm -l rhdh-agent-sandbox.io/pending-catalog-entity`)
