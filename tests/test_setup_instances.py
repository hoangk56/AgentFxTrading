import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

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
    assert set(data["strategies"]) == {"tms_orb", "judas", "flowrsi"}
    assert data["strategies"]["judas"]["label"] == "Judas Sweep"
    assert len(data["symbols"]) == 15
    assert len(data["cells"]) == 45
    assert all(set(c) == {"symbol", "strategy", "period", "session"} for c in data["cells"])


def test_start_saves_config_and_starts_each_new_selection(account, fake_docker, tmp_path):
    res = _post(account["id"], [{"symbol": "XAUUSD", "strategy": "tms_orb"}, {"symbol": "GBPUSD", "strategy": "judas"}])
    assert res.status_code == 200, res.text
    results = res.json()["results"]
    assert [r["status"] for r in results] == ["started", "started"]
    assert [r["name"] for r in results] == ["cbot-demo-setup-xauusd-newyork", "cbot-demo-setup-gbpusd-KZ-london-ny-judas"]
    assert results[0]["message"] == "ok"

    row = get_account_registry().get_ctrader_account(account["id"])
    expected = build_run_command(row, "tms_orb", "XAUUSD", str(dashboard_module.PROJECT_ROOT), str(tmp_path))
    assert fake_docker.calls[0] == ("cbot-demo-setup-xauusd-newyork", expected)
    assert len(fake_docker.calls) == 2

    pm = get_portfolio_manager()
    cfg = pm.get_cbot_config("cbot-demo-setup-xauusd-newyork")
    assert cfg["run_command"] == expected
    assert cfg["description"] == "TMS+ORB XAUUSD m15 — Setup"
    assert f"-v {tmp_path}:/root" in expected                       # CTRADER_HOME from env
    assert "--pwd-file=/root/ctrader_data/ctid_demo-setup_pwd" in expected
    assert pm.get_cbot_config("cbot-demo-setup-gbpusd-KZ-london-ny-judas")["description"] == "Judas Sweep GBPUSD m15 — Setup"


def test_save_only_never_calls_docker(account, fake_docker):
    res = _post(account["id"], [{"symbol": "EURUSD", "strategy": "flowrsi"}], start=False)
    results = res.json()["results"]
    assert results == [{"symbol": "EURUSD", "strategy": "flowrsi", "name": "cbot-demo-setup-eurusd-all-flowrsi",
                        "status": "saved", "message": "Config saved"}]
    assert fake_docker.calls == []
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-eurusd-all-flowrsi") is not None


def test_existing_name_is_reported_and_not_started(account, fake_docker):
    first = _post(account["id"], [{"symbol": "US30", "strategy": "tms_orb"}]).json()["results"]
    assert first[0]["status"] == "started"
    second = _post(account["id"], [{"symbol": "US30", "strategy": "tms_orb"}]).json()["results"]
    assert second[0]["status"] == "exists"
    assert second[0]["name"] == "cbot-demo-setup-us30-newyork"
    assert len(fake_docker.calls) == 1


def test_unknown_pair_is_error_and_batch_continues(account, fake_docker):
    res = _post(account["id"], [
        {"symbol": "NZDUSD", "strategy": "tms_orb"},       # symbol not in the matrix
        {"symbol": "eurusd", "strategy": "flowrsi"},        # symbol case-normalised
        {"symbol": "XAUUSD", "strategy": "nope"},
    ])
    results = res.json()["results"]
    assert results[0]["status"] == "error" and "preset" in results[0]["message"] and results[0]["name"] == ""
    assert results[1]["status"] == "started" and results[1]["symbol"] == "EURUSD"
    assert results[2]["status"] == "error"
    assert len(fake_docker.calls) == 1


def test_docker_failure_keeps_config_for_retry(account, monkeypatch):
    fake = FakeDocker(success=False)
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    res = _post(account["id"], [{"symbol": "DE40", "strategy": "tms_orb"}])
    result = res.json()["results"][0]
    assert result["status"] == "error" and result["message"] == "boom"
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-de40-london") is not None


def test_unknown_account_is_404(fake_docker):
    res = _post(999999, [{"symbol": "XAUUSD", "strategy": "tms_orb"}])
    assert res.status_code == 404
    assert res.json()["success"] is False
    assert fake_docker.calls == []


def test_empty_selection_is_ok(account, fake_docker):
    res = _post(account["id"], [])
    assert res.status_code == 200 and res.json() == {"results": []}


def test_installed_lists_each_saved_cell_with_its_account(account, fake_docker):
    assert client.get("/api/setup/installed").json() == {"installed": []}
    _post(account["id"], [{"symbol": "XAUUSD", "strategy": "tms_orb"}, {"symbol": "EURUSD", "strategy": "flowrsi"}], start=False)
    res = client.get("/api/setup/installed")
    assert res.status_code == 200
    assert res.json()["installed"] == [
        {"symbol": "XAUUSD", "strategy": "tms_orb", "name": "cbot-demo-setup-xauusd-newyork",
         "account_id": account["id"], "account_label": "Setup", "account_type": "demo"},
        {"symbol": "EURUSD", "strategy": "flowrsi", "name": "cbot-demo-setup-eurusd-all-flowrsi",
         "account_id": account["id"], "account_label": "Setup", "account_type": "demo"},
    ]
    assert fake_docker.calls == []   # a listing never touches Docker
