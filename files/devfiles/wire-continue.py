#!/usr/bin/env python3
"""Configure Continue 2.x for this DevSpaces workspace.

Writes live keys to ~/.continue/config.yaml (local only; Continue 2 ignores
project .continue/config.json). Placeholders in the repo tree stay secret-free.

MCP:
  - red-hat-security — official CVE/advisory API (Customer Portal SSO on first use)
  - hub-mcp-actions  — Hub catalog/TechDocs when mcp-token + Hub Route exist
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONTINUE_SECRET = os.environ.get("CONTINUE_SECRET", "rhdh-agent-sandbox-continue")
HUB_SECRETS = os.environ.get("SECRETS_NAME", "rhdh-agent-sandbox-secrets")
RH_SECURITY_URL = "https://security-mcp.api.redhat.com/mcp"


def _oc(*args: str) -> str:
    try:
        out = subprocess.check_output(["oc", *args], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return ""


def _secret_key(name: str, key: str) -> str:
    raw = _oc("get", "secret", name, "-o", f"jsonpath={{.data.{key}}}")
    if not raw:
        return ""
    try:
        return base64.b64decode(raw).decode()
    except Exception:
        return ""


def _env_or_secret(env_name: str, secret: str, key: str) -> str:
    return (os.environ.get(env_name) or "").strip() or _secret_key(secret, key)


def _ys(value: str) -> str:
    return json.dumps(value)


def _cleanup_placeholder_mcp() -> None:
    """Continue 2 also loads YAML from .continue/mcpServers/ (workspace + parents)."""
    names = (
        "new-mcp-server.yaml",
        "new-mcp-server.json",
        # Leftover streamable-http stubs 401 and paint the Tools list red.
        "red-hat-security.yaml",
        "red-hat-security.json",
    )
    roots = [Path.home() / ".continue", Path.cwd() / ".continue"]
    here = Path.cwd()
    for parent in [here, *here.parents]:
        roots.append(parent / ".continue")
        if parent.as_posix() in {"/", "/projects"}:
            break
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        mcp_dir = root / "mcpServers"
        for name in names:
            path = mcp_dir / name
            if path.is_file():
                path.unlink()
                print(f"Removed leftover MCP file {path}")


def _prewarm_mcp_remote() -> None:
    try:
        subprocess.run(
            [
                "bash",
                "-lc",
                # Download the package without invoking its CLI (--help is parsed as a URL).
                'source "$HOME/.nvm/nvm.sh" 2>/dev/null; npx -y -p mcp-remote@latest node -e "process.exit(0)"',
            ],
            timeout=90,
            check=False,
        )
    except Exception as exc:
        print(f"mcp-remote prewarm skipped: {exc}")


def _hub_mcp_url() -> str:
    url = (os.environ.get("HUB_MCP_URL") or "").strip()
    if url:
        return url
    host = _oc(
        "get",
        "route",
        "-l",
        "app.kubernetes.io/name=developer-hub",
        "-o",
        "jsonpath={.items[0].spec.host}",
    )
    if host:
        return f"https://{host}/api/mcp-actions/v1"
    return ""


def _copy_skeleton(lang: str) -> None:
    src = Path(f"files/templates/skeletons/{lang}")
    if src.is_dir():
        shutil.copytree(src, Path("."), dirs_exist_ok=True)
        print(f"Copied skeleton {src}")


def _bin_dir() -> Path:
    path = Path.home() / ".local" / "share" / "rhdh-agent-sandbox" / "bin"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _oauth_url_file() -> Path:
    path = Path.home() / ".mcp-auth"
    path.mkdir(parents=True, exist_ok=True)
    return path / "last-oauth-url.txt"


def _install_oauth_helpers() -> None:
    """Stop Che Simple Browser from hijacking mcp-remote's OAuth URL.

    Che maps xdg-open/gio to code-redirect-N. Opening that route root shows
    Express 'Cannot GET /' and never hits 127.0.0.1:3334 inside the pod.
    """
    xdg = _bin_dir() / "xdg-open"
    xdg.write_text(
        "#!/bin/bash\n"
        'URL="${1:-}"\n'
        'mkdir -p "$HOME/.mcp-auth"\n'
        'if [[ "$URL" == http://* || "$URL" == https://* ]]; then\n'
        '  printf "%s\\n" "$URL" > "$HOME/.mcp-auth/last-oauth-url.txt"\n'
        '  echo "RH-SECURITY-OAUTH: open this URL in your laptop browser '
        '(not Che Simple Browser): $URL" >&2\n'
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    xdg.chmod(0o755)
    gio = _bin_dir() / "gio"
    gio.write_text(
        "#!/bin/bash\n"
        'if [[ "${1:-}" == "open" ]]; then\n'
        "  shift\n"
        '  exec xdg-open "$@"\n'
        "fi\n"
        'exec /usr/bin/gio "$@"\n',
        encoding="utf-8",
    )
    gio.chmod(0o755)


def _clear_stale_mcp_lock() -> None:
    root = Path.home() / ".mcp-auth"
    if not root.is_dir():
        return
    for lock in root.rglob("*lock.json"):
        try:
            pid = int(json.loads(lock.read_text(encoding="utf-8")).get("pid") or 0)
            os.kill(pid, 0)
        except Exception:
            lock.unlink(missing_ok=True)
            print(f"Removed stale mcp-remote lock {lock}")


def _merge_vscode_port_settings() -> None:
    """Keep Che from auto-previewing mcp-remote's callback port via code-redirect."""
    patch = {
        "remote.portsAttributes": {
            "3334": {
                "label": "mcp-remote OAuth callback",
                "onAutoForward": "ignore",
                "protocol": "http",
            }
        }
    }
    candidates = [
        Path.cwd() / ".vscode" / "settings.json",
        Path("/projects/agent-sandbox/.vscode/settings.json"),
    ]
    seen: set[str] = set()
    for settings in candidates:
        key = str(settings)
        if key in seen:
            continue
        seen.add(key)
        parent = settings.parent
        if not parent.parent.exists() and settings.parent.name == ".vscode":
            continue
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        data: dict = {}
        if settings.is_file():
            try:
                loaded = json.loads(settings.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except json.JSONDecodeError:
                data = {}
        ports = data.setdefault("remote.portsAttributes", {})
        if not isinstance(ports, dict):
            ports = {}
            data["remote.portsAttributes"] = ports
        ports["3334"] = patch["remote.portsAttributes"]["3334"]
        ports["8080"] = {
            "label": "Red Hat Security SSO helper",
            "onAutoForward": "ignore",
            "protocol": "https",
        }
        settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _share_dir() -> Path:
    path = Path.home() / ".local" / "share" / "rhdh-agent-sandbox"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _persist_self() -> None:
    dest = _share_dir() / "wire-continue.py"
    src = Path(__file__).resolve()
    if src.is_file():
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _oauth_helper_path() -> Path:
    return _share_dir() / "rh-security-oauth.py"


def _persist_oauth_helper() -> Path:
    dest = _oauth_helper_path()
    candidates = [
        Path(__file__).resolve().parent / "rh-security-oauth.py",
        Path("/opt/rhdh-agent-sandbox/rh-security-oauth.py"),
        Path("/projects/agent-sandbox/files/devfiles/rh-security-oauth.py"),
    ]
    for src in candidates:
        try:
            if src.is_file() and src.resolve() != dest.resolve():
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                dest.chmod(0o755)
                return dest
        except OSError:
            continue
    return dest


def _port_open(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _oauth_public_url() -> str:
    helper = _oauth_helper_path()
    if not helper.is_file():
        return ""
    try:
        out = subprocess.check_output(
            ["python3", str(helper), "--public-url"],
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        return out.decode().strip().rstrip("/")
    except Exception:
        return ""


def _start_oauth_helper() -> str:
    """Serve the SSO helper on :8080 (Devfile public endpoint http-8080)."""
    dest = _persist_oauth_helper()
    if not dest.is_file():
        print("rh-security-oauth.py not found next to wire-continue; SSO helper not started.")
        return ""
    log = Path.home() / ".mcp-auth" / "rh-oauth.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not _port_open(8080):
        with log.open("a", encoding="utf-8") as handle:
            subprocess.Popen(
                ["python3", str(dest)],
                stdout=handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        for _ in range(25):
            time.sleep(0.2)
            if _port_open(8080):
                break
    return _oauth_public_url()


def _install_continue_wrapper() -> None:
    """Prefer live MCP via mcp-remote; otherwise a stdio helper (avoids -32000)."""
    path = _bin_dir() / "rh-security-mcp.sh"
    helper = "$HOME/.local/share/rhdh-agent-sandbox/rh-security-oauth.py"
    path.write_text(
        "#!/bin/bash\n"
        'source "$HOME/.nvm/nvm.sh" 2>/dev/null\n'
        'export PATH="$HOME/.local/share/rhdh-agent-sandbox/bin:$PATH"\n'
        f'HELPER="{helper}"\n'
        'if [[ -f "$HELPER" ]] && ! python3 "$HELPER" --probe-mcp >/dev/null 2>&1; then\n'
        '  exec python3 "$HELPER" --stdio-bridge\n'
        "fi\n"
        f"exec npx -y mcp-remote@latest {RH_SECURITY_URL} 3334 "
        "--transport http-only --host 127.0.0.1 --auth-timeout 300\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _mcp_remote_launch() -> str:
    return (
        'source "$HOME/.nvm/nvm.sh" 2>/dev/null; '
        'exec "$HOME/.local/share/rhdh-agent-sandbox/bin/rh-security-mcp.sh"'
    )


def _forward_oauth_callback(raw: str) -> None:
    raw = raw.strip().strip("'\"")
    parsed = urllib.parse.urlparse(raw)
    qs = urllib.parse.parse_qs(parsed.query)
    if "code" not in qs and parsed.fragment:
        qs = urllib.parse.parse_qs(parsed.fragment)
    if "code" not in qs:
        for part in parsed.path.split("/"):
            if "code=" in urllib.parse.unquote(part):
                qs = urllib.parse.parse_qs(urllib.parse.unquote(part))
                break
    if "code" not in qs:
        raise SystemExit(
            "No code= parameter in the pasted URL. Copy the full address bar "
            "after Red Hat login (it starts with http://127.0.0.1:3334 or localhost)."
        )
    params = {"code": qs["code"][0]}
    if qs.get("state"):
        params["state"] = qs["state"][0]
    if qs.get("iss"):
        params["iss"] = qs["iss"][0]
    target = "http://127.0.0.1:3334/oauth/callback?" + urllib.parse.urlencode(params)
    print(f"Forwarding callback to mcp-remote in this workspace...")
    try:
        with urllib.request.urlopen(target, timeout=20) as resp:
            print(resp.read().decode("utf-8", errors="replace")[:500])
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"Could not reach mcp-remote on 127.0.0.1:3334 ({exc}). "
            "Toggle Continue red-hat-security off, re-run this command, and paste again."
        ) from exc


def _tokens_exist() -> bool:
    root = Path.home() / ".mcp-auth"
    return any(root.rglob("*tokens.json")) if root.is_dir() else False


def auth_rh_security() -> int:
    """Start the :8080 SSO helper and print the public Simple Browser URL."""
    _install_oauth_helpers()
    _install_continue_wrapper()
    _clear_stale_mcp_lock()
    url = _start_oauth_helper()
    extra = [a for a in sys.argv[1:] if a != "--auth-rh-security" and not a.startswith("-")]
    if extra:
        _forward_oauth_callback(extra[0])
        return 0 if _tokens_exist() else 1
    print()
    print("Helper:", (url + "/") if url else f"http://127.0.0.1:8080/")
    if _tokens_exist():
        print("Already have tokens. Continue Agent is enough unless you need to re-login.")
    else:
        print("Open that URL, Conectar, then swap 127.0.0.1:3334 for the helper host.")
    return 0 if url or _port_open(8080) else 1


def main() -> int:
    base = _env_or_secret("LITELLM_API_BASE", CONTINUE_SECRET, "LITELLM_API_BASE")
    key = _env_or_secret("LITELLM_API_KEY", CONTINUE_SECRET, "LITELLM_API_KEY")
    if not base or not key:
        print(
            "Set LITELLM_API_BASE and LITELLM_API_KEY "
            f"(or mount Secret {CONTINUE_SECRET}), then re-run wire-continue."
        )
        return 0

    default_model = os.environ.get("CONTINUE_DEFAULT_MODEL") or "granite"
    lang = os.environ.get("AGENT_LANGUAGE") or "python"
    _copy_skeleton(lang)

    models = [
        ("Granite (LiteLLM)", "granite", "[chat, edit, apply, autocomplete]"),
        ("Qwen3 (LiteLLM)", "qwen3", "[chat, edit, apply]"),
        ("LiteMaaS Qwen (LiteLLM)", "litemaas-qwen", "[chat, edit, apply]"),
    ]
    models.sort(key=lambda item: 0 if item[1] == default_model else 1)

    lines = [
        "name: Main Config",
        "version: 1.0.0",
        "schema: v1",
        "models:",
    ]
    for title, model_id, roles in models:
        lines += [
            f"  - name: {title}",
            "    provider: openai",
            f"    model: {model_id}",
            f"    apiBase: {_ys(base)}",
            f"    apiKey: {_ys(key)}",
            f"    roles: {roles}",
        ]

    hub_url = _hub_mcp_url()
    mcp_token = _env_or_secret("MCP_TOKEN", HUB_SECRETS, "mcp-token")
    _install_oauth_helpers()
    _install_continue_wrapper()
    _clear_stale_mcp_lock()
    _merge_vscode_port_settings()
    _persist_self()
    helper_url = _start_oauth_helper()
    # mcp-remote talks to the official MCP after tokens exist. Until then (or if
    # the token is 401), the wrapper exposes a stdio setup tool instead of -32000.
    # SSO callback is the public http-8080 helper, not localhost:3334.
    lines += [
        "mcpServers:",
        "  - name: red-hat-security",
        "    command: bash",
        "    args:",
        "      - -lc",
        f"      - {_ys(_mcp_remote_launch())}",
        "    connectionTimeout: 300000",
        "    timeout: 300000",
    ]
    if hub_url and mcp_token:
        lines += [
            "  - name: hub-mcp-actions",
            "    type: streamable-http",
            f"    url: {_ys(hub_url)}",
            "    requestOptions:",
            "      headers:",
            f"        Authorization: {_ys('Bearer ' + mcp_token)}",
        ]

    home_cfg = Path.home() / ".continue"
    home_cfg.mkdir(parents=True, exist_ok=True)
    (home_cfg / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    proj = Path(".continue")
    proj.mkdir(parents=True, exist_ok=True)
    for leftover in (
        home_cfg / "mcpServers" / "red-hat-security.json",
        home_cfg / "mcpServers" / "red-hat-security.yaml",
        proj / "mcpServers" / "red-hat-security.json",
        proj / "mcpServers" / "red-hat-security.yaml",
    ):
        leftover.unlink(missing_ok=True)

    _cleanup_placeholder_mcp()
    _prewarm_mcp_remote()

    (proj / "config.json").write_text(
        "{\n"
        '  "models": [\n'
        '    {"title": "Granite (LiteLLM)", "provider": "openai", "model": "granite",'
        ' "apiBase": "${LITELLM_API_BASE}", "apiKey": "${LITELLM_API_KEY}"},\n'
        '    {"title": "Qwen3 (LiteLLM)", "provider": "openai", "model": "qwen3",'
        ' "apiBase": "${LITELLM_API_BASE}", "apiKey": "${LITELLM_API_KEY}"},\n'
        '    {"title": "LiteMaaS Qwen (LiteLLM)", "provider": "openai", "model": "litemaas-qwen",'
        ' "apiBase": "${LITELLM_API_BASE}", "apiKey": "${LITELLM_API_KEY}"}\n'
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )

    mcp_names = ["red-hat-security (mcp-remote + browser SSO)"]
    if hub_url and mcp_token:
        mcp_names.append("hub-mcp-actions")
    print(
        f"Wrote ~/.continue/config.yaml models={[m[1] for m in models]} "
        f"mcp={mcp_names} language={lang}"
    )
    print("Reload the Che Code window if Continue still shows 'No models configured'.")
    print("MCP tools require Continue Agent or Plan mode (Chat has tools disabled).")
    helper = _oauth_helper_path()
    mcp_ok = False
    if helper.is_file():
        try:
            mcp_ok = (
                subprocess.call(
                    ["python3", str(helper), "--probe-mcp"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                )
                == 0
            )
        except Exception:
            mcp_ok = False
    if mcp_ok:
        print("Red Hat Security MCP: already connected. Use Continue Agent.")
    elif helper_url:
        print(f"Red Hat Security MCP: {helper_url}/")
    else:
        print("Red Hat Security MCP: start the :8080 helper (auth-rh-security-mcp).")
    return 0


if __name__ == "__main__":
    if "--auth-rh-security" in sys.argv:
        sys.exit(auth_rh_security())
    sys.exit(main())
