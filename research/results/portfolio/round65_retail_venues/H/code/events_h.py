"""Build stream H events from first_candles.csv (declared in ../HYPOTHESES_H.md): perp >= 7 d old at L, L in
2020-01-01..2024-12-27, name-collision guard, Upbit overlap class. Writes ../h_events.csv. No returns here."""
import csv, os, sys, time
import numpy as np
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BD = os.path.join(R, "bithumb"); UP = os.path.join(R, "upbit")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
H, DAY, CUT = 3600000, 86400000, 1735689600000
L0, L1 = 1577836800000 - H, 1735344000000  # entry te = L + 1 h >= 2020-01-01; L < 2024-12-28


def perp_1d(sym):
    with open(os.path.join(R, "binance", "perp_1d", sym + ".csv")) as f:
        r = csv.reader(f); next(r)
        a = np.array([[float(x[0]), float(x[4])] for x in r if x], float)
    return a[a[:, 0] < CUT]


def close_on(a, t):  # close of the UTC daily bar containing t
    i = np.searchsorted(a[:, 0], t, side="right") - 1
    return a[i, 1] if i >= 0 and a[i, 0] + DAY > t else np.nan


def upbit_first():
    """coin -> (kind, t): kind 'L60' (K2 event hour), 'F240' (first 240-min candle), 'floor' (listed before the
    pull floor), 'none' (no KRW history before 2025 in K's pull)."""
    out = {}
    for line in open(os.path.join(UP, "pull_m240.out")):
        p = line.split()
        if len(p) != 4:
            continue
        c, st = p[0], p[3]
        if st == "floor":
            out[c] = ("floor", None); continue
        f = os.path.join(UP, "m240", c + ".csv")
        t = None
        if os.path.exists(f):
            with open(f) as fh:
                fh.readline(); x = fh.readline()
                if x.strip():
                    t = int(float(x.split(",")[0]))
        out[c] = ("F240", t) if t is not None and t < CUT else ("none", None)
    with open(os.path.join(UP, "k2_events.csv")) as f:
        for x in csv.DictReader(f):
            out[x["coin"]] = ("L60", int(x["L"]))
    return out


if __name__ == "__main__":
    btc_b = {int(r[0]): float(r[1]) for r in list(csv.reader(open(os.path.join(BD, "btc_days.csv"))))[1:]}
    bb = perp_1d("BTCUSDT")
    U = upbit_first()
    rows, drop = [], []
    for x in csv.DictReader(open(os.path.join(BD, "first_candles.csv"))):
        if x["status"] != "ok":
            continue
        L = int(x["L"]); sym = x["sym"]; coin = x["coin"]
        if coin in ("BTC", "USDC"):  # as k2.events(): BTC is the hedge, USDC a stablecoin
            continue
        a = perp_1d(sym)
        pf = int(a[0, 0]) if len(a) else None
        if pf is None or pf > L - 7 * 86400000 or not (L0 <= L < L1):
            continue
        d0 = int(x["d0"]); tclose = d0 + DAY - 1
        sc = 1000.0 if sym.startswith("1000") and not sym.startswith("1000000") else (1e6 if sym.startswith("1000000") or sym.startswith("1M") else 1.0)
        bk = btc_b.get(d0)
        ratio = (float(x["d0_close"]) / bk) / ((close_on(a, tclose) / sc) / close_on(bb, tclose)) if bk else np.nan
        u = U.get(coin, ("never", None))
        if u[0] in ("L60", "F240") and u[1] is not None and abs(u[1] - L) <= 7 * DAY:
            cls = "joint_bithumb_first" if L < u[1] else ("joint_upbit_first" if L > u[1] + (4 * H if u[0] == "F240" else 0) else "joint_same_hour")
        elif u[0] in ("L60", "F240") and u[1] is not None:
            cls = "bithumb_only_upbit_earlier" if u[1] < L else "bithumb_only_upbit_later"
        elif u[0] == "floor":
            cls = "bithumb_only_upbit_earlier"
        else:
            cls = "bithumb_only_upbit_none"
        r = dict(coin=coin, sym=sym, L=L, Lutc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(L / 1000)), perp_first=pf,
                 perp_age_d=round((L - pf) / DAY, 1), ratio=round(float(ratio), 3) if np.isfinite(ratio) else "", upbit_kind=u[0],
                 upbit_t=time.strftime("%Y-%m-%d %H:%M", time.gmtime(u[1] / 1000)) if u[1] else "", cls=cls,
                 d0_krw=x["d0_krw"], h0_krw=x["h0_krw"])
        if np.isfinite(ratio) and not (1 / 3 <= ratio <= 3):
            r["drop"] = "collision"; drop.append(r)
        elif not np.isfinite(ratio):
            r["drop"] = "no_ratio"; drop.append(r)
        else:
            r["drop"] = ""; rows.append(r)
    keys = ["coin", "sym", "L", "Lutc", "perp_first", "perp_age_d", "ratio", "upbit_kind", "upbit_t", "cls", "d0_krw", "h0_krw", "drop"]
    with open(os.path.join(OUT, "h_events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys); w.writeheader(); [w.writerow(r) for r in rows + drop]
    print(len(rows), "events kept;", len(drop), "dropped")
    for r in drop:
        print("DROP", r["coin"], r["Lutc"], r["ratio"], r["drop"])
    from collections import Counter
    print(Counter(r["cls"] for r in rows))
    print(Counter(r["Lutc"][:4] for r in rows))
