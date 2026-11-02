"""Descriptive (VAL only): Deribit USDC linear perp funding vs inverse perp, annualised by year. python -I usdc.py"""
import numpy as np
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit_funding/"
for c in ("BTC", "ETH"):
    for inst in (f"{c}-PERPETUAL", f"{c}_USDC-PERPETUAL"):
        a = np.loadtxt(R + f"funding_{inst}.csv", delimiter=",", skiprows=1)
        a = a[(a[:, 0] < 1735689600000) & (a[:, 0] >= 1648771200000)]  # 2022-04 .. 2024 (USDC perps listed 2022-03)
        y = a[:, 0].astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
        print(inst, {int(k): round(float(100 * 24 * 365 * a[y == k, 2].mean()), 2) for k in np.unique(y)})
