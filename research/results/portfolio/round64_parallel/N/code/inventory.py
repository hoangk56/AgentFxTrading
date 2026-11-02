"""Stream N: rule B (round63_parallel/B, frozen) executed from a standing long-spot / short-perp inventory.
Declared in ../HYPOTHESES_N.md. Imports B's basis.py / universe.py unchanged; all series cut at 2025-01-01 by B's loader.
Units: Q = B's trade notional (1.0)."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BCODE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "round63_parallel", "B", "code"))
sys.path.insert(0, BCODE)
import basis  # noqa: E402  (frozen, unedited)
from basis import load, simulate, cl_t, DAY, H  # noqa: E402

CUT = basis.CUT
assert CUT == 1735689600000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000)}
YEARS = [(y, int(np.datetime64(f"{y}-01-01", "ms").astype(np.int64)), int(np.datetime64(f"{y + 1}-01-01", "ms").astype(np.int64)))
         for y in range(2020, 2025)]
SPOT_FEE, PERP_FEE = 0.0010, 0.0005


def settled_mask(c, run=6, spot_move=0.01):
    """Hours inside a run of >= `run` perp bars with high == low while spot's close moves > 1 % across the run."""
    Fh, Fl, Sc = c["Fh"], c["Fl"], c["Sc"]
    flat = (Fh == Fl) & ~np.isnan(Fh)
    n = len(flat)
    out = np.zeros(n, bool)
    j = 0
    while j < n:
        if flat[j]:
            k = j
            while k < n and flat[k]:
                k += 1
            if k - j >= run:
                s0 = Sc[j - 1] if j > 0 else np.nan
                seg = Sc[j:k]
                seg = seg[~np.isnan(seg)]
                if len(seg) and s0 == s0 and s0 > 0 and np.nanmax(np.abs(seg / s0 - 1)) > spot_move:
                    out[j:k] = True
            j = k
        else:
            j += 1
    return out


