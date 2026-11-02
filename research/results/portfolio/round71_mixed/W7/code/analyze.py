"""Stream W7: grade the declared cells (HYPOTHESES_W7.md) on IS 2020-21 / VAL 2022-24. Reads the compact npz from
research/data/listing_window/npz, never anything >= 2025-01-01. Usage: python -I analyze.py [--desc]
--desc prints only the discount distribution at the signal times (no returns)."""
import csv, json, os, sys
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/listing_window"
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
W7 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round71_mixed/W7"
END = 1735689600000
SIG = (15, 60)
KS = (50, 100)
EXITS = (0, 30)
SENS_EXITS = (-240, 240)  # withdrawal clock +- 4 h (sensitivity, information)
FILL_MAX = 300  # s to find a taker print of the needed side
rng = np.random.default_rng(71)


def load_dff():
    d = {}
    for r in csv.DictReader(open(os.path.join(R, "rates/DFF.csv"))):
        try:
            d[r["observation_date"]] = float(r["DFF"])
        except ValueError:
            pass
    return d


DFF = load_dff()


def load_funding(leg, sym):
    paths = ([os.path.join(R, "binance/funding", sym + ".csv"), os.path.join(R, "binance/funding_window", sym + ".csv"),
              os.path.join(D, "funding", "bn_" + sym + ".csv")] if leg == "bnperp" else
             [os.path.join(R, "bybit/funding", sym + ".csv"), os.path.join(R, "bybit_basis/funding", sym + ".csv"),
              os.path.join(D, "funding", "by_" + sym + ".csv")])
    t, r = [], []
    for p in paths:
        if os.path.exists(p):
            for row in csv.DictReader(open(p)):
                tt = int(float(row["t"]))
                if tt < END:
                    t.append(tt); r.append(float(row["rate"]))
    if not t:
        return None
    t = np.array(t); r = np.array(r); o = np.argsort(t)
    t, i = np.unique(t[o], return_index=True)
    return t, r[o][i]


