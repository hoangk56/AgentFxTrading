"""Account ledger (app/ledger.py, /api/ledger): expected balance, discrepancy, and deposits / withdrawals.

The ledger starts from 0: expected = cash movements + P&L of every closed position; discrepancy = broker - expected.
A balance change that no close explains is listed until the user records it as a deposit or a withdrawal; the first
balance the server saw is a change from 0, of which the closes booked before it explain a part.
"""
import pytest
from fastapi.testclient import TestClient

from app import ledger
from app.accounts import AccountRegistry, get_account_registry
from app.db import get_db_connection
from app.portfolio import PortfolioManager, get_portfolio_manager
from app.server import app

client = TestClient(app)


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "ledger.db")
    PortfolioManager(db_path=path)          # positions, cash movements
    AccountRegistry(path)                   # accounts, balance log
    conn = get_db_connection(path)
    yield conn
    conn.close()


ACCOUNT = {"account_id": "demo-1", "account_number": "1", "account_type": "demo", "label": "demo"}


def _log(conn, log_id, t, before, after, account="demo-1"):
    conn.execute("INSERT INTO account_balance_log (id, account_id, recorded_at, balance_before, balance) "
                 "VALUES (?, ?, ?, ?, ?)", (log_id, account, t, before, after))
    conn.commit()


def _close(conn, pos_id, t, pnl, account="demo-1"):
    conn.execute("INSERT INTO positions (id, bot_id, symbol, side, volume, entry_price, entry_time, exit_time, pnl, "
                 "status, account_id) VALUES (?, 'cbot-x-usdjpy-fix-gotobi', 'USDJPY', 'BUY', 0.1, 150, ?, ?, ?, "
                 "'closed', ?)", (pos_id, t, t, pnl, account))
    conn.commit()


def _seed(conn):
    _log(conn, 1, "2026-09-20 00:00:00", None, 1000.0)                 # opening balance
    _close(conn, 11, "2026-09-20 01:00:05", 12.5)
    _log(conn, 2, "2026-09-20 01:00:10", 1000.0, 1012.5)               # the close
    _log(conn, 3, "2026-09-20 02:00:00", 1012.5, 1512.5)               # a deposit nobody recorded yet
    _close(conn, 12, "2026-09-20 03:00:01", -4.0)
    _close(conn, 13, "2026-09-20 03:00:02", -6.0)
    _log(conn, 4, "2026-09-20 03:00:04", 1512.5, 1502.5)               # two bots closing at the same minute


def test_the_ledger_starts_from_zero(db):
    _seed(db)
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["closed_pnl"], e["closed_trades"]) == (0.0, 2.5, 3)
    assert (e["expected_balance"], e["broker_balance"], e["discrepancy"]) == (2.5, 1502.5, 1500.0)
    assert e["balanced"] is False
    # the first balance (money deposited before the server logged it) and a deposit nobody recorded yet
    assert [(u["log_id"], u["delta"], u["opening"]) for u in e["unexplained"]] == [(1, 1000.0, True), (3, 500.0, False)]
    assert e["unexplained"][0]["balance_before"] == 0.0


def test_confirming_the_suggestions_balances_the_ledger(db):
    _seed(db)
    opening_id = ledger.add_movement(db, "demo-1", None, balance_log_id=1)
    movement_id = ledger.add_movement(db, "demo-1", None, balance_log_id=3, note="Nạp")
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["withdrawals"], e["discrepancy"], e["balanced"]) == (1500.0, 0.0, 0.0, True)
    assert e["unexplained"] == []
    assert [(m["id"], m["amount"], m["balance_log_id"]) for m in e["movements"]] == [
        (opening_id, 1000.0, 1), (movement_id, 500.0, 3)]
    with pytest.raises(ledger.LedgerError, match="already recorded"):
        ledger.add_movement(db, "demo-1", None, balance_log_id=3)


def test_closes_booked_before_the_first_balance_explain_part_of_it(db):
    _close(db, 10, "2026-09-18 10:00:00", 60.0)
    _close(db, 11, "2026-09-19 10:00:00", -20.0)
    _log(db, 1, "2026-09-20 00:00:00", None, 1040.0)
    _close(db, 12, "2026-09-20 00:01:00", 5.0)                           # after it: the next change's
    _log(db, 2, "2026-09-20 00:01:05", 1040.0, 1045.0)
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["closed_pnl"], e["closed_trades"], e["discrepancy"]) == (45.0, 3, 1000.0)
    [opening] = e["unexplained"]
    assert (opening["log_id"], opening["delta"], opening["earlier_closes"], opening["earlier_pnl"]) == (1, 1000.0, 2, 40.0)
    ledger.add_movement(db, "demo-1", None, balance_log_id=1)
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["expected_balance"], e["discrepancy"], e["unexplained"]) == (1000.0, 1045.0, 0.0, [])


def test_a_first_balance_the_earlier_closes_explain_is_not_listed(db):
    _close(db, 10, "2026-09-18 10:00:00", 25.0)
    _log(db, 1, "2026-09-20 00:00:00", None, 25.0)
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["unexplained"], e["balanced"]) == ([], True)
    with pytest.raises(ledger.LedgerError, match="closed trades explain"):
        ledger.add_movement(db, "demo-1", None, balance_log_id=1)


