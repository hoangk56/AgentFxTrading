"""Status of the A2-D5L executor (app/a2_live.py) for the Research screen, read from its files only (`trades.csv`,
`state.json`, `STOP_A2` in A2_STATE_DIR); it never calls Binance.

Registered promotion (research/results/portfolio/round65_retail_venues/A2/PREREG_A2_D5L.md): HOLD + forward demo
pooled t >= 2.5 on real fills, with the notice seen <= 3 s after N on >= 80 % of live notices. Only live trades count.
Choice this module adds (the PREREG is silent): PROMOTE_CHECK needs at least 10 closed live trades, since HOLD alone
already has t 3.11 and one trade would otherwise "pass". PROMOTE_CHECK is never a promotion: the user decides.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.basis_b import pooled_t, sd_from_t
from app.forward_status import forward_t

HOLD_N, HOLD_MEAN_BP, HOLD_T = 91, 780.3, 3.11
PROMOTE_T = 2.5
MIN_LIVE = 10
DETECT_S, DETECT_SHARE = 3.0, 0.80
PREREG = "research/results/portfolio/round65_retail_venues/A2/PREREG_A2_D5L.md"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _folder(env=os.environ) -> Path:
    p = Path((env.get("A2_STATE_DIR") or "").strip() or "data/a2_live")
    return p if p.is_absolute() else REPO_ROOT / p


def _num(v) -> Optional[float]:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x else None          # NaN (a leg closed with nothing left to reduce) -> None


def _ts(v) -> Optional[float]:
    try:
        return dt.datetime.fromisoformat(v).timestamp() if v else None
    except ValueError:
        return None


def _minute(v) -> Optional[str]:
    t = _ts(v)
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M") if t else None


def _row(r: Dict[str, Any]) -> Dict[str, Any]:
    post, entry, exit_ = _ts(r.get("post_utc")), _ts(r.get("entry_utc")), _ts(r.get("exit_utc"))
    detect = _ts(r.get("detect_utc"))
    alt_in, ask = _num(r.get("alt_entry")), _num(r.get("alt_ask_before"))
    return {"coin": r.get("coin"), "perp": r.get("perp") or None, "mode": r.get("mode"),
            "notional": _num(r.get("notional")), "post_time": _minute(r.get("post_utc")),
            "seen_s": round(detect - post, 2) if detect and post else None,
            "entry_s": round(entry - post, 2) if entry and post else None,
            "hold_h": round((exit_ - entry) / 3600, 2) if exit_ and entry else None,
            "slip_bp": round((alt_in / ask - 1) * 1e4, 1) if alt_in and ask else None,
            "exit_reason": r.get("exit_reason") or None, "net_bp": _num(r.get("net_bp")), "note": r.get("note") or None}


def evaluate(trades: List[Dict[str, Any]], open_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = [_row(r) for r in trades]
    traded = [r for r in rows if r["exit_reason"] not in (None, "skipped")]
    live = [r for r in traded if r["mode"] == "live"]
    # (exit time, net bp) per closed live trade, for the research screen's periods (app/research_periods.py)
    dated = [[r.get("exit_utc"), _num(r.get("net_bp"))] for r in trades
             if r.get("mode") == "live" and r.get("exit_reason") not in (None, "", "skipped")
             and r.get("exit_utc") and _num(r.get("net_bp")) is not None]
    vals = [r["net_bp"] for r in live if r["net_bp"] is not None]
    seen = [r["seen_s"] for r in rows if r["mode"] == "live" and r["seen_s"] is not None]
    share = sum(s <= DETECT_S for s in seen) / len(seen) if seen else None
    pt = pooled_t(HOLD_N, HOLD_MEAN_BP, sd_from_t(HOLD_MEAN_BP, HOLD_N, HOLD_T), vals) if vals else None
    if not vals:
        verdict, reason = "NO_DATA", "Chưa có lệnh thật nào đóng."
    elif len(vals) >= MIN_LIVE and pt is not None and pt >= PROMOTE_T and (share is None or share >= DETECT_SHARE):
        verdict, reason = "PROMOTE_CHECK", f"{len(vals)} lệnh thật, t gộp {pt:.2f}."
    else:
        verdict, reason = "CONTINUE", f"{len(vals)}/{MIN_LIVE} lệnh thật đã đóng."
    return {
        "n": len(vals), "cum_net_bp": round(sum(vals), 1) if vals else None,
        "mean_net_bp": round(sum(vals) / len(vals), 1) if vals else None,
        "forward_t": forward_t(vals), "pooled_t": round(pt, 2) if pt is not None else None,
        "seen_le3_share": round(share, 3) if share is not None else None,
        "skipped": sum(1 for r in rows if r["exit_reason"] == "skipped"),
        "dry_n": sum(1 for r in traded if r["mode"] == "dry"),
        "verdict": verdict, "verdict_reason": reason,
        "open": [{"coin": e.get("coin"), "perp": e.get("perp"), "mode": e.get("mode"),
                  "entry_time": _minute(e.get("entry_utc")), "notional": _num(e.get("notional"))}
                 for e in open_events],
        "closed": list(reversed(rows)),
        "rules": {"promote_t": PROMOTE_T, "min_live": MIN_LIVE, "detect_s": DETECT_S, "detect_share": DETECT_SHARE,
                  "hold": {"n": HOLD_N, "mean_bp": HOLD_MEAN_BP, "t": HOLD_T}},
        "prereg": PREREG,
        "dated": dated,
    }


def status(env=os.environ) -> Dict[str, Any]:
    folder = _folder(env)
    trades_path, state_path = folder / "trades.csv", folder / "state.json"
    trades: List[Dict[str, Any]] = []
    if trades_path.exists():
        with open(trades_path, newline="") as fh:
            trades = list(csv.DictReader(fh))
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    out = evaluate(trades, list((state.get("open") or {}).values()))
    live = (env.get("A2_LIVE") or "").strip() == "1"
    return {**out, "available": state_path.exists(), "mode": "live" if live else "dry",
            "notional": _num(env.get("A2_NOTIONAL_USDT")), "leverage": _num(env.get("A2_LEVERAGE")),
            "stopped": (folder / "STOP_A2").exists(),
            "updated": dt.datetime.fromtimestamp(state_path.stat().st_mtime, dt.timezone.utc)
            .strftime("%Y-%m-%d %H:%M") if state_path.exists() else None}