class Series:
    def __init__(self, path):
        z = np.load(path, allow_pickle=False)
        self.ok = "missing" not in z.files
        if not self.ok:
            return
        self.w0 = int(z["w0"]); self.t_first = int(z["t_first"])
        for k in ("last", "fb", "fs", "lb", "ls", "nb", "ns"):
            setattr(self, k, z[k])
        self.n = len(self.last)
        # forward-filled last taker-buy / sell / trade with the age of the print
        idx = np.arange(self.n)
        self.ff = {}
        for k in ("lb", "ls", "last"):
            a = getattr(self, k); has = np.isfinite(a)
            j = np.where(has, idx, -1); np.maximum.accumulate(j, out=j)
            self.ff[k] = (np.where(j >= 0, a[np.maximum(j, 0)], np.nan), np.where(j >= 0, idx - j, 10 ** 9))
        # next index with a first taker-buy / sell print at or after i
        self.nx = {}
        for k in ("fb", "fs"):
            a = getattr(self, k); has = np.isfinite(a)
            j = np.where(has, idx, self.n); j = np.minimum.accumulate(j[::-1])[::-1]
            self.nx[k] = j

    def sec(self, ms):
        return int((ms - self.w0) // 1000)

    def mid(self, ms, max_age=60):
        """Mid estimate from data strictly before ms: mean of the last taker-buy and taker-sell prints <= 60 s old,
        else the last trade (<= 300 s old)."""
        i = self.sec(ms) - 1
        if i < 0 or i >= self.n:
            return np.nan
        b, ab = self.ff["lb"][0][i], self.ff["lb"][1][i]
        s, as_ = self.ff["ls"][0][i], self.ff["ls"][1][i]
        if ab <= max_age and as_ <= max_age:
            return 0.5 * (b + s)
        l, al = self.ff["last"][0][i], self.ff["last"][1][i]
        return l if al <= 300 else np.nan

    def fill(self, ms, side):
        """First taker print of side ('fb' = we buy, 'fs' = we sell) in a second >= ms; (price, delay s)."""
        i = max(self.sec(ms), 0)
        if i >= self.n:
            return np.nan, None
        j = self.nx[side][i]
        if j >= self.n or j - i > FILL_MAX:
            return np.nan, None
        return float(getattr(self, side)[j]), j - i

    def halfspread(self, ms, win=10):
        i = max(self.sec(ms), 0); a, b = self.fb[i:i + win], self.fs[i:i + win]
        if np.isfinite(a).any() and np.isfinite(b).any():
            m = 0.5 * (np.nanmean(a) + np.nanmean(b))
            return max(0.0, 1e4 * (np.nanmean(a) - np.nanmean(b)) / 2 / m)
        return np.nan


def fees(leg, ms):
    perp = 5.0 if leg == "bnperp" else (7.5 if ms < 1676592000000 else 5.5)  # Bybit 5.5 bp from 2023-02-17
    return 2 * 10.0 + 2 * perp  # spot taker 10 bp a side + perp taker a side, round trip


def dff_bp(ms, hours):
    day = str(np.datetime64(int(ms), "ms"))[:10]
    r = DFF.get(day)
    k = sorted(DFF)
    if r is None:
        r = DFF[max(x for x in k if x <= day)]
    return r / 100 / 365 * hours / 24 * 1.5 * 1e4  # spot notional + 50 % perp margin, excess over Fed funds


def trade(sp, rf, leg, fund, t_in, t_out, late=0):
    """Long spot / short ref perp from t_in (+late s) to t_out. Returns dict or None."""
    a = t_in + late * 1000
    se, dse = sp.fill(a, "fb"); pe, dpe = rf.fill(a, "fs")
    sx, dsx = sp.fill(t_out, "fs"); px, dpx = rf.fill(t_out, "fb")
    if not np.all(np.isfinite([se, pe, sx, px])):
        return None
    spot = 1e4 * (sx / se - 1); hedge = -1e4 * (px / pe - 1)
    ti = a + 1000 * max(dse, dpe); to = t_out + 1000 * max(dsx, dpx)
    f = 0.0
    if fund is not None:
        m = (fund[0] > ti) & (fund[0] <= to)
        f = 1e4 * float(fund[1][m].sum())
    fee = fees(leg, a); dff = dff_bp(a, (to - ti) / 3.6e6)
    hs = np.nansum([sp.halfspread(a), rf.halfspread(a), sp.halfspread(t_out), rf.halfspread(t_out)])
    net = spot + hedge + f - fee - dff
    return dict(spot=spot, hedge=hedge, fund=f, fee=fee, dff=dff, hs=hs, net=net, net15=net - 0.5 * fee - 0.5 * hs)


def cl_t(x, g):
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return np.nan
    m = x.mean(); u = {}
    for xi, gi in zip(x, g):
        u[gi] = u.get(gi, 0.0) + (xi - m)
    G = len(u)
    if G < 2:
        return np.nan
    v = sum(s * s for s in u.values()) / n ** 2 * G / (G - 1)
    return m / np.sqrt(v) if v > 0 else np.nan


def load_events():
    out = []
    for e in csv.DictReader(open(os.path.join(D, "meta", "pull_list.csv"))):
        p = os.path.join(D, "npz", f"{e['sym']}_{e['L_day']}_spot.npz")
        if not os.path.exists(p):
            continue
        sp = Series(p)
        if not sp.ok or sp.t_first < 0:
            continue
        e["sp"] = sp
        e["L0"] = sp.t_first // 60000 * 60000  # listing clock: first spot trade floored to the minute
        e["W"] = e["L0"] + 86400000  # withdrawal clock approximation
        for leg in ("bnperp", "byperp"):
            q = os.path.join(D, "npz", f"{e['sym']}_{e['L_day']}_{leg}.npz")
            e[leg] = Series(q) if os.path.exists(q) else None
        e["year"] = int(e["L_day"][:4]); e["era"] = "IS" if e["year"] <= 2021 else "VAL"
        out.append(e)
    return out


def ref_at(e, S):
    """Binance perp if live (first trade before S and a print in the 300 s before S), else Bybit."""
    for leg in ("bnperp", "byperp"):
        r = e[leg]
        if r is not None and r.ok and 0 <= r.t_first < S - 60000:
            i = r.sec(S) - 1
            if 0 <= i < r.n and r.ff["last"][1][i] <= 300:
                return leg, r
    return None, None


def signal(e, m):
    S = e["L0"] + m * 60000
    leg, rf = ref_at(e, S)
    if rf is None:
        return None
    a, b = e["sp"].mid(S), rf.mid(S)
    if not (np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0):
        return None
    f = 10.0 ** np.round(np.log10(a / b))
    d = 1e4 * np.log(a / (f * b))
    return dict(S=S, leg=leg, rf=rf, d=d, f=f)


def stats(rows, key="net"):
    x = np.array([r[key] for r in rows], float)
    if len(x) == 0:
        return dict(n=0)
    g = [r["day"] for r in rows]
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    return dict(n=len(x), days=len(set(g)), mean=x.mean(), median=float(np.median(x)), t=cl_t(x, g),
                sr=x.mean() / sd if sd and sd > 0 else np.nan, win=float((x > 0).mean()))


def main():
    desc = "--desc" in sys.argv
    evs = load_events()
    # data error screen (declared): |d| >= 2000 bp at a signal time
    sig = {}
    for e in evs:
        for m in SIG:
            s = signal(e, m)
            if s is not None and abs(s["d"]) >= 2000:
                s["bad"] = True
            sig[(e["sym"], m)] = s
    print("events with spot data:", len(evs), " by era:", {er: sum(e["era"] == er for e in evs) for er in ("IS", "VAL")})
    for m in SIG:
        for er in ("IS", "VAL"):
            ds = [sig[(e["sym"], m)]["d"] for e in evs if e["era"] == er and sig[(e["sym"], m)] is not None
                  and not sig[(e["sym"], m)].get("bad")]
            legs = [sig[(e["sym"], m)]["leg"] for e in evs if e["era"] == er and sig[(e["sym"], m)] is not None
                    and not sig[(e["sym"], m)].get("bad")]
            bad = sum(1 for e in evs if e["era"] == er and sig[(e["sym"], m)] is not None and sig[(e["sym"], m)].get("bad"))
            ds = np.array(ds)
            if len(ds) == 0:
                print(f"discount +{m} {er}: n 0"); continue
            q = np.percentile(ds, [5, 10, 25, 50, 75, 90, 95])
            print(f"discount +{m}min {er}: n {len(ds)} (bn {legs.count('bnperp')} / by {legs.count('byperp')}, bad {bad}) "
                  f"q5/10/25/50/75/90/95 {' / '.join(f'{v:+.0f}' for v in q)} bp; <=-50 {np.sum(ds <= -50)}, "
                  f"<=-100 {np.sum(ds <= -100)}, >=+50 {np.sum(ds >= 50)}, >=+100 {np.sum(ds >= 100)}")
    if desc:
        return
    res = {}
    trades_out = []
    cells = [(m, k, x) for m in SIG for k in KS for x in EXITS]
    for (m, k, x) in cells:
        name = f"S{m}_k{k}_X{x}"
        rows = []
        for e in evs:
            s = sig[(e["sym"], m)]
            if s is None or s.get("bad") or s["d"] > -k:
                continue
            rf = s["rf"]; fund = load_funding(s["leg"], str(np.asarray(np.load(os.path.join(
                D, "npz", f"{e['sym']}_{e['L_day']}_{s['leg']}.npz"))["sym"])))
            tout = e["W"] + x * 60000
            tr = trade(e["sp"], rf, s["leg"], fund, s["S"], tout)
            if tr is None:
                continue
            late = trade(e["sp"], rf, s["leg"], fund, s["S"], tout, late=60)
            sens = {dx: trade(e["sp"], rf, s["leg"], fund, s["S"], e["W"] + dx * 60000) for dx in SENS_EXITS}
            day = str(np.datetime64(int(s["S"]), "ms"))[:10]
            # capacity: spot taker-buy quote notional in the 60 s after the entry
            i = e["sp"].sec(s["S"]); cap = float(e["sp"].nb[i:i + 60].sum())
            r = dict(sym=e["sym"], era=e["era"], year=e["year"], day=day, leg=s["leg"], d=s["d"], cap=cap,
                     late=late["net"] if late else np.nan,
                     sens_m=sens[SENS_EXITS[0]]["net"] if sens[SENS_EXITS[0]] else np.nan,
                     sens_p=sens[SENS_EXITS[1]]["net"] if sens[SENS_EXITS[1]] else np.nan, **tr)
            rows.append(r)
            trades_out.append(dict(cell=name, **{kk: v for kk, v in r.items()}))
        # random: same coin, random second in [L0 + 15 min, L0 + 23 h], unconditional, same exit / fills / costs
        rnd = {}
        for er in ("IS", "VAL"):
            ev_rows = [r for r in rows if r["era"] == er]
            if not ev_rows:
                continue
            means, ts = [], []
            pre = []
            for r in ev_rows:
                e = next(z for z in evs if z["sym"] == r["sym"])
                s = sig[(e["sym"], m)]
                fund = load_funding(s["leg"], str(np.asarray(np.load(os.path.join(
                    D, "npz", f"{e['sym']}_{e['L_day']}_{s['leg']}.npz"))["sym"])))
                pool = []
                for _ in range(400):
                    u = e["L0"] + int(rng.integers(15 * 60, 23 * 3600)) * 1000
                    tr = trade(e["sp"], s["rf"], s["leg"], fund, u, e["W"] + x * 60000)
                    if tr is not None:
                        pool.append(tr["net"])
                pre.append((np.array(pool), r["day"]))
            for _ in range(1000):
                xs = np.array([p[rng.integers(len(p))] for p, _ in pre if len(p)])
                gs = [d for p, d in pre if len(p)]
                means.append(xs.mean()); ts.append(cl_t(xs, gs))
            rnd[er] = (np.array(means), np.array(ts))
        res[name] = dict(rows=rows, rnd=rnd)
    # report
    out = {}
    print("\ncell | era | n (days) | net | median | t | SR | win | x1.5 | late+60s | spot leg | hedge leg | funding | fees | "
          "half-spread (info) | W-4h / W+4h | years | random % | power")
    nullmax = {er: [] for er in ("IS", "VAL")}
    for name, v in res.items():
        out[name] = {}
        for er in ("IS", "VAL"):
            rows = [r for r in v["rows"] if r["era"] == er]
            st = stats(rows)
            if st["n"] == 0:
                print(f"{name} | {er} | 0"); out[name][er] = st; continue
            mean = lambda k: float(np.nanmean([r[k] for r in rows]))
            yrs = {}
            for r in rows:
                yrs.setdefault(r["year"], []).append(r["net"])
            ystr = ", ".join(f"{y} {np.mean(a):+.0f} ({len(a)})" for y, a in sorted(yrs.items()))
            rp = float((v["rnd"][er][0] < st["mean"]).mean() * 100) if er in v["rnd"] else np.nan
            pw = st["sr"] * np.sqrt(st["n"] / 3 * 1.83) if er == "VAL" and np.isfinite(st["sr"]) else np.nan
            legs = sum(r["leg"] == "bnperp" for r in rows)
            print(f"{name} | {er} | {st['n']} ({st['days']}) | {st['mean']:+.1f} | {st['median']:+.1f} | {st['t']:.2f} | "
                  f"{st['sr']:.2f} | {st['win']:.0%} | {mean('net15'):+.1f} | {mean('late'):+.1f} | {mean('spot'):+.1f} | "
                  f"{mean('hedge'):+.1f} | {mean('fund'):+.1f} | {mean('fee'):.1f} | {mean('hs'):.1f} | "
                  f"{mean('sens_m'):+.1f} / {mean('sens_p'):+.1f} | {ystr} | {rp:.1f} | {pw:.2f} | bn {legs} by {st['n'] - legs}")
            out[name][er] = dict(st, x15=mean("net15"), late=mean("late"), spot=mean("spot"), hedge=mean("hedge"),
                                 fund=mean("fund"), fee=mean("fee"), hs=mean("hs"), sens_m=mean("sens_m"),
                                 sens_p=mean("sens_p"), years={str(y): [float(np.mean(a)), len(a)] for y, a in yrs.items()},
                                 random_pct=rp, power=pw, bn=legs, cap_median=float(np.median([r["cap"] for r in rows])))
    # max-over-cells null of t (random draws), per era
    for er in ("IS", "VAL"):
        tmat = np.array([res[n]["rnd"][er][1] for n in res if er in res[n]["rnd"]])
        real = [out[n][er].get("t", np.nan) for n in res if er in res[n]["rnd"]]
        if len(tmat):
            mx = np.nanmax(tmat, axis=0)
            print(f"max-over-cells null t {er}: real max {np.nanmax(real):.2f}; null median {np.nanmedian(mx):.2f}, "
                  f"p95 {np.nanpercentile(mx, 95):.2f}; p = {np.mean(mx >= np.nanmax(real)):.3f}")
    json.dump(out, open(os.path.join(W7, "out", "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(W7, "out", "trades.csv"), "w", newline="") as f:
        ks = list(trades_out[0].keys()) if trades_out else ["cell"]
        w = csv.DictWriter(f, fieldnames=ks); w.writeheader(); w.writerows(trades_out)


if __name__ == "__main__":
    main()
