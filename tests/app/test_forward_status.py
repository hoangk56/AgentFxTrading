"""Forward-test status: the registered stop / promotion rules applied to closed trades."""
import math
import sqlite3

import pytest

from app.forward_status import (CANDIDATES, COMMISSION_BP, evaluate, forward_status, forward_t, load_nets, pooled_t,
                                trade_net_bp)


def test_trade_net_bp_signs_and_commission():
    assert trade_net_bp("buy", 100.0, 100.01) == pytest.approx(1.0 - COMMISSION_BP)
    assert trade_net_bp("sell", 100.0, 100.01) == pytest.approx(-1.0 - COMMISSION_BP)
    assert trade_net_bp("SELL", 1.2, 1.1988) == pytest.approx(10.0 - COMMISSION_BP)


def test_pooled_t_with_no_forward_trades_is_holds_own_t():
    c = CANDIDATES["ecb_f3"]
    assert pooled_t(c.hold_n, c.hold_mean, c.hold_sd, []) == pytest.approx(2.16, abs=0.01)
    g = CANDIDATES["gold_levels"]
    assert pooled_t(g.hold_n, g.hold_mean, g.hold_sd, []) == pytest.approx(1.43, abs=0.01)


def test_pooled_t_matches_direct_computation():
    c = CANDIDATES["ecb_e1"]
    fwd = [5.0, -3.0, 2.0, -8.0, 4.0]
    n = c.hold_n + len(fwd)
    mean = (c.hold_n * c.hold_mean + sum(fwd)) / n
    ss = c.hold_sd ** 2 * (c.hold_n - 1) + c.hold_n * (c.hold_mean - mean) ** 2 + sum((v - mean) ** 2 for v in fwd)
    expected = mean / (math.sqrt(ss / (n - 1)) / math.sqrt(n))
    assert pooled_t(c.hold_n, c.hold_mean, c.hold_sd, fwd) == pytest.approx(expected)


def test_no_data():
    r = evaluate(CANDIDATES["ecb_f3"], [])
    assert r["verdict"] == "NO_DATA" and r["n"] == 0


def test_f3_stops_only_after_60_trades_when_pooled_t_at_or_below_minus_one():
    c = CANDIDATES["ecb_f3"]
    bad = [-40.0, -35.0, -45.0] * 20          # 60 trades, far below HOLD's +2
    assert evaluate(c, bad[:59])["verdict"] == "CONTINUE"
    r = evaluate(c, bad)
    assert r["verdict"] == "STOP" and "t gộp" in r["reasons"][0]


def test_e1_pooled_t_stop_waits_for_100_trades():
    c = CANDIDATES["ecb_e1"]
    bad = [-60.0, -55.0, -65.0, -50.0] * 25   # 100 trades
    assert evaluate(c, bad[:99])["verdict"] == "CONTINUE"
    assert evaluate(c, bad)["verdict"] == "STOP"


def test_gold_stops():
    c = CANDIDATES["gold_levels"]
    # 60 trades, cumulative net < 0
    assert evaluate(c, [-1.0] * 59)["verdict"] == "CONTINUE"
    r60 = evaluate(c, [-1.0] * 60)
    assert r60["verdict"] == "STOP" and "tổng ròng" in r60["reasons"][0]
    # 120 trades, cumulative > 0 but below expected sum minus 1.5 sd
    n = 120
    floor = n * 3.62 - 1.5 * 22.9 * math.sqrt(n)
    nets = [(floor - 5.0) / n] * n
    assert floor > 0 and sum(nets) > 0
    r120 = evaluate(c, nets)
    assert r120["verdict"] == "STOP" and "1.5 sd" in " ".join(r120["reasons"])


def test_promote_check_needs_t_and_100_trades_and_lists_manual_conditions():
    c = CANDIDATES["ecb_e1"]
    strong = [8.0, 6.0, 10.0, 4.0] * 25
    r = evaluate(c, strong)
    assert r["verdict"] == "PROMOTE_CHECK"
    assert any("spread x1.5" in m for m in r["manual"])
    assert evaluate(c, strong[:99])["verdict"] == "CONTINUE"     # too few trades


def test_continue_says_what_is_missing():
    r = evaluate(CANDIDATES["gold_levels"], [3.0, -2.0, 5.0])
    assert r["verdict"] == "CONTINUE"
    assert any("cần thêm" in x for x in r["reasons"])


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "fs.db"
    conn = sqlite3.connect(str(path))
    conn.execute("""CREATE TABLE positions (id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id TEXT, symbol TEXT, side TEXT,
        volume REAL, entry_price REAL, entry_time TEXT, exit_time TEXT, exit_price REAL, pnl REAL, status TEXT,
        account_id TEXT)""")
    rows = [
        ("cbot-live-eurusd-ecb-f3", "sell", 1.2000, "2026-10-01 11:00", 1.1988, "closed"),   # +10 bp gross
        ("cbot-demo-eurusd-ecb-f3", "sell", 1.2000, "2026-10-02 11:00", 1.2006, "closed"),   # -5 bp gross
        ("cbot-demo-eurusd-ecb-e1", "sell", 1.2000, "2026-10-02 11:00", 1.1999, "closed"),
        ("cbot-live-eurusd-ecb-f3", "sell", 1.2000, "2026-10-03 11:00", None, "open"),       # not closed
    ]
    for bot, side, ent, et, ex, st in rows:
        conn.execute("INSERT INTO positions (bot_id, symbol, side, volume, entry_price, entry_time, exit_price, status,"
                     " account_id) VALUES (?,?,?,?,?,?,?,?,?)", (bot, "EURUSD", side, 0.01, ent, et, ex, st, "a"))
    conn.commit()
    conn.close()
    return str(path)