def sim_coin(c, want_in, p, settled):
    """Hourly inventory simulation for one coin. want_in[j]: coin eligible at open j (before hysteresis).
    Returns dict of per-hour arrays (price, fund, cost by type, cash, held, cover) and event counts."""
    n = c["n"]
    Fo, Fh, So = c["Fo"].tolist(), c["Fh"].tolist(), c["So"].tolist()
    fund = np.diff(c["fcum"], prepend=0.0).tolist()
    rank = c["rank"].tolist()
    cash = c["cash"].tolist()
    want_in = want_in.tolist()
    settled = settled.tolist() if p["guard"] else [False] * n
    Ns, lo, hi, m, cm = p["N"], p["lo"], p["hi"], p["m"], p["cost_mult"]
    Cap = Ns * (1 + m)
    liq_mult = (1 + m) / 1.05
    # last index with both opens valid
    vb = np.where(~np.isnan(c["Fo"]) & ~np.isnan(c["So"]))[0]
    if not len(vb):
        return None
    last_valid = int(vb[-1])
    a_price = np.zeros(n); a_fund = np.zeros(n); a_cash = np.zeros(n); a_cap = np.zeros(n)
    a_cost = {k: np.zeros(n) for k in ("build", "reset", "unwind", "liq")}
    held = np.zeros(n, bool); cover = np.zeros(n); kind = np.zeros(n, np.int8)
    ev = dict(builds=0, resets=0, unwinds=0, liqs=0, settled_unwinds=0, stale_unwinds=0)
    hold = False
    us = up = Fr = 0.0
    Fp = Sp = np.nan        # last valid prices (ffill)
    stale = 0
    out_h = 0               # consecutive hours not eligible
    dead = False            # stays out after a settled-perp unwind until the flat run ends

    def hs(j):
        return 0.0003 if rank[j] < 10 else 0.0005

    for j in range(n):
        F, S = Fo[j], So[j]
        okF, okS = F == F, S == S
        if hold:
            # step open j-1 -> open j (hour j-1); liquidation check on hour j-1's high
            Fcur = F if okF else Fp
            Scur = S if okS else Sp
            liq = False
            if j > 0 and Fh[j - 1] == Fh[j - 1] and Fh[j - 1] > Fr * liq_mult:
                Fx = Fr * liq_mult
                a_cost["liq"][j] += 0.05 * up * Fx
                ev["liqs"] += 1
                if p.get("liq_mode", "declared") == "rehedge":
                    # info variant: re-short at the liquidation price at once (spot assumed at Fx x the last S/F ratio)
                    Sx = Fx * Sp / Fp
                    a_price[j] += us * (Sx - Sp) - up * (Fx - Fp)
                    a_cost["liq"][j] += cm * (PERP_FEE + hs(j)) * up * Fx
                    up = us * Sx / Fx
                    Fr = Fx
                    a_price[j] += us * (Scur - Sx) - up * (Fcur - Fx)
                    a_fund[j] += fund[j] * up * Fcur
                else:
                    a_price[j] += us * (Scur - Sp) - up * (Fx - Fp)
                    liq = True
            else:
                a_price[j] += us * (Scur - Sp) - up * (Fcur - Fp)
                a_fund[j] += fund[j] * up * Fcur
            a_cash[j] += Cap * cash[j] / 8760
            a_cap[j] += Cap
            stale = 0 if (okF and okS) else stale + 1
            Fp, Sp = Fcur, Scur
            if liq:
                # rebuild the perp short at this open (perp leg trade), handled as a reset below
                up = 0.0
        else:
            if okF:
                Fp = F
            if okS:
                Sp = S
        elig = want_in[j]
        out_h = 0 if elig else out_h + 1
        if settled[j]:
            dead = True
        elif dead and not settled[j] and j > 0 and not settled[j - 1]:
            dead = False
        want = (elig or (hold and out_h < p["hyst"])) and not dead and j < last_valid
        if hold:
            exit_now = False
            if settled[j]:
                ev["settled_unwinds"] += 1; exit_now = True; kind[j] = 1
            elif stale >= 24 or j >= last_valid:
                ev["stale_unwinds"] += 1; exit_now = True; kind[j] = 2
            elif not want:
                exit_now = True
            if exit_now:
                # settled perp: the short is closed by the exchange at the flat print (fee as a taker close)
                a_cost["unwind"][j] += cm * ((SPOT_FEE + hs(j)) * us * Sp + (PERP_FEE + hs(j)) * up * Fp)
                ev["unwinds"] += 1
                hold = False; us = up = 0.0
                continue
            if not (okF and okS):
                held[j] = True
                cover[j] = min(1.0, us * Sp)
                continue
            vs = us * S
            if up == 0.0 or vs < lo or vs > hi:
                a_cost["reset" if up > 0 else "liq"][j] += cm * ((SPOT_FEE + hs(j)) * abs(Ns - vs) + (PERP_FEE + hs(j)) * abs(Ns - up * F))
                us, up, Fr = Ns / S, Ns / F, F
                ev["resets"] += 1
            held[j] = True
            cover[j] = min(1.0, us * S)
        elif want and okF and okS:
            a_cost["build"][j] += cm * (SPOT_FEE + PERP_FEE + 2 * hs(j)) * Ns
            us, up, Fr = Ns / S, Ns / F, F
            Fp, Sp = F, S
            hold = True; stale = 0
            ev["builds"] += 1
            held[j] = True
            cover[j] = min(1.0, Ns)
    return dict(price=a_price, fund=a_fund, cash=a_cash, cap=a_cap, cost=a_cost, held=held, cover=cover, ev=ev, kind=kind)


def nw_t(x, lag=10):
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return np.nan
    u = x - x.mean()
    v = (u @ u) / n
    for k in range(1, lag + 1):
        v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / np.sqrt(v / n) if v > 0 else np.nan
