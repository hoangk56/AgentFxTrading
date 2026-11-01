"""Round 63 stream C: run the 54 declared cells on IS / VAL (no HOLD). Writes ../out/cells.json and ../out/cells.txt."""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xs  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
JS = (1, 4, 24)
HS = (1, 4, 24)


def cells():
    out = []
    for fam in ("REV", "MOM"):
        for kind in ("raw", "resid"):
            for J in JS:
                for H in HS:
                    out.append((fam, kind, J, H))
    for fam in ("VLO", "VHI"):
        for J in JS:
            for H in HS:
                out.append((fam, "raw", J, H))
    return out


def q_of(fam):
    return 4 if fam in ("VLO", "VHI") else 8


def summarise(b, H):
    res = {}
    for era, rng in (("IS", xs.IS), ("VAL", xs.VAL)):
        m = xs.era_mask(b["tms"], rng)
        r = b["net"][m]
        st = xs.tstats(r, b["tms"][m])
        sd = r.std(ddof=1)
        st.update(n_reb=int(m.sum()), mean_reb_bp=1e4 * r.mean(), sr_reb=r.mean() / sd if sd > 0 else 0.0,
                  gross_reb_bp=1e4 * b["gross"][m].mean(), fund_reb_bp=1e4 * b["fund"][m].mean(),
                  cost_reb_bp=1e4 * b["cost"][m].mean(), turn=float(b["turn"][m].mean()))
        res[era] = st
    res["years"] = xs.years(b["net"], b["tms"])
    n_hold = 667 * 24 / H
    res["power_reb"] = res["VAL"]["sr_reb"] * np.sqrt(n_hold)
    res["power_day"] = res["VAL"]["sr_day"] * np.sqrt(667)
    return res


def run_cell(cx, fam, kind, J, H):
    ts, S = xs.precompute(cx, J, H, kind, fam)
    W = xs.weights(S, q_of(fam))
    out = {}
    M = xs.mats(cx, ts, H)
    b = xs.book(M, W)
    out["base"] = summarise(b, H)
    out["cost15"] = summarise(xs.book(M, W, cost_mult=1.5), H)
    out["maker"] = summarise(xs.book(M, W, fee=0.0002, spread=False), H)
    out["gross_only"] = summarise(xs.book(M, W, fee=0.0, spread=False, funding=False), H)
    out["late1"] = summarise(xs.book(xs.mats(cx, ts, H, lag=1), W), H)
    out["vwap"] = summarise(xs.book(xs.mats(cx, ts, H, exe="vwap"), W), H)
    # funding-stamp split (H = 1 and 4 only: rebalance instants at 00/08/16 UTC vs others)
    if H < 24:
        hr = (b["tms"] // xs.HOUR) % 24
        st = np.isin(hr, (0, 8, 16))
        for nm, m in (("stamp", st), ("nonstamp", ~st)):
            bb = {k: (v[m] if isinstance(v, np.ndarray) and v.ndim == 1 else v) for k, v in b.items()}
            out["split_" + nm] = summarise(bb, H * 3)  # power not meaningful here
    # BTC beta of the book's daily returns (VAL) and top-coin share of gross
    return out, b


def main():
    t0 = time.time()
    Pn = xs.load()
    cx = xs.Ctx(Pn)
    print("panel", len(cx.syms), f"{time.time() - t0:.0f}s", flush=True)
    res = {}
    for c in cells():
        o, b = run_cell(cx, *c)
        key = "|".join(map(str, c))
        res[key] = o
        B, V = o["base"]["IS"], o["base"]["VAL"]
        print(f"{key:18s} IS {B['mean_reb_bp']:7.2f}bp t{B['t']:6.2f} g{B['gross_reb_bp']:7.2f} c{B['cost_reb_bp']:6.2f}"
              f" | VAL {V['mean_reb_bp']:7.2f}bp t{V['t']:6.2f} g{V['gross_reb_bp']:7.2f} | late IS t"
              f"{o['late1']['IS']['t']:6.2f} VAL t{o['late1']['VAL']['t']:6.2f} | pow {o['base']['power_reb']:5.2f}"
              f" {time.time() - t0:.0f}s", flush=True)
    json.dump(res, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
