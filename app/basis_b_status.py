"""Stop / promotion status of the basis B demo against the rules registered in
research/results/portfolio/round63_parallel/B/PREREG_B_cheap_basis.md ("Demo plan"):
- stop if the cumulative net after 40 demo signals (fillable or not) is < 0, or if > 30 % of signals are not fillable
  for lack of borrow;
- LIVE when HOLD + demo pooled t >= 2.5 on fillable trades, with not-fillable signals counted at 0.

Choices this module adds (the PREREG is silent): both stops and the promotion are read once 40 signals have closed
(HOLD alone already has t 14, so a promotion before the stop check would test nothing); a demo signal's net is the
book net (real book prices, measured borrow rate) and falls back to the registered net (open prices, modelled
spreads) when the book exit is missing; a signal whose borrow is unknown blocks PROMOTE_CHECK. PROMOTE_CHECK is never
a promotion: the user decides.
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

from app import basis_b as R
from app import basis_b_store as store
from app.forward_status import forward_t

HOLD_N, HOLD_MEAN_BP, HOLD_T = 429, 213.5, 14.38
STOP_AFTER = 40
STOP_NOT_FILLABLE = 0.30
PROMOTE_T = 2.5
PREREG = "research/results/portfolio/round63_parallel/B/PREREG_B_cheap_basis.md"


def _iso(ms: Optional[int]) -> Optional[str]:
    if ms is None:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="minutes") + "Z"


def _bp(x: Optional[float]) -> Optional[float]:
    return None if x is None else round(x * 1e4, 1)


def demo_value(t: Dict[str, Any]) -> Optional[float]:
    """Net counted for the stop / pooled t, as a fraction: 0 for a not-fillable signal."""
    if t.get("status") != "closed":
        return None
    if t.get("fillable") == 0:
        return 0.0
    v = t.get("net_book")
    return v if v is not None else t.get("net_registered")


def evaluate(trades: List[Dict[str, Any]], now_ms: Optional[int] = None) -> Dict[str, Any]:
    now_ms = now_ms or int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    closed = [t for t in trades if t.get("status") == "closed"]
    opened = [t for t in trades if t.get("status") == "open"]
    vals = [v for v in (demo_value(t) for t in closed) if v is not None]
    fill = sum(1 for t in trades if t.get("fillable") == 1)
    nofill = sum(1 for t in trades if t.get("fillable") == 0)
    unknown = sum(1 for t in trades if t.get("fillable") is None)
    cum = sum(vals)
    hold_sd = R.sd_from_t(HOLD_MEAN_BP, HOLD_N, HOLD_T)
    pt = R.pooled_t(HOLD_N, HOLD_MEAN_BP, hold_sd, [v * 1e4 for v in vals]) if vals else None
    share = nofill / (fill + nofill) if (fill + nofill) else None
    n = len(vals)
    if n == 0:
        verdict, reason = "NO_DATA", "Chưa có tín hiệu nào đóng."
    elif n < STOP_AFTER:
        verdict, reason = "CONTINUE", f"{n}/{STOP_AFTER} tín hiệu đã đóng; quy tắc dừng đọc ở tín hiệu thứ {STOP_AFTER}."
    elif cum < 0:
        verdict, reason = "STOP", f"Tổng ròng sau {n} tín hiệu âm ({cum * 1e4:+.0f} bp)."
    elif share is not None and share > STOP_NOT_FILLABLE:
        verdict, reason = "STOP", f"{share:.0%} tín hiệu không vay được coin (ngưỡng dừng {STOP_NOT_FILLABLE:.0%})."
    elif unknown:
        verdict, reason = "CONTINUE", f"{unknown} tín hiệu chưa đo được lượng vay; chưa xét nâng hạng."
    elif pt is not None and pt >= PROMOTE_T:
        verdict, reason = "PROMOTE_CHECK", (f"t gộp HOLD + demo {pt:.2f} >= {PROMOTE_T}: đủ điều kiện xét lên live "
                                            "(người dùng quyết).")
    else:
        verdict, reason = "CONTINUE", f"t gộp {pt:.2f} < {PROMOTE_T}." if pt is not None else "Chưa tính được t."
    return {
        "signals": len(trades), "closed_n": len(closed), "fillable": fill, "not_fillable": nofill,
        "unknown_borrow": unknown, "not_fillable_share": share,
        "cum_net_bp": round(cum * 1e4, 1), "mean_net_bp": round(cum / n * 1e4, 1) if n else None,
        "pooled_t": round(pt, 2) if pt is not None else None, "forward_t": forward_t([v * 1e4 for v in vals]),
        "verdict": verdict, "verdict_reason": reason,
        "open": [{"coin": t["symbol"], "entry_time": _iso(t["entry_ms"]), "d_bp": round(t["d_bp"], 1),
                  "hours_open": (now_ms - t["entry_ms"]) // R.H_MS, "fillable": t.get("fillable")}
                 for t in sorted(opened, key=lambda t: -t["entry_ms"])],
        "closed": [{"coin": t["symbol"], "entry_time": _iso(t["entry_ms"]), "exit_time": _iso(t.get("exit_ms")),
                    "hold_h": ((t["exit_ms"] - t["entry_ms"]) // R.H_MS) if t.get("exit_ms") else None,
                    "exit_reason": t.get("exit_reason"),
                    "net_bp_registered": _bp(t.get("net_registered")), "net_bp_book": _bp(t.get("net_book")),
                    "fund_bp": _bp(t.get("fund_part")),
                    "fillable": None if t.get("fillable") is None else bool(t["fillable"]),
                    "borrow_rate_y": (round(t["rate_hourly_in"] * R.HOURS_PER_YEAR, 4)
                                      if t.get("rate_hourly_in") is not None else None),
                    "inventory_usd": round(t["inventory_usd"]) if t.get("inventory_usd") is not None else None,
                    "spread_bp": [t.get("perp_spread_bp_in"), t.get("spot_spread_bp_in")]}
                   for t in sorted(closed, key=lambda t: -t["entry_ms"])[:50]],
        "rules": {"stop_after": STOP_AFTER, "stop_not_fillable_share": STOP_NOT_FILLABLE, "promote_t": PROMOTE_T,
                  "hold": {"n": HOLD_N, "mean_bp": HOLD_MEAN_BP, "t": HOLD_T}},
        "prereg": PREREG,
    }


def status(db_target=None) -> Dict[str, Any]:
    """Everything the research screen shows for basis B (contract in docs/research-screen.md)."""
    try:
        store.init_schema(db_target)
        trades = store.load_trades(db_target=db_target)
        runs = store.last_runs(1, db_target=db_target)
    except Exception as e:                          # noqa: BLE001 - the screen shows "no data" instead of failing
        return {"available": False, "error": str(e)[:200], "verdict": "NO_DATA", "verdict_reason": "Không đọc được bảng."}
    last = runs[0] if runs else None
    out = evaluate(trades)
    out.update({
        "available": last is not None,
        "last_run": (last.get("finished_at") or last.get("started_at")) if last else None,
        "last_error": last.get("error") if last else None,
        "has_secret": bool(last.get("has_secret")) if last else False,
    })
    return out
