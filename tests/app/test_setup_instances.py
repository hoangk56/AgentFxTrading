
import pytest
from fastapi.testclient import TestClient

from app.server import app
import app.dashboard as dashboard_module
from app.accounts import get_account_registry
from app.portfolio import get_portfolio_manager
from app.cbot_presets import build_run_command

client = TestClient(app)


class FakeDocker:
    def __init__(self, success=True):
        self.calls = []
        self.success = success
        self.is_available = True

    def start_container(self, name, command):
        self.calls.append((name, command))
        return {"success": self.success, "message": "ok" if self.success else "boom"}


@pytest.fixture
def fake_docker(monkeypatch):
    fake = FakeDocker()
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    return fake


@pytest.fixture
def account(tmp_path, monkeypatch):
    """A fresh demo account 'Setup' (slug demo-setup) with CTRADER_HOME in tmp_path; cleans its bot configs."""
    monkeypatch.setenv("CTRADER_HOME", str(tmp_path))
    reg = get_account_registry()
    with reg._get_connection() as conn:
        conn.execute("DELETE FROM ctrader_accounts")
        conn.execute("DELETE FROM cbot_configs WHERE name LIKE 'cbot-demo-setup-%'")
        conn.commit()
    res = client.post("/api/ctrader-accounts", json={
        "label": "Setup", "ctid_email": "me@example.com", "password": "pw",
        "account_number": "10101649", "account_type": "demo"})
    assert res.status_code == 201, res.text
    acc = res.json()["account"]
    yield acc
    with reg._get_connection() as conn:
        conn.execute("DELETE FROM cbot_configs WHERE name LIKE 'cbot-demo-setup-%'")
        conn.commit()


def _post(account_id, selections, start=True):
    return client.post("/api/setup/instances", json={"account_id": account_id, "selections": selections, "start": start})


def test_presets_endpoint_shape():
    res = client.get("/api/setup/presets")
    assert res.status_code == 200
    data = res.json()
    assert set(data["strategies"]) == {"gotobi", "ecb_f3", "ecb_e1"}
    assert data["strategies"]["gotobi"]["label"] == "Gotobi Fix"
    assert data["symbols"] == ["USDJPY", "EURJPY", "GBPJPY", "EURUSD"]
    assert len(data["cells"]) == 5        # gotobi on 3 JPY pairs, the ECB window's F3 and E1 on EURUSD
    assert {c["symbol"] for c in data["cells"] if c["strategy"] == "gotobi"} == {"USDJPY", "EURJPY", "GBPJPY"}
    assert {c["strategy"] for c in data["cells"] if c["symbol"] == "EURUSD"} == {"ecb_f3", "ecb_e1"}
    assert all(set(c) == {"symbol", "strategy", "period", "session"} for c in data["cells"])


def test_start_saves_config_and_starts_each_new_selection(account, fake_docker, tmp_path):
    res = _post(account["id"], [{"symbol": "USDJPY", "strategy": "gotobi"}, {"symbol": "GBPJPY", "strategy": "gotobi"}])
    assert res.status_code == 200, res.text
    results = res.json()["results"]
    assert [r["status"] for r in results] == ["started", "started"]
    assert [r["name"] for r in results] == ["cbot-demo-setup-usdjpy-fix-gotobi", "cbot-demo-setup-gbpjpy-fix-gotobi"]
    assert results[0]["message"] == "ok"

    row = get_account_registry().get_ctrader_account(account["id"])
    expected = build_run_command(row, "gotobi", "USDJPY", str(dashboard_module.PROJECT_ROOT), str(tmp_path))
    assert fake_docker.calls[0] == ("cbot-demo-setup-usdjpy-fix-gotobi", expected)
    assert len(fake_docker.calls) == 2

    pm = get_portfolio_manager()
    cfg = pm.get_cbot_config("cbot-demo-setup-usdjpy-fix-gotobi")
    assert cfg["run_command"] == expected
    assert cfg["description"] == "Gotobi Fix USDJPY m15 — Setup"
    assert f"-v {tmp_path}:/root" in expected                       # CTRADER_HOME from env
    assert "--pwd-file=/root/ctrader_data/ctid_demo-setup_pwd" in expected
    assert pm.get_cbot_config("cbot-demo-setup-gbpjpy-fix-gotobi")["description"] == "Gotobi Fix GBPJPY m15 — Setup"


