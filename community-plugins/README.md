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

CI pushes packs to GHCR and attempts to mark them **public** (required for anonymous Sandbox pulls). Hub catalog entities still load from GitHub `files/catalog/` URLs — do not point `catalogIndex.extraImages` at these asset packs unless they are real RHDH catalog-index images.
Asset packs above complement that with demo-specific Skills / Prompts / MCP catalog entities mounted by the Helm chart ConfigMap.
