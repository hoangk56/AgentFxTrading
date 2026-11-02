"""Dashboard login (app/auth.py): a session cookie for everything that comes through nginx, nothing for the cBots'
direct calls to 127.0.0.1:8000, and no login at all while DASHBOARD_USERNAME / DASHBOARD_PASSWORD are unset."""
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app import auth
from app.server import app

CREDS = ("admin", "s3cret pass")
PROXIED = {"X-Real-IP": "203.0.113.9", "X-Forwarded-For": "203.0.113.9"}


@pytest.fixture
def login_on(monkeypatch, tmp_path):
    monkeypatch.setenv("DASHBOARD_USERNAME", CREDS[0])
    monkeypatch.setenv("DASHBOARD_PASSWORD", CREDS[1])
    monkeypatch.setattr(auth, "SECRET_FILE", tmp_path / "session_secret")
    monkeypatch.setattr(auth, "_secret", None)
    monkeypatch.setattr(auth, "_failures", {})


def _client(**kw):
    return TestClient(app, follow_redirects=False, **kw)


def _login(client, username=CREDS[0], password=CREDS[1], next_path="/"):
    return client.post("/login", data={"username": username, "password": password, "next": next_path})


def test_without_credentials_there_is_no_login():
    client = _client()
    assert client.get("/api/watchdog/status").status_code == 200
    assert client.get("/login?next=/static/js/auth.js").headers["location"] == "/static/js/auth.js"
    assert "Logout" not in client.get("/").text


def test_a_page_redirects_to_the_login_and_the_api_answers_401(login_on):
    client = _client()
    res = client.get("/?x=1")
    assert res.status_code == 303 and res.headers["location"] == "/login?next=%2F%3Fx%3D1"
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 401 and res.headers["X-Login-Required"] == "1"
    assert client.post("/api/ledger/movements", json={}).status_code == 401
    page = client.get("/login?next=/%3Fx%3D1")
    assert page.status_code == 200 and 'name="password"' in page.text and 'value="/?x=1"' in page.text
    assert client.get("/static/js/auth.js").status_code == 200


def test_the_right_password_opens_a_session(login_on):
    client = _client(base_url="https://testserver")
    res = _login(client, username='adm"in<', password="wrong")
    assert res.status_code == 401 and "Sai tên đăng nhập hoặc mật khẩu" in res.text
    assert 'value="adm&#34;in&lt;"' in res.text                  # kept for the next try, escaped
    res = _login(client)
    assert res.status_code == 303 and res.headers["location"] == "/"
    cookie = res.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie and "secure" in cookie and "max-age=2592000" in cookie
    assert client.get("/api/dashboard/summary").status_code == 200
    page = client.get("/")
    assert page.status_code == 200 and 'action="/logout"' in page.text
    assert client.get("/login?next=/%3Fx%3D1").headers["location"] == "/?x=1"

    res = client.post("/logout")
    assert res.status_code == 303 and res.headers["location"] == "/login"
    assert client.get("/api/dashboard/summary").status_code == 401


def test_the_cookie_is_not_secure_only_over_plain_http(login_on):
    cookie = _login(_client()).headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" not in cookie


def test_cbots_calling_the_loopback_directly_need_no_login_but_nginx_traffic_does(login_on):
    local = _client(client=("127.0.0.1", 40000))
    assert local.get("/api/watchdog/status").status_code == 200
    assert local.get("/api/cbot/commands?bot_id=cbot-x").status_code != 401
    assert local.get("/api/watchdog/status", headers=PROXIED).status_code == 401
    assert local.get("/api/watchdog/status", headers={"X-Forwarded-For": "1.2.3.4"}).status_code == 401
    assert _client(client=("::1", 40000)).get("/api/watchdog/status").status_code == 200
    assert _client(client=("10.0.0.5", 40000)).get("/api/watchdog/status").status_code == 401


def test_the_dashboard_websocket_needs_the_session(login_on):
    client = _client()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/ws/dashboard"):
            pass
    assert e.value.code == 1008
    _login(client)
    with client.websocket_connect("/ws/dashboard"):
        pass


@pytest.mark.parametrize("target, landing", [
    ("//evil.example/x", "/"),
    ("https://evil.example/", "/"),
    ("/\\evil.example", "/"),
    ("/login?next=/login", "/"),
    ("/#ledger", "/#ledger"),
])
def test_the_login_only_returns_to_this_site(login_on, target, landing):
    assert _login(_client(), next_path=target).headers["location"] == landing


def test_repeated_failures_lock_the_ip_out(login_on):
    client = _client()
    for _ in range(auth.MAX_FAILURES):
        assert _login(client, password="nope").status_code == 401
    res = _login(client)
    assert res.status_code == 429 and "set-cookie" not in res.headers
    assert _login(_client(client=("198.51.100.7", 1))).status_code == 303       # another IP is not locked


def test_a_session_ends_when_it_expires_or_the_password_changes(login_on, monkeypatch):
    token = auth.make_token(CREDS, now=1_000_000)
    assert auth.token_valid(token, CREDS, now=1_000_000 + auth.SESSION_SECONDS - 1)
    assert not auth.token_valid(token, CREDS, now=1_000_000 + auth.SESSION_SECONDS)
    assert not auth.token_valid(token, (CREDS[0], "new password"), now=1_000_000)
    for forged in ("", "abc", "9999999999.", "9999999999." + "0" * 64, token.split(".")[0] + ".x"):
        assert not auth.token_valid(forged, CREDS, now=1_000_000)

    client = _client()
    _login(client)
    assert client.get("/api/dashboard/summary").status_code == 200
    monkeypatch.setenv("DASHBOARD_PASSWORD", "new password")
    assert client.get("/api/dashboard/summary").status_code == 401


def test_the_session_secret_is_created_once_and_private(login_on):
    first = auth._server_secret()
    assert auth.SECRET_FILE.read_bytes() == first and len(first) == 64
    assert auth.SECRET_FILE.stat().st_mode & 0o077 == 0
    auth._secret = None
    assert auth._server_secret() == first
