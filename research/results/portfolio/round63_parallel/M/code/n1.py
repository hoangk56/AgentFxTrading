"""Round 63 stream M: N1a-c (round 23, Tolusic 2026 daily-reopen gap fade, 6 USD pairs) at the ECN cost, plus the
Dukascopy SWFX (ECN) spread by New York minute in 2010-2015 as a measured cost for the 17:00-18:00 NY minutes.
Fill at X = close of the bar labelled X (= eng price at X + 1 min)."""
import datetime as dt
import json
import sys

import numpy as np

import eng
import run

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD"]
PIP = {p: (0.01 if p.endswith("JPY") else 0.0001) for p in PAIRS}
MIN = 60000
DUKA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/duka"


def fill(sym, x_ms):
    """mid / spread of the bar labelled x (<= 10 min stale) -> (mid, spr, ok)."""
    mid, spr, _ = eng.row(sym)
    k = eng.quote_k(sym, np.asarray(x_ms) + MIN)
    ok = k >= 0
    return np.where(ok, mid[np.maximum(k, 0)], np.nan), np.where(ok, spr[np.maximum(k, 0)], np.nan), ok


def bar_at(sym, x_ms):
    """mid of the bar labelled exactly x (no staleness) or nan."""
    mid = eng.row(sym)[0]
    k = (np.asarray(x_ms, dtype=np.int64) - eng.T0) // MIN
    ok = (k >= 0) & (k < eng.NMIN)
    out = np.full(k.shape, np.nan); out[ok] = mid[k[ok]]
    return out


def sessions():
    d = dt.date(2015, 12, 31); out = []
    while d <= dt.date(2024, 12, 30):
        if d.weekday() in (6, 0, 1, 2, 3):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def events(sym, variant):
    days = sessions()
    t17 = np.array([eng.loc_ms(d, 17, 0, "NY") for d in days])
    # P0: bar 16:59, else last quote 16:30-16:59
    p0 = np.full(len(days), np.nan)
    for back in range(0, 30):
        x = bar_at(sym, t17 - (1 + back) * MIN)
        p0 = np.where(np.isnan(p0), x, p0)
    # R: first bar with a quote at labels 17:00..17:30
    R = np.full(len(days), np.nan); tr = np.full(len(days), -1, dtype=np.int64)
    for j in range(0, 31):
        x = bar_at(sym, t17 + j * MIN)
        new = np.isnan(R) & ~np.isnan(x)
        R = np.where(new, x, R); tr = np.where(new, t17 + j * MIN, tr)
    g = (R - p0) / PIP[sym]
    thr = 2.0 if variant == "N1c" else 1.0
    ev = ~np.isnan(g) & (np.abs(g) >= thr) & (t17 >= eng.T0) & (t17 < eng.T1 - 3 * 3600 * 1000)
    side = -np.sign(g)
    ent = tr + MIN if variant in ("N1a", "N1c") else t17 + 5 * MIN
    ext = t17 + 60 * MIN
    return side[ev], ent[ev], ext[ev], np.array(days)[ev]


def trades_fill(sym, side, ent, ext):
    a, sa, oka = fill(sym, ent); b, sb, okb = fill(sym, ext)
    a1, sa1, oka1 = fill(sym, ent + MIN); b1, sb1, okb1 = fill(sym, ext + MIN)
    ok = oka & okb & oka1 & okb1 & (ext > ent)
    g = side * np.log(b / a) * 1e4; g1 = side * np.log(b1 / a1) * 1e4
    lo, up, ic = eng.costs(sym, a, b, sa, sb, ent)
    _, up1, _ = eng.costs(sym, a1, b1, sa1, sb1, ent)
    k = lambda x: x[ok]
    return dict(sym=sym, ms_in=k(ent), ms_out=k(ext), side=k(side), gross=k(g), lo=k(lo), up=k(up), ic=k(ic),
                gross1=k(g1), up1=k(up1))


def random_hour(variant, t_rule, seeds=run.SEEDS):
    rng = np.random.default_rng(777)
    thr = 2.0 if variant == "N1c" else 1.0
    days = sessions()
    t17 = np.array([eng.loc_ms(d, 17, 0, "NY") for d in days])
    res = {"IS": [], "VAL": []}
    for _ in range(seeds):
        nets, ents = [], []
        for sym in PAIRS:
            H = t17 + rng.integers(1, 23, len(days)) * 3600 * 1000      # 18:00 .. 15:00 NY next day
            g = (bar_at(sym, H) - bar_at(sym, H - 2 * MIN)) / PIP[sym]
            ev = ~np.isnan(g) & (np.abs(g) >= thr) & (H < eng.T1 - 2 * 3600 * 1000)
            t = trades_fill(sym, -np.sign(g[ev]), H[ev] + MIN, H[ev] + 60 * MIN)
            nets.append(t["gross"] - t["up"]); ents.append(t["ms_in"])
        nets = np.concatenate(nets); ents = np.concatenate(ents)
        for e, m in run.era_masks(ents).items():
            res[e].append(np.nanmean(nets[m]))
    out = {}
    for e, m in run.era_masks(t_rule["ms_in"]).items():
        mu = np.nanmean(t_rule["gross"][m] - t_rule["up"][m])
        out[e] = float(100 * np.mean(mu > np.array(res[e])))
    return out


