#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-0.1.0}"
REGISTRY="${REGISTRY:-ghcr.io}"
PREFIX="${PREFIX:-maximilianoPizarro/rhdh-agent-sandbox}"
ENGINE="${ENGINE:-}"

if [[ -z "${ENGINE}" ]]; then
  if command -v podman >/dev/null 2>&1; then
    ENGINE=podman
  else
    ENGINE=docker
  fi
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
PACKS=(ai-skills-pack ai-prompts-pack plugin-catalog-index)

for pack in "${PACKS[@]}"; do
  img="${REGISTRY}/${PREFIX}/${pack}:${TAG}"
  echo "==> Building ${img}"
  "${ENGINE}" build -t "${img}" -f "${ROOT}/${pack}/Containerfile" "${ROOT}/${pack}"
  echo "==> Pushing ${img}"
  "${ENGINE}" push "${img}"
done

echo "Done. Published ${#PACKS[@]} images with tag ${TAG}"