def test_load_nets_filters_by_suffix_and_closed_only(db):
    nets = load_nets(CANDIDATES["ecb_f3"], db)
    assert nets == [pytest.approx(10.0 - COMMISSION_BP), pytest.approx(-5.0 - COMMISSION_BP)]
    assert len(load_nets(CANDIDATES["ecb_e1"], db)) == 1
    assert load_nets(CANDIDATES["gold_levels"], db) == []


def test_forward_status_covers_all_candidates(db):
    out = {r["key"]: r for r in forward_status(db)}
    assert set(out) == set(CANDIDATES)
    assert out["ecb_f3"]["n"] == 2 and out["gold_levels"]["verdict"] == "NO_DATA"


@pytest.mark.parametrize("key,strategy,symbol", [("ecb_f3", "ecb_f3", "EURUSD"), ("ecb_e1", "ecb_e1", "EURUSD"),
                                                 ("gold_levels", "gold_levels", "XAUUSD")])
def test_bot_suffix_matches_the_container_names_the_presets_build(key, strategy, symbol):
    from app.cbot_presets import container_name
    assert container_name("demo", strategy, symbol).endswith(CANDIDATES[key].bot_suffix)


def _status(key, verdict, **kw):
    return {"key": key, "label": key.upper(), "verdict": verdict, "n": 60, "mean": -3.0, "pooled_t": -1.2,
            "reasons": ["why"], "manual": ["spread x1.5 net > 0"], **kw}


def test_alerts_fire_once_per_change_into_stop_or_promote_check():
    from app.forward_status import ForwardAlerts
    sent = []
    alerts = ForwardAlerts(lambda text, key=None: sent.append((text, key)))
    assert alerts.check([_status("a", "CONTINUE"), _status("b", "NO_DATA")]) == []
    assert len(alerts.check([_status("a", "STOP")])) == 1
    assert alerts.check([_status("a", "STOP")]) == []            # unchanged: silent
    assert alerts.check([_status("a", "CONTINUE")]) == []        # leaving a state is not alerted
    assert len(alerts.check([_status("a", "STOP")])) == 1        # back into it: alerted again
    promo = alerts.check([_status("b", "PROMOTE_CHECK", mean=4.0, pooled_t=2.6)])
    assert len(promo) == 1 and "Chưa kiểm ở đây: spread x1.5" in promo[0] and promo[0].startswith("🟢")
    assert sent[0][1] == ("forward", "a", "STOP")


def test_calendar_guard_reads_valid_through_and_days_left(tmp_path):
    import datetime
    from app.forward_status import calendar_guard
    seed = tmp_path / "seed.csv"
    seed.write_text("# header\n# valid_through=2026-12-11\nutc_minute,event\n2026-11-02T15:00,x\n")
    assert calendar_guard(datetime.date(2026, 11, 30), seed) == {"valid_through": "2026-12-11", "days_left": 11}
    assert calendar_guard(datetime.date(2026, 12, 20), seed)["days_left"] == -9
    seed.write_text("# header\nutc_minute,event\n")
    assert calendar_guard(datetime.date(2026, 11, 30), seed) is None
    assert calendar_guard(datetime.date(2026, 11, 30), tmp_path / "missing.csv") is None


def test_calendar_alert_only_inside_the_warning_window():
    from app.forward_status import ForwardAlerts
    sent = []
    alerts = ForwardAlerts(lambda text, key=None: sent.append(text))
    assert alerts.check_calendar({"valid_through": "2026-12-11", "days_left": 43}) is None
    assert alerts.check_calendar(None) is None and sent == []
    assert "còn 11 ngày" in alerts.check_calendar({"valid_through": "2026-12-11", "days_left": 11})
    assert "hết hạn" in alerts.check_calendar({"valid_through": "2026-12-11", "days_left": -1})
    assert len(sent) == 2


def test_forward_t_is_mean_over_standard_error():
    assert forward_t([]) is None and forward_t([3.0]) is None
    assert forward_t([1.0, 3.0]) == pytest.approx(2.0)          # mean 2, sd 1.414, se 1.0
    assert forward_t([2.0, 2.0]) is None                        # sd 0


def test_evaluate_reports_forward_t_beside_pooled_t():
    out = evaluate(CANDIDATES["ecb_f3"], [1.0, 3.0])
    assert out["forward_t"] == pytest.approx(2.0) and "pooled_t" in out
    assert evaluate(CANDIDATES["ecb_f3"], [])["forward_t"] is None
