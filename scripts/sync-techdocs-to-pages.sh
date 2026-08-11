#!/usr/bin/env bash
# Sync platform TechDocs markdown from files/techdocs/platform/docs to docs-src for GitHub Pages.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/files/techdocs/platform/docs"
DEST="${ROOT}/docs-src"

declare -A PERMALINKS=(
  [index.md]="/"
  [quickstart.md]="/quickstart/"
  [architecture.md]="/architecture/"
  [golden-paths.md]="/golden-paths/"
  [demo-script.md]="/demo-script/"
)

declare -A TITLES=(
  [index.md]="Agent-friendly Developer Hub"
  [quickstart.md]="Quickstart"
  [architecture.md]="Architecture"
  [golden-paths.md]="Golden Paths"
  [demo-script.md]="Demo script"
)

for md in index.md quickstart.md architecture.md golden-paths.md demo-script.md; do
  src_file="${SRC}/${md}"
  dest_file="${DEST}/${md}"
  if [[ ! -f "${src_file}" ]]; then
    echo "WARN: missing ${src_file}" >&2
    continue
  fi
  title="${TITLES[$md]}"
  permalink="${PERMALINKS[$md]}"
  {
    echo "---"
    echo "layout: default"
    echo "title: ${title}"
    echo "permalink: ${permalink}"
    echo "---"
    echo
    # Strip first heading if present (Jekyll title comes from front matter)
    tail -n +1 "${src_file}" | sed '1{/^# /d;}'
  } > "${dest_file}"
  echo "Synced ${md} -> ${dest_file}"
done

# Copy platform diagram assets used by synced pages
mkdir -p "${DEST}/assets/diagrams"
if [[ -d "${SRC}/assets" ]]; then
  cp -f "${SRC}/assets/"*.png "${DEST}/assets/diagrams/" 2>/dev/null || true
fi

echo "TechDocs platform sync complete."
