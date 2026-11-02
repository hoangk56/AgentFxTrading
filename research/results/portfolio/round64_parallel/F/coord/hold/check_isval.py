"""Check mode: rule.py on stream F's IS / VAL data must reproduce PREREG_DRAFT_F (380 / +273.0 / 4.05; 770 / +270.5 / 3.76)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule
D = os.path.join(rule.R, "data", "binance_1m_wicks", "npz")
u = np.load(os.path.join(rule.R, "data", "binance_1m_wicks", "univ.npz"))
U, RK, usyms = u["U"], u["rank"], list(u["syms"])
T0, END, VAL0 = 1577836800000, 1735689600000, 1640995200000
have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in __import__("glob").glob(os.path.join(D, "*.npz"))})
T = rule.trades(D, U, RK, usyms, T0, END, have, END)
for lab, q in (("IS", T0 + T["t"] * 60000 < VAL0), ("VAL", T0 + T["t"] * 60000 >= VAL0)):
    L, _ = rule.summary({k: v[q] for k, v in T.items()}, T0, lab)
    print("\n".join(L))
