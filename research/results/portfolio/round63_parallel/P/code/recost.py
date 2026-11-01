"""Re-cost the main cells with the half spread measured from 2024 taker prints (cost_check.py medians):
1.0c below 0.95, 0.8c for 0.95-0.97, 0.6c at 0.97+ (and the p75: 1.5c / 1.4c / 1.4c)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A

def h_med(p, mult):
    return (0.010 if p < 0.95 else 0.008 if p < 0.97 else 0.006) * mult

def h_p75(p, mult):
    return (0.015 if p < 0.95 else 0.014) * mult

U, _ = A.load_universe()
cells = {
    "P1-all-thr0.90-T1d": lambda r: A.p1_trade(r, A.DAY, 0.90, "all"),
    "P1-all-thr0.90-T7d": lambda r: A.p1_trade(r, 7 * A.DAY, 0.90, "all"),
    "P1-all-thr0.80-T7d": lambda r: A.p1_trade(r, 7 * A.DAY, 0.80, "all"),
    "P2a-L1h": lambda r: A.p2a_trade(r, A.H),
    "P2a-L12h": lambda r: A.p2a_trade(r, 12 * A.H),
    "P2b-first95": lambda r: A.p2b_trade(r),
}
for lab, hf in (("measured median", h_med), ("measured p75", h_p75)):
    A.half_spread = hf
    print(f"--- half spread = {lab} ---")
    for name, g in cells.items():
        rows = []
        for r in U:
            tr = g(r)
            if tr is not None:
                rows.append((r, tr, A.ret(r, tr)))
        ev = A.aggregate(rows)
        a, b = A.summarize(ev, "IS"), A.summarize(ev, "VAL")
        print(f"{name:20s} IS {100 * a['mean']:+.2f}% t{a['t']:+.2f} n{a['n']} | VAL {100 * b['mean']:+.2f}% t{b['t']:+.2f} n{b['n']}")
