# Community packs on GHCR

CI publishes asset packs to:

```text
ghcr.io/maximilianoPizarro/rhdh-agent-sandbox/<pack>:<tag>
```

Packs:

- `ai-skills-pack`
- `ai-prompts-pack`
- `plugin-catalog-index` (extra Extensions/catalog index)

## Build locally

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u maximilianoPizarro --password-stdin
./community-plugins/build-and-push.sh 0.1.0
```

## What loads in RHDH

- Demo AI index content: `ghcr.io/maximilianoPizarro/rhdh-agent-sandbox/plugin-catalog-index:0.1.0` (asset pack; Hub catalog entities load from GitHub `files/catalog/` URLs)
- Skills/Prompts/MCP entities: also shipped in Helm ConfigMap `rhdh-agent-sandbox-catalog` and via GitHub `files/catalog/` locations once the repo is public
