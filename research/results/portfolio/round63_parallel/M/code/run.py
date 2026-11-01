"""Round 63 stream M: grade every single-symbol row at the venue cost (IS 2016-21, VAL 2022-24).
Usage: PYTHONPATH=<repo>:<this dir> python run.py [ids...]  -> out/<id>.json, out/<id>_trades.npz"""
import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np

import eng
import rules

import os
OUT = Path(__file__).resolve().parent.parent / ("out_r24read" if os.environ.get("M_R24READ") == "1" else "out")
OUT.mkdir(exist_ok=True)
SEEDS = 200
F = math.sqrt(1.73 / 3)


def era_masks(ms):
    return {"IS": ms < eng.VAL0, "VAL": ms >= eng.VAL0}


def n_years(ms, era):
    if era == "VAL":
        return 3.0
    first = dt.datetime.fromtimestamp(int(ms.min()) / 1000, eng.UTC)
    return (dt.datetime(2022, 1, 1, tzinfo=eng.UTC) - first).days / 365.25


def stats(t, m):
    ms = t["ms_in"][m]; day = eng.day_of(ms)
    g = t["gross"][m]; up = t["up"][m]; lo = t["lo"][m]; ic = t["ic"][m]
    nu = g - up
    mid, tmid = eng.cl_t(g, day)
    mu, tu = eng.cl_t(nu, day)
    ml, tl = eng.cl_t(g - lo, day)
    mic, tic = eng.cl_t(g - ic, day)
    se = mu / tu if tu and not np.isnan(tu) and tu != 0 else np.nan
    yrs = eng.year_of(ms)
    by = {int(y): float(np.nanmean(nu[yrs == y])) for y in np.unique(yrs)}
    return dict(n=int(m.sum()), mid=mid, t_mid=tmid, net_up=mu, t_up=tu, net_lo=ml, t_lo=tl, net_ic=mic, t_ic=tic,
                cost_up=float(np.nanmean(up)), cost_lo=float(np.nanmean(lo)), cost_ic=float(np.nanmean(ic)),
                x15=float(np.nanmean(g - 1.5 * up)), lat1=float(np.nanmean(t["gross1"][m] - t["up1"][m])),
                sd=float(np.nanstd(nu, ddof=1)), se=se, by_year=by)


def random_ctrl(r, t_rule, seed0=0):
    """% of seeds whose era mean (net at the upper bound) the rule beats, per era."""
    sym = r["sym"]; rng = np.random.default_rng(12345 + seed0)
    res = {"IS": [], "VAL": []}
    if r["ctrl"] == "day":
        (a, b, tz) = r["clock"]
        pool = r["pool"]
        ev = sorted(r["events"])
        for _ in range(SEEDS):
            pick = []
            for d in ev:
                era_val = d >= dt.date(2022, 1, 1)
                cand = [p for p in pool if p.weekday() == d.weekday() and (p >= dt.date(2022, 1, 1)) == era_val]
                pick.append(cand[rng.integers(len(cand))])
            ms_in = np.array([eng.loc_ms(d, *a, tz) for d in pick]); ms_out = np.array([eng.loc_ms(d, *b, tz) for d in pick])
            side = r["side_fn"](ms_in, np.arange(len(ms_in)))
            lg = eng.legs(sym, side, ms_in, ms_out)
            nu = lg["gross"] - lg["up"]
            for e, m in era_masks(ms_in).items():
                res[e].append(np.nanmean(nu[m]))
    else:
        n = len(r["ms_in"]); idx = np.arange(n)
        for _ in range(SEEDS):
            if r["ctrl"] == "fwd":
                s = rng.integers(1, 181, n)
            else:
                s = rng.integers(1, 181, n) * rng.choice([-1, 1], n)
            ms_in = r["ms_in"] + s * 60000; ms_out = r["ms_out"] + s * 60000
            side = r["side_fn"](ms_in, idx)
            lg = eng.legs(sym, side, ms_in, ms_out)
            nu = lg["gross"] - lg["up"]
            bad = eng.in_roll(ms_in, ms_out) | np.isnan(side) | (side == 0)
            nu = np.where(bad, np.nan, nu)
            for e, m in era_masks(r["ms_in"]).items():   # era by the rule's own day
                res[e].append(np.nanmean(nu[m]))
    out = {}
    for e, m in era_masks(t_rule["ms_in"]).items():
        mu = np.nanmean(t_rule["gross"][m] - t_rule["up"][m])
        arr = np.array(res[e])
        out[e] = float(100 * np.mean(mu > arr[~np.isnan(arr)]))
    return out


