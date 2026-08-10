# Community AI asset packs (Quay)

These packages ship **installable AI assets** (skills, prompts, catalog index) related to the sandbox demo that are **not** included in the Developer Hub image.

Images are published by CI (Podman) to:

```text
quay.io/maximilianopizarro/rhdh-agent-sandbox:<name>-<tag>
```

| Pack | Purpose |
|---|---|
| `ai-skills-pack` | Cursor/agent skills markdown + catalog metadata |
| `ai-prompts-pack` | Saved prompts for Lightspeed / MCP workflows |
| `plugin-catalog-index` | Extra catalog index image for Extensions discovery |

## Local build (Podman)

```bash
printf '%s' "$QUAY_PASSWORD" | podman login quay.io -u "$QUAY_USERNAME" --password-stdin
ENGINE=podman REGISTRY=quay.io REPO=maximilianopizarro/rhdh-agent-sandbox \
  ./community-plugins/build-and-push.sh 0.1.0
```

Requires Podman and a Quay robot account with push access.

## RHDH dynamic plugins note

CI pushes packs to Quay. Make the Quay repository **public** (or use a pull secret) for Sandbox anonymous pulls. Hub catalog entities still load from the chart ConfigMap (`files/catalog/`) — do not point `catalogIndex.extraImages` at these asset packs unless they are real RHDH catalog-index images.
