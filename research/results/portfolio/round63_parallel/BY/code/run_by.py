"""Stream BY grading run: B's frozen cell k100_H24_cheap on Bybit (IS 2020-21, VAL 2022-24 only).
Writes ../out/by_results.json, ../out/trades_by.npz, ../out/trades_by.csv."""
import csv, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import by  # noqa: E402  (patches B.trade_net with Bybit fees)
B = by.B
import run as Brun  # noqa: E402  (B's run.py: random_null, crash_mask)
Brun.trade_net = by.trade_net
from basis import simulate, summarize, by_year, cl_t, ERAS, DAY  # noqa: E402

OUT = os.path.join(HERE, "..", "out")
K, HH, SIDE = 100, 24, -1


def daily(T, m):
    d = (T["t"][m] // DAY).astype(np.int64)
    u, inv = np.unique(d, return_inverse=True)
    return dict(zip(u.tolist(), np.bincount(inv, weights=T["net"][m]).tolist()))


def corr_days(a, b, days_all):
    both = sorted(set(a) & set(b))
    union = sorted(set(a) | set(b))
    out = {"n_both": len(both), "n_union": len(union)}
    if len(both) > 2:
        out["corr_both"] = float(np.corrcoef([a[d] for d in both], [b[d] for d in both])[0, 1])
    if len(union) > 2:
        out["corr_union"] = float(np.corrcoef([a.get(d, 0) for d in union], [b.get(d, 0) for d in union])[0, 1])
    out["corr_calendar"] = float(np.corrcoef([a.get(d, 0) for d in days_all], [b.get(d, 0) for d in days_all])[0, 1])
    return out


def base(sym):
    import re
    s = sym[:-4]
    m = re.match(r"^(10+)([A-Z].*)$", s)
    if m:
        return m.group(2)
    m = re.match(r"^([A-Z0-9]*[A-Z])(10+)$", s)
    return m.group(1) if m else s


def main(reps=1000):
    t0 = time.time()
    coins = by.load()
    print("coins", len(coins), "load s", round(time.time() - t0), flush=True)
    res = {"ncoins": len(coins)}
    # coverage per year: universe coin-hours with data and valid deviation
    cov = {}
    for y in range(2020, 2025):
        a = np.datetime64(f"{y}-01-01", "ms").astype(np.int64); b = np.datetime64(f"{y + 1}-01-01", "ms").astype(np.int64)
        tot = val = coinsy = 0
        for c in coins:
            w = c["inU"] & (c["hours"] >= a) & (c["hours"] < b)
            if w.any():
                coinsy += 1
            tot += w.sum(); val += (w & ~np.isnan(c["b"] - c["m"])).sum()
        cov[y] = dict(coins=coinsy, member_hours=int(tot), valid_dev_share=float(val / tot) if tot else None)
    res["coverage"] = cov
    print("coverage", cov, flush=True)

    T = simulate(coins, K, HH, SIDE)
    TL = simulate(coins, K, HH, SIDE, lag=1)
    for era in ("IS", "VAL"):
        s = summarize(T, era)
        if s.get("n"):
            m = B.era_mask(T, era)
            s["median_bp"] = float(np.median(T["net"][m]) * 1e4)
            s["win"] = float((T["net"][m] > 0).mean())
            T15 = dict(T); T15["net"] = T["net"] - 0.5 * T["cost"]
            s15 = summarize(T15, era)
            s["x1.5_bp"], s["x1.5_t"] = s15["net_bp"], s15["t"]
            sl = summarize(TL, era)
            ml = B.era_mask(TL, era)
            s["late"] = dict(n=sl.get("n"), net_bp=sl.get("net_bp"), t=sl.get("t"),
                             median_bp=float(np.median(TL["net"][ml]) * 1e4) if ml.any() else None)
            nc = ~Brun.crash_mask(T["t"])
            s["nocrash"] = {k: summarize(Brun.sub(T, nc), era).get(k) for k in ("n", "net_bp", "t")}
            rng = np.random.default_rng(6301 if era == "IS" else 6302)
            means, ts = Brun.random_null(coins, T, SIDE, era, reps, rng)
            s["beats_random"] = float(np.nanmean(means < T["net"][m].mean()))
            s["random_mean_bp"] = float(np.nanmean(means) * 1e4)
            s["random_t_p95"] = float(np.nanpercentile(ts, 95))
            # concentration
            dsum = daily(T, m)
            tot = sum(dsum.values())
            s["top5_days_share"] = float(sum(sorted(dsum.values(), reverse=True)[:5]) / tot) if tot else None
            per_coin = {}
            for ci, v in zip(T["ci"][m], T["net"][m]):
                per_coin[coins[ci]["perp"]] = per_coin.get(coins[ci]["perp"], 0) + v
            top = sorted(per_coin.items(), key=lambda kv: -kv[1])[:5]
            s["top5_coins"] = [(k, round(v * 1e4)) for k, v in top]
            s["top5_coins_share"] = float(sum(v for _, v in top) / tot) if tot else None
            s["ncoins_traded"] = len(per_coin)
        res[era] = s
        print(era, {k: v for k, v in s.items() if not isinstance(v, (list, dict))}, flush=True)
    res["years"] = by_year(T)
    yrs_med = {}
    yy = np.asarray(T["t"], dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    for y in np.unique(yy):
        w = yy == y
        yrs_med[int(y)] = dict(n=int(w.sum()), net_bp=float(T["net"][w].mean() * 1e4), median_bp=float(np.median(T["net"][w]) * 1e4),
                               t=float(cl_t(T["net"][w], T["t"][w] // DAY)), fund_bp=float(T["fund"][w].mean() * 1e4),
                               price_bp=float(T["price"][w].mean() * 1e4))
    res["years_detail"] = yrs_med
    print("years", yrs_med, flush=True)

    # power at VAL size
    v = res["VAL"]
    if v.get("n"):
        res["power_trade"] = float(v["sr"] * np.sqrt(1.8 * v["n"] / 3))
        res["power_day"] = float(v["sr_day"] * np.sqrt(1.8 * v["days"] / 3))

    # B (Binance) comparison
    bt = list(csv.DictReader(open(os.path.join(OUT, "b_trades_named.csv"))))
    Bt = np.array([int(r["t"]) for r in bt]); Bn = np.array([float(r["net"]) for r in bt])
    Bb = np.array([base(r["perp"]) for r in bt])
    BT = dict(t=Bt, net=Bn)
    comp = {}
    for era in ("IS", "VAL"):
        a_, b_ = ERAS[era]
        mb = (Bt >= a_) & (Bt < b_)
        my = B.era_mask(T, era)
        cal = list(range(a_ // DAY, b_ // DAY))
        c = corr_days(daily(T, my), daily(BT, mb), cal)
        # trade-level overlap: same base coin, entry within 2 h
        yb = np.array([base(coins[ci]["perp"]) for ci in T["ci"][my]]) if my.any() else np.array([])
        yt, yn = T["t"][my], T["net"][my]
        match, pairs = 0, []
        for bb, tt, nn in zip(yb, yt, yn):
            w = np.where((Bb == bb) & (np.abs(Bt - tt) <= 2 * 3600000))[0]
            if len(w):
                match += 1
                pairs.append((nn, Bn[w[0]]))
        c["by_trades"] = int(my.sum()); c["b_trades"] = int(mb.sum()); c["matched"] = match
        if len(pairs) > 2:
            p = np.array(pairs)
            c["matched_corr"] = float(np.corrcoef(p[:, 0], p[:, 1])[0, 1])
            c["matched_by_net_bp"] = float(p[:, 0].mean() * 1e4); c["matched_b_net_bp"] = float(p[:, 1].mean() * 1e4)
            un = np.ones(len(yb), bool)
            for i_, (bb, tt) in enumerate(zip(yb, yt)):
                if ((Bb == bb) & (np.abs(Bt - tt) <= 2 * 3600000)).any():
                    un[i_] = False
            c["unmatched_n"] = int(un.sum())
            c["unmatched_net_bp"] = float(yn[un].mean() * 1e4) if un.any() else None
            c["unmatched_t"] = float(cl_t(yn[un], yt[un] // DAY)) if un.sum() > 2 else None
        comp[era] = c
    res["vs_binance"] = comp
    print("vs binance", comp, flush=True)

    # margin snapshot (today): spot marginTrading of the traded coins
    spot_info = {x["symbol"]: x.get("marginTrading") for x in json.load(open(os.path.join(by.BD, "instruments_spot.json")))}
    mg = {}
    for era in ("IS", "VAL"):
        m = B.era_mask(T, era)
        cnt = {}
        for ci in T["ci"][m]:
            k_ = spot_info.get(coins[ci]["spot"], "not listed today")
            cnt[k_] = cnt.get(k_, 0) + 1
        nets = {}
        for ci, nv in zip(T["ci"][m], T["net"][m]):
            k_ = spot_info.get(coins[ci]["spot"], "not listed today")
            nets.setdefault(k_, []).append(nv)
        mg[era] = {k_: dict(n=cnt[k_], net_bp=float(np.mean(nets[k_]) * 1e4)) for k_ in cnt}
    res["margin_today"] = mg
    print("margin", mg, flush=True)

    np.savez(os.path.join(OUT, "trades_by.npz"), **{k: v for k, v in T.items()})
    with open(os.path.join(OUT, "trades_by.csv"), "w") as f:
        f.write("perp,entry_utc,hold_h,net_bp,price_bp,fund_bp,cost_bp,carry_bp,forced\n")
        for i in range(len(T["e"])):
            c = coins[T["ci"][i]]
            f.write(f"{c['perp']},{np.datetime64(int(T['t'][i]), 'ms')},{T['x'][i] - T['e'][i]},{T['net'][i] * 1e4:.1f},"
                    f"{T['price'][i] * 1e4:.1f},{T['fund'][i] * 1e4:.1f},{T['cost'][i] * 1e4:.1f},{T['carry'][i] * 1e4:.1f},{T['forced'][i]}\n")
    assert (T["t"] < by.CUT).all() if len(T["t"]) else True
    with open(os.path.join(OUT, "by_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print("done s", round(time.time() - t0))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
