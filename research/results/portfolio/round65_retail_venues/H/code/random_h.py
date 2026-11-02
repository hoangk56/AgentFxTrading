"""Random benchmark for stream H (as K2's random_k2): gross short-alt / long-BTC on local 1h closes, fill at the
close of the 1h bar starting at L + 1 h; (a) other mapped alts (perp > 30 d old) at the same hour, (b) same coin at
random hours 30-180 d after L. 500 draws. Usage: python -I random_h.py > ../h_random.txt"""
import csv, glob, os, sys
import numpy as np
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
H, DAY, CUT = 3600000, 86400000, 1735689600000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, CUT)}


def _read(p):
    with open(p) as f:
        r = csv.reader(f); next(r)
        a = np.array([[float(x[0]), float(x[4])] for x in r if x], float)
    return a[a[:, 0] < CUT] if len(a) else a


def b1h(sym):
    cands = [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv"),
             os.path.join(R, "upbit", "binance", "perp_1h", sym + ".csv"), os.path.join(R, "bithumb", "perp_1h", sym + ".csv")] + \
        glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv"))
    best = None
    for p in cands:
        if os.path.exists(p):
            a = _read(p)
            if len(a) and (best is None or a[0, 0] < best[0, 0] or (a[0, 0] == best[0, 0] and len(a) > len(best))):
                best = a
    return {int(t): c for t, c in best} if best is not None else {}


def main():
    ev = [x for x in csv.DictReader(open(os.path.join(OUT, "h_trades.csv"))) if x.get("te")]
    mapped = sorted({x["sym"] for x in csv.DictReader(open(os.path.join(R, "bithumb", "first_candles.csv")))} - {"BTCUSDT"})
    hb = b1h("BTCUSDT")
    H1 = {s: b1h(s) for s in mapped}
    H1 = {s: d for s, d in H1.items() if d}
    pf = {s: min(d) for s, d in H1.items()}
    print("1h series:", len(H1), "of", len(mapped), "mapped; events with 1h:", sum(x["sym"] in H1 for x in ev))
    rng = np.random.default_rng(11)
    def g(s, t0, hold):
        a0, a1, b0, b1 = H1[s].get(t0), H1[s].get(t0 + hold), hb.get(t0), hb.get(t0 + hold)
        if None in (a0, a1, b0, b1):
            return np.nan
        return -((a1 / a0 - 1) - (b1 / b0 - 1))
    for hold in (72, 24):
        for grp in ("all", "bithumb_only", "joint"):
            act, ra, rb = [], [], []
            for e in ev:
                if grp != "all" and not e["cls"].startswith(grp):
                    continue
                s, L = e["sym"], int(e["L"])
                if s not in H1:
                    continue
                t0 = L + H
                x = g(s, t0, hold * H)
                if not np.isfinite(x):
                    continue
                act.append((t0, x))
                others = [o for o in H1 if o != s and pf[o] < t0 - 30 * DAY and t0 in H1[o] and (t0 + hold * H) in H1[o]]
                ra.append([g(o, t0, hold * H) for o in rng.choice(others, 500)] if others else [np.nan] * 500)
                hrs = [t for t in range(L + 30 * DAY, min(L + 180 * DAY, CUT - 4 * DAY), H) if t in H1[s]]
                rb.append([g(s, int(t), hold * H) for t in rng.choice(hrs, 500)] if hrs else [np.nan] * 500)
            if not act:
                continue
            act = np.array(act); ra = np.array(ra); rb = np.array(rb)
            for era, (lo, hi) in ERAS.items():
                w = (act[:, 0] >= lo) & (act[:, 0] < hi)
                if w.sum() < 3:
                    print(hold, grp, era, "n", int(w.sum())); continue
                m = act[w, 1].mean()
                A = np.nanmean(ra[w], axis=0); B = np.nanmean(rb[w], axis=0)
                print(f"H{hold} {grp} {era} n {int(w.sum())} gross_h1 {m*1e4:+.0f} | other alts: pct {(A<m).mean()*100:.1f} median {np.median(A)*1e4:+.0f}"
                      f" | same coin: pct {(B<m).mean()*100:.1f} median {np.median(B)*1e4:+.0f}", flush=True)


main()
