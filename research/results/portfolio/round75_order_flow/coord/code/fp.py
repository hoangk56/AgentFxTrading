"""Round 75 shared footprint layer (read-only for streams). Definitions follow research/methods/order-flow-footprint.md.

Import by path:
    spec = importlib.util.spec_from_file_location("fp", ".../round75_order_flow/coord/code/fp.py")
Data: research/data/footprint/<SYM>/<YYYY-MM>.npz (build_fp.py) and derived/<SYM>_tf<TF>.npz (derive()).
Every loader cuts at ts < 2025-01-01: HOLD stays closed.
"""
import glob
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
DATA = os.path.join(ROOT, "research", "data", "footprint")
KEY_MUL = 100_000
HOLD_MIN = 1735689600 // 60  # 2025-01-01 00:00 UTC in epoch minutes
IS_END_MIN = 1640995200 // 60  # 2022-01-01
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
# build_fp packs fp_key = minute * 1e5 + bucket, but BTC above $22,026 has bucket >= 1e5, which carries one into the
# minute field. BTC's real buckets are all >= ~81,600 (price >= ~$3,500), so a remainder below WRAP means a carry.
# ETH (2020 buckets down to ~44k) and SOL never reach 1e5, so they are never unwrapped. Found by stream U, 2026-11-03.
WRAP = {"BTCUSDT": 60_000}


def split_key(key, sym):
    """fp_key -> (epoch minute, 1 bp bucket), undoing the BTC carry."""
    minute, b = key // KEY_MUL, key % KEY_MUL
    if sym in WRAP:
        c = b < WRAP[sym]
        minute = minute - c
        b = b + c * KEY_MUL
    return minute, b


def _months(sym):
    return sorted(p for p in glob.glob(os.path.join(DATA, sym, "*.npz")) if os.path.basename(p) < "2025-01")


def load_minutes(sym):
    """Dense-by-trade 1m bars: min (epoch minute), o h l c, vb (aggressive buy qty), vs (aggressive sell qty), n."""
    parts = [np.load(p) for p in _months(sym)]
    out = {k: np.concatenate([z["m_" + k] for z in parts]) for k in ("min", "o", "h", "l", "c", "vb", "vs", "n")}
    keep = out["min"] < HOLD_MIN
    return {k: v[keep] for k, v in out.items()}


def load_big(sym, min_usd=100_000.0):
    """aggTrades with notional >= min_usd (>= 100k stored): ts ms, p, q, side (+1 aggressive buy, -1 sell)."""
    parts = [np.load(p) for p in _months(sym)]
    ts = np.concatenate([z["big_ts"] for z in parts])
    p = np.concatenate([z["big_p"] for z in parts])
    q = np.concatenate([z["big_q"] for z in parts])
    s = np.concatenate([z["big_side"] for z in parts])
    keep = (ts < HOLD_MIN * 60000) & (p * q >= min_usd)
    return {"ts": ts[keep], "p": p[keep], "q": q[keep], "side": s[keep]}


def bucket(price):
    """1 bp log-price grid used by the cache."""
    return np.floor(1e4 * np.log(price)).astype(np.int64)


def row_k(sym):
    """Rows per footprint cell: k = round(median IS 30m range in bp / 20), at least 1 (declared rule)."""
    m = load_minutes(sym)
    m = {k: v[m["min"] < IS_END_MIN] for k, v in m.items()}
    b = bars(m, 30)
    rng = 1e4 * np.log(b["h"] / b["l"])
    return max(1, int(round(np.median(rng) / 20.0)))


def bars(m, tf):
    """Aggregate 1m bars to tf-minute bars aligned to epoch multiples of tf (UTC). Bars without trades are absent."""
    g = m["min"] // tf
    ub, first = np.unique(g, return_index=True)
    last = np.r_[first[1:], len(g)] - 1
    return {"start": ub * tf, "o": m["o"][first], "h": np.maximum.reduceat(m["h"], first),
            "l": np.minimum.reduceat(m["l"], first), "c": m["c"][last],
            "vb": np.add.reduceat(m["vb"], first), "vs": np.add.reduceat(m["vs"], first),
            "n": np.add.reduceat(m["n"], first)}