def test_save_only_never_calls_docker(account, fake_docker):
    res = _post(account["id"], [{"symbol": "EURJPY", "strategy": "gotobi"}], start=False)
    results = res.json()["results"]
    assert results == [{"symbol": "EURJPY", "strategy": "gotobi", "name": "cbot-demo-setup-eurjpy-fix-gotobi",
                        "status": "saved", "message": "Config saved"}]
    assert fake_docker.calls == []
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-eurjpy-fix-gotobi") is not None


def test_existing_name_is_reported_and_not_started(account, fake_docker):
    first = _post(account["id"], [{"symbol": "GBPJPY", "strategy": "gotobi"}]).json()["results"]
    assert first[0]["status"] == "started"
    second = _post(account["id"], [{"symbol": "GBPJPY", "strategy": "gotobi"}]).json()["results"]
    assert second[0]["status"] == "exists"
    assert second[0]["name"] == "cbot-demo-setup-gbpjpy-fix-gotobi"
    assert len(fake_docker.calls) == 1


def test_unknown_pair_is_error_and_batch_continues(account, fake_docker):
    res = _post(account["id"], [
        {"symbol": "EURUSD", "strategy": "gotobi"},        # pair not in the matrix (EURUSD is the ECB window's)
        {"symbol": "eurjpy", "strategy": "gotobi"},         # symbol case-normalised
        {"symbol": "USDJPY", "strategy": "nope"},
        {"symbol": "BTCUSD", "strategy": "donchian"},       # the removed Crypto Donchian
    ])
    results = res.json()["results"]
    assert results[0]["status"] == "error" and "preset" in results[0]["message"] and results[0]["name"] == ""
    assert results[1]["status"] == "started" and results[1]["symbol"] == "EURJPY"
    assert results[2]["status"] == "error" and results[3]["status"] == "error"
    assert len(fake_docker.calls) == 1


def test_docker_failure_keeps_config_for_retry(account, monkeypatch):
    fake = FakeDocker(success=False)
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    res = _post(account["id"], [{"symbol": "EURJPY", "strategy": "gotobi"}])
    result = res.json()["results"][0]
    assert result["status"] == "error" and result["message"] == "boom"
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-eurjpy-fix-gotobi") is not None


def test_unknown_account_is_404(fake_docker):
    res = _post(999999, [{"symbol": "USDJPY", "strategy": "gotobi"}])
    assert res.status_code == 404
    assert res.json()["success"] is False
    assert fake_docker.calls == []


def test_empty_selection_is_ok(account, fake_docker):
    res = _post(account["id"], [])
    assert res.status_code == 200 and res.json() == {"results": []}


def test_installed_lists_each_saved_cell_with_its_account(account, fake_docker):
    assert client.get("/api/setup/installed").json() == {"installed": []}
    _post(account["id"], [{"symbol": "USDJPY", "strategy": "gotobi"}, {"symbol": "EURJPY", "strategy": "gotobi"}],
          start=False)
    res = client.get("/api/setup/installed")
    assert res.status_code == 200
    assert res.json()["installed"] == [
        {"symbol": "USDJPY", "strategy": "gotobi", "name": "cbot-demo-setup-usdjpy-fix-gotobi",
         "account_id": account["id"], "account_label": "Setup", "account_type": "demo"},
        {"symbol": "EURJPY", "strategy": "gotobi", "name": "cbot-demo-setup-eurjpy-fix-gotobi",
         "account_id": account["id"], "account_label": "Setup", "account_type": "demo"},
    ]
    assert fake_docker.calls == []   # a listing never touches Docker
