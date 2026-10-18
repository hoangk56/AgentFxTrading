import csv

import pytest

from research.tools import gold_demo_check as gdc

# The holdout's trade file is a local research output (.gitignore keeps research/results/**/*trades*.csv out of git).
needs_hold = pytest.mark.skipif(not (gdc.PREREG / "trades_HOLD.csv").exists(), reason="no local trades_HOLD.csv")

COLS = ("trigger_utc,arm_utc,level,side,stop,order_price,s60,trigger_bid,trigger_ask,model_entry_utc,model_entry,"
        "model_entry_mid,model_exit_utc,model_exit,model_exit_mid,model_net_bp,position_id,lots,fill_utc,fill_price,"
        "close_utc,close_price,close_reason,fill_net_bp,entry_slip_vs_model,entry_slip_s60,net_profit,missed,note").split(",")


def _log(path, trades):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for k, (net, slip, missed) in enumerate(trades):
            day = f"2026-11-{1 + k % 28:02d}"
            w.writerow({c: "" for c in COLS} | {
                "trigger_utc": f"{day}T14:00:00.000", "side": "1", "model_entry": "4500.1", "model_entry_mid": "4500.05",
                "model_exit": "4501.0", "model_exit_mid": "4501.05", "model_net_bp": str(net),
                "fill_price": "" if missed else "4500.1", "close_price": "" if missed else "4501.0",
                "fill_net_bp": str(net), "entry_slip_s60": str(slip), "missed": "1" if missed else "0",
                "note": "no order was working" if missed else ""})
    return path


def test_val_reference_is_the_registered_calendar_val():
    mean, sd = gdc.val_mean_sd()
    assert mean == pytest.approx(3.62) and sd == pytest.approx(3.62 / 0.158)


@needs_hold
def test_pooled_t_without_demo_trades_is_the_holdout_t():
    r = gdc.check([], [], gdc.hold_trades(), *gdc.val_mean_sd())
    assert r["pooled_t"] == pytest.approx(1.43, abs=0.005)
    assert not r["promote"] and not r["stop"]


@needs_hold
def test_stop_rules_fire_at_their_counts(tmp_path):
    vm, vsd = gdc.val_mean_sd()
    hold = gdc.hold_trades()
    # 59 losing trades: below zero but not yet 60
    f, m = gdc.demo_trades(_log(tmp_path / "a.csv", [(-1.0, 0.0, False)] * 59 + [(0.0, 0.0, True)]))
    r = gdc.check(f, m, hold, vm, vsd)
    assert r["n"] == 59 and r["missed"] == 1 and not r["stop_60"]
    f, m = gdc.demo_trades(_log(tmp_path / "b.csv", [(-1.0, 0.0, False)] * 60))
    assert gdc.check(f, m, hold, vm, vsd)["stop_60"]
    # 120 trades just under the expected sum minus 1.5 sd
    floor = 120 * vm - 1.5 * vsd * 120 ** 0.5
    f, m = gdc.demo_trades(_log(tmp_path / "c.csv", [(floor / 120 - 0.01, 0.0, False)] * 120))
    r = gdc.check(f, m, hold, vm, vsd)
    assert r["stop_120"] and r["cum"] < r["floor_120"]
    # median slippage worse than one s60 from 30 trades on
    f, m = gdc.demo_trades(_log(tmp_path / "d.csv", [(5.0, 1.2, False)] * 29))
    assert not gdc.check(f, m, hold, vm, vsd)["stop_slip"]
    f, m = gdc.demo_trades(_log(tmp_path / "e.csv", [(5.0, 1.2, False)] * 30))
    assert gdc.check(f, m, hold, vm, vsd)["stop_slip"]