def derive(sym, tf, k=None):
    """Footprint of tf-minute bars with k bp rows, saved to derived/<SYM>_tf<TF>.npz (coordinator runs this once)."""
    k = k or row_k(sym)
    keys, bids, asks = [], [], []
    for p in _months(sym):
        z = np.load(p)
        minute, b = split_key(z["fp_key"], sym)
        keep = minute < HOLD_MIN
        cell = (minute[keep] // tf) * KEY_MUL + b[keep] // k
        uk, inv = np.unique(cell, return_inverse=True)
        keys.append(uk)
        bids.append(np.bincount(inv, weights=z["fp_bid"][keep], minlength=len(uk)))
        asks.append(np.bincount(inv, weights=z["fp_ask"][keep], minlength=len(uk)))
    uk, inv = np.unique(np.concatenate(keys), return_inverse=True)
    bid = np.bincount(inv, weights=np.concatenate(bids), minlength=len(uk))
    ask = np.bincount(inv, weights=np.concatenate(asks), minlength=len(uk))
    os.makedirs(os.path.join(DATA, "derived"), exist_ok=True)
    np.savez(os.path.join(DATA, "derived", f"{sym}_tf{tf}.npz"), bar=(uk // KEY_MUL) * tf, row=uk % KEY_MUL,
             bid=bid, ask=ask, k=k, tf=tf)


def load_fp(sym, tf):
    """Footprint cells sorted by (bar start minute, row): bar, row, bid, ask, plus k (bp per row) and tf.
    A row covers prices with floor(1e4 ln p) // k == row, i.e. [exp(row*k/1e4), exp((row+1)*k/1e4))."""
    z = np.load(os.path.join(DATA, "derived", f"{sym}_tf{tf}.npz"))
    keep = z["bar"] < HOLD_MIN
    out = {n: z[n][keep] for n in ("bar", "row", "bid", "ask")}
    out["k"], out["tf"] = int(z["k"]), int(z["tf"])
    out["ptr"] = np.r_[np.flatnonzero(np.r_[True, np.diff(out["bar"]) != 0]), len(out["bar"])]
    return out


def row_price(row, k, edge="low"):
    """Price at the lower (or upper) edge of a row."""
    return np.exp((np.asarray(row) + (1 if edge == "high" else 0)) * k / 1e4)


def poc(f):
    """Per bar: the row with the largest bid + ask (lowest row on a tie). Returns (bar starts, poc rows)."""
    tot = f["bid"] + f["ask"]
    s = f["ptr"][:-1]
    mx = np.maximum.reduceat(tot, s)
    seg = np.repeat(np.arange(len(s)), np.diff(f["ptr"]))
    hit = tot == mx[seg]
    first_hit = np.full(len(s), -1)
    idx = np.flatnonzero(hit)
    first_hit[seg[idx[::-1]]] = idx[::-1]
    return f["bar"][s], f["row"][first_hit]


def imbalances(f, ratio=3.0, floor=0.0):
    """Diagonal imbalances as in the book (its figure: the opposite cell must be > 0).
    sell[i]: bid(r) >= ratio * ask(r + 1) in the same bar, ask(r + 1) > 0, bid(r) >= floor.
    buy[i]:  ask(r) >= ratio * bid(r - 1) in the same bar, bid(r - 1) > 0, ask(r) >= floor."""
    bar, row, bid, ask = f["bar"], f["row"], f["bid"], f["ask"]
    up = np.r_[(bar[1:] == bar[:-1]) & (row[1:] == row[:-1] + 1), False]  # cell i has a neighbour at r + 1
    dn = np.r_[False, up[:-1]]  # cell i has a neighbour at r - 1
    ask_up = np.r_[ask[1:], 0.0] * up
    bid_dn = np.r_[0.0, bid[:-1]] * dn
    sell = (ask_up > 0) & (bid >= ratio * ask_up) & (bid >= floor)
    buy = (bid_dn > 0) & (ask >= ratio * bid_dn) & (ask >= floor)
    return buy, sell


def stacked(f, flag, n=3):
    """Runs of >= n consecutive rows flagged in the same bar: list of (bar start, low row, high row)."""
    bar, row = f["bar"], f["row"]
    out = []
    idx = np.flatnonzero(flag)
    j = 0
    while j < len(idx):
        a = b = idx[j]
        while j + 1 < len(idx) and idx[j + 1] == b + 1 and bar[idx[j + 1]] == bar[a] and row[idx[j + 1]] == row[b] + 1:
            j += 1
            b = idx[j]
        if b - a + 1 >= n:
            out.append((bar[a], row[a], row[b]))
        j += 1
    return out


def unfinished(f):
    """Per bar: unfinished high (top row has bid > 0 and ask > 0) and unfinished low (bottom row, same test).
    Returns bar starts, top row, bottom row, uh, ul."""
    s, e = f["ptr"][:-1], f["ptr"][1:] - 1
    uh = (f["bid"][e] > 0) & (f["ask"][e] > 0)
    ul = (f["bid"][s] > 0) & (f["ask"][s] > 0)
    return f["bar"][s], f["row"][e], f["row"][s], uh, ul


def _selftest():
    # The book's figure (rows top to bottom): bid 0 13 61 42 0, ask 2 14 88 7 4. Imbalances only at bid 13 and 61.
    rows = np.array([10, 11, 12, 13, 14])
    bid = np.array([0, 42, 61, 13, 0], float)  # rows 10..14 bottom to top
    ask = np.array([4, 7, 88, 14, 2], float)
    f = {"bar": np.zeros(5, int), "row": rows, "bid": bid, "ask": ask, "ptr": np.array([0, 5])}
    buy, sell = imbalances(f)
    assert list(np.flatnonzero(sell)) == [2, 3], sell
    assert not buy.any(), buy
    assert stacked(f, np.array([0, 1, 1, 1, 0], bool)) == [(0, 11, 13)]
    _, top, bot, uh, ul = unfinished(f)
    assert top[0] == 14 and bot[0] == 10 and not uh[0] and not ul[0]
    _, pr = poc(f)
    assert pr[0] == 12
    m, b = split_key(np.array([7 * KEY_MUL + 2674, 7 * KEY_MUL + 91273]), "BTCUSDT")
    assert list(m) == [6, 7] and list(b) == [102674, 91273]
    m, b = split_key(np.array([7 * KEY_MUL + 44335]), "ETHUSDT")
    assert m[0] == 7 and b[0] == 44335
    print("fp selftest ok")


if __name__ == "__main__":
    _selftest()
