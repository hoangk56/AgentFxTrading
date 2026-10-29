"""Dashboard login: one user whose name and password come from .env (DASHBOARD_USERNAME, DASHBOARD_PASSWORD).

Every HTTP request and WebSocket needs a session cookie, except:
- requests made straight to the server on the loopback interface: the cBots (--network host, 127.0.0.1:8000) and
  local scripts. nginx sets X-Real-IP and X-Forwarded-For on everything it proxies, so a loopback request that
  carries either one came from the internet and needs the login;
- the login page and /static (CSS, JS, favicon: nothing private).
With either variable unset the login is off (local runs, tests) and the server says so in its log at start.

The cookie is `<expiry>.<HMAC-SHA256>`, keyed with a random secret kept in webui_data/session_secret plus the username
and password, so changing either one logs every browser out. Failed logins are throttled per client IP (the real
one: uvicorn reads it from X-Forwarded-For, which nginx fills from Cloudflare's).
"""
import hashlib
import hmac
import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import cookie_parser
from starlette.websockets import WebSocketClose

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECRET_FILE = PROJECT_ROOT / "webui_data" / "session_secret"
COOKIE = "agentfx_session"
SESSION_SECONDS = 30 * 24 * 3600
MAX_FAILURES = 5                 # failed logins per client IP ...
FAILURE_WINDOW = 15 * 60         # ... within this many seconds lock that IP out for the rest of the window
PROXY_HEADERS = (b"x-forwarded-for", b"x-real-ip", b"forwarded")
LOOPBACK = ("127.0.0.1", "::1")
PUBLIC_PATHS = ("/login", "/logout", "/favicon.ico")

router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

_secret: Optional[bytes] = None
_secret_lock = threading.Lock()
_failures: Dict[str, List[float]] = {}


def credentials() -> Optional[Tuple[str, str]]:
    """(username, password) from the environment, or None when the login is off."""
    user, password = os.environ.get("DASHBOARD_USERNAME", ""), os.environ.get("DASHBOARD_PASSWORD", "")
    return (user, password) if user and password else None


def login_enabled() -> bool:
    return credentials() is not None


def _server_secret() -> bytes:
    """The random secret of this installation, created on first use. If it cannot be stored, sessions last until
    the next restart."""
    global _secret
    with _secret_lock:
        if _secret is None:
            try:
                _secret = SECRET_FILE.read_bytes().strip()
            except FileNotFoundError:
                _secret = secrets.token_hex(32).encode()
                try:
                    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
                    fd = os.open(SECRET_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, "wb") as f:
                        f.write(_secret)
                except OSError as e:
                    logger.warning(f"Could not store the session secret in {SECRET_FILE} ({e}): logins end at restart")
        return _secret


def _key(creds: Tuple[str, str]) -> bytes:
    return hmac.new(_server_secret(), f"{creds[0]}\0{creds[1]}".encode(), hashlib.sha256).digest()


def make_token(creds: Tuple[str, str], now: Optional[float] = None) -> str:
    expiry = str(int((now if now is not None else time.time()) + SESSION_SECONDS))
    return f"{expiry}.{hmac.new(_key(creds), expiry.encode(), hashlib.sha256).hexdigest()}"


def token_valid(token: Optional[str], creds: Tuple[str, str], now: Optional[float] = None) -> bool:
    expiry, _, signature = (token or "").partition(".")
    if not expiry.isdigit() or int(expiry) <= (now if now is not None else time.time()):
        return False
    expected = hmac.new(_key(creds), expiry.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _header(scope, name: bytes) -> Optional[str]:
    for key, value in scope.get("headers") or ():
        if key == name:
            return value.decode("latin-1")
    return None


def is_direct_local(scope) -> bool:
    """A request to 127.0.0.1:8000 that did not come through nginx: a cBot or a local script."""
    client = scope.get("client")
    if not client or client[0] not in LOOPBACK:
        return False
    return not any(key in PROXY_HEADERS for key, _ in scope.get("headers") or ())


def _is_public(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith("/static/")


def request_allowed(scope) -> bool:
    creds = credentials()
    if creds is None or _is_public(scope.get("path", "")) or is_direct_local(scope):
        return True
    token = cookie_parser(_header(scope, b"cookie") or "").get(COOKIE)
    return token_valid(token, creds)


def safe_next(target: Optional[str]) -> str:
    """Where to go after the login: a path on this site, never another host or the login page itself."""
    if not target or not target.startswith("/") or target.startswith(("//", "/\\")) or target.startswith("/login"):
        return "/"
    return target


class LoginMiddleware:
    """Pure ASGI, so it covers the WebSocket handshake too."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket") or request_allowed(scope):
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await WebSocketClose(code=1008)(scope, receive, send)
            return
        path = scope.get("path", "")
        if scope.get("method") == "GET" and not path.startswith(("/api/", "/portfolio/")):
            query = scope.get("query_string", b"").decode("latin-1")
            target = path + (f"?{query}" if query else "")
            response = RedirectResponse(f"/login?next={quote(target, safe='')}", status_code=303)
        else:
            response = JSONResponse({"detail": "Login required"}, status_code=401, headers={"X-Login-Required": "1"})
        await response(scope, receive, send)


# ---------- rate limit ----------

def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "?"


def _locked(ip: str, now: float) -> bool:
    recent = [t for t in _failures.get(ip, []) if now - t < FAILURE_WINDOW]
    if recent:
        _failures[ip] = recent
    else:
        _failures.pop(ip, None)
    return len(recent) >= MAX_FAILURES


# ---------- routes ----------

def _page(request: Request, next_path: str, error: Optional[str] = None, status_code: int = 200, username: str = ""):
    return templates.TemplateResponse(request=request, name="login.html", status_code=status_code,
                                      context={"next": next_path, "error": error, "username": username},
                                      headers={"Cache-Control": "no-store"})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    target = safe_next(next)
    if not login_enabled() or request_allowed({**request.scope, "path": target}):
        return RedirectResponse(target, status_code=303)
    return _page(request, target)


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    creds = credentials()
    if creds is None:
        return RedirectResponse("/", status_code=303)
    form = parse_qs((await request.body()).decode("utf-8", "replace"))
    username = (form.get("username") or [""])[0]
    password = (form.get("password") or [""])[0]
    target = safe_next((form.get("next") or ["/"])[0])
    ip, now = _client_ip(request), time.time()
    if _locked(ip, now):
        logger.warning(f"Dashboard login refused: {ip} is locked out after {MAX_FAILURES} failures")
        return _page(request, target, "Sai quá nhiều lần. Thử lại sau 15 phút.", 429, username)
    # compare both, always: the time taken says nothing about which one was wrong
    user_ok = hmac.compare_digest(username.encode(), creds[0].encode())
    password_ok = hmac.compare_digest(password.encode(), creds[1].encode())
    if not (user_ok and password_ok):
        _failures.setdefault(ip, []).append(now)
        logger.warning(f"Dashboard login failed from {ip}")
        return _page(request, target, "Sai tên đăng nhập hoặc mật khẩu.", 401, username)
    _failures.pop(ip, None)
    logger.info(f"Dashboard login from {ip}")
    response = RedirectResponse(target, status_code=303)
    response.set_cookie(COOKIE, make_token(creds, now), max_age=SESSION_SECONDS, path="/", httponly=True,
                        samesite="lax", secure=request.url.scheme == "https")
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE, path="/")
    return response
