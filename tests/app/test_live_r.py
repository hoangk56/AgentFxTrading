"""Real-money R of live R-sized research algorithms (app/live_r.py): real Gotobi legs only, since the live date."""
import sqlite3

import pytest

import app.research_api as api
from app.close_reasons import DECOY_PREFIX
from app.live_r import expand_bots, live_r_status, pip_size, trade_r
from tests._paths import FIXTURES_DIR

BOT = "cbot-live-live-usdjpy-fix-gotobi"


def test_expand_bots():
    assert expand_bots("cbot-live-live-{usdjpy,eurjpy}-fix-gotobi") == [
        "cbot-live-live-usdjpy-fix-gotobi", "cbot-live-live-eurjpy-fix-gotobi"]
    assert expand_bots("cbot-x") == ["cbot-x"]
    assert expand_bots(" ") == [] and expand_bots(None) == []


def test_pip_size():
    assert pip_size("USDJPY") == 0.01 and pip_size("eurjpy") == 0.01 and pip_size("EURUSD") == 0.0001


def test_trade_r_sign_and_pip():
    assert trade_r({"symbol": "USDJPY", "side": "buy", "entry_price": 150.00, "exit_price": 150.30,
                    "sl_pips": 30}) == pytest.approx(1.0)
    assert trade_r({"symbol": "EURUSD", "side": "sell", "entry_price": 1.1000, "exit_price": 1.1010,
                    "sl_pips": 20}) == pytest.approx(-0.5)
    assert trade_r({"symbol": "USDJPY", "side": "buy", "entry_price": 150, "exit_price": 151, "sl_pips": 0}) is None
    assert trade_r({"symbol": "USDJPY", "side": "buy", "entry_price": 150, "exit_price": None, "sl_pips": 30}) is None


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lr.db"
    conn = sqlite3.connect(str(path))
    conn.execute("""CREATE TABLE positions (id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id TEXT, symbol TEXT, side TEXT,
        volume REAL, entry_price REAL, exit_price REAL, sl_pips REAL, entry_time TEXT, exit_time TEXT, status TEXT,
        account_id TEXT, close_reason TEXT)""")
    conn.execute("CREATE TABLE accounts (account_id TEXT, account_type TEXT, is_configured INTEGER)")
    conn.executemany("INSERT INTO accounts VALUES (?,?,?)", [("live-1", "live", 1), ("demo-1", "demo", 1)])
    rows = [  # bot, side, entry, exit, sl, entry_time, exit_time, account, reason
        (BOT, "sell", 150.00, 149.70, 30, "2026-10-05 00:55:30", "2026-10-05 02:55:00", "live-1", "Session exit"),  # +1R
        (BOT, "sell", 150.00, 150.15, 30, "2026-10-06 00:55:30", "2026-10-06 02:55:00", "live-1", "x"),   # 6th: decoy day
        (BOT, "sell", 150.00, 150.15, 30, "2026-10-05 00:56:00", "2026-10-05 01:30:00", "live-1",
         DECOY_PREFIX + "x"),                                                                            # decoy reason
        (BOT, "sell", 150.00, 149.70, 30, "2026-10-05 00:55:30", "2026-10-05 02:55:00", "demo-1", "x"),   # demo account
        (BOT, "sell", 150.00, 149.70, 30, "2026-09-25 00:55:30", "2026-09-25 02:55:00", "live-1", "x"),   # before since
        (BOT, "sell", 150.00, 149.70, 0, "2026-10-05 00:55:40", "2026-10-05 02:55:00", "live-1", "x"),    # no stop
        ("cbot-other", "sell", 150.00, 149.70, 30, "2026-10-05 00:55:30", "2026-10-05 02:55:00", "live-1", "x"),
    ]
    for bot, side, ent, ex, sl, et, xt, acc, reason in rows:
        conn.execute("INSERT INTO positions (bot_id, symbol, side, volume, entry_price, exit_price, sl_pips, entry_time,"
                     " exit_time, status, account_id, close_reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     (bot, "USDJPY", side, 1.0, ent, ex, sl, et, xt, "closed", acc, reason))
    conn.commit()
    conn.close()
    return str(path)


def test_status_keeps_real_live_legs_since_the_live_date(db):
    out = live_r_status("cbot-live-live-{usdjpy,eurjpy}-fix-gotobi", "2026-09-30", db)
    assert out["n"] == 1 and out["skipped"] == 1
    assert out["mean"] == pytest.approx(1.0) and out["forward_t"] is None


def test_status_without_a_live_date_takes_every_real_leg(db):
    assert live_r_status(BOT, None, db)["n"] == 2


def test_research_payload_gives_gotobi_a_live_r_tracker(tmp_path, monkeypatch, db):
    reg = tmp_path / "registry.yaml"
    reg.write_text("algorithms:\n  - {id: G, name: G, tier: live, forward: null, bot: '" + BOT + "'}\n"
                   "  - {id: D, name: D, tier: demo, forward: null, bot: '" + BOT + "'}\n", encoding="utf-8")
    plain = tmp_path / "plain.yaml"
    plain.write_text("G: {unit: R, history: [{date: 2026-09-30, kind: live, text: x}]}\nD: {unit: R}\n",
                     encoding="utf-8")
    monkeypatch.setattr(api, "_live_r_db", lambda: db)
    out = {a["id"]: a for a in api.research_payload(reg, plain)["algorithms"]}
    tr = out["G"]["tracker"]
    assert tr["kind"] == "live_r" and tr["available"] and tr["data"]["n"] == 1
    assert out["D"]["tracker"] is None                       # demo tier: no live_r


def test_db_failure_gives_an_unavailable_tracker(tmp_path, monkeypatch):
    reg = tmp_path / "registry.yaml"
    reg.write_text("algorithms:\n  - {id: G, name: G, tier: live, forward: null, bot: x}\n", encoding="utf-8")
    plain = tmp_path / "plain.yaml"
    plain.write_text("G: {unit: R}\n", encoding="utf-8")
    monkeypatch.setattr(api, "_live_r_db", lambda: str(tmp_path / "missing" / "no.db"))
    tr = api.research_payload(reg, plain)["algorithms"][0]["tracker"]
    assert tr["kind"] == "live_r" and tr["available"] is False
