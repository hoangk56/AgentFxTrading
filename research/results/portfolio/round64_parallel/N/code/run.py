"""Stream N driver: reproduce B, simulate inventory configurations, B overlay, coverage, concurrency, drawdowns.
Usage: research/.venv/bin/python run.py [configs...]   (writes ../out/report.txt and ../out/results.json)"""
import json, os, sys, time
import numpy as np
from inventory import load, simulate, cl_t, DAY, H, ERAS, YEARS, CUT, settled_mask, sim_coin, nw_t
import basis

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
BASE = dict(N=1.25, lo=1.0, hi=1.5, m=0.5, cost_mult=1.0, guard=True, hyst=48, sel="all", M=None)
CONFIGS = {
    "P": {},
    "P_noguard": dict(guard=False),
    "P_cost1.5": dict(cost_mult=1.5),
    "m0.25": dict(m=0.25),
    "m1.0": dict(m=1.0),
    "band0.9-1.75": dict(lo=0.9, hi=1.75),
    "IS_top10": dict(sel="istop", M=10),
    "IS_top20": dict(sel="istop", M=20),
    "rank<10": dict(sel="rank", M=10),
    "rank<20": dict(sel="rank", M=20),
    "rank<30": dict(sel="rank", M=30),
    "rank<40": dict(sel="rank", M=40),
    # post-hoc information variants (added after seeing P's liquidation list and churn; not declared)
    "info_rehedge": dict(liq_mode="rehedge"),
    "info_m1.0_rehedge": dict(m=1.0, liq_mode="rehedge"),
    "info_hyst14d": dict(hyst=336),
}
D0 = int(np.datetime64("2019-09-01", "ms").astype(np.int64)) // DAY
ND = CUT // DAY - D0
YRS = {"IS": 731 / 365.25, "VAL": 1096 / 365.25}


