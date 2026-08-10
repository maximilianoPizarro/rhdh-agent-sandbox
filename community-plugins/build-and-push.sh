#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-0.1.0}"
REGISTRY="${REGISTRY:-quay.io}"
REPO="${REPO:-maximilianopizarro/rhdh-agent-sandbox}"
ENGINE="${ENGINE:-podman}"

if ! command -v "${ENGINE}" >/dev/null 2>&1; then
  echo "ERROR: container engine '${ENGINE}' not found in PATH (this script defaults to podman)." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
PACKS=(ai-skills-pack ai-prompts-pack plugin-catalog-index)

for pack in "${PACKS[@]}"; do
  img="${REGISTRY}/${REPO}:${pack}-${TAG}"
  echo "==> Building ${img}"
  "${ENGINE}" build -t "${img}" -f "${ROOT}/${pack}/Containerfile" "${ROOT}/${pack}"
  echo "==> Pushing ${img}"
  "${ENGINE}" push "${img}"
done

echo "Done. Published ${#PACKS[@]} images under ${REGISTRY}/${REPO}:*-${TAG}"
