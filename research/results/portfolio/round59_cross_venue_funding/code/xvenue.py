"""Round 59: cross-venue perp-perp funding spread (Binance vs another venue), as declared in ../HYPOTHESES.md."""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round58_unconstrained_carry", "code"))
import carry as C  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "..", "..", "data")
FEE = {"bybit": 0.00055, "hl": 0.00045}


def load_other(venue, syms, nd):
    F = np.full((len(syms), nd), np.nan)
    FU = np.zeros((len(syms), nd))
    NS = np.zeros((len(syms), nd))
    for i, s in enumerate(syms):
        for kind in ("perp_1d", "funding"):
            p = os.path.join(DATA, venue if venue != "hl" else "hyperliquid", kind, s + ".csv")
            if not os.path.exists(p):
                continue
            _, a = C._read(p)
            if not len(a):
                continue
            d = C.day_of(a[:, 0])
            m = (d >= 0) & (d < nd)
            if kind == "perp_1d":
                F[i, d[m]] = a[m, 4]
            else:
                np.add.at(FU[i], d[m], a[m, 1])
                np.add.at(NS[i], d[m], 1)
    FU[NS == 0] = np.nan
    return F, FU


def load(venue, syms, hold=False):
    P = C.load_panel(syms, hold=hold)
    nd = P["F"].shape[1]
    P["F2"], P["fund2"] = load_other(venue, syms, nd)
    P["venue"] = venue
    return P


def pair_pnl(P, i, d, side):
    """P&L of day d per unit notional; side +1 = short Binance / long other, -1 = the reverse."""
    Fb, F2 = P["F"][i], P["F2"][i]
    fb = P["fund"][i, d]
    f2 = P["fund2"][i, d]
    fb = 0.0 if np.isnan(fb) else fb
    f2 = 0.0 if np.isnan(f2) else f2
    q = 1.0 / Fb[d - 1]
    short_b = -(Fb[d] - Fb[d - 1]) * q + fb * q * Fb[d - 1]
    long_2 = (F2[d] - F2[d - 1]) * q - f2 * q * F2[d - 1]
    return side * (short_b + long_2)


def simulate(P, U, L=7, th_in=0.15, th_out=0.05, K=10, cost_mult=1.0, lag=0, d0=0, d1=None, cash=None):
    F, F2 = P["F"], P["F2"]
    n, nd = F.shape
    d1 = nd if d1 is None else d1
    spread = P["fund"] - P["fund2"]
    sig = C.trailing_mean(spread, L) * 365.0
    if lag:
        sig = np.concatenate([np.full((n, lag), np.nan), sig[:, :-lag]], axis=1)
    fee2 = FEE[P["venue"]]
    book = np.zeros(nd)
    dep = np.zeros(nd)
    held, eps = {}, []

    def cost(i):
        hs = 0.0001 if P["syms"][i] in ("BTCUSDT", "ETHUSDT") else 0.0003
        return cost_mult * (0.0005 + fee2 + 4 * hs)

    for d in range(d0, d1):
        for i in list(held):
            e, side, c = held[i]
            if np.isnan(F[i, d]) or np.isnan(F2[i, d]):
                book[d - 1] -= c / K
                eps.append((i, e, d - 1, side, 2 * c))
                del held[i]
                continue
            book[d] += pair_pnl(P, i, d, side) / K
            dep[d] += 1.0 / K
        if d == d1 - 1:
            break
        for i in list(held):
            e, side, c = held[i]
            s = sig[i, d]
            if np.isnan(s) or abs(s) < th_out or np.sign(s) != side:
                book[d] -= c / K
                eps.append((i, e, d, side, 2 * c))
                del held[i]
        free = K - len(held)
        if free > 0:
            ok = U[:, d] & ~np.isnan(sig[:, d]) & (np.abs(np.nan_to_num(sig[:, d])) > th_in) & ~np.isnan(F2[:, d])
            cand = [i for i in np.where(ok)[0] if i not in held]
            cand.sort(key=lambda i: -abs(sig[i, d]))
            for i in cand[:free]:
                c = cost(i)
                held[i] = (d, int(np.sign(sig[i, d])), c)
                book[d] -= c / K
    for i, (e, side, c) in held.items():
        book[d1 - 1] -= c / K
        eps.append((i, e, d1 - 1, side, 2 * c))
    r = book[d0:d1]
    ex = None
    if cash is not None:
        ex = r - dep[d0:d1] * (2.0 / 3.0) * cash[d0:d1]
    return r, eps, ex, dep[d0:d1]


def random_book(P, U, eps, d0, d1, K=10, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    book = np.zeros(d1)
    fee2 = FEE[P["venue"]]
    for (_, e, x, _, c) in eps:
        dur = x - e
        if dur <= 0:
            continue
        for _t in range(50):
            e2 = int(rng.integers(d0, max(d0 + 1, d1 - dur)))
            pool = np.where(U[:, e2] & ~np.isnan(P["F2"][:, e2]))[0]
            if not len(pool):
                continue
            i = int(rng.choice(pool))
            seg = slice(e2, e2 + dur + 1)
            if np.isnan(P["F"][i, seg]).any() or np.isnan(P["F2"][i, seg]).any():
                continue
            side = int(rng.choice([-1, 1]))
            for d in range(e2 + 1, e2 + dur + 1):
                book[d] += pair_pnl(P, i, d, side) / K
            book[e2] -= c / 2 / K
            book[e2 + dur] -= c / 2 / K
            break
    return book[d0:d1]


def fed_funds(days_ms):
    rows = [r for r in csv.reader(open(os.path.join(DATA, "rates", "DFF.csv")))][1:]
    ff = {r[0]: float(r[1]) for r in rows if r[1] not in ("", ".")}
    out, last = [], 0.0
    for t in days_ms:
        k = str(np.datetime64(int(t), "ms"))[:10]
        last = ff.get(k, last)
        out.append(last / 100 / 365)
    return np.array(out)
