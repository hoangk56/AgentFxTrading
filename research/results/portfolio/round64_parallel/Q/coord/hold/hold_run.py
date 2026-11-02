"""Registered HOLD run of PREREG_Q1 (run once): stream Q's unchanged code (q.py load / simulate, run.py trades_for /
price_1m / stats / M1) with the cut constants widened to 2024-12-01..2026-10-30 and the data folder pointed to
research/data/binance_cm_hold. Usage: python -I hold_run.py need | run
need: writes binance_cm_hold/need_m1.txt (1m days to pull) and the HOLD trade count only (no prices printed).
run : prices on 1m bars and prints the DEMO gates."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
QC = os.path.abspath(os.path.join(HERE, "..", "..", "code"))
sys.path.insert(0, QC)
import q
R = os.path.abspath(os.path.join(QC, "..", "..", "..", "..", ".."))
OUTD = os.path.join(R, "data", "binance_cm_hold")
HOLD0, END = 1735689600000, 1793318400000
q.CM = OUTD
q.BB = OUTD                      # USDT-M funding fallback: binance_cm_hold/funding/<SYM>.csv (after binance/funding)
q.T0 = 1733011200000             # 2024-12-01: 31 days of warm-up for the 168 h median
q.CUT = END
q.J0, q.J1 = q.T0 // q.H, q.CUT // q.H
q.N = q.J1 - q.J0
q.ERAS = {"HOLD": (HOLD0, END)}
import run  # binds J0, N, ERAS from the patched q
CELL = ("Q1", 100, 72)


def hold_trades(pairs):
    T = run.trades_for(pairs, CELL)
    return [t for t in T if HOLD0 <= run.ms(t["e"]) < END - 72 * q.H - 2 * q.H]


if __name__ == "__main__":
    pairs = q.load()
    T = hold_trades(pairs)
    if sys.argv[1] == "need":
        lines = set()
        for t in T:
            p = pairs[t["pi"]]
            te, tx = run.ms(t["e"]), run.ms(t["x"])
            for mk, sym in ((p["Amarket"], p["A"]), ("um", p["U"])):
                for tt in (te - q.M, te + q.M, te + 5 * q.M, tx + q.M):
                    lines.add((mk, sym, run.day_of(tt)))
        with open(os.path.join(OUTD, "need_m1.txt"), "w") as f:
            for x in sorted(lines):
                f.write(" ".join(x) + "\n")
        print("HOLD screen trades", len(T), "1m days", len(lines))
        sys.exit()
    rows = run.price_1m(pairs, CELL, T, run.M1())
    K = [r for r in rows if r["guard"] and not np.isnan(r["net"])]
    s = run.stats(K); s15 = run.stats(K, cost_mult=1.5); sl = run.stats(K, "late")
    print(f"HOLD screen n {len(rows)}, dropped guard {sum(1 for r in rows if not r['guard'])}, "
          f"dropped no-1m {sum(1 for r in rows if r['guard'] and np.isnan(r['net']))}")
    print("HOLD", json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}))
    print(f"  x1.5 net {s15.get('net_bp', float('nan')):+.1f} t {s15.get('t', float('nan')):.2f}; T+2 min net {sl.get('net_bp', float('nan')):+.1f} t {sl.get('t', float('nan')):.2f}")
    if K:
        day = np.array([r["te"] // q.DAY for r in K]); x = np.array([r["net"] for r in K])
        u, inv = np.unique(day, return_inverse=True); ds = np.bincount(inv, weights=x)
        top = np.sort(ds)[-5:].sum() / x.sum() if x.sum() != 0 else float("nan")
        print(f"  event-days {len(u)}; top-5 days share of net {top:.3f}; price {np.mean([r['price'] for r in K])*1e4:+.1f} "
              f"funding {np.mean([r['fund'] for r in K])*1e4:+.1f} cost {np.mean([r['cost'] for r in K])*1e4:.1f} bp")
        for y in sorted({str(np.datetime64(int(r['te']), 'ms'))[:4] for r in K}):
            v = [r["net"] for r in K if str(np.datetime64(int(r['te']), 'ms'))[:4] == y]
            print(f"  {y}: n {len(v)} net {np.mean(v)*1e4:+.1f}")
        days = [str(np.datetime64(int(d * q.DAY), 'ms'))[:10] for d in u[np.argsort(-np.abs(ds))[:5]]]
        print("  largest |day| P&L:", days)
    ev_days = s.get("days", 0)
    verdict = "INCONCLUSIVE (< 3 event-days)" if ev_days < 3 else ("PASS (DEMO bar: net > 0)" if s.get("net_bp", -1) > 0 else "FAIL (net <= 0): drop")
    print(verdict)
