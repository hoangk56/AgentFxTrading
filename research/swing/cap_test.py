"""C1 Crypto Donchian with other per-bot caps, i.e. MaxPositions of cBot/CryptoDonchianBot.cs
(research/results/portfolio/crypto_donchian_max_positions_2026-09-28.md).

C1 runs as registered with the cap at 1, 2, 3 (registered), 4, 5 and none. Per era it reports mean R with t clustered
by stacking episode (a chain of overlapping positions in one bot), net $, the drawdown on a mark-to-market equity
curve (open positions valued at every H4 close) and return / DD, the worst episode and the peak $ at risk; then
mean R by stack rank, return / DD at the four H4 bar phases, and the verdict of the plan in the result file.

    python -m research.swing.cap_test
"""
import math
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from research.swing import swing as S
from research.swing.swing_rules import donchian

SYMBOLS = ("BTCUSD", "ETHUSD")
C1 = dict(n=55, exit_n=20, shorts=True, slk=3.0)
CAPS: Tuple[Optional[int], ...] = (1, 2, 3, 4, 5, None)    # None = no cap
REGISTERED_CAP = 3
PHASES_MIN = (0, 60, 120, 180)
ERAS = ("IS", "VAL", "HOLD")
IS_VAL = "IS+VAL"


def cap_label(cap: Optional[int]) -> str:
    return "none" if cap is None else str(cap)


def run_c1(cap: Optional[int], phase_min: int = 0) -> List[S.Trade]:
    k = 10_000 if cap is None else cap
    return S.run_bots(donchian, SYMBOLS, tf=(240, phase_min), cap=k, per_symbol=k, **C1)


def in_era(t: S.Trade, era: str) -> bool:
    if era == IS_VAL:
        return t.t_in < S.HOLD_START
    return era == "ALL" or S.era_of(t.t_in) == era


# ---------------------------------------------------------------- stacking structure
def ranks(trades: Sequence[S.Trade]) -> List[int]:
    """Per trade: the positions of its bot (one bot per symbol) open at its entry, plus one. A position that closes
    at the entry minute is no longer open, as in swing.admit."""
    return [1 + sum(1 for p in trades if p.symbol == t.symbol and p.t_in < t.t_in < p.t_out) for t in trades]


def episodes(trades: Sequence[S.Trade]) -> List[Tuple[str, int]]:
    """Per trade: its episode, a chain of overlapping positions in one bot. A new episode starts when a bot opens a
    position with nothing open."""
    out: List[Optional[Tuple[str, int]]] = [None] * len(trades)
    by_symbol: Dict[str, List[int]] = defaultdict(list)
    for i, t in enumerate(trades):
        by_symbol[t.symbol].append(i)
    for sym, idx in by_symbol.items():
        idx.sort(key=lambda i: trades[i].t_in)
        ep, reach = -1, None
        for i in idx:
            if reach is None or trades[i].t_in >= reach:
                ep, reach = ep + 1, trades[i].t_out
            reach = max(reach, trades[i].t_out)
            out[i] = (sym, ep)
    return out


def cluster_t(rs: Sequence[float], groups: Sequence) -> Tuple[int, float, float]:
    """n, mean and its t with a cluster-robust standard error (clusters = groups, small-sample factor G/(G-1)).
    With one trade per cluster this is the plain t."""
    a = np.asarray(rs, float)
    n = len(a)
    if n == 0:
        return 0, float("nan"), float("nan")
    mu = float(a.mean())
    ids: Dict = {}
    inv = np.array([ids.setdefault(g, len(ids)) for g in groups])
    g = len(ids)
    if g < 2:
        return n, mu, 0.0
    sums = np.bincount(inv, weights=a - mu)
    var = float((sums ** 2).sum()) / n ** 2 * g / (g - 1)
    return n, mu, mu / math.sqrt(var) if var > 0 else 0.0


