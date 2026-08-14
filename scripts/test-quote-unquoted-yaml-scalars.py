#!/usr/bin/env python3
"""Regression tests for catalog entity YAML quoting.

Keep the regex in sync with:
  templates/agent-applier.yaml → quote_unquoted_yaml_scalars
  community-plugins/.../quoteUnquotedYamlScalars.ts
"""
from __future__ import annotations

import json
import re
import sys


def quote_unquoted_yaml_scalars(text: str) -> str:
    keys = (
        "description",
        "rhdh-agent-sandbox.io/agent-spec",
    )
    key_re = "|".join(re.escape(k) for k in keys)

    def repl(m: re.Match[str]) -> str:
        indent, key, val = m.group(1), m.group(2), m.group(3)
        stripped = val.strip()
        if not stripped or stripped[0] in ('"', "'", "|", ">"):
            return m.group(0)
        return f"{indent}{key}: {json.dumps(stripped)}"

    return re.sub(
        rf"^([ \t]*)({key_re}): ([^\n]+)$",
        repl,
        text,
        flags=re.MULTILINE,
    )


def main() -> int:
    broken = """\
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: cve-triage-agent
  description: You are a triage agent. Example questions: Are all pods healthy?
  annotations:
    rhdh-agent-sandbox.io/agent-spec: Prefer read-only list and get actions
"""
    quoted = quote_unquoted_yaml_scalars(broken)
    if 'description: "You are a triage agent. Example questions: Are all pods healthy?"' not in quoted:
        print("FAIL: description was not quoted", file=sys.stderr)
        print(quoted, file=sys.stderr)
        return 1
    if 'rhdh-agent-sandbox.io/agent-spec: "Prefer read-only list and get actions"' not in quoted:
        print("FAIL: agent-spec was not quoted", file=sys.stderr)
        print(quoted, file=sys.stderr)
        return 1

    already = "  description: >-\n    keep block\n  description: \"already\"\n"
    if quote_unquoted_yaml_scalars(already) != already:
        print("FAIL: block/quoted scalars were rewritten", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
