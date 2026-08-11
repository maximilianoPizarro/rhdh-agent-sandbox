#!/usr/bin/env bash
# Copy SKILL.md files from ai-skills-pack into MCP TechDocs sites (build-time sync).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS="${ROOT}/community-plugins/ai-skills-pack/skills"
TECHDOCS="${ROOT}/files/techdocs/mcp"

copy_skill() {
  local skill_name="$1"
  local dest_api="$2"
  local dest_file="$3"
  local src="${SKILLS}/${skill_name}/SKILL.md"
  local dst="${TECHDOCS}/${dest_api}/docs/skills/${dest_file}"
  if [[ -f "${src}" ]]; then
    mkdir -p "$(dirname "${dst}")"
    cp "${src}" "${dst}"
    echo "Synced ${skill_name} -> ${dest_api}/docs/skills/${dest_file}"
  else
    echo "WARN: missing ${src}" >&2
  fi
}

copy_skill openshift-mcp openshift-mcp-server openshift-mcp.md
copy_skill openshift-mcp kubernetes-mcp-server openshift-mcp.md
copy_skill lightspeed-rag rhdh-mcp-actions lightspeed-rag.md
copy_skill devspaces-ai rhdh-mcp-actions devspaces-ai.md
copy_skill red-hat-cve-explainer red-hat-security-mcp red-hat-cve-explainer.md
copy_skill red-hat-product-lifecycle red-hat-security-mcp red-hat-product-lifecycle.md
copy_skill red-hat-diagnostics red-hat-security-mcp red-hat-diagnostics.md
copy_skill red-hat-support-severity red-hat-security-mcp red-hat-support-severity.md
copy_skill red-hat-security-mcp-setup red-hat-security-mcp red-hat-security-mcp-setup.md

echo "MCP skills TechDocs sync complete."
