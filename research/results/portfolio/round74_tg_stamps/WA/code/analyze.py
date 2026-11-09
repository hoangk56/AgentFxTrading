"""Stream WA: test the 42 declared cells (HYPOTHESES_WA.md) on IS 2020-21 and VAL 2022-24 with perp 1-minute opens.
Entry: open of the first 1-minute bar starting at or after post + 5 s; exit: open h minutes later. Net = gross - 12 bp.
One trade at a time per cell and coin. t clustered by UTC day. Random benchmark: same events, same side, entry time
uniform within the same UTC day (1,000 draws, shared per event across cells -> max-over-cells null).
Writes WA/results/cells.csv and prints the tables. Data end 2024-12-31 (HOLD closed). Run with python -I."""
import csv, os, sys, collections, datetime as dt
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/whale_alert"
OUTD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/WA/results"
os.makedirs(OUTD, exist_ok=True)
COST = 12.0
H = (5, 15, 60)
RULES = {"BI": (("BI",), -1), "BO": (("BO",), 1), "EI": (("EI",), -1), "EO": (("EO",), 1),
         "F": (("BI", "BO", "EI", "EO"), None), "M": (("M",), 1), "B": (("B",), -1)}
SIDE = {"BI": -1, "BO": 1, "EI": -1, "EO": 1, "M": 1, "B": -1}
SYM = {"BI": "BTCUSDT", "BO": "BTCUSDT", "EI": "ETHUSDT", "EO": "ETHUSDT", "M": "BTCUSDT", "B": "BTCUSDT"}
END = 1735689600
NR = 1000
rng = np.random.default_rng(74)

K = {}
for s in ("BTCUSDT", "ETHUSDT"):
    z = np.load(os.path.join(D, f"k1m_{s}.npz"))
    assert z["t"].max() < END * 1000
    K[s] = (z["t"], z["o"])


def px(sym, ts_s, delay_bars=0, h=5):
    """ts_s: array of decision times (s). Returns (entry price, exit price, ok mask)."""
    t, o = K[sym]
    j = np.searchsorted(t, np.ceil(np.asarray(ts_s) * 1000), "left") + delay_bars
    j = np.clip(j, 0, len(t) - 1)
    te = t[j] + h * 60000
    k = np.clip(np.searchsorted(t, te, "left"), 0, len(t) - 1)
    ok = (t[k] == te) & (te < END * 1000) & (t[j] >= np.ceil(np.asarray(ts_s) * 1000))
    return o[j], o[k], ok, t[j]


def load():
    ev = []
    with open(os.path.join(D, "events.csv")) as f:
        for r in csv.DictReader(f):
            if r["era"] in ("IS", "VAL"):
                ev.append(dict(id=int(r["id"]), ts=float(r["ts"]), era=r["era"], kind=r["kind"], usd=float(r["usd"])))
    ev.sort(key=lambda e: (e["ts"], e["id"]))
    return ev


def ct(x, day):
    """mean and day-clustered t."""
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return (x.mean() if n else np.nan), np.nan
    u, inv = np.unique(day, return_inverse=True); G = len(u)
    m = x.mean()
    r = np.bincount(inv, weights=x - m)
    v = G / max(G - 1, 1) * (r ** 2).sum() / n ** 2
    return m, m / np.sqrt(v) if v > 0 else np.nan


def select(ev, kinds, minusd, h):
    """one trade at a time per coin; returns list of events (in time order) traded."""
    busy = {}; out = []
    for e in ev:
        if e["kind"] not in kinds or e["usd"] < minusd:
            continue
        sym = SYM[e["kind"]]
        if e["ts"] < busy.get(sym, -1):
            continue
        busy[sym] = e["ts"] + 5 + 60 + h * 60  # conservative: until the exit bar
        out.append(e)
    return out


def trades(sel, h, delay=0, ts_override=None):
    g = np.full(len(sel), np.nan); tj = np.zeros(len(sel))
    for sym in ("BTCUSDT", "ETHUSDT"):
        ix = [i for i, e in enumerate(sel) if SYM[e["kind"]] == sym]
        if not ix:
            continue
        ts = np.array([sel[i]["ts"] for i in ix]) if ts_override is None else ts_override[ix]
        a, b, ok, tt = px(sym, ts + 5, delay, h)
        sd = np.array([SIDE[sel[i]["kind"]] for i in ix])
        r = np.where(ok, sd * (b / a - 1) * 1e4, np.nan)
        g[ix] = r; tj[ix] = tt
    return g


