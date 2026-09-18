import sqlite3
import sys
from pathlib import Path

import pytest

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.accounts import AccountRegistry

CTRADER_COLUMNS = {"id", "slug", "ctid_email", "account_number", "account_type", "label", "pwd_file", "created_at"}


@pytest.fixture
def registry(tmp_path):
    return AccountRegistry(str(tmp_path / "accounts_test.db"))


def _insert(reg, slug="demo-main", account_type="demo", label="Demo Main", number="10101649"):
    return reg.insert_ctrader_account(slug, "me@example.com", number, account_type, label,
                                      f"/root/ctrader_data/ctid_{slug}_pwd")


def test_ctrader_accounts_crud(registry):
    assert registry.list_ctrader_accounts() == []
    row = _insert(registry)
    assert set(row) == CTRADER_COLUMNS
    assert row["id"] >= 1
    assert row["slug"] == "demo-main"
    assert row["pwd_file"] == "/root/ctrader_data/ctid_demo-main_pwd"
    assert row["created_at"]

    assert registry.get_ctrader_account(row["id"])["label"] == "Demo Main"
    assert registry.get_ctrader_account(row["id"] + 1000) is None
    assert registry.get_ctrader_account_by_slug("demo-main")["id"] == row["id"]
    assert registry.get_ctrader_account_by_slug("nope") is None
    assert [a["slug"] for a in registry.list_ctrader_accounts()] == ["demo-main"]

    assert registry.delete_ctrader_account(row["id"]) is True
    assert registry.delete_ctrader_account(row["id"]) is False
    assert registry.get_ctrader_account(row["id"]) is None
    assert registry.list_ctrader_accounts() == []


def test_slug_is_unique(registry):
    _insert(registry)
    with pytest.raises(sqlite3.IntegrityError):
        _insert(registry, number="999")


def test_account_type_is_checked(registry):
    with pytest.raises(sqlite3.IntegrityError):
        _insert(registry, slug="x-main", account_type="paper")


def test_list_orders_live_first_then_label(registry):
    _insert(registry, slug="demo-zulu", account_type="demo", label="Zulu")
    _insert(registry, slug="demo-alpha", account_type="demo", label="Alpha")
    _insert(registry, slug="live-ic", account_type="live", label="IC", number="6094347")
    assert [a["slug"] for a in registry.list_ctrader_accounts()] == ["live-ic", "demo-alpha", "demo-zulu"]


def test_upsert_configured_account_marks_dashboard_account(registry):
    registry.upsert_configured_account("live-6094347", "6094347", "live", "IC")
    accounts = registry.list_accounts()          # configured only
    assert len(accounts) == 1
    assert accounts[0]["account_id"] == "live-6094347"
    assert accounts[0]["label"] == "IC"
    assert accounts[0]["is_configured"] == 1
    # Re-upsert relabels instead of duplicating (unique on number+type)
    registry.upsert_configured_account("live-6094347", "6094347", "live", "IC Main")
    accounts = registry.list_accounts()
    assert len(accounts) == 1 and accounts[0]["label"] == "IC Main"


def test_seed_from_env_still_uses_the_upsert(registry, monkeypatch):
    monkeypatch.setenv("DASHBOARD_ACCOUNTS", "demo-1|7654321|demo|Demo Test;live-main|1234567|live|Live Main")
    registry.seed_from_env()
    ids = sorted(a["account_id"] for a in registry.list_accounts())
    assert ids == ["demo-1", "live-main"]
