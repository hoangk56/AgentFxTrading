"""Stream A cells (declared in HYPOTHESES_A.md): long alt perp / short BTCUSDT perp from notice + E min to L or L + 1 h.
Fills via k2rule.px (fapi 1m, unchanged), funding via k2rule.funding with the long-alt sign, costs 42 bp. Random draws on
fapi 1m windows (logged through k2rule.get). Cut at ts < 2025-01-01."""
import os, sys, csv, json, pickle
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import k2rule as K
import perps
A = os.path.join(os.path.dirname(__file__), "..")
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
CACHE = os.path.join(R, "upbit_announce", "cache"); os.makedirs(CACHE, exist_ok=True)
CUT = 1735689600000; H = 3600000; M = 60000; DAY = 86400000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, CUT)}
E_GRID = (1, 5, 15)
X_GRID = ("L", "L1h")

# ---- cached fills (pricing logic is k2rule.px itself)
PXF = os.path.join(CACHE, "px.pkl")
_PX = pickle.load(open(PXF, "rb")) if os.path.exists(PXF) else {}
_px0 = K.px


def px(sym, t):
    assert t < CUT
    k = (sym, t)
    if k not in _PX:
        _PX[k] = _px0(sym, t)
    return _PX[k]


K.px = px


def events():
    ev = [r for r in csv.DictReader(open(os.path.join(A, "notice_events_L.csv")))]
    by_nid = {}
    for r in ev:
        r["N"] = int(r["N"])
        if r["L1m"]:
            r["L"] = int(r["L1m"]); r["Lsrc"] = "candle"
        elif r["stated"]:
            r["L"] = int(r["stated"]) + 5 * M; r["Lsrc"] = "stated+5"
        else:
            r["L"] = None; r["Lsrc"] = ""
        by_nid.setdefault(r["nid"], []).append(r)
    for r in ev:
        if r["L"] is None:  # same-notice sibling (MATIC <- SOL)
            sib = [x for x in by_nid[r["nid"]] if x["L"] and x["Lsrc"] == "candle"]
            if sib:
                r["L"] = sib[0]["L"]; r["Lsrc"] = "sibling " + sib[0]["coin"]
    kept = [r for r in ev if r["L"]]
    dropped = [r["coin"] for r in ev if not r["L"]]
    for r in kept:
        r["era"] = "IS" if r["N"] < ERAS["VAL"][0] else "VAL"
        r["day"] = r["N"] // DAY; r["year"] = r["N_utc"][:4]
    return kept, dropped


def leg(sym, te, tx, cost=K.COST):
    """Long alt / short BTC between the closes of the 1m bars starting at te and tx."""
    if tx + 2 * M >= CUT:
        return None
    ae, ax, be, bx = px(sym, te), px(sym, tx), px("BTCUSDT", te), px("BTCUSDT", tx)
    if not all(np.isfinite([ae, ax, be, bx])):
        return None
    price = (ax / ae - 1) - (bx / be - 1)
    fund = -K.funding(sym, te + M, tx + M) + K.funding("BTCUSDT", te + M, tx + M)
    return price, fund, price + fund - cost


def times(r, E, X, late=0):
    te = r["N"] // M * M + (E + late) * M
    tx = r["L"] - M if X == "L" else r["L"] + 60 * M
    if X == "L" and r["L"] - (te + M) < 5 * M:
        return None
    return te, tx


# ---- random draws on fapi 1m windows
WIN = os.path.join(CACHE, "win.pkl")
_W = pickle.load(open(WIN, "rb")) if os.path.exists(WIN) else {}


def window(sym, start):
    assert start < CUT
    k = (sym, start)
    if k not in _W:
        js = K.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={start}&limit=1500") or []
        a = np.array([(int(x[0]), float(x[4])) for x in js if int(x[0]) < CUT], float) if js else np.zeros((0, 2))
        _W[k] = a
    return _W[k]


def close_at(a, t):
    if not len(a):
        return np.nan
    i = np.searchsorted(a[:, 0], t)
    return a[i, 1] if i < len(a) and a[i, 0] <= t + 4 * M else np.nan


SP = perps.span()
ALIVE = sorted(SP)