def main():
    ev = load()
    print("events", collections.Counter((e["era"], e["kind"]) for e in ev))
    # random times shared per event: uniform second within the event's UTC day, leaving room for the exit
    day0 = {e["id"]: (int(e["ts"]) // 86400) * 86400 for e in ev}
    RT = {e["id"]: day0[e["id"]] + rng.uniform(0, 86400 - 3900, NR) for e in ev}
    rows = []; nullmax = {"IS": np.full(NR, -np.inf), "VAL": np.full(NR, -np.inf)}
    for era in ("IS", "VAL"):
        E = [e for e in ev if e["era"] == era]
        for rule, (kinds, _) in RULES.items():
            for minusd in (0, 1e8):
                for h in H:
                    sel = select(E, kinds, minusd, h)
                    if len(sel) < 3:
                        rows.append(dict(era=era, rule=rule, size=">=100M" if minusd else "all", h=h, n=len(sel))); continue
                    g = trades(sel, h)
                    ok = np.isfinite(g); s2 = [e for e, k in zip(sel, ok) if k]; g = g[ok]
                    day = np.array([int(e["ts"]) // 86400 for e in s2])
                    net = g - COST
                    m, t = ct(net, day)
                    m15, t15 = ct(g - 1.5 * COST, day)
                    gl = trades(s2, h, delay=1); okl = np.isfinite(gl)
                    ml, tl = ct(gl[okl] - COST, day[okl])
                    # pre-event drift: side-signed return over the 60 min before the post
                    pre = trades(s2, 60, ts_override=np.array([e["ts"] for e in s2]) - 3600 - 5)
                    # random
                    R = np.array([RT[e["id"]] for e in s2])  # n x NR
                    GR = np.full(R.shape, np.nan)
                    for sym in ("BTCUSDT", "ETHUSDT"):
                        ix = np.array([i for i, e in enumerate(s2) if SYM[e["kind"]] == sym], int)
                        if len(ix) == 0:
                            continue
                        a, b, okr, _ = px(sym, R[ix].ravel(), 0, h)
                        sd = np.array([SIDE[s2[i]["kind"]] for i in ix])[:, None]
                        GR[ix] = sd * np.where(okr, b / a - 1, np.nan).reshape(len(ix), NR) * 1e4
                    rm = np.zeros(NR); rt = np.zeros(NR)
                    for k in range(NR):
                        okr = np.isfinite(GR[:, k])
                        rm[k], rt[k] = ct(GR[okr, k] - COST, day[okr])
                    pct = (rm < m).mean() * 100
                    nullmax[era] = np.maximum(nullmax[era], np.nan_to_num(rt, nan=-np.inf))
                    yrs = collections.defaultdict(list)
                    for e, x in zip(s2, net):
                        yrs[dt.datetime.fromtimestamp(e["ts"], dt.timezone.utc).year].append(x)
                    sh = net.mean() / net.std(ddof=1)
                    rows.append(dict(era=era, rule=rule, size=">=100M" if minusd else "all", h=h, n=len(net),
                                     days=len(set(day)), gross=round(float(g.mean()), 2), net=round(float(m), 2), t=round(float(t), 2),
                                     net15=round(m15, 2), late_net=round(ml, 2), late_t=round(tl, 2),
                                     sd=round(net.std(ddof=1), 1), sharpe=round(sh, 3),
                                     rand_mean=round(rm.mean(), 2), excess=round(m - rm.mean(), 2), rand_pct=round(pct, 1),
                                     pre60=round(np.nanmean(pre), 2),
                                     years=" ".join(f"{y}:{np.mean(v):+.1f}({len(v)})" for y, v in sorted(yrs.items()))))
                    print(rows[-1], flush=True)
    keys = ["era", "rule", "size", "h", "n", "days", "gross", "net", "t", "net15", "late_net", "late_t", "sd", "sharpe",
            "rand_mean", "excess", "rand_pct", "pre60", "years"]
    with open(os.path.join(OUTD, "cells.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in rows]
    for era in ("IS", "VAL"):
        nm = nullmax[era]
        print(era, "max-over-42-cells random t: mean", round(nm.mean(), 2), "p95", round(np.percentile(nm, 95), 2))
    with open(os.path.join(OUTD, "nullmax.txt"), "w") as f:
        for era in ("IS", "VAL"):
            nm = nullmax[era]
            f.write(f"{era} mean {nm.mean():.2f} p95 {np.percentile(nm, 95):.2f}\n")


if __name__ == "__main__":
    main()
