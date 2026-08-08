# Community AI asset packs (GHCR)

These packages ship **installable AI assets** (skills, prompts, catalog index) for the sandbox demo.

Images are published by CI to:

```text
ghcr.io/maximilianoPizarro/rhdh-agent-sandbox/<name>:<tag>
```

| Pack | Purpose |
|---|---|
| `ai-skills-pack` | Cursor/agent skills markdown + catalog metadata |
| `ai-prompts-pack` | Saved prompts for Lightspeed / MCP workflows |
| `plugin-catalog-index` | Extra catalog index image for Extensions discovery |

## Local build

```bash
./community-plugins/build-and-push.sh 0.1.0
```

Requires `docker` or `podman` and permission to push to GHCR (`echo $GITHUB_TOKEN | docker login ghcr.io -u USER --password-stdin`).

## RHDH dynamic plugins note

RHDH also loads the official community plugin index (`ghcr.io/redhat-developer/rhdh-plugin-community-index:1.10`) via `global.catalogIndex.extraImages`.
Asset packs above complement that with demo-specific Skills / Prompts / MCP catalog entities mounted by the Helm chart ConfigMap.
