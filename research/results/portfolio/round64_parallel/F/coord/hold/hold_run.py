"""Registered HOLD run of PREREG_F_wick_fade (run once): frozen rule (rule.py, reproduced IS / VAL exactly) on
2025-01-01..2026-10-29 with the HOLD universe (hold_univ.py). Prints the gates."""
import glob, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule
D = os.path.join(rule.R, "data", "binance_1m_wicks_hold")
rule.FUND_DIRS = [os.path.join(D, "funding")] + rule.FUND_DIRS  # 21 HOLD symbols absent from binance/funding
u = np.load(os.path.join(D, "univ_full.npz")); U, RK, usyms = u["U"], u["rank"], list(u["syms"])
T0, END = 1735689600000, 1793318400000
have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(D, "npz", "*.npz"))})
have = [s for s in have if s in usyms]
T = rule.trades(os.path.join(D, "npz"), U, RK, usyms, T0, END, have, END)
L, s = rule.summary(T, T0, "HOLD")
print("\n".join(L))
g1 = s["m"] > 0 and s["t"] >= 2.0
g2 = s["m15"] > 0 and s["ml"] > 0 and s["mo"] > 0
g3 = s["yr"].get(2025, -1) > 0 and s["yr"].get(2026, -1) > 0
print(f"gate1 net>0 & t>=2.0: {g1}; gate2 x1.5 / late / mean-OHLC > 0: {g2}; gate3 2025 & 2026 > 0: {g3}")
print("PASS" if (g1 and g2 and g3) else "FAIL")
day = (T0 + T["t"].astype(np.int64) * 60000) // 86400000
cs = np.bincount(T["sym"].astype(int), weights=T["net"]); top = np.argsort(-cs)[:5]
print("top-5 coins share of net:", round(float(cs[top].sum() / T["net"].sum()), 3), [usyms[i] for i in top])
ud, inv = np.unique(day, return_inverse=True); ds = np.bincount(inv, weights=T["net"])
print("top-5 days share of net:", round(float(np.sort(ds)[-5:].sum() / T["net"].sum()), 3), "days", len(ud))
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hold_trades.npz"), **T)
