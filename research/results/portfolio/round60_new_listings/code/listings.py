"""Round 60: short new Binance USDT-M perp listings, BTC-hedged, as declared in ../HYPOTHESES.md.

Episodes are fixed-quantity (no rebalancing), so squeezes show at full size. HOLD entries (>= 2025-01-01) are dropped
unless hold=True.
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round58_unconstrained_carry", "code"))
import carry as C  # noqa: E402

B = C.DATA
DAY = C.DAY
EXCL_BASE = {"USDC", "BTCDOM", "DEFI", "FOOTBALL", "BLUEBIRD", "TUSD", "USDP", "FDUSD", "EUR", "BUSD", "USD1", "XUSD",
             "XAU", "XAG", "PAXG", "XAUT", "TSLA", "NVDA", "AAPL", "MSTR", "COIN", "HOOD", "AMZN", "GOOGL", "META",
             "MSFT", "CRCL", "SPY", "QQQ", "XPT", "XPD", "OIL", "CL", "NATGAS"}
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000),
        "HOLD": (1735689600000, 1790553600000)}  # HOLD entries to 2026-09-28


def base_of(sym):
    b = sym[:-4]
    for pre in ("1000000", "1000", "1M"):
        if b.startswith(pre) and len(b) > len(pre) and not b[len(pre)].isdigit():
            b = b[len(pre):]
            break
    if b.endswith("2") and len(b) > 2 and not b[-2].isdigit():
        b = b[:-1]
    return b


def load_series(sym, hold):
    end = C.ERAS["HOLD"][1] if hold else C.HOLD_START
    nd = int((end - C.T0) // DAY)
    F = np.full(nd, np.nan)
    QV = np.full(nd, np.nan)
    fu = np.zeros(nd)
    p = os.path.join(B, "perp_1d", sym + ".csv")
    _, a = C._read(p)
    if len(a):
        d = C.day_of(a[:, 0]); m = (d >= 0) & (d < nd)
        F[d[m]] = a[m, 4]; QV[d[m]] = a[m, 6]
    for sub in ("funding", "funding_window"):
        p = os.path.join(B, sub, sym + ".csv")
        if os.path.exists(p):
            _, a = C._read(p)
            if len(a):
                d = C.day_of(a[:, 0]); m = (d >= 0) & (d < nd)
                np.add.at(fu, d[m], a[m, 1])
            break
    return F, QV, fu


def events(syms):
    """List of (sym, L0 day index) after exclusions; earliest listing per base kept."""
    firsts = []
    for s in syms:
        p = os.path.join(B, "perp_1d", s + ".csv")
        with open(p) as f:
            next(f)
            line = f.readline()
        if not line:
            continue
        firsts.append((int(float(line.split(",")[0])), s))
    firsts.sort()
    seen, out = set(), []
    for t, s in firsts:
        b = base_of(s)
        if b in EXCL_BASE or b in seen:
            seen.add(b)
            continue
        seen.add(b)
        out.append((s, int((t - C.T0) // DAY)))
    return out


def spot_first():
    out = {}
    p = os.path.join(B, "spot_first.csv")
    for line in open(p):
        k, v = line.strip().split(",")
        if v:
            out[k] = int(v)
    return out


def episode(Fa, fa, Fb, fb, e, H, side=-1, cost_a=0.0015, cost_b=0.0006, hedge=True):
    """Fixed-quantity episode entered at close of day e, exit at close of e + H (or last valid close).
    side -1 = short the alt. Returns (net return on notional, max adverse alt move, exit day) or None."""
    x = e + H
    seg = Fa[e:x + 1]
    if np.isnan(Fa[e]) or np.isnan(Fb[e]):
        return None
    valid = ~np.isnan(seg)
    if not valid[1:].any():
        return None
    last = e + int(np.where(valid)[0][-1])
    x = min(x, last)
    d = np.arange(e + 1, x + 1)
    alt = side * (Fa[x] / Fa[e] - 1) - side * np.nansum(fa[d] * Fa[d - 1] / Fa[e])
    r = alt - 2 * cost_a
    if hedge:
        btc = (Fb[x] / Fb[e] - 1) - np.nansum(fb[d] * Fb[d - 1] / Fb[e])
        r += -side * btc - 2 * cost_b
    adverse = np.nanmax(Fa[e:x + 1]) / Fa[e] - 1 if side < 0 else 1 - np.nanmin(Fa[e:x + 1]) / Fa[e]
    return r, adverse, x


def cluster_t(r, keys):
    r = np.asarray(r); keys = np.asarray(keys)
    mu = r.mean()
    u = np.unique(keys)
    g = np.array([np.sum(r[keys == k] - mu) for k in u])
    se = np.sqrt(np.sum(g ** 2)) / len(r) * np.sqrt(len(u) / max(1, len(u) - 1))
    return mu / se if se > 0 else 0.0