def grade(s, rnd):
    IS, VAL = s["IS"], s["VAL"]
    yrs = {**IS["by_year"], **VAL["by_year"]}
    ypos = sum(v > 0 for v in yrs.values()); ny = len(yrs)
    power = VAL["t_up"] * F
    checks = IS["x15"] > 0 and VAL["x15"] > 0 and IS["lat1"] > 0 and VAL["lat1"] > 0
    live = (IS["t_up"] >= 2.5 and VAL["t_up"] >= 1.5 and ypos >= 2 / 3 * ny and rnd["IS"] >= 95 and rnd["VAL"] >= 95
            and checks and power >= 3)
    demo = IS["t_up"] >= 2.0 and VAL["net_up"] > 0 and rnd["IS"] >= 90 and rnd["VAL"] >= 90 and checks
    live_lo = IS["t_lo"] >= 2.5 and VAL["t_lo"] >= 1.5 and VAL["t_lo"] * F >= 3
    demo_lo = IS["t_lo"] >= 2.0 and VAL["net_lo"] > 0
    se_is = IS["se"]; se_val = VAL["se"]
    live_cost = min(IS["mid"] - 2.5 * se_is, VAL["mid"] - 1.5 * se_val, VAL["mid"] - (3 / F) * se_val)
    p065 = (0.65 * VAL["mid"] - VAL["cost_up"]) / se_val * F
    fails = []
    if IS["t_up"] < 2.5: fails.append("IS t")
    if VAL["t_up"] < 1.5: fails.append("VAL t")
    if ypos < 2 / 3 * ny: fails.append("years")
    if min(rnd.values()) < 95: fails.append("random")
    if not checks: fails.append("x1.5/+1m")
    if power < 3: fails.append("power")
    tier = "LIVE" if live else ("DEMO" if demo else "none")
    return dict(tier=tier, years_pos=f"{ypos}/{ny}", power=power, power065=p065, live_cost=live_cost,
                tier_lo="LIVE" if live_lo else ("DEMO-numbers" if demo_lo else "none"), fails=fails)


def run_rule(fn):
    r = fn()
    side = r["side_fn"](r["ms_in"], np.arange(len(r["ms_in"])))
    t = eng.trades(r["sym"], side, r["ms_in"], r["ms_out"], carry=r.get("carry"))
    s = {e: stats(t, m) for e, m in era_masks(t["ms_in"]).items()}
    for e in s:
        s[e]["per_year"] = s[e]["n"] / n_years(t["ms_in"][era_masks(t["ms_in"])[e]], e)
    rnd = random_ctrl(r, t)
    g = grade(s, rnd)
    rec = dict(id=r["id"], sym=r["sym"], sel=rules.SEL[r["id"]], contaminated=r["id"] in rules.CONTAM, ctrl=r["ctrl"],
               IS=s["IS"], VAL=s["VAL"], random=rnd, **g)
    json.dump(rec, open(OUT / f"{r['id']}.json", "w"), indent=1, default=float)
    np.savez(OUT / f"{r['id']}_trades.npz", **{k: v for k, v in t.items() if k != "sym"})
    print(f"{r['id']:4s} {r['sym']:7s} IS n {s['IS']['n']:5d} mid {s['IS']['mid']:+.2f} up {s['IS']['net_up']:+.2f} "
          f"(t {s['IS']['t_up']:+.2f}) lo {s['IS']['net_lo']:+.2f} (t {s['IS']['t_lo']:+.2f}) | VAL n {s['VAL']['n']:4d} "
          f"mid {s['VAL']['mid']:+.2f} up {s['VAL']['net_up']:+.2f} (t {s['VAL']['t_up']:+.2f}) lo {s['VAL']['net_lo']:+.2f} "
          f"(t {s['VAL']['t_lo']:+.2f}) | rnd {rnd['IS']:.0f}/{rnd['VAL']:.0f} pow {g['power']:+.2f} "
          f"yrs {g['years_pos']} -> {g['tier']} (lo {g['tier_lo']})", flush=True)
    return rec


if __name__ == "__main__":
    want = set(sys.argv[1:])
    cur = None
    for fn in rules.SINGLE:
        if want and fn.__name__ not in want:
            continue
        rec = run_rule(fn)
        for k in list(eng._rows):
            if k != rec["sym"]:
                eng.drop(k)
