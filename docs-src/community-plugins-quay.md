---
title: Community packs / Quay
---

# Community packs on Quay

CI publishes **optional asset packs** (skills / prompts / catalog index) for related community content that is **not** baked into the Developer Hub image. Images go to:

```text
quay.io/maximilianopizarro/rhdh-agent-sandbox:<pack>-<tag>
```

| Pack | Image tag example | Contents |
|---|---|---|
| `ai-skills-pack` | `ai-skills-pack-0.1.0` | Skill markdown bundles |
| `ai-prompts-pack` | `ai-prompts-pack-0.1.0` | Prompt markdown bundles |
| `plugin-catalog-index` | `plugin-catalog-index-0.1.0` | Extra catalog/index assets for packaging demos |

Repository: [quay.io/maximilianopizarro/rhdh-agent-sandbox](https://quay.io/repository/maximilianopizarro/rhdh-agent-sandbox)

## Build locally (Podman)

```bash
printf '%s' "$QUAY_PASSWORD" | podman login quay.io -u "$QUAY_USERNAME" --password-stdin

ENGINE=podman REGISTRY=quay.io REPO=maximilianopizarro/rhdh-agent-sandbox \
  ./community-plugins/build-and-push.sh 0.1.0
```

Requires **Podman** (default engine). Override with `ENGINE=…` only if you know what you are doing.

## GitHub Actions

On push to `main` / `workflow_dispatch`, the `quay` job:

1. Installs Podman  
2. Logs into Quay with secrets `QUAY_USERNAME` and `QUAY_PASSWORD`  
3. Builds and pushes the three tags above  

Set the repo visibility in Quay to **public** for anonymous Developer Sandbox pulls, or configure a pull secret in the namespace.

## What actually loads in RHDH

> **Important**
>
> These Quay packs are **not** installed as RHDH dynamic plugins. Hub AI entities come from the Helm ConfigMap `rhdh-agent-sandbox-catalog` (`files/catalog/*` mounted at `/opt/app-root/src/catalog`).

Use Quay packs to distribute the same skills/prompts as OCI artifacts for Continue or other tooling. Keep `catalogIndex.extraImages` empty unless the image is a real RHDH catalog index — a wrong image fails `install-dynamic-plugins` and blocks the Hub pod.
