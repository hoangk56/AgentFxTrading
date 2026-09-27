"""M1, month-end value-date USD demand: the candidate of the 2026-09-27 round-3 search
(research/results/portfolio/prereg_month_end_usd_2026-09-27.md, flow_search_2026-09-27.md).

Buy USD against JPY, CHF and EUR from 10:00 to 13:00 UTC on the third-to-last weekday of the month, the last day
whose T+2 spot trade settles inside the month. One bot, three symbols, cap 3; stop 3 x ATR20(H1); 1x default lot.

    python -m research.swing.month_end_usd           # IS and VAL only
    python -m research.swing.month_end_usd --hold    # the registered holdout (run once)

Three USD pairs on the same day are close to one USD bet, so t is also given on day-clustered R (the sum of the
day's trades), which is the number the pre-registration judges.
"""
import argparse
import csv
import datetime
import math
from pathlib import Path

import numpy as np

from research.swing import swing as S
from research.swing import swing_rules as SR

SYMBOLS = ("USDJPY", "USDCHF", "EURUSD")
PARAMS = dict(bd=3, start_utc=10 * 60, end_utc=13 * 60, slk=3.0)
TF = (5, 0)
PF = Path(__file__).resolve().parents[1] / "results" / "portfolio"
SEEDS = 500


def run(spread_mult=1.0, symbols=SYMBOLS, **over):
    p = dict(PARAMS, **over)
    return S.run_bot(SR.month_end_usd, list(symbols), TF, cap=3, per_symbol=1, spread_mult=spread_mult, **p)


def in_eras(trades, eras):
    return [t for t in trades if S.era_of(t.t_in) in eras]


def day_sums(trades):
    out = {}
    for t in trades:
        out[t.t_in // S.DAY_MS] = out.get(t.t_in // S.DAY_MS, 0.0) + t.r
    return out


def clustered_t(trades):
    x = np.array(list(day_sums(trades).values()))
    if len(x) < 2:
        return len(x), float(x.mean()) if len(x) else 0.0, 0.0
    return len(x), float(x.mean()), float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x))))


def line(trades, label):
    n, mu, t = S.tstat([x.r for x in trades])
    nd, mud, td = clustered_t(trades)
    net = sum(x.usd for x in trades)
    years = {}
    for x in trades:
        years[S.year_of(x.t_in)] = years.get(S.year_of(x.t_in), 0.0) + x.usd
    return (f"{label:10s} n {n:4d} ({nd} days)  mean R {mu:+.3f}  t {t:+.1f}  day-clustered t {td:+.1f}  "
            f"net ${net:+,.0f}  years > 0: {sum(v > 0 for v in years.values())}/{len(years)}")


def random_day_control(eras, seeds=SEEDS):
    """Summed R of the real days vs 1 random other weekday per month (same symbols, window, side, stop)."""
    every = in_eras(run(bd=None), eras)
    per_day = day_sums(every)
    real = sum(t.r for t in in_eras(run(), eras))
    k_of = SR.weekdays_from_month_end(datetime.date(2016, 1, 1), datetime.date(2026, 9, 24))
    day0 = datetime.date(1970, 1, 1)
    by_month = {}
    for d, r in per_day.items():
        date = day0 + datetime.timedelta(days=int(d))
        if k_of.get(date) != PARAMS["bd"]:
            by_month.setdefault((date.year, date.month), []).append(r)
    rng = np.random.default_rng(7)
    ctrl = np.array([sum(rng.choice(v) for v in by_month.values()) for _ in range(seeds)])
    return real, float(ctrl.mean()), float(ctrl.std()), float(np.mean(real > ctrl))


def max_dd(trades):
    curve = np.cumsum([t.usd for t in sorted(trades, key=lambda t: t.t_out)])
    return float(np.max(np.maximum.accumulate(np.r_[0.0, curve]) - np.r_[0.0, curve])) if len(curve) else 0.0


