#!/usr/bin/env python3
"""DevSpaces helper for Red Hat Security MCP SSO.

UI on :8080 (public Route). OAuth redirect_uri is loopback-only
(http://127.0.0.1:3334/oauth/callback); after SSO, swap that host for the
helper URL (or paste). Tokens go to ~/.mcp-auth for Continue / mcp-remote.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MCP_URL = "https://security-mcp.api.redhat.com/mcp"
PRM_URL = "https://security-mcp.api.redhat.com/.well-known/oauth-protected-resource/mcp"
SCOPE = "api.graphql"
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = int(os.environ.get("RH_SECURITY_OAUTH_PORT", "8080"))
LOOPBACK_PORT = 3334
# mcp-auth DCR echoes any redirect_uri but authorize only allows loopback.
LOOPBACK_REDIRECT = f"http://127.0.0.1:{LOOPBACK_PORT}/oauth/callback"
SESSION_TTL = 900

HOME = Path.home()
AUTH_ROOT = HOME / ".mcp-auth"
SHARE = HOME / ".local" / "share" / "rhdh-agent-sandbox"
SESSION_FILE = AUTH_ROOT / "rh-oauth-session.json"
STATUS_FILE = AUTH_ROOT / "rh-oauth-status.json"


def _b64url(raw: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _pkce() -> tuple[str, str]:
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def mcp_remote_dir() -> Path:
    AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    matches = sorted(AUTH_ROOT.glob("mcp-remote-*"), key=lambda p: p.name)
    if matches:
        return matches[-1]
    path = AUTH_ROOT / "mcp-remote-0.1.37"
    path.mkdir(parents=True, exist_ok=True)
    return path


def token_paths() -> list[Path]:
    hashed = _md5(MCP_URL)
    return [mcp_remote_dir() / f"{hashed}_tokens.json"]


def load_tokens() -> dict | None:
    for path in token_paths():
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and data.get("access_token"):
                return data
    root = AUTH_ROOT
    if not root.is_dir():
        return None
    for path in root.rglob("*tokens.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("access_token"):
            return data
    return None


def save_tokens(tokens: dict, redirect_uri: str) -> Path:
    directory = mcp_remote_dir()
    hashed = _md5(MCP_URL)
    dest = directory / f"{hashed}_tokens.json"
    dest.write_text(json.dumps(tokens), encoding="utf-8")
    dest.chmod(0o600)
    info_path = directory / f"{hashed}_client_info.json"
    info = {}
    if info_path.is_file():
        try:
            loaded = json.loads(info_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                info = loaded
        except json.JSONDecodeError:
            info = {}
    uris = list(info.get("redirect_uris") or [])
    if redirect_uri and redirect_uri not in uris:
        uris.append(redirect_uri)
    info.update(
        {
            "client_id": info.get("client_id") or "mcp-client",
            "redirect_uris": uris or [redirect_uri],
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "client_name": "RHDH Agent Sandbox DevSpaces",
            "scope": SCOPE,
        }
    )
    info_path.write_text(json.dumps(info), encoding="utf-8")
    return dest


def clear_tokens() -> None:
    if not AUTH_ROOT.is_dir():
        return
    for path in AUTH_ROOT.rglob("*tokens.json"):
        path.unlink(missing_ok=True)


def remember_public_base(url: str) -> None:
    url = (url or "").strip().rstrip("/")
    if not url or "code-redirect" in url or "127.0.0.1" in url or "localhost" in url:
        return
    AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        (AUTH_ROOT / "rh-oauth-public-base.txt").write_text(url + "\n", encoding="utf-8")
    except OSError:
        pass


def public_base_from_headers(headers) -> str:
    host = (headers.get("X-Forwarded-Host") or headers.get("Host") or "").split(",")[0].strip()
    proto = (headers.get("X-Forwarded-Proto") or "http").split(",")[0].strip()
    if host and "code-redirect" not in host and "127.0.0.1" not in host:
        url = f"{proto}://{host}"
        remember_public_base(url)
        return url
    return discover_public_base()


def discover_public_base() -> str:
    env = (os.environ.get("RH_SECURITY_OAUTH_PUBLIC_BASE") or "").strip().rstrip("/")
    if env:
        return env
    marker = AUTH_ROOT / "rh-oauth-public-base.txt"
    if marker.is_file():
        saved = marker.read_text(encoding="utf-8").strip().rstrip("/")
        if saved:
            return saved
    dw_name = os.environ.get("DEVWORKSPACE_NAME") or ""
    ns = os.environ.get("DEVWORKSPACE_NAMESPACE") or ""
    dash = (os.environ.get("CHE_DASHBOARD_URL") or "").strip()
    apps = ""
    if dash:
        host = urllib.parse.urlparse(dash).hostname or ""
        if host.startswith("devspaces."):
            apps = host[len("devspaces.") :]
        elif ".apps." in host:
            apps = host[host.index("apps.") :]
    if dw_name and apps:
        user = ns[:-4] if ns.endswith("-dev") else (ns or dw_name)
        return f"https://{user}-{dw_name}-http-8080.{apps}"
    return ""


def _json_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def oauth_meta() -> dict:
    prm = _json_get(PRM_URL)
    resource = prm.get("resource") or MCP_URL
    servers = prm.get("authorization_servers") or ["https://mcp-auth.api.redhat.com"]
    issuer = str(servers[0]).rstrip("/")
    as_meta = _json_get(f"{issuer}/.well-known/oauth-authorization-server")
    return {
        "resource": resource,
        "issuer": issuer,
        "authorize": as_meta.get("authorization_endpoint") or f"{issuer}/authorize",
        "token": as_meta.get("token_endpoint") or f"{issuer}/token",
        "register": as_meta.get("registration_endpoint") or f"{issuer}/register",
    }


def register_client(meta: dict) -> str:
    body = json.dumps(
        {
            "client_name": "MCP CLI Proxy",
            "redirect_uris": [
                LOOPBACK_REDIRECT,
                f"http://localhost:{LOOPBACK_PORT}/oauth/callback",
            ],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
            "scope": SCOPE,
            "application_type": "native",
        }
    ).encode()
    req = urllib.request.Request(
        meta["register"],
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data.get("client_id") or "mcp-client"
    except urllib.error.HTTPError:
        return "mcp-client"


def token_request(url: str, fields: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(fields).encode(),
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"token HTTP {exc.code}: {detail}") from exc


def probe_mcp(access_token: str | None = None) -> dict:
    token = access_token
    if not token:
        stored = load_tokens()
        token = (stored or {}).get("access_token")
    if not token:
        return {"ok": False, "reason": "no-tokens", "http": 0}
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "rhdh-agent-sandbox", "version": "0.1.0"},
            },
        }
    ).encode()
    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2024-11-05",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:400]
            return {"ok": True, "reason": "ok", "http": resp.status, "preview": body}
    except urllib.error.HTTPError as exc:
        www = exc.headers.get("WWW-Authenticate", "") if exc.headers else ""
        return {
            "ok": False,
            "reason": "mcp-401" if exc.code == 401 else f"http-{exc.code}",
            "http": exc.code,
            "www": www[:300],
        }
    except Exception as exc:
        return {"ok": False, "reason": "error", "http": 0, "error": str(exc)[:200]}


def write_status(payload: dict) -> None:
    AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(payload), encoding="utf-8")


def current_status() -> dict:
    tokens = load_tokens()
    probe = probe_mcp((tokens or {}).get("access_token")) if tokens else {
        "ok": False,
        "reason": "no-tokens",
        "http": 0,
    }
    extra = {}
    if STATUS_FILE.is_file():
        try:
            extra = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            extra = {}
    return {
        "tokens": bool(tokens),
        "scope": (tokens or {}).get("scope", ""),
        "mcp": probe,
        "public_base": discover_public_base(),
        "last": extra,
    }


def load_session() -> dict:
    if not SESSION_FILE.is_file():
        return {}
    try:
        data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if time.time() - float(data.get("created") or 0) > SESSION_TTL:
        SESSION_FILE.unlink(missing_ok=True)
        return {}
    return data if isinstance(data, dict) else {}


def save_session(data: dict) -> None:
    AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data), encoding="utf-8")
    SESSION_FILE.chmod(0o600)


CSS = """
    :root { --rh:#c9190b; --ink:#151515; --muted:#6a6e73; --bg:#f0f0f0; --card:#fff; --ok:#3e8635; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: RedHatText, "Noto Sans", Helvetica, Arial, sans-serif; background:var(--bg); color:var(--ink); }
    header { background:var(--ink); color:#fff; padding:1rem 1.5rem; }
    header span { color:#c7c7c7; font-size:.9rem; }
    main { max-width: 36rem; margin: 1.5rem auto; padding: 0 1rem 2rem; }
    .card { background:var(--card); border-radius:8px; padding:1.25rem 1.4rem; box-shadow:0 2px 6px rgba(0,0,0,.08); }
    h1 { font-size:1.3rem; margin:0 0 .5rem; }
    p { line-height:1.45; color:#3c3f42; }
    .pill { display:inline-block; border-radius:999px; padding:.25rem .7rem; font-size:.8rem; font-weight:600; background:#e9f7e6; color:var(--ok); }
    a.btn, button { display:inline-block; background:var(--rh); color:#fff; border:0; border-radius:4px; padding:.7rem 1.15rem; font-size:1rem; font-weight:600; text-decoration:none; cursor:pointer; }
    a.btn.secondary, button.secondary { background:#fff; color:var(--ink); border:1px solid #d2d2d2; }
    .row { display:flex; gap:.6rem; flex-wrap:wrap; margin-top:1rem; }
    pre { background:#f5f5f5; padding:.6rem .7rem; border-radius:4px; overflow:auto; font-size:.85rem; }
    .note { font-size:.85rem; color:var(--muted); margin-top:1rem; }
    .err { background:#faeae8; padding:.75rem; border-radius:4px; color:#7d1007; }
    details { margin-top:1rem; color:#3c3f42; }
    input[type=text] { width:100%; padding:.55rem .65rem; border:1px solid #d2d2d2; border-radius:4px; font:inherit; margin:.35rem 0; }
"""

PAGE_OK = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Red Hat Security MCP</title><style>__CSS__</style></head>
<body>
  <header><strong>Red Hat Security MCP</strong><br/><span>DevSpaces</span></header>
  <main><div class="card">
    <h1>Listo</h1>
    <p><span class="pill">conectado</span></p>
    __MESSAGE__
    <p>En Continue usá modo <strong>Agent</strong> y preguntá por un CVE. Las 7 tools ya están. El triángulo amarillo o <em>Finish Setup</em> de Continue no hace falta.</p>
    <p class="note">No vuelvas a pegar URLs. El token se refresca solo.</p>
    <div class="row"><a class="btn secondary" href="/login">Volver a conectar</a></div>
  </div></main>
</body></html>
"""

PAGE_SETUP = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Red Hat Security MCP</title><style>__CSS__</style></head>
<body>
  <header><strong>Red Hat Security MCP</strong><br/><span>DevSpaces</span></header>
  <main><div class="card">
    <h1>Conectar</h1>
    __MESSAGE__
    <p>Un botón. Después, en la barra de direcciones, reemplazá <code>http://127.0.0.1:3334</code> por este host y Enter:</p>
    <pre id="host">__PUBLIC__</pre>
    <div class="row">
      <a class="btn" href="/login">Conectar con Red Hat</a>
      <button type="button" class="secondary" id="copy">Copiar host</button>
    </div>
    <details>
      <summary>O pegá la URL de 127.0.0.1 (Ctrl+V en esta página)</summary>
      <form id="pasteform" method="POST" action="/paste">
        <input id="url" name="url" type="text" autocomplete="off" placeholder="http://127.0.0.1:3334/oauth/callback?code=..."/>
        <button type="submit">Canjear</button>
      </form>
    </details>
  </div></main>
  <script>
    const host = document.getElementById('host');
    document.getElementById('copy').onclick = () => navigator.clipboard.writeText(host.textContent.trim());
    document.addEventListener('paste', (e) => {
      const t = (e.clipboardData && e.clipboardData.getData('text')) || '';
      if (!t.includes('code=')) return;
      e.preventDefault();
      document.getElementById('url').value = t.trim();
      document.getElementById('pasteform').submit();
    });
  </script>
</body></html>
"""

PAGE_LOGIN = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Red Hat Security MCP</title><style>__CSS__</style></head>
<body>
  <header><strong>Red Hat Security MCP</strong><br/><span>DevSpaces</span></header>
  <main><div class="card">
    <h1>Siguiente</h1>
    <p>1. Copiá este host:</p>
    <pre id="host">__PUBLIC__</pre>
    <p>2. Abrí Red Hat, otorgá acceso.</p>
    <p>3. La barra va a <code>http://127.0.0.1:3334/oauth/callback?code=...</code>. Reemplazá solo <code>http://127.0.0.1:3334</code> por el host copiado y Enter.</p>
    <div class="row">
      <button type="button" class="secondary" id="copy">Copiar host</button>
      <a class="btn" href="__AUTH__">Ir a Red Hat</a>
    </div>
  </div></main>
  <script>
    const host = document.getElementById('host').textContent.trim();
    document.getElementById('copy').onclick = () => navigator.clipboard.writeText(host);
  </script>
</body></html>
"""


def _html_shell(template: str, **repl) -> str:
    html = template.replace("__CSS__", CSS)
    for key, value in repl.items():
        html = html.replace(f"__{key}__", value)
    return html


def render_page(message_html: str = "", public: str | None = None) -> str:
    st = current_status()
    public = (public or st.get("public_base") or discover_public_base() or "").rstrip("/")
    mcp_ok = bool((st.get("mcp") or {}).get("ok"))
    if mcp_ok:
        if not message_html:
            message_html = "<p>Token válido contra el MCP oficial.</p>"
        return _html_shell(PAGE_OK, MESSAGE=message_html)
    if not message_html:
        message_html = ""
    return _html_shell(PAGE_SETUP, MESSAGE=message_html, PUBLIC=html_escape(public))


class Handler(BaseHTTPRequestHandler):
    server_version = "rh-security-oauth/0.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        public = public_base_from_headers(self.headers)
        try:
            if path in ("/", "/index.html"):
                self._send(200, render_page(public=public))
                return
            if path == "/api/status":
                self._send(200, json.dumps(current_status()), "application/json")
                return
            if path == "/login":
                self._login()
                return
            if path == "/logout":
                clear_tokens()
                write_status({"event": "logout"})
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            if path == "/oauth/callback":
                self._callback(qs)
                return
            if path == "/paste":
                self._paste((qs.get("url") or [""])[0])
                return
            if path == "/health":
                self._send(200, json.dumps({"ok": True}), "application/json")
                return
            self._send(404, render_page('<p class="err">Not found.</p>'))
        except Exception as exc:
            self._send(500, render_page(f'<p class="err">{html_escape(str(exc))}</p>'))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/paste":
            self._send(404, render_page('<p class="err">Not found.</p>'))
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        fields = urllib.parse.parse_qs(raw)
        self._paste((fields.get("url") or [""])[0])

    def _login(self) -> None:
        meta = oauth_meta()
        client_id = register_client(meta)
        verifier, challenge = _pkce()
        state = secrets.token_urlsafe(24)
        save_session(
            {
                "created": time.time(),
                "verifier": verifier,
                "state": state,
                "redirect_uri": LOOPBACK_REDIRECT,
                "client_id": client_id,
                "token": meta["token"],
                "resource": meta["resource"],
            }
        )
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": LOOPBACK_REDIRECT,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "scope": SCOPE,
            "resource": meta["resource"],
        }
        loc = meta["authorize"] + "?" + urllib.parse.urlencode(params)
        public = public_base_from_headers(self.headers)
        self._send(
            200,
            _html_shell(
                PAGE_LOGIN,
                PUBLIC=html_escape(public),
                AUTH=html_escape(loc),
            ),
        )

    def _paste(self, raw: str) -> None:
        raw = (raw or "").strip().strip("'\"")
        if not raw:
            self._send(400, render_page('<p class="err">Pegá la URL completa con <code>?code=</code>.</p>'))
            return
        parsed = urllib.parse.urlparse(raw)
        qs = urllib.parse.parse_qs(parsed.query)
        if "code" not in qs and parsed.fragment:
            qs = urllib.parse.parse_qs(parsed.fragment)
        self._callback(qs)

    def _callback(self, qs: dict[str, list[str]]) -> None:
        err = (qs.get("error") or [""])[0]
        if err:
            desc = (qs.get("error_description") or [err])[0]
            self._send(400, render_page(f'<p class="err">SSO error: {html_escape(desc)}</p>'))
            return
        code = (qs.get("code") or [""])[0]
        state = (qs.get("state") or [""])[0]
        session = load_session()
        if not code:
            self._send(400, render_page('<p class="err">Callback sin <code>code</code>.</p>'))
            return
        if not session or session.get("state") != state:
            self._send(
                400,
                render_page(
                    '<p class="err">State inválido o sesión vencida. Pulsá '
                    "<strong>Conectar con Red Hat</strong> otra vez y pegá la URL nueva.</p>"
                ),
            )
            return
        fields = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": session["redirect_uri"],
            "client_id": session["client_id"],
            "code_verifier": session["verifier"],
            "resource": session.get("resource") or MCP_URL,
        }
        tokens = token_request(session["token"], fields)
        if not tokens.get("access_token"):
            self._send(500, render_page('<p class="err">El token endpoint no devolvió access_token.</p>'))
            return
        save_tokens(tokens, session["redirect_uri"])
        SESSION_FILE.unlink(missing_ok=True)
        probe = probe_mcp(tokens.get("access_token"))
        write_status({"event": "login", "scope": tokens.get("scope", ""), "mcp": probe})
        if probe.get("ok"):
            msg = "<p>Listo. Continue → modo Agent → preguntá por un CVE.</p>"
        else:
            msg = (
                '<p class="err">Tokens guardados, pero initialize al MCP devolvió '
                f"{html_escape(str(probe.get('http')))} ({html_escape(str(probe.get('reason')))}). "
                "Continue puede mostrar la tool de setup en vez de CVE hasta que el token "
                "incluya <code>api.graphql</code>.</p>"
            )
        self._send(200, render_page(msg))


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def serve() -> int:
    import threading

    SHARE.mkdir(parents=True, exist_ok=True)
    AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    public = discover_public_base() or f"http://127.0.0.1:{LISTEN_PORT}"
    httpd = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    try:
        loopback = ThreadingHTTPServer(("127.0.0.1", LOOPBACK_PORT), Handler)
        threading.Thread(target=loopback.serve_forever, daemon=True).start()
        print(f"Also listening on 127.0.0.1:{LOOPBACK_PORT} for OAuth callback", flush=True)
    except OSError as exc:
        print(f"Port {LOOPBACK_PORT} busy ({exc}); paste the callback URL into the helper.", flush=True)
    print(f"Red Hat Security SSO helper on :{LISTEN_PORT} and 127.0.0.1:{LOOPBACK_PORT}", flush=True)
    print(f"Open helper UI: {public}/", flush=True)
    print(f"OAuth redirect_uri (mcp-client allowlist): {LOOPBACK_REDIRECT}", flush=True)
    httpd.serve_forever()
    return 0


def _stdio_read() -> dict | None:
    first = sys.stdin.buffer.readline()
    if not first:
        return None
    if first.lstrip().startswith(b"{"):
        return json.loads(first)
    headers: dict[str, str] = {}
    line = first
    while line not in (b"\r\n", b"\n", b""):
        if b":" in line:
            key, value = line.decode("ascii", errors="replace").split(":", 1)
            headers[key.strip().lower()] = value.strip()
        line = sys.stdin.buffer.readline()
        if not line:
            return None
    size = int(headers.get("content-length") or 0)
    body = sys.stdin.buffer.read(size) if size else b"{}"
    return json.loads(body)


def _stdio_write(msg: dict) -> None:
    data = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(data)}\r\n\r\n".encode("ascii") + data)
    sys.stdout.buffer.flush()


def stdio_bridge() -> int:
    public = discover_public_base() or f"http://127.0.0.1:{LISTEN_PORT}"
    st = current_status()
    if (st.get("mcp") or {}).get("ok"):
        reason = "ok"
    elif st.get("tokens"):
        reason = (st.get("mcp") or {}).get("reason") or "mcp-401"
    else:
        reason = "no-tokens"
    tool_text = (
        f"Red Hat Security MCP needs a one-time SSO ({reason}).\n"
        f"Open {public}/ — if already connected, use Continue Agent and ask about a CVE."
    )
    tool = {
        "name": "redhat_security_connect",
        "description": "How to finish Red Hat Customer Portal SSO for this DevSpaces workspace.",
        "inputSchema": {"type": "object", "properties": {}},
    }
    while True:
        try:
            req = _stdio_read()
        except json.JSONDecodeError:
            continue
        if req is None:
            return 0
        method = req.get("method")
        req_id = req.get("id")
        if method == "initialize":
            ver = (req.get("params") or {}).get("protocolVersion") or "2024-11-05"
            _stdio_write(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": ver,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "red-hat-security-setup", "version": "0.1.0"},
                    },
                }
            )
        elif method in ("notifications/initialized", "initialized", "notifications/cancelled"):
            continue
        elif method == "ping":
            _stdio_write({"jsonrpc": "2.0", "id": req_id, "result": {}})
        elif method == "tools/list":
            _stdio_write({"jsonrpc": "2.0", "id": req_id, "result": {"tools": [tool]}})
        elif method == "resources/list":
            _stdio_write({"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}})
        elif method == "prompts/list":
            _stdio_write({"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}})
        elif method == "tools/call":
            _stdio_write(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": tool_text}],
                        "isError": False,
                    },
                }
            )
        elif req_id is not None:
            _stdio_write(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown method {method}"},
                }
            )
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--public-url" in args:
        print(discover_public_base() or f"http://127.0.0.1:{LISTEN_PORT}")
        return 0
    if "--probe-mcp" in args:
        probe = probe_mcp()
        print(json.dumps(probe))
        return 0 if probe.get("ok") else 1
    if "--stdio-bridge" in args:
        return stdio_bridge()
    if "--status" in args:
        print(json.dumps(current_status(), indent=2))
        return 0
    return serve()


if __name__ == "__main__":
    sys.exit(main())