def test_a_manual_withdrawal_counts_and_can_be_deleted(db):
    _log(db, 1, "2026-09-20 00:00:00", None, 1000.0)
    _log(db, 2, "2026-09-20 05:00:00", 1000.0, 800.0)
    ledger.add_movement(db, "demo-1", 1000, "2026-09-01T00:00:00Z", "Nạp ban đầu")
    movement_id = ledger.add_movement(db, "demo-1", -200, "2026-09-20T05:00:00Z", "Rút")
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["withdrawals"], e["expected_balance"], e["discrepancy"]) == (1000.0, 200.0, 800.0, 0.0)
    assert [u["log_id"] for u in e["unexplained"]] == [1, 2]      # typed by hand, so the changes stay listed
    assert ledger.delete_movement(db, movement_id) is True
    assert ledger.delete_movement(db, movement_id) is False
    assert ledger.account_ledger(db, ACCOUNT)["discrepancy"] == -200.0


def test_movements_before_the_first_balance_count(db):
    _log(db, 1, "2026-09-20 00:00:00", None, 1000.0)
    ledger.add_movement(db, "demo-1", 1000, "2026-09-19T12:00:00Z")
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["expected_balance"], e["balanced"]) == (1000.0, 1000.0, True)


def test_an_account_with_no_balance_yet_has_no_broker_figures(db):
    _close(db, 10, "2026-09-18 10:00:00", 12.0)
    ledger.add_movement(db, "demo-1", 500, "2026-09-17T00:00:00Z")
    e = ledger.account_ledger(db, ACCOUNT)
    assert (e["deposits"], e["closed_pnl"], e["expected_balance"]) == (500.0, 12.0, 512.0)
    assert e["broker_balance"] is None and e["discrepancy"] is None and e["balanced"] is None
    assert e["unexplained"] == []


@pytest.mark.parametrize("amount, when, note, message", [
    (0, None, None, "non-zero"),
    ("abc", None, None, "number"),
    (float("inf"), None, None, "non-zero"),
    (10, "yesterday", None, "ISO"),
    (10, "2099-01-01T00:00:00Z", None, "future"),
    (10, None, "two\nlines", "one line"),
    (10, None, "x" * 201, "one line"),
])
def test_invalid_movements_are_refused(db, amount, when, note, message):
    with pytest.raises(ledger.LedgerError, match=message):
        ledger.add_movement(db, "demo-1", amount, when, note)


def test_a_balance_change_of_another_account_or_one_a_close_explains_cannot_be_confirmed(db):
    _seed(db)
    with pytest.raises(ledger.LedgerError, match="does not belong"):
        ledger.add_movement(db, "live-2", None, balance_log_id=3)
    with pytest.raises(ledger.LedgerError, match="closed trades explain"):
        ledger.add_movement(db, "demo-1", None, balance_log_id=2)


def test_parse_utc_reads_every_stored_format():
    assert ledger.parse_utc("2026-09-24 10:10:54.15+00").isoformat() == "2026-09-24T10:10:54.150000+00:00"
    assert ledger.parse_utc("2026-09-24 10:10:54").isoformat() == "2026-09-24T10:10:54+00:00"
    assert ledger.parse_utc("2026-09-24T03:10:54Z").isoformat() == "2026-09-24T03:10:54+00:00"
    assert ledger.parse_utc("") is None and ledger.parse_utc("garbage") is None


# --- API ---------------------------------------------------------------------------------------

@pytest.fixture
def api_account():
    reg = get_account_registry()
    account_id = reg.upsert_from_bot("990066", "live", "ledger-test", 2000.0, 2000.0)
    reg.upsert_from_bot("990066", "live", "ledger-test", 2250.0, 2250.0)          # an unrecorded deposit
    yield account_id
    conn = get_db_connection(get_portfolio_manager().db_path)
    for table in ("account_cash_movements", "account_balance_log", "accounts"):
        conn.execute(f"DELETE FROM {table} WHERE account_id = ?", (account_id,))
    conn.commit()
    conn.close()
    reg._logged_balance.pop(account_id, None)


def _entry(scope, account_id):
    return next(e for e in client.get(f"/api/ledger?account_id={scope}").json()["accounts"]
                if e["account_id"] == account_id)


def test_api_lists_the_ledger_per_mode_and_confirms_the_suggestions(api_account):
    assert all(e["account_type"] == "demo" for e in client.get("/api/ledger?account_id=demo").json()["accounts"])
    e = _entry("live", api_account)
    assert (e["discrepancy"], e["balanced"]) == (2250.0, False)
    opening, suggestion = e["unexplained"]
    assert (opening["opening"], opening["delta"]) == (True, 2000.0)
    assert suggestion["delta"] == 250.0 and suggestion["recorded_at_vn"]

    for u in (opening, suggestion):
        res = client.post("/api/ledger/movements", json={"account_id": api_account, "balance_log_id": u["log_id"]})
        assert res.status_code == 201, res.text
    e = _entry(api_account, api_account)
    assert (e["deposits"], e["discrepancy"], e["unexplained"]) == (2250.0, 0.0, [])
    assert e["movements"][0]["occurred_at_vn"]

    assert client.delete(f"/api/ledger/movements/{res.json()['id']}").json() == {"success": True}
    assert client.delete(f"/api/ledger/movements/{res.json()['id']}").status_code == 404


def test_api_refuses_bad_input(api_account):
    assert client.post("/api/ledger/movements", json={"account_id": "nope", "amount": 5}).status_code == 404
    assert client.post("/api/ledger/movements", json={"account_id": "live", "amount": 5}).status_code == 404
    res = client.post("/api/ledger/movements", json={"account_id": api_account, "amount": 0})
    assert res.status_code == 422 and "non-zero" in res.json()["message"]


def test_ledger_handlers_run_off_the_event_loop():
    import inspect
    from app import ledger_api
    for handler in (ledger_api.api_ledger, ledger_api.api_add_movement, ledger_api.api_delete_movement):
        assert not inspect.iscoroutinefunction(handler), handler.__name__
