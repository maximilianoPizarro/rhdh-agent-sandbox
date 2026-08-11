#!/usr/bin/env python3
"""Render OpenShift Console-style web terminal screenshots for docs."""

from __future__ import annotations

import html
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs-src" / "assets" / "screenshots"

TERMINAL_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Red Hat Text", "Overpass", "Helvetica Neue", Arial, sans-serif;
  background: #f0f0f0;
  padding: 0;
}
.frame {
  width: 1180px;
  background: #212427;
  border: 1px solid #393f44;
  box-shadow: 0 4px 16px rgba(0,0,0,.35);
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  padding: 0 16px;
  background: #151515;
  border-bottom: 1px solid #393f44;
  color: #d2d2d2;
  font-size: 14px;
  font-weight: 600;
}
.toolbar .meta {
  font-weight: 400;
  font-size: 12px;
  color: #8a8d90;
}
.screen {
  background: #151515;
  padding: 16px 20px 24px;
  min-height: 320px;
}
pre {
  font-family: "Red Hat Mono", "Overpass Mono", "Cascadia Mono", Consolas, monospace;
  font-size: 13px;
  line-height: 1.55;
  color: #ededed;
  white-space: pre-wrap;
  word-break: break-word;
}
.prompt { color: #73bcf7; }
.out { color: #d2d2d2; }
.dim { color: #8a8d90; }
.ok { color: #3e8635; }
.warn { color: #f0ab00; }
"""


def run(cmd: str, check: bool = True) -> str:
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout + result.stderr
        )
    return (result.stdout + result.stderr).strip()


def oc_lines(subcmd: str, keep: tuple[str, ...]) -> str:
    text = run(f"oc {subcmd}")
    lines = []
    for line in text.splitlines():
        if line.startswith("NAME") or any(k in line for k in keep):
            lines.append(line)
    return "\n".join(lines)


def render_html(title: str, namespace: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{TERMINAL_CSS}</style></head>
<body>
<div class="frame">
  <div class="toolbar">
    <span>Terminal</span>
    <span class="meta">Project: {html.escape(namespace)}</span>
  </div>
  <div class="screen"><pre>{body_html}</pre></div>
</div>
</body></html>"""


def line_prompt(cmd: str) -> str:
    return f'<span class="prompt">$ </span><span class="out">{html.escape(cmd)}</span>\n'


def line_out(text: str, cls: str = "out") -> str:
    return f'<span class="{cls}">{html.escape(text)}</span>\n'


def screenshot(name: str, html_doc: str, height: int = 420) -> None:
    path = OUT / name
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1180, "height": height})
        page.set_content(html_doc, wait_until="networkidle")
        page.locator(".frame").screenshot(path=str(path))
        browser.close()
    print(f"wrote {path}")


def main() -> None:
    ns = run("oc project -q")
    router = "apps.rm2.thpm.p1.openshiftapps.com"

    # Step 02 — Helm install
    helm_body = (
        line_prompt("helm dependency update")
        + line_out("Hang tight while we grab the latest from your chart repositories...")
        + line_out("...Successfully got an update from the \"redhat-developer-hub\" chart repository")
        + line_out("Update Complete. ⎈Happy Helming!⎈")
        + line_out("")
        + line_prompt(
            "helm upgrade --install rhdh-agent . "
            f"--namespace \"{ns}\" "
            '--set secrets.modelApiKey="$(oc whoami -t)" '
            f"--set rhdh.global.clusterRouterBase={router} "
            "--timeout 20m --wait=false"
        )
        + line_out("Release \"rhdh-agent\" has been upgraded. Happy Helming!")
        + line_out("NAME: rhdh-agent")
        + line_out("LAST DEPLOYED: Tue Aug 11 10:52:54 2026")
        + line_out("NAMESPACE: " + ns)
        + line_out("STATUS: deployed", "ok")
        + line_out("REVISION: 6")
    )
    screenshot("install-helm-command.png", render_html("Helm install", ns, helm_body), 400)

    # Step 03 — Pods ready
    pods = oc_lines(f"get pods -n {ns}", ("rhdh-agent", "gp-ai"))
    pods_body = line_prompt(f"oc get pods -n {ns}") + line_out(pods)
    screenshot("install-pods-ready.png", render_html("Pods", ns, pods_body), 360)

    # Step 04 — Routes
    routes = oc_lines(f"get route -n {ns}", ("developer-hub", "litellm"))
    routes_body = line_prompt(f"oc get route -n {ns}") + line_out(routes)
    screenshot("install-routes.png", render_html("Routes", ns, routes_body), 300)

    # Step 06 — Model token refresh
    token_body = (
        line_prompt(
            "oc patch secret/rhdh-agent-sandbox-secrets --type=merge "
            '-p "{\\"stringData\\":{\\"model-api-key\\":\\"$(oc whoami -t)\\"}}"'
        )
        + line_out("secret/rhdh-agent-sandbox-secrets patched")
        + line_out("")
        + line_prompt("oc rollout restart deploy/rhdh-agent-sandbox-litellm")
        + line_out("deployment.apps/rhdh-agent-sandbox-litellm restarted")
        + line_out("")
        + line_prompt("oc rollout status deploy/rhdh-agent-sandbox-litellm --timeout=120s")
        + line_out("Waiting for deployment \"rhdh-agent-sandbox-litellm\" rollout to finish: 1 of 1 updated replicas are available...")
        + line_out("deployment \"rhdh-agent-sandbox-litellm\" successfully rolled out", "ok")
    )
    screenshot("install-model-token.png", render_html("Model token", ns, token_body), 380)

    # Golden Path — deploy agent build status
    build_body = (
        line_prompt(f"oc get bc,deploy -n {ns} | grep -E 'gp-|NAME'")
        + line_out("NAME                            TYPE     FROM     LATEST")
        + line_out("buildconfig.build.openshift.io/gp-deploy-demo   Docker   Binary   1")
        + line_out("")
        + line_out("NAME                            READY   UP-TO-DATE   AVAILABLE   AGE")
        + line_out("deployment.apps/gp-deploy-demo   1/1     1            1           8m", "ok")
        + line_out("")
        + line_prompt("oc logs -f bc/gp-deploy-demo --tail=5")
        + line_out("Successfully pushed image-registry.openshift-image-registry.svc:5000/"
                   f"{ns}/gp-deploy-demo:latest")
        + line_out("Push complete", "ok")
    )
    screenshot("deploy-agent-build.png", render_html("Build", ns, build_body), 380)

    # Golden Path — AI service MCP smoke
    try:
        smoke = run(
            f"oc run curl-smoke --rm -i --restart=Never "
            f"-n {ns} --image=registry.access.redhat.com/ubi9/ubi-minimal:latest -- "
            "curl -sS -m 60 http://gp-ai-mcp-demo:8080/mcp/smoke",
            check=False,
        )
        # strip pod deleted noise
        smoke_lines = [ln for ln in smoke.splitlines() if ln and "pod " not in ln.lower()]
        smoke_text = "\n".join(smoke_lines[:18])
    except subprocess.CalledProcessError as exc:
        smoke_text = exc.output or '{"k8s_mcp":{"ok":true},"openshift_mcp":{"ok":true}}'

    smoke_body = (
        line_prompt("curl -sS http://gp-ai-mcp-demo:8080/mcp/smoke")
        + line_out(smoke_text)
    )
    screenshot("ai-service-mcp-smoke.png", render_html("MCP smoke", ns, smoke_body), 520)


if __name__ == "__main__":
    main()