def rand_same(r, rng):
    """Four 25 h windows of the same coin and BTC, 30-180 d before N."""
    out = []
    for j in range(4):
        st = (r["N"] - int(rng.integers(30 * 1440, 180 * 1440)) * M) // M * M
        out.append((st, window(r["perp"], st), window("BTCUSDT", st)))
    return out


def rand_other(r, rng, te0, tx1):
    cand = [s for s in ALIVE if s not in (r["perp"], "BTCUSDT") and any(a <= r["N"] - 7 * DAY and b >= r["N"] + DAY for a, b in SP[s])]
    pick = rng.choice(cand, size=min(8, len(cand)), replace=False)
    return [(s, window(s, te0)) for s in pick]


def main():
    ev, dropped = events()
    rng = np.random.default_rng(6501)
    rows = []
    for r in ev:
        te0 = r["N"] // M * M + 1 * M
        rs = rand_same(r, rng)
        ro = rand_other(r, rng, te0, r["L"] + 65 * M)
        bw = window("BTCUSDT", te0)
        # descriptive split
        n0 = r["N"] // M * M
        d = {}
        for name, (a, b) in {"pre24": (n0 - 24 * H - M, n0 - M), "N_N1": (n0 - M, n0 + M), "N1_L": (n0 + M, r["L"] - M),
                             "L_L1h": (r["L"] - M, r["L"] + 60 * M), "pre1h": (n0 - 61 * M, n0 - M)}.items():
            if b > a:
                g = leg(r["perp"], a, b, cost=0)
                d[name] = g[0] if g else np.nan
            else:
                d[name] = np.nan
        cells = {}
        for E in E_GRID:
            for X in X_GRID:
                tt = times(r, E, X)
                if not tt:
                    continue
                te, tx = tt
                base = leg(r["perp"], te, tx)
                if base is None:
                    continue
                lt = times(r, E, X, late=5)
                late = leg(r["perp"], *lt) if lt else None
                hold = tx - te
                rsame = []
                for st, aw, bww in rs:
                    for _ in range(60):
                        s0 = st + int(rng.integers(0, max(1, 1500 - hold // M - 2))) * M
                        g = (close_at(aw, s0 + hold) / close_at(aw, s0) - 1) - (close_at(bww, s0 + hold) / close_at(bww, s0) - 1)
                        if np.isfinite(g):
                            rsame.append(g)
                roth = []
                for s, aw in ro:
                    g = (close_at(aw, tx) / close_at(aw, te) - 1) - (close_at(bw, tx) / close_at(bw, te) - 1)
                    if np.isfinite(g):
                        roth.append(g)
                cells[f"A{E}-{X}"] = dict(te=te, tx=tx, price=base[0], fund=base[1], net=base[2], net15=base[0] + base[1] - 1.5 * K.COST,
                                         late=late[2] if late else np.nan, rs=rsame, ro=roth)
        # chained A then K2 (information): long from N + E to K2's own entry fill, then K2
        Lh = r["L"] // H * H
        k2 = K.trade(r["perp"], Lh) if Lh + H + 72 * H + 2 * M < CUT else None
        chain = {}
        for E in E_GRID:
            te = r["N"] // M * M + E * M
            a = leg(r["perp"], te, Lh + H) if Lh + H > te else None
            chain[E] = (a[2] if a else np.nan, k2[3] if k2 else np.nan)
        rows.append(dict(coin=r["coin"], perp=r["perp"], nid=r["nid"], N_utc=r["N_utc"], L=r["L"], Lsrc=r["Lsrc"], src=r["src"],
                         lag_min=(r["L"] - r["N"]) / M, era=r["era"], day=r["day"], year=r["year"], desc=d, cells=cells, chain=chain))
        print(r["coin"], r["N_utc"], f'lag {(r["L"] - r["N"]) / M:.0f} min', {k: round(v["net"] * 1e4) for k, v in cells.items()}, flush=True)
    pickle.dump(_PX, open(PXF, "wb")); pickle.dump(_W, open(WIN, "wb"))
    pickle.dump(dict(rows=rows, dropped=dropped), open(os.path.join(CACHE, "rows.pkl"), "wb"))
    return rows, dropped


if __name__ == "__main__":
    main()