def duka_spreads():
    """mean spread (bp) by New York minute label, 2010-2015, Dukascopy SWFX M1 (bid / ask at bar close)."""
    out = {}
    for sym in PAIRS:
        try:
            z = np.load(f"{DUKA}/m1/{sym}.npz"); ts = z["ts"]; bid = z["c"]; ask = z["ca"]
        except FileNotFoundError:
            z = np.load(f"{DUKA}/m1c/{sym}.npz"); ts = z["ts"]; bid = z["bid"].astype(float); ask = z["ask"].astype(float)
        t0 = int(dt.datetime(2010, 1, 1, tzinfo=eng.UTC).timestamp() * 1000)
        t1 = int(dt.datetime(2016, 1, 1, tzinfo=eng.UTC).timestamp() * 1000)
        m = (ts >= t0) & (ts < t1) & (ask > bid)
        ts, bid, ask = ts[m], bid[m], ask[m]
        sp = (ask - bid) / ((ask + bid) / 2) * 1e4
        nym = eng.ny_minute(ts)
        tab = {}
        for lab in [16 * 60 + 55, 16 * 60 + 59] + list(range(17 * 60, 17 * 60 + 11)) + [17 * 60 + 30, 18 * 60, 18 * 60 + 1,
                                                                                         12 * 60, 3 * 60]:
            v = sp[nym == lab]
            tab[f"{lab // 60:02d}:{lab % 60:02d}"] = (float(np.median(v)), float(np.mean(v)), int(v.size))
        out[sym] = tab
    return out


def ic_spreads():
    """same table from IC (2016-2024): mean spread in bp by NY minute label."""
    out = {}
    for sym in PAIRS:
        mid, spr, _ = eng.row(sym)
        ok = ~np.isnan(mid)
        k = np.flatnonzero(ok)
        ms = eng.T0 + k * MIN
        nym = eng.ny_minute(ms)
        sp = spr[k] / mid[k] * 1e4
        tab = {}
        for lab in [16 * 60 + 59, 17 * 60, 17 * 60 + 1, 17 * 60 + 2, 17 * 60 + 5, 18 * 60, 12 * 60]:
            v = sp[nym == lab]
            tab[f"{lab // 60:02d}:{lab % 60:02d}"] = (float(np.median(v)), float(np.mean(v)), int(v.size))
        out[sym] = tab
        eng.drop(sym)
    return out


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("duka", "all"):
        d = duka_spreads(); json.dump(d, open(run.OUT / "n1_duka_spreads.json", "w"), indent=1)
        for s, tab in d.items():
            print("DUKA", s, {k: round(v[0], 2) for k, v in tab.items()})
        c = ic_spreads(); json.dump(c, open(run.OUT / "n1_ic_spreads.json", "w"), indent=1)
        for s, tab in c.items():
            print("IC  ", s, {k: round(v[0], 2) for k, v in tab.items()})
    if what in ("rules", "all"):
        for variant in ("N1a", "N1b", "N1c"):
            ts = []
            for sym in PAIRS:
                side, ent, ext, _ = events(sym, variant)
                ts.append(trades_fill(sym, side, ent, ext))
            t = eng.cat(ts)
            s = {e: run.stats(t, m) for e, m in run.era_masks(t["ms_in"]).items()}
            for e in s:
                s[e]["per_year"] = s[e]["n"] / (6.0 if e == "IS" else 3.0)
            rnd = random_hour(variant, t)
            g = run.grade(s, rnd)
            rec = dict(id=variant, sym="6USD", sel="lit", contaminated=False, ctrl="hour", IS=s["IS"], VAL=s["VAL"],
                       random=rnd, **g)
            json.dump(rec, open(run.OUT / f"{variant}.json", "w"), indent=1, default=float)
            np.savez(run.OUT / f"{variant}_trades.npz", **t)
            print(f"{variant} IS n {s['IS']['n']} mid {s['IS']['mid']:+.2f} up {s['IS']['net_up']:+.2f} "
                  f"(t {s['IS']['t_up']:+.2f}) lo {s['IS']['net_lo']:+.2f} | VAL n {s['VAL']['n']} mid {s['VAL']['mid']:+.2f} "
                  f"up {s['VAL']['net_up']:+.2f} (t {s['VAL']['t_up']:+.2f}) lo {s['VAL']['net_lo']:+.2f} (t {s['VAL']['t_lo']:+.2f}) "
                  f"| cost up {s['VAL']['cost_up']:.2f} lo {s['VAL']['cost_lo']:.2f} | rnd {rnd} -> {g['tier']}", flush=True)
            for sym in PAIRS:
                eng.drop(sym)
