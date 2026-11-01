"""HOLD look of the registered cell k100_H24_cheap (PREREG_B_cheap_basis.md), run once.
Imports the frozen universe.py / basis.py unchanged and only overrides at runtime: universe.END and basis.CUT ->
2026-10-30 00:00 UTC, basis.ERAS['HOLD'] = 2025-01-01..2026-10-30.
  hold_run.py check   data coverage only (no events, no returns)
  hold_run.py run     the registered HOLD result
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import universe
HOLD = (1735689600000, 1793318400000)
universe.END = HOLD[1]
import basis
basis.CUT = HOLD[1]
basis.ERAS["HOLD"] = HOLD
from basis import load, simulate, summarize, cl_t, DAY


def ts(ms):
    return str(np.datetime64(int(ms), "ms"))[:16]


def check():
    keep, U, R, days = universe.universe(60)
    coins = load()
    have = {c["perp"] for c in coins}
    d0 = np.searchsorted(days, HOLD[0])
    hold_syms = [keep[i][0] for i in np.where(U[:, d0:].any(1))[0] if keep[i][0] not in basis.EXCL]
    miss = [s for s in hold_syms if s not in have]
    print("HOLD universe alts", len(hold_syms), "loaded", len(hold_syms) - len(miss), "missing", miss)
    tot_u = tot_v = 0
    low = []
    nofund = []
    for c in coins:
        w = c["inU"] & (c["hours"] >= HOLD[0]) & (c["hours"] < HOLD[1])
        if not w.any():
            continue
        v = w & ~np.isnan(c["b"] - c["m"])
        tot_u += w.sum(); tot_v += v.sum()
        if v.sum() < 0.5 * w.sum():
            low.append((c["perp"], int(w.sum()), int(v.sum()), round(float(np.nanmedian(c["tickS"][w])) * 1e4, 1)))
        # funding coverage: last stamp vs last traded perp hour in HOLD
        f = np.where(np.diff(np.concatenate([[0.0], c["fcum"]])) != 0)[0]
        lastf = c["hours"][f[-1]] if len(f) else -1
        tr = np.where(w & (c["Fn"] >= 20))[0]
        if len(tr) and c["hours"][tr[-1]] > lastf + 2 * DAY:
            nofund.append((c["perp"], ts(lastf) if lastf > 0 else None, ts(c["hours"][tr[-1]]), c["has_funding"]))
    print(f"HOLD universe coin-hours {tot_u}, valid deviation {tot_v} ({tot_v / max(tot_u, 1):.1%})")
    print("coins with < 50 % valid HOLD universe hours (perp, hours, valid, median spot rel tick bp):", len(low))
    for x in low:
        print("  ", x)
    print("coins with perp trading > 2 days past last funding stamp:", nofund)


def run():
    coins = load()
    names = np.array([c["perp"] for c in coins])
    print("coins loaded", len(coins))
    T = simulate(coins, 100, 24, -1)
    TL = simulate(coins, 100, 24, -1, lag=1)
    T15 = dict(T); T15["net"] = T["net"] - 0.5 * T["cost"]
    print("\nreproduction check (registered IS 303 / +286.5 / t 2.46, VAL 333 / +174.6 / t 6.41):")
    for era in ("IS", "VAL"):
        s = summarize(T, era)
        print(f"  {era}: n {s['n']} net {s['net_bp']:.1f} t {s['t']:.2f}")
    a, b = HOLD
    m = (T["t"] >= a) & (T["t"] < b)
    mL = (TL["t"] >= a) & (TL["t"] < b)
    x, xL, x15 = T["net"][m], TL["net"][mL], T15["net"][m]
    day, dayL = T["t"][m] // DAY, TL["t"][mL] // DAY
    s = summarize(T, "HOLD")
    print("\n=== HOLD 2025-01-01..2026-10-29, k100_H24_cheap, taker costs ===")
    if not len(x):
        print("no trades"); return
    print(f"n {len(x)}  event-days {s['days']}  coins {len(np.unique(T['ci'][m]))}")
    print(f"net {x.mean()*1e4:.1f} bp  median {np.median(x)*1e4:.1f}  t(day) {cl_t(x, day):.2f}  win {np.mean(x > 0):.0%}"
          f"  SR/trade {s['sr']:.3f}  SR/day {s['sr_day']:.3f}")
    print(f"gross {s['gross_bp']:.1f}  funding {s['fund_bp']:.1f}  cost {s['cost_bp']:.1f}  carry {s['carry_bp']:.2f}"
          f"  hold {s['hold_h']:.1f} h  forced {s['forced']}  adv>25% {s['adv25']:.1%}  adv>50% {s['adv50']:.1%}")
    print(f"costs x1.5: net {x15.mean()*1e4:.1f} bp  t {cl_t(x15, day):.2f}")
    print(f"one hour late: n {len(xL)} net {xL.mean()*1e4:.1f} bp  median {np.median(xL)*1e4:.1f}  t {cl_t(xL, dayL):.2f}")
    y = np.asarray(T["t"][m], dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    for yy in (2025, 2026):
        w = y == yy
        if w.any():
            print(f"year {yy}: n {w.sum()} net {x[w].mean()*1e4:.1f} bp median {np.median(x[w])*1e4:.1f}"
                  f" t {cl_t(x[w], day[w]):.2f}")
        else:
            print(f"year {yy}: n 0")
    sym = names[T["ci"][m]]
    u, inv = np.unique(sym, return_inverse=True)
    sc = np.bincount(inv, weights=x); o = np.argsort(-sc)
    print(f"share of HOLD P&L from top 5 coins: {sc[o[:5]].sum() / x.sum():.2f}",
          [(u[j], int((inv == j).sum()), round(sc[j] * 1e4, 0)) for j in o[:5]])
    ud, iv = np.unique(day, return_inverse=True); sd = np.bincount(iv, weights=x); od = np.argsort(-sd)
    print(f"share of HOLD P&L from top 5 days: {sd[od[:5]].sum() / x.sum():.2f}",
          [(ts(ud[j] * DAY)[:10], int((iv == j).sum()), round(sd[j] * 1e4, 0)) for j in od[:5]])
    print(f"bottom 5 coins:", [(u[j], int((inv == j).sum()), round(sc[j] * 1e4, 0)) for j in o[-5:]])
    idx = np.where(m)[0]
    for label, order in (("worst 10 trades", np.argsort(x)[:10]), ("best 10 trades", np.argsort(-x)[:10])):
        print(label + ":")
        for k in order:
            i = idx[k]; c = coins[T["ci"][i]]; e, xx, h = T["e"][i], T["x"][i], T["h"][i]
            print(f"  {c['perp']:14s} {ts(T['t'][i])} net {T['net'][i]*1e4:8.0f} price {T['price'][i]*1e4:8.0f}"
                  f" fund {T['fund'][i]*1e4:6.0f} hold {xx-e:3d} d {1e4*(c['b'][h]-c['m'][h]):6.0f}"
                  f" Fo {c['Fo'][e]:.5g}->{c['Fo'][xx]:.5g} So {c['So'][e]:.5g}->{c['So'][xx]:.5g}"
                  f" Fn {c['Fn'][h]:.0f} Sn {c['Sn'][h]:.0f} adv {T['adv'][i]:.2f} forced {T['forced'][i]}")
    o2 = np.argsort(-np.abs(x))
    print(f"top-10 |net| trades share of sum: {x[o2[:10]].sum() / x.sum():.2f}; trimmed 1 % mean "
          f"{np.sort(x)[int(.01*len(x)):len(x)-int(.01*len(x))].mean()*1e4:.1f} bp")
    print(f"\nVERDICT (registered DEMO bar: FAIL if HOLD net <= 0): {'PASS (DEMO bar)' if x.mean() > 0 else 'FAIL'}")


if __name__ == "__main__":
    {"check": check, "run": run}[sys.argv[1]]()
