"""Round 75 coordinator check: rebuild stream MN's n = 2, TP = 2R cell from its HYPOTHESES text only (MN's code not read).

    research/.venv/bin/python -I .../verify_mn.py ETHUSDT
Prints zone counts and IS / VAL trades and net bp, to compare with MN/out/run_<SYM>.log and stats_*_3sym.txt.
"""
import csv
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fp", os.path.join(HERE, "fp.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)

SLIP = {"BTCUSDT": 1.0, "ETHUSDT": 1.0, "SOLUSDT": 2.0}
MAKER, TAKER = 2.0, 5.0


def daily_atr(sym):
    """ATR14 for UTC day index d: mean true range of days d-14..d-1 from perp_1d, None if fewer than 14."""
    rows = []
    with open(os.path.join(fp.ROOT, "research", "data", "binance", "perp_1d", sym + ".csv")) as f:
        for r in csv.DictReader(f):
            t = int(r["t"]) // 60000
            if t >= fp.HOLD_MIN:
                break
            rows.append((t // 1440, float(r["h"]), float(r["l"]), float(r["c"])))
    atr = {}
    trs = []
    for i, (d, h, l, c) in enumerate(rows):
        if len(trs) >= 14:
            atr[d] = sum(trs[-14:]) / 14.0
        if i > 0 and rows[i - 1][0] == d - 1:
            pc = rows[i - 1][3]
            trs.append(max(h, pc) - min(l, pc))
        else:
            trs = []  # the first day has no previous close
    return atr


def funding(sym):
    out = []
    with open(os.path.join(fp.ROOT, "research", "data", "binance", "funding", sym + ".csv")) as f:
        for r in csv.DictReader(f):
            t = int(r["t"]) // 60000
            if t < fp.HOLD_MIN:
                out.append((t, float(r["rate"])))
    a = np.array(out)
    return a[:, 0].astype(np.int64), a[:, 1]


def main():
    sym = sys.argv[1]
    m = fp.load_minutes(sym)
    mm, mo, mh, ml, mc = m["min"], m["o"], m["h"], m["l"], m["c"]
    gap_after = np.r_[np.diff(mm) > 30, False]  # a hole > 30 min starts after minute i
    gcum = np.r_[0, np.cumsum(gap_after)]
    f = fp.load_fp(sym, 30)
    k = f["k"]
    bs, pr = fp.poc(f)
    b = fp.bars(m, 30)
    assert np.array_equal(b["start"], bs)
    atr = daily_atr(sym)
    fu_t, fu_r = funding(sym)

    # zones: close of the 2nd bar of a run of consecutive bars with the same POC row
    zones = []
    run = 1
    for i in range(1, len(bs)):
        if bs[i] - bs[i - 1] == 30 and pr[i] == pr[i - 1]:
            run += 1
            if run == 2:
                zones.append(i)
        else:
            run = 1
    cnt = dict(zones=len(zones), departed=0, tested=0, filled=0, gap_zone=0, gap_trade=0)
    cand = []
    for i in zones:
        r = pr[i]
        lo, hi = float(fp.row_price(r, k)), float(fp.row_price(r, k, "high"))
        expiry = bs[i] + 30 + 336 * 30
        up = dn = 0
        usable = side = None
        j = i + 1
        while j < len(bs) and bs[j] + 30 <= expiry:
            if b["l"][j] > hi:
                up += 1
            elif b["h"][j] < lo:
                dn += 1
            if up == 2 or dn == 2:
                usable, side = bs[j] + 30, (1 if up == 2 else -1)
                break
            j += 1
        if usable is None:
            continue
        cnt["departed"] += 1
        a = np.searchsorted(mm, usable)
        e = np.searchsorted(mm, expiry)
        if side == 1:
            hit = np.flatnonzero(ml[a:e] <= hi)
        else:
            hit = np.flatnonzero(mh[a:e] >= lo)
        if len(hit) == 0:
            continue
        t = a + hit[0]
        cnt["tested"] += 1
        if side == 1 and not ml[t] <= hi * (1 - 1e-4) or side == -1 and not mh[t] >= lo * (1 + 1e-4):
            continue
        cnt["filled"] += 1
        z0 = np.searchsorted(mm, bs[i])
        if gcum[t] - gcum[z0] > 0:
            cnt["gap_zone"] += 1
            continue
        tend = np.searchsorted(mm, mm[t] + 1440, side="right") - 1
        if gcum[tend] - gcum[t] > 0:
            cnt["gap_trade"] += 1
            continue
        d = mm[t] // 1440
        if d not in atr:
            continue
        cand.append((mm[t], i, t, tend, side, hi if side == 1 else lo, 0.15 * atr[d]))
    cand.sort()
    trades = []
    last_exit = -1
    for fm, i, t, tend, side, entry, sd in cand:
        if fm <= last_exit:
            continue
        stop = entry - side * sd
        tp = entry + side * 2 * sd
        cost = MAKER
        ex = None
        if (ml[t] <= stop) if side == 1 else (mh[t] >= stop):
            ex, px, cost = t, stop * (1 - side * SLIP[sym] / 1e4), cost + TAKER
        else:
            for u in range(t + 1, tend + 1):
                if (ml[u] <= stop) if side == 1 else (mh[u] >= stop):
                    base = min(stop, mo[u]) if side == 1 else max(stop, mo[u])
                    ex, px, cost = u, base * (1 - side * SLIP[sym] / 1e4), cost + TAKER
                    break
                if (mh[u] > tp) if side == 1 else (ml[u] < tp):
                    ex, px, cost = u, tp, cost + MAKER
                    break
            if ex is None:
                ex, px, cost = tend, mc[tend], cost + TAKER
        a, z = np.searchsorted(fu_t, fm, side="right"), np.searchsorted(fu_t, mm[ex], side="right")
        fund = side * fu_r[a:z].sum() * 1e4
        net = side * (px / entry - 1) * 1e4 - cost - fund
        trades.append((fm, net))
        last_exit = mm[ex]
    tr = np.array(trades)
    print(sym, cnt)
    for name, sel in (("IS", tr[:, 0] < fp.IS_END_MIN), ("VAL", tr[:, 0] >= fp.IS_END_MIN)):
        x = tr[sel, 1]
        print(f"  {name} n {len(x)} net {x.mean():.2f} bp")


if __name__ == "__main__":
    main()
