# Community packs on GHCR

CI publishes **optional asset packs** (skills/prompts bundles) to:

```text
ghcr.io/maximilianoPizarro/rhdh-agent-sandbox/<pack>:<tag>
```

| Pack | Contents |
|---|---|
| `ai-skills-pack` | Skill markdown bundles |
| `ai-prompts-pack` | Prompt markdown bundles |
| `plugin-catalog-index` | Extra catalog/index assets for packaging demos |

## Build locally

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u maximilianoPizarro --password-stdin
./community-plugins/build-and-push.sh 0.1.0
```

## What actually loads in RHDH

!!! important
    These GHCR packs are **not** installed as RHDH dynamic plugins. Hub AI entities come from the Helm ConfigMap `rhdh-agent-sandbox-catalog` (`files/catalog/*` mounted at `/opt/app-root/src/catalog`).

Use GHCR packs if you want to distribute the same skills/prompts as OCI artifacts for Continue or other tooling. Keep `catalogIndex.extraImages` empty unless the image is a real RHDH catalog index — a wrong image fails `install-dynamic-plugins` and blocks the Hub pod.
