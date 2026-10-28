"""
Forward-test status of the research candidates, from the closed trades in `positions`.

Each candidate carries the stop and promotion rules *as registered* in its own PREREG (docs/forward-candidates.md lists
the files). Nothing here chooses a threshold: a number that is not in a PREREG is not in this module. The verdict is one
of NO_DATA, CONTINUE, STOP or PROMOTE_CHECK. PROMOTE_CHECK means every promotion number this module can compute passes;
`manual` names the registered conditions it cannot read off `positions` (spread x1.5 needs the quotes, the realised
round-trip cost and the gold entry slippage need the bot's own log), so PROMOTE_CHECK is never a promotion.

Trade net, in bp, is the research's: the real fills' price move over the entry price, minus the 0.6 bp commission.
The pooled t joins the registered HOLD run, known only by (n, mean, sd), to the forward trades as independent trades.
The PREREGs cluster by day; for these bots (at most about one trade a day) the two agree closely.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from app.db import get_db_connection

COMMISSION_BP = 0.6


@dataclass(frozen=True)
class Candidate:
    key: str
    label: str
    bot_suffix: str                  # bot_id ends with this (cbot_presets.STRATEGIES suffix + session slug)
    tier: str
    hold_n: int
    hold_mean: float                 # bp per trade, net
    hold_sd: float
    min_trades_stop_t: int           # trades before the pooled-t stop is read
    stop_t: float                    # stop when pooled t <= this
    min_trades_promote: int = 100
    promote_t: float = 2.5
    # Gold only: cumulative stop at 60 trades, and VAL's per-trade mean / sd for the 120-trade floor.
    stop_cum_after: Optional[int] = None
    floor_after: Optional[int] = None
    val_mean: Optional[float] = None
    val_sd: Optional[float] = None
    manual: Tuple[str, ...] = ()
    prereg: str = ""


def _sd(mean: float, n: int, t: float) -> float:
    """Per-trade sd implied by a reported mean and t over n trades."""
    return abs(mean) * math.sqrt(n) / t


# HOLD figures are the registered holdout results (n, net mean, t); the sd follows from them.
CANDIDATES: Dict[str, Candidate] = {c.key: c for c in (
    Candidate(
        key="ecb_f3", label="ECB Window F3 (E1 on USD-TOP days)", bot_suffix="-ecb-f3", tier="RELAXED",
        hold_n=117, hold_mean=2.00, hold_sd=_sd(2.00, 117, 2.16),
        min_trades_stop_t=60, stop_t=-1.0,
        manual=("spread x1.5 net > 0", "realised mean round-trip cost <= 1.5 bp"),
        prereg="round24_relaxed/PREREG_R24_relaxed_hold.md; PREREG_DRAFT_C_ecb_window_variants.md"),
    Candidate(
        key="ecb_e1", label="ECB Window E1 (short EURUSD 11:00-13:00 London)", bot_suffix="-ecb-e1", tier="DEMO",
        hold_n=444, hold_mean=0.64, hold_sd=_sd(0.64, 444, 0.99),
        min_trades_stop_t=100, stop_t=-1.0,
        manual=("spread x1.5 net > 0", "realised mean round-trip cost <= 1.5 bp"),
        prereg="round13_structural/PREREG_M_eurusd_midday.md"),
    Candidate(
        key="gold_levels", label="Gold $50 levels (G1-XAU50)", bot_suffix="-levels-gold50", tier="DEMO",
        hold_n=228, hold_mean=2.87, hold_sd=_sd(2.87, 228, 1.43),
        min_trades_stop_t=10 ** 9, stop_t=-1.0,   # gold has no pooled-t stop; its three stops are below
        stop_cum_after=60, floor_after=120, val_mean=3.62, val_sd=22.9,
        manual=("spread x1.5 net > 0", "median entry slippage <= 1 x s60 after 30 trades "
                "(research.tools.gold_demo_check on <BotId>_trades.csv)"),
        prereg="round27_levels_opens/PREREG_G_gold_round50_cascade.md"),
)}


def trade_net_bp(side: str, entry: float, exit_: float, commission_bp: float = COMMISSION_BP) -> float:
    move = (exit_ - entry) if side.lower() == "buy" else (entry - exit_)
    return move / entry * 1e4 - commission_bp


def pooled_t(hold_n: int, hold_mean: float, hold_sd: float, values: Sequence[float]) -> float:
    """t of the mean over HOLD (summary) plus forward trades, as independent trades."""
    n = hold_n + len(values)
    if n < 3:
        return float("nan")
    total = hold_n * hold_mean + sum(values)
    mean = total / n
    ss = hold_sd ** 2 * (hold_n - 1) + hold_n * (hold_mean - mean) ** 2
    ss += sum((v - mean) ** 2 for v in values)
    sd = math.sqrt(ss / (n - 1))
    return mean / (sd / math.sqrt(n)) if sd > 0 else float("nan")


def evaluate(cand: Candidate, nets: Sequence[float]) -> dict:
    """Verdict for one candidate from its forward trades' net bp, oldest first."""
    n = len(nets)
    out = {"key": cand.key, "label": cand.label, "tier": cand.tier, "n": n, "manual": list(cand.manual),
           "prereg": cand.prereg, "reasons": []}
    if n == 0:
        return {**out, "verdict": "NO_DATA", "mean": None, "cum": 0.0, "pooled_t": pooled_t(
            cand.hold_n, cand.hold_mean, cand.hold_sd, []), "hold_n": cand.hold_n}
    cum = sum(nets)
    pt = pooled_t(cand.hold_n, cand.hold_mean, cand.hold_sd, nets)
    out.update(mean=cum / n, cum=cum, pooled_t=pt, hold_n=cand.hold_n)

    if cand.stop_cum_after is not None and n >= cand.stop_cum_after and cum < 0:
        out["reasons"].append(f"after {cand.stop_cum_after} trades the cumulative net is {cum:+.1f} bp < 0")
    if cand.floor_after is not None and n >= cand.floor_after:
        floor = n * cand.val_mean - 1.5 * cand.val_sd * math.sqrt(n)
        out["floor"] = floor
        if cum < floor:
            out["reasons"].append(f"after {cand.floor_after} trades the cumulative net {cum:+.1f} bp is below "
                                  f"the expected sum minus 1.5 sd ({floor:+.1f})")
    if n >= cand.min_trades_stop_t and pt <= cand.stop_t:
        out["reasons"].append(f"after {cand.min_trades_stop_t} trades the pooled t {pt:+.2f} <= {cand.stop_t}")
    if out["reasons"]:
        return {**out, "verdict": "STOP"}

    if pt >= cand.promote_t and n >= cand.min_trades_promote:
        return {**out, "verdict": "PROMOTE_CHECK"}
    need = []
    if n < cand.min_trades_promote:
        need.append(f"{cand.min_trades_promote - n} more trades")
    if not pt >= cand.promote_t:
        need.append(f"pooled t {pt:+.2f} < {cand.promote_t}")
    out["reasons"] = need
    return {**out, "verdict": "CONTINUE"}


def load_nets(cand: Candidate, db_target=None) -> List[float]:
    """Net bp of every closed trade whose bot_id ends with the candidate's suffix, oldest entry first."""
    conn = get_db_connection(db_target)
    try:
        rows = conn.execute(
            "SELECT side, entry_price, exit_price FROM positions "
            "WHERE status = 'closed' AND exit_price IS NOT NULL AND entry_price > 0 AND bot_id LIKE ? "
            "ORDER BY entry_time", (f"%{cand.bot_suffix}",)).fetchall()
    finally:
        conn.close()
    return [trade_net_bp(r["side"], r["entry_price"], r["exit_price"]) for r in rows]


def forward_status(db_target=None, keys: Optional[Iterable[str]] = None) -> List[dict]:
    return [evaluate(CANDIDATES[k], load_nets(CANDIDATES[k], db_target)) for k in (keys or CANDIDATES)]
