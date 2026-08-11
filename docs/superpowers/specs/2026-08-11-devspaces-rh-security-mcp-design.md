# DevSpaces Continue + Red Hat Security MCP

**Date:** 2026-08-11  
**Status:** Draft for review  
**Approach:** B — preconfigure MCP + Simple Browser SSO in Che Code

## Problem

The DevSpaces Golden Path prewires Continue → LiteLLM (chat) and Hub MCP Actions (catalog/TechDocs). Red Hat Security MCP (`https://security-mcp.api.redhat.com/mcp`) is needed for live CVE/advisory tools and skills already shipped in skeletons, but it is not preconfigured. Auth is Customer Portal SSO (browser), not a static bearer.

## Goals

1. Scaffolded DevSpaces workspaces include `red-hat-security` in Continue MCP config (no secrets in git).
2. First tool use authenticates via **Simple Browser inside Che Code**.
3. Journey docs document Path C (Security MCP) with a smoke prompt and an explicit host-browser fallback.
4. Skills under `.cursor/skills/` / `.continue/skills/` remain usable once authenticated.

## Non-goals

- Proxying Security MCP through the cluster or Hub.
- Storing RHSSO tokens in Kubernetes Secrets.
- Changing Hub Lightspeed MCP wiring.

## Design

### Preconfiguration

- Extend Devfile `wire-continue` (all language skeletons) to write into `~/.continue/config.yaml`:

```yaml
mcpServers:
  - name: red-hat-security
    type: streamable-http
    url: https://security-mcp.api.redhat.com/mcp
```

- Also ship repo-safe `.continue/mcpServers/red-hat-security.yaml` in skeletons (no headers/env).
- Do **not** add `apiKey` / `Authorization` — SSO is handled by the MCP client.

### Auth UX (Simple Browser)

- Add Devfile command `auth-rh-security-mcp` that:
  1. Prints short instructions.
  2. Opens / focuses Che Code **Simple Browser** on the SSO URL when Continue surfaces one, or on a documented Customer Portal login entry point.
- Happy path: user completes login in Simple Browser; Continue stores session for subsequent tool calls.
- Fallback: same URL in a host browser tab if Simple Browser cannot complete redirects.

### Docs / journey

- Add Path C beside LiteLLM (A) and Hub MCP (B) in `docs-src/devspaces-journey.md`.
- Smoke: ask Continue to explain a known CVE with Red Hat severity (uses Security MCP tools / CVE skill).

### Catalog / Hub

- No new Hub entity required for this pass; existing `red-hat-security-mcp` API / skills catalog entries stay as documentation anchors.

## Risks

| Risk | Mitigation |
|------|------------|
| Continue OAuth/localhost redirect fails in remote IDE | Document fallback; prefer URL printed by Continue |
| Simple Browser cookie isolation vs RHSSO | Fallback to host tab |
| Transport type mismatch (`streamable-http` vs `http`) | Verify against Continue version shipped via OpenVSX; adjust one field if needed |

## Success criteria

- After `wire-continue`, Continue lists `red-hat-security` MCP server.
- After Simple Browser login, a CVE smoke question returns Red Hat severity data without manual `.mcp.json` edits.
- Host-browser fallback is documented in one short paragraph.