def era_days(a, b):
    return slice(a // DAY - D0, b // DAY - D0)


def maxdd(x):
    c = np.cumsum(x)
    peak = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float((peak - c).max()) if len(c) else 0.0


def run_config(coins, settled, T, name, ov, istop):
    p = dict(BASE); p.update(ov)
    agg = {k: np.zeros(ND) for k in ("price", "fund", "cash", "cap", "build", "reset", "unwind", "liq", "held")}
    ev = {}
    per_coin = []
    covered = np.zeros(len(T["e"]))
    for ci, c in enumerate(coins):
        want = c["inU"].copy()
        if p["sel"] == "istop":
            if ci not in istop[:p["M"]]:
                continue
        elif p["sel"] == "rank":
            want &= c["rank"] < p["M"]
        if not want.any():
            continue
        r = sim_coin(c, want, p, settled[ci])
        if r is None:
            continue
        d = (c["hours"] // DAY - D0).astype(int)
        ok = (d >= 0) & (d < ND)
        for k in ("price", "fund", "cash", "cap"):
            np.add.at(agg[k], d[ok], r[k][ok])
        for k in ("build", "reset", "unwind", "liq"):
            np.add.at(agg[k], d[ok], r["cost"][k][ok])
        np.add.at(agg["held"], d[ok], r["held"][ok].astype(float))
        for k, v in r["ev"].items():
            ev.setdefault(k, {e: 0 for e in ERAS})
        # events by era: approximate by counting per-hour cost markers is messy; count totals by era from arrays
        net_c = r["price"] + r["fund"] - sum(r["cost"].values())
        tot = {}
        for e, (a, b) in ERAS.items():
            w = (c["hours"] >= a) & (c["hours"] < b)
            tot[e] = float(net_c[w].sum()), float((r["fund"][w]).sum()), float(r["price"][w].sum())
            ev["resets"][e] += int(((r["cost"]["reset"] > 0) & w).sum())
            ev["liqs"][e] += int(((r["cost"]["liq"] > 0) & w).sum())
            ev["builds"][e] += int(((r["cost"]["build"] > 0) & w).sum())
            ev["unwinds"][e] += int(((r["cost"]["unwind"] > 0) & w).sum())
            ev["settled_unwinds"][e] += int(((r["kind"] == 1) & w).sum())
            ev["stale_unwinds"][e] += int(((r["kind"] == 2) & w).sum())
        per_coin.append((c["perp"], tot))
        w = np.where(T["ci"] == ci)[0]
        if len(w):
            covered[w] = r["cover"][T["e"][w]]
    agg["held"] /= 24.0
    agg["cost"] = agg["build"] + agg["reset"] + agg["unwind"] + agg["liq"]
    agg["inv"] = agg["price"] + agg["fund"] - agg["cost"]
    agg["capd"] = agg["cap"] / 24.0          # mean capital that day (Q)
    # B overlay in this route: price + funding - B costs (no borrow, no spot-leg cash charge), scaled by coverage
    broute = (T["price"] + T["fund"] - T["cost"]) * covered
    bfull = T["price"] + T["fund"] - T["cost"]
    bday = np.zeros(ND)
    xd = ((T["t"] + (T["x"] - T["e"]) * H) // DAY - D0).astype(int)
    np.add.at(bday, np.clip(xd, 0, ND - 1), broute)
    res = dict(params=p, eras={}, years={})
    def block(sl, mask_t, yrs):
        cap = agg["capd"][sl]
        mc = cap[cap > 0].mean() if (cap > 0).any() else np.nan
        mcap_all = cap.mean()
        s = {k: float(agg[k][sl].sum() / yrs) for k in ("price", "fund", "build", "reset", "unwind", "liq", "cost", "inv", "cash")}
        s["excess_inv"] = s["inv"] - s["cash"]
        nb = int(mask_t.sum()); ncov = float((covered[mask_t] > 0).sum())
        s["B_n_all"] = nb
        s["B_n_cov"] = int(ncov)
        s["B_share_trades"] = ncov / nb if nb else np.nan
        s["B_cov_frac_mean"] = float(covered[mask_t].mean()) if nb else np.nan
        s["B_share_pnl"] = float(broute[mask_t].sum() / bfull[mask_t].sum()) if nb else np.nan
        s["B_route_Qyr"] = float(broute[mask_t].sum() / yrs)
        s["B_frozen_net_bp"] = float(T["net"][mask_t].mean() * 1e4) if nb else np.nan
        s["B_route_bp_cov"] = float(broute[mask_t][covered[mask_t] > 0].sum() / max(covered[mask_t].sum(), 1e-9) * 1e4) if nb else np.nan
        s["combined"] = s["inv"] + s["B_route_Qyr"]
        s["excess_comb"] = s["combined"] - s["cash"]
        s["cap_mean"] = float(mcap_all)
        s["cap_max"] = float(cap.max())
        s["held_mean"] = float(agg["held"][sl].mean())
        s["held_max"] = float(agg["held"][sl].max())
        s["cash_rate"] = float(s["cash"] / mcap_all) if mcap_all > 0 else np.nan
        for k in ("inv", "excess_inv", "combined", "excess_comb", "fund", "price", "cost"):
            s[k + "_pct"] = float(s[k] / mcap_all * 100) if mcap_all > 0 else np.nan
        s["route_cost_Qyr"] = -s["excess_inv"]
        s["route_cost_per_Btrade_bp"] = float(s["route_cost_Qyr"] / (ncov / yrs) * 1e4) if ncov else np.nan
        dex = agg["inv"][sl] + bday[sl] - agg["cash"][sl]
        s["t_nw_excess_comb"] = float(nw_t(dex))
        s["t_nw_excess_inv"] = float(nw_t(agg["inv"][sl] - agg["cash"][sl]))
        s["dd_comb_Q"] = maxdd(agg["inv"][sl] + bday[sl])
        s["dd_inv_Q"] = maxdd(agg["inv"][sl])
        s["dd_excess_comb_Q"] = maxdd(dex)
        s["dd_comb_pct"] = float(s["dd_comb_Q"] / mcap_all * 100) if mcap_all > 0 else np.nan
        s["worst_day_comb_Q"] = float((agg["inv"][sl] + bday[sl]).min())
        return s
    for e, (a, b) in ERAS.items():
        mt = (T["t"] >= a) & (T["t"] < b)
        res["eras"][e] = block(era_days(a, b), mt, YRS[e])
        res["eras"][e]["events"] = {k: v[e] for k, v in ev.items() if isinstance(v, dict)}
    for y, a, b in YEARS:
        mt = (T["t"] >= a) & (T["t"] < b)
        res["years"][y] = block(era_days(a, b), mt, (b - a) / DAY / 365.25)
    res["per_coin"] = per_coin
    res["_agg"] = agg
    res["_bday"] = bday
    res["_covered"] = covered
    return res


def concurrency(T, coins):
    out = {}
    for e, (a, b) in ERAS.items():
        h0, h1 = a // H, b // H
        cnt = np.zeros(h1 - h0)
        for ci, ee, xx in zip(T["ci"], T["e"], T["x"]):
            s = coins[ci]["hours"][ee] // H - h0
            L = xx - ee
            if 0 <= s < len(cnt):
                cnt[s:s + L] += 1
        act = cnt[cnt > 0]
        out[e] = dict(max=int(cnt.max()), p999=float(np.percentile(cnt, 99.9)), p99=float(np.percentile(cnt, 99)),
                      p95=float(np.percentile(cnt, 95)), mean=float(cnt.mean()), share_hours_open=float((cnt > 0).mean()),
                      p95_when_open=float(np.percentile(act, 95)) if len(act) else 0.0)
    return out


def main(names):
    t0 = time.time()
    coins = load()
    T = simulate(coins, 100, 24, -1)
    rep = {e: basis.summarize(T, e) for e in ERAS}
    print("coins", len(coins), "load+B s", round(time.time() - t0), flush=True)
    print("B repro", {e: (r["n"], round(r["net_bp"], 1), round(r["t"], 2)) for e, r in rep.items()}, flush=True)
    assert rep["IS"]["n"] == 303 and abs(rep["IS"]["net_bp"] - 286.5) < 0.1 and abs(rep["IS"]["t"] - 2.46) < 0.01
    assert rep["VAL"]["n"] == 333 and abs(rep["VAL"]["net_bp"] - 174.6) < 0.1
    assert max(c["hours"].max() for c in coins) < CUT
    settled = [settled_mask(c) for c in coins]
    sett = [(coins[i]["perp"], int(s.sum()), str(np.datetime64(int(coins[i]["hours"][np.argmax(s)]), "ms"))[:13])
            for i, s in enumerate(settled) if s.any()]
    print("settled-perp runs", sett, flush=True)
    a, b = ERAS["IS"]
    mi = (T["t"] >= a) & (T["t"] < b)
    cnts = np.bincount(T["ci"][mi], minlength=len(coins))
    netis = np.bincount(T["ci"][mi], weights=T["net"][mi], minlength=len(coins))
    istop = [int(i) for i in np.lexsort((-netis, -cnts)) if cnts[i] > 0]
    conc = concurrency(T, coins)
    print("concurrency", conc, flush=True)
    results = dict(B_repro={e: {k: float(v) for k, v in r.items()} for e, r in rep.items()}, settled=sett,
                   istop=[(coins[i]["perp"], int(cnts[i]), float(netis[i] * 1e4)) for i in istop[:20]],
                   concurrency=conc, configs={})
    for nm in names:
        r = run_config(coins, settled, T, nm, CONFIGS[nm], istop)
        if nm == "P":
            np.savez(os.path.join(OUT, "daily_P.npz"), bday=r["_bday"], covered=r["_covered"],
                     **{k: v for k, v in r["_agg"].items()})
        for k in ("_agg", "_bday", "_covered"):
            r.pop(k)
        results["configs"][nm] = r
        E = r["eras"]
        print(nm, round(time.time() - t0), {e: dict(cap=round(E[e]["cap_mean"], 1), inv=round(E[e]["inv"], 2),
              cash=round(E[e]["cash"], 2), exc=round(E[e]["excess_inv"], 2), B=round(E[e]["B_route_Qyr"], 2),
              exc_comb_pct=round(E[e]["excess_comb_pct"], 2), share=round(E[e]["B_share_pnl"], 2)) for e in E}, flush=True)
    tag = "_".join(n.replace("<", "lt") for n in names) if len(names) < len(CONFIGS) else "all"
    with open(os.path.join(OUT, f"results_{tag}.json"), "w") as f:
        json.dump(results, f, indent=1, default=float)
    print("done s", round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:] or list(CONFIGS))