def load_other(name):
    out = []
    with open(PF / name) as fh:
        for r in csv.DictReader(fh):
            t = datetime.datetime.strptime(r["t_out_utc"], "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)
            out.append((int(t.timestamp() * 1000), float(r["usd_at_100_risk"])))
    return out


def pnl_corr(trades, other, lo, hi):
    """Daily and monthly P&L correlation (weekdays, zeros on days without a trade)."""
    def agg(pairs, key):
        d = {}
        for t, v in pairs:
            if lo <= t < hi:
                d[key(t)] = d.get(key(t), 0.0) + v
        return d
    dkey = lambda t: t // S.DAY_MS
    mkey = lambda t: (S.year_of(t), datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).month)
    mine = [(t.t_out, t.usd) for t in trades]
    a, b = agg(mine, dkey), agg(other, dkey)
    days = [k for k in range(lo // S.DAY_MS, hi // S.DAY_MS) if (k + 3) % 7 < 5]
    am, bm = agg(mine, mkey), agg(other, mkey)
    months = sorted(set(am) | set(bm))
    cd = np.corrcoef([a.get(k, 0.0) for k in days], [b.get(k, 0.0) for k in days])[0, 1]
    cm = np.corrcoef([am.get(k, 0.0) for k in months], [bm.get(k, 0.0) for k in months])[0, 1]
    return float(cd), float(cm)


def write_trades(trades, path):
    fmt = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["symbol", "side", "era", "t_in_utc", "t_out_utc", "entry", "exit", "stop_dist", "lot_x_default",
                    "r", "usd_at_100_risk", "exit_reason"])
        for t in sorted(trades, key=lambda t: (t.t_in, t.symbol)):
            w.writerow([t.symbol, t.side, S.era_of(t.t_in), fmt(t.t_in), fmt(t.t_out), f"{t.entry:.5f}",
                        f"{t.exit:.5f}", f"{t.risk:.5f}", f"{t.scale:.2f}", f"{t.r:.4f}", f"{t.usd:.2f}", t.why])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hold", action="store_true", help="also compute the registered holdout (run it once)")
    args = ap.parse_args(argv)
    eras = ("IS", "VAL", "HOLD") if args.hold else ("IS", "VAL")
    base = in_eras(run(), eras)
    wide = in_eras(run(spread_mult=1.5), eras)
    print("M1 month-end value-date USD:", ", ".join(SYMBOLS), PARAMS)
    for e in eras:
        tr = in_eras(base, (e,))
        print(line(tr, e), f" max DD ${max_dd(tr):,.0f}")
        print(line(in_eras(wide, (e,)), f"  x1.5 spr"))
        for s in SYMBOLS:
            print(line([t for t in tr if t.symbol == s], f"  {s}"))
        real, mu, sd, beat = random_day_control((e,))
        print(f"  random-day control: real summed R {real:+.1f}, control {mu:+.1f} +/- {sd:.1f}, "
              f"real beats {beat:.1%} of {SEEDS} seeds")
    years = {}
    for t in base:
        years.setdefault(S.year_of(t.t_in), []).append(t)
    print("by year:", "  ".join(f"{y} ${sum(t.usd for t in v):+,.0f} (R {np.mean([t.r for t in v]):+.2f})"
                                for y, v in sorted(years.items())))
    print("placebo, same window on the k-th last weekday (day-clustered t per era):")
    for k in range(1, 11):
        tr = in_eras(run(bd=k), eras)
        print(f"  k={k:2d} " + "  ".join(f"{e} {clustered_t(in_eras(tr, (e,)))[2]:+.1f}" for e in eras))
    hi = S.HOLD_START if not args.hold else S._ms(2026, 9, 25)
    for name, fn, lo in (("C3", "trades_C3_gotobi_jpy_basket.csv", S._ms(2016)),
                         ("C1", "trades_C1_crypto_donchian_h4.csv", S._ms(2018))):
        cd, cm = pnl_corr(base, load_other(fn), lo, hi)
        print(f"P&L correlation with {name}: daily {cd:+.3f}, monthly {cm:+.3f}")
    if args.hold:
        write_trades(base, PF / "trades_M1_month_end_usd.csv")


if __name__ == "__main__":
    main()
