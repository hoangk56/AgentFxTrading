"""K1 rule (declared in ../HYPOTHESES_K.md): Upbit coin-specific premium r on 4h closes -> Binance alt perp vs BTC perp.
gen_trades() produces entry / exit times from bucket data only (no fill prices)."""
import numpy as np
from kdata import GRID, B4, H, panel

KRW_MIN = 40e6
WIN, WIN_MIN = 42, 30
COLLIDE = 0.20
CELLS = [(sig, side, k, Hh) for side in (+1, -1) for sig in ("RAW", "DEV") for k in (200, 500) for Hh in (24, 72)]


def cell_name(sig, side, k, Hh):
    return f"{'L' if side > 0 else 'S'}-{sig}-k{k}-H{Hh}"


def prep(coins):
    keep = []
    for c in coins:
        r = c["r"]
        fin = np.isfinite(r)
        if fin.sum() < 50:
            continue
        c["med_abs"] = float(np.median(np.abs(r[fin])))
        if c["med_abs"] > COLLIDE:
            c["dropped"] = True
            continue
        c["valid"] = fin & (c["ukrw"] >= KRW_MIN)
        # trailing median of r over the previous 42 buckets (finite only), need >= 30
        m = np.full(len(r), np.nan)
        for i in range(len(r)):
            w = r[max(0, i - WIN):i]
            w = w[np.isfinite(w)]
            if len(w) >= WIN_MIN:
                m[i] = np.median(w)
        c["m"] = m
        keep.append(c)
    return keep


def gen_trades(coins, sig, side, k, Hh):
    """Returns list of dicts: ci, i (entry bucket), j (exit bucket), T entry/exit (bucket end ms), s_entry, forced."""
    out = []
    kk = k / 1e4
    nb = Hh // 4
    for ci, c in enumerate(coins):
        r, v, m = c["r"], c["valid"], c["m"]
        anchor = np.zeros(len(r)) if sig == "RAW" else m
        s = side * (r - anchor)
        ok = v & np.isfinite(s)
        i, n = 0, len(r)
        while i < n:
            if not (ok[i] and s[i] > kk):
                i += 1; continue
            a = anchor[i]
            se = s[i]
            j_exit, forced = None, True
            for j in range(i + 1, min(i + nb, n - 1) + 1):
                if j == i + nb:
                    j_exit = j; break
                if v[j] and np.isfinite(r[j]) and side * (r[j] - a) <= se / 2:
                    j_exit, forced = j, False; break
            if j_exit is None:  # data ends
                break
            out.append(dict(ci=ci, i=i, j=j_exit, Te=int(GRID[i] + B4), Tx=int(GRID[j_exit] + B4), s=se, forced=forced))
            i = j_exit + 1
    return out


if __name__ == "__main__":
    coins, base = panel()
    coins = prep(coins)
    print(len(coins), "coins kept")
    for cell in CELLS:
        T = gen_trades(coins, *cell)
        print(cell_name(*cell), len(T))
