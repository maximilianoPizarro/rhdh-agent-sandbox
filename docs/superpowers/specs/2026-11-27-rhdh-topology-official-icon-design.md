# Design: Official RHDH Topology icon

**Date:** 2026-11-27  
**Scope:** OpenShift Topology / console icon for Deployment `rhdh-agent-sandbox-developer-hub` only.

## Problem

The Hub Deployment pods use `app.openshift.io/custom-icon` pointing at this chart’s custom sandbox asset (`docs/assets/icon.png` — robot in hexagon). Topology therefore shows a non-product icon. The goal is the **official Red Hat Developer Hub** product mark in Topology.

## Non-goals

- Hub UI sidebar `app.branding.fullLogo` / `iconLogo` / favicon inside Developer Hub
- Replacing `docs/assets/icon.png` used by GitHub Pages / site branding
- Theme color or title changes

## Approach (chosen)

Point the existing Helm value at the upstream official favicon from the RHDH product repo (square PNG, suitable for Topology):

`https://raw.githubusercontent.com/redhat-developer/rhdh/main/packages/app/public/favicon-96x96.png`

Alternatives considered and rejected for this change:

- **Vendor** the PNG into `docs/assets/` — more durable if upstream moves paths; deferred unless URL breakage becomes an issue
- **Live-only annotate** — would be overwritten by the next `helm upgrade`

## Change

In `values.yaml`, under `rhdh.podAnnotations`:

| Key | From | To |
|-----|------|----|
| `app.openshift.io/custom-icon` | `https://raw.githubusercontent.com/maximilianopizarro/rhdh-agent-sandbox/main/docs/assets/icon.png` | `https://raw.githubusercontent.com/redhat-developer/rhdh/main/packages/app/public/favicon-96x96.png` |

No template changes: the subchart already maps `rhdh.podAnnotations` onto the Hub pod template.

## Apply

`helm upgrade` the existing release so the Deployment pod template picks up the new annotation (triggers a rollout).

## Verification

1. Annotation on the Deployment pod template equals the upstream favicon URL:
   ```bash
   oc get deploy rhdh-agent-sandbox-developer-hub \
     -o jsonpath='{.spec.template.metadata.annotations.app\.openshift\.io/custom-icon}{"\n"}'
   ```
2. Topology (Developer perspective) shows the official RHDH mark (network nodes + red magnifying glass), not the sandbox robot icon.

## Risks

- Upstream path moves on `redhat-developer/rhdh` `main` → icon 404 in Topology. Mitigation: switch to vendored asset (approach 2) if that happens.