# ---------------------------------------------------------------- equity and risk
@lru_cache(maxsize=None)
def _marks(symbol: str, tf: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Close time (ms, after its last minute), bid close and ask close of every bar."""
    b = S.bars(symbol, *tf)
    return S.m1(symbol)["ts"][b.last] + S.MIN, b.c, b.ca


def mtm_increments(trades: Sequence[S.Trade], tf: Tuple[int, int] = S.H4) -> List[Tuple[int, float]]:
    """(time, change of equity in $) for every trade: its open value at each bar close while it is open (bid close
    for longs, ask close for shorts; costs come at the exit), then its net $ at the exit."""
    out: List[Tuple[int, float]] = []
    for t in trades:
        close_t, bid, ask = _marks(t.symbol, tf)
        lo = int(np.searchsorted(close_t, t.t_in, side="right"))
        hi = int(np.searchsorted(close_t, t.t_out, side="left"))
        px = bid[lo:hi] if t.side > 0 else ask[lo:hi]
        value = (px - t.entry) * t.side * S.BASE_RISK_USD * t.scale / t.risk
        prev = 0.0
        for when, v in zip(close_t[lo:hi], value):
            out.append((int(when), float(v) - prev))
            prev = float(v)
        out.append((t.t_out, t.usd - prev))
    return out


def drawdown(increments: Sequence[Tuple[int, float]]) -> float:
    """Max drawdown of the equity made of these (time, change) pairs; changes at one time count together."""
    if not increments:
        return 0.0
    per_time: Dict[int, float] = defaultdict(float)
    for when, d in increments:
        per_time[when] += d
    eq = np.r_[0.0, np.cumsum([per_time[k] for k in sorted(per_time)])]
    return float(np.max(np.maximum.accumulate(eq) - eq))


def realized_drawdown(trades: Sequence[S.Trade]) -> float:
    return drawdown([(t.t_out, t.usd) for t in trades])


def peak_risk(trades: Sequence[S.Trade]) -> float:
    """Most $ at risk (default risk x lot multiplier, at the stop) held at once over all the bots."""
    ev = sorted([(t.t_in, 1, S.BASE_RISK_USD * t.scale) for t in trades] +
                [(t.t_out, 0, -S.BASE_RISK_USD * t.scale) for t in trades])      # exits first at one time
    return float(max(np.cumsum([e[2] for e in ev]))) if ev else 0.0


# ---------------------------------------------------------------- report
def era_stats(trades: Sequence[S.Trade], era: str, tf=S.H4) -> dict:
    tr = [t for t in trades if in_era(t, era)]
    eps = episodes(tr)
    n, mu, t = cluster_t([x.r for x in tr], eps)
    net = sum(x.usd for x in tr)
    dd = drawdown(mtm_increments(tr, tf))
    by_ep: Dict[Tuple[str, int], float] = defaultdict(float)
    for x, e in zip(tr, eps):
        by_ep[e] += x.usd
    return dict(n=n, r=mu, t=t, sum_r=sum(x.r for x in tr), net=net, dd=dd, dd_real=realized_drawdown(tr),
                ret_dd=net / dd if dd > 0 else float("nan"), worst_ep=min(by_ep.values()) if by_ep else 0.0,
                peak=peak_risk(tr), episodes=len(by_ep))


def rank_stats(trades: Sequence[S.Trade], era: str, rank_of) -> Dict[str, Tuple[int, float, float]]:
    rk = ranks(trades)
    eps = episodes(trades)
    groups: Dict[str, List[int]] = defaultdict(list)
    for i, t in enumerate(trades):
        if in_era(t, era):
            groups[rank_of(rk[i])].append(i)
    return {k: cluster_t([trades[i].r for i in v], [eps[i] for i in v]) for k, v in groups.items()}


def _rank_label(r: int) -> str:
    return str(r) if r <= 4 else "5+"


def main():
    runs = {cap: run_c1(cap) for cap in CAPS}
    stats = {cap: {era: era_stats(runs[cap], era) for era in ERAS + (IS_VAL,)} for cap in CAPS}

    print("## 1. Caps, both bots pooled (registered bar phase)\n")
    print("| cap | era | n | episodes | mean R | t (episodes) | sum R | net $ | max DD $ (MTM) | max DD $ (realized) "
          "| return / DD | worst episode $ | peak $ at risk |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for cap in CAPS:
        for era in ERAS:
            s = stats[cap][era]
            print(f"| {cap_label(cap)} | {era} | {s['n']} | {s['episodes']} | {s['r']:+.3f} | {s['t']:+.1f} | "
                  f"{s['sum_r']:+.1f} | {s['net']:+,.0f} | {s['dd']:,.0f} | {s['dd_real']:,.0f} | "
                  f"{s['ret_dd']:.2f} | {s['worst_ep']:+,.0f} | {s['peak']:,.0f} |")

    print("\n## 2. Per symbol: mean R / return per DD\n")
    print("| cap | " + " | ".join(f"{s} {e}" for s in SYMBOLS for e in ERAS) + " |")
    print("|---|" + "---|" * (len(SYMBOLS) * len(ERAS)))
    for cap in CAPS:
        cells = []
        for sym in SYMBOLS:
            tr = [t for t in runs[cap] if t.symbol == sym]
            for era in ERAS:
                s = era_stats(tr, era)
                cells.append(f"{s['r']:+.3f} / {s['ret_dd']:.2f}")
        print(f"| {cap_label(cap)} | " + " | ".join(cells) + " |")

    print("\n## 3. Mean R by stack rank (n, mean R, t by episode)\n")
    for cap in (REGISTERED_CAP, None):
        print(f"cap {cap_label(cap)}:\n")
        print("| rank | " + " | ".join(ERAS) + " | IS+VAL |\n|---|---|---|---|---|")
        per = {era: rank_stats(runs[cap], era, _rank_label) for era in ERAS + (IS_VAL,)}
        for k in sorted({k for d in per.values() for k in d}):
            cells = []
            for era in ERAS + (IS_VAL,):
                n, mu, t = per[era].get(k, (0, float("nan"), float("nan")))
                cells.append(f"{n} / {mu:+.3f} / {t:+.1f}")
            print(f"| {k} | " + " | ".join(cells) + " |")
        print()

    print("## 4. Return / DD on IS+VAL by bar phase\n")
    print("| cap | " + " | ".join(f"{p // 60} h" for p in PHASES_MIN) + " |\n|---|" + "---|" * len(PHASES_MIN))
    phase_ret: Dict[Optional[int], Dict[int, float]] = {}
    for cap in CAPS:
        phase_ret[cap] = {}
        for ph in PHASES_MIN:
            tr = runs[cap] if ph == 0 else run_c1(cap, ph)
            phase_ret[cap][ph] = era_stats(tr, IS_VAL, (240, ph))["ret_dd"]
        print(f"| {cap_label(cap)} | " + " | ".join(f"{phase_ret[cap][p]:.2f}" for p in PHASES_MIN) + " |")

    print("\n## 5. Verdict (plan in the result file)\n")
    others = [c for c in CAPS if c != REGISTERED_CAP]
    cand = max(others, key=lambda c: stats[c]["IS"]["ret_dd"])
    base = stats[REGISTERED_CAP]
    c1 = all(stats[cand][e]["ret_dd"] >= 1.10 * base[e]["ret_dd"] for e in ("IS", "VAL"))
    wins = sum(phase_ret[cand][p] > phase_ret[REGISTERED_CAP][p] for p in PHASES_MIN)
    c2 = wins >= 3
    if cand is not None and cand < REGISTERED_CAP:
        rk = {e: rank_stats(runs[REGISTERED_CAP], e, lambda r: "1" if r == 1 else "2-3") for e in ("IS", "VAL")}
        c3 = all(rk[e]["2-3"][1] < rk[e]["1"][1] for e in ("IS", "VAL"))
        why3 = "rank 2-3 mean R < rank 1 in IS and VAL (cap-3 run): " + ", ".join(
            f"{e} {rk[e]['2-3'][1]:+.3f} vs {rk[e]['1'][1]:+.3f}" for e in ("IS", "VAL"))
    else:
        rk = {e: rank_stats(runs[None], e, lambda r: "4+" if r >= 4 else "1-3") for e in ("IS", "VAL", IS_VAL)}
        top = {e: rk[e].get("4+", (0, float("nan"), float("nan"))) for e in rk}
        c3 = top["IS"][1] > 0 and top["VAL"][1] > 0 and top[IS_VAL][2] >= 2.0
        why3 = "rank >= 4 (uncapped run): " + ", ".join(
            f"{e} n {top[e][0]} R {top[e][1]:+.3f} t {top[e][2]:+.1f}" for e in ("IS", "VAL", IS_VAL))
    print(f"- candidate (best IS return / DD besides 3): cap {cap_label(cand)}")
    print(f"- 1. return / DD >= 1.10 x cap 3 in IS and VAL: {c1} (IS {stats[cand]['IS']['ret_dd']:.2f} vs "
          f"{base['IS']['ret_dd']:.2f}, VAL {stats[cand]['VAL']['ret_dd']:.2f} vs {base['VAL']['ret_dd']:.2f})")
    print(f"- 2. beats cap 3 on IS+VAL at >= 3 of 4 phases: {c2} ({wins}/4)")
    print(f"- 3. {why3}: {c3}")
    print(f"- **{'replace 3 with ' + cap_label(cand) if c1 and c2 and c3 else 'keep 3'}**")


if __name__ == "__main__":
    main()
