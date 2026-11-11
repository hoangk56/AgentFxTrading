import csv
import json

from app import a2_live as A
from app import a2_live_status as S
from app import research_api


def write(folder, rows, open_events=None):
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "trades.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=A.TRADE_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in A.TRADE_FIELDS})
    (folder / "state.json").write_text(json.dumps({"seen": [1], "open": open_events or {}}))


def trade(mode="live", net=500.0, post="2026-11-12T04:50:01+00:00", detect="2026-11-12T04:50:03+00:00", **kw):
    return {"coin": "HYPE", "perp": "HYPEUSDT", "mode": mode, "notional": 1000, "post_utc": post, "detect_utc": detect,
            "entry_utc": "2026-11-12T04:50:06+00:00", "exit_utc": "2026-11-12T06:05:02+00:00", "alt_entry": 75.0,
            "alt_ask_before": 74.9, "exit_reason": "krw open", "net_bp": net, **kw}


def env(tmp_path, **kw):
    return {"A2_STATE_DIR": str(tmp_path), **kw}


def test_no_files_is_unavailable(tmp_path):
    s = S.status(env(tmp_path / "none"))
    assert s["available"] is False and s["verdict"] == "NO_DATA" and s["closed"] == []


def test_only_live_trades_count_and_rows_are_derived(tmp_path):
    write(tmp_path, [trade(), trade(mode="dry", net=-900), {"coin": "CARDS", "mode": "live", "exit_reason": "skipped",
                                                           "note": "no Binance USDT-M perp",
                                                           "post_utc": "2026-11-12T05:00:00+00:00"}])
    s = S.status(env(tmp_path, A2_LIVE="1", A2_NOTIONAL_USDT="4000", A2_LEVERAGE="2"))
    assert s["available"] and s["mode"] == "live" and s["notional"] == 4000 and s["leverage"] == 2
    assert s["n"] == 1 and s["mean_net_bp"] == 500 and s["dry_n"] == 1 and s["skipped"] == 1
    assert s["verdict"] == "CONTINUE" and s["pooled_t"] > 3
    first = s["closed"][-1]                                  # newest first, so the oldest is last
    assert first["seen_s"] == 2.0 and first["entry_s"] == 5.0 and first["hold_h"] == 1.25
    assert first["slip_bp"] == round((75.0 / 74.9 - 1) * 1e4, 1)
    assert s["seen_le3_share"] == 1.0


def test_promote_check_needs_ten_live_trades(tmp_path):
    write(tmp_path, [trade(net=600 + i) for i in range(9)])
    assert S.status(env(tmp_path))["verdict"] == "CONTINUE"
    write(tmp_path, [trade(net=600 + i) for i in range(10)])
    assert S.status(env(tmp_path))["verdict"] == "PROMOTE_CHECK"


def test_slow_detection_blocks_promotion(tmp_path):
    write(tmp_path, [trade(net=600 + i, detect="2026-11-12T04:50:06+00:00") for i in range(10)])
    s = S.status(env(tmp_path))
    assert s["seen_le3_share"] == 0 and s["verdict"] == "CONTINUE"


def test_nan_exit_is_not_counted(tmp_path):
    write(tmp_path, [trade(net="")], {"9:X": {"coin": "X", "perp": "XUSDT", "mode": "live",
                                              "entry_utc": "2026-11-12T04:50:06+00:00", "notional": 1000}})
    s = S.status(env(tmp_path))
    assert s["n"] == 0 and s["verdict"] == "NO_DATA"
    assert s["open"] == [{"coin": "X", "perp": "XUSDT", "mode": "live", "entry_time": "2026-11-12 04:50",
                          "notional": 1000.0}]


def test_research_api_joins_the_a2_tracker(monkeypatch, tmp_path):
    monkeypatch.setattr(S, "_folder", lambda env=None: tmp_path)
    write(tmp_path, [trade()])
    tr = research_api.a2_live_tracker()
    assert tr["kind"] == "a2_live" and tr["available"] and tr["data"]["n"] == 1


def test_committed_registry_points_a2_at_the_tracker():
    algos, _, warnings = research_api.load_registry()
    a2 = next(a for a in algos if a["id"] == "a2-upbit-notice-5s")
    assert a2["forward"] == "a2_live" and a2["tier"] == "demo"
