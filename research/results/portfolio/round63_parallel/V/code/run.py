"""Stream V: simulate every declared cell for one currency and save positions / weekly books.
Run: python -I run.py <BTC|ETH>. Output: V/out/sims_<cur>.pkl."""
import sys, os, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vrp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
QD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit"
IS0, IS1, VAL1 = vrp.ms(vrp.IS_A), vrp.ms(vrp.IS_B), vrp.ms(vrp.VAL_B)
RNG = np.random.default_rng(63)


def era(t):
    return "IS" if IS0 <= t < IS1 else ("VAL" if IS1 <= t < VAL1 else None)


def model_quote(m, t_ref, tenor_days, sig_ratio, hs):
    """Synthetic exact-ATM quote at hour t_ref priced at DVOL x ratio (random null and model-priced rule)."""
    S0 = m.px(t_ref)
    dv = m.dvol_at(t_ref)
    sig = dv * sig_ratio
    T = t_ref + tenor_days * vrp.DAY
    tau = tenor_days / 365.0
    c, _ = vrp.bs(S0, S0, tau, sig, 1)
    p, _ = vrp.bs(S0, S0, tau, sig, -1)
    return dict(f0=None, t_ref=t_ref - vrp.H // 2, T=T, S0=S0, K=S0, P=float(c + p), Pc=float(c), Pp=float(p), hs=hs,
                route=["model", "model"], sig=sig, iv_atm=np.nan, dvol=dv)


def trade_excess(m, s, t0):
    days = (s["T"] - t0) / vrp.DAY
    return (s["final"] - s["cap"] * m.cash(t0) * days / 360) / s["cap"]


def main(cur):
    t_start = time.time()
    m = vrp.Mkt(cur)
    Q = pickle.load(open(f"{QD}/quotes_{cur}.pkl", "rb"))
    res = {"cur": cur}
    # IS-only term ratios (sig / DVOL) and half spreads, used by fallback-free model pricing
    ratio, hsmed = {}, {}
    for tenor in (7, 30):
        qs = [q for q in Q[(tenor, False)] if era(q["f0"]) == "IS"]
        ratio[tenor] = float(np.median([q["sig"] / q["dvol"] for q in qs]))
        hsmed[tenor] = float(np.nanmedian([q["hs"] for q in qs]))
    res["ratio"], res["hsmed"] = ratio, hsmed
    weeks = [f for f in vrp.fridays("2021-03-26", "2024-12-31") if f + 8 * vrp.H + 7 * vrp.DAY <= vrp.CUT]
    res["weeks"] = weeks
    for tenor in (7, 30):
        for hh in (24, 4):
            for var in ("base", "cost15", "late"):
                qs = Q[(tenor, var == "late")]
                qs = [q for q in qs if q["T"] < vrp.CUT and era(q["f0"]) is not None]
                sims = []
                for q in qs:
                    s = vrp.simulate(m, q, hh, cost_mult=1.5 if var == "cost15" else 1.0, lag=1 if var == "late" else 0)
                    s["f0"] = q["f0"]; s["route"] = q["route"]; s["hs"] = q["hs"]; s["dvol"] = q["dvol"]
                    s["sig"] = q["sig"]; s["K"] = q["K"]
                    s["rv30"] = m.rv30(q["f0"] + 8 * vrp.H)
                    s["ex"] = trade_excess(m, s, q["t_ref"])
                    # margin: Deribit MM ~ 0.075 x S per short leg + option mark; equity = C + path
                    hrs = s["hours"]
                    St = np.array([m.px(t) for t in hrs])
                    tau = (s["T"] - hrs) / vrp.DAY / 365.0
                    dv0 = q["dvol"]
                    sg = np.array([q["sig"] * m.dvol_at(t) / dv0 for t in hrs[:-1]])
                    Vt = np.append(vrp.straddle(St[:-1], q["K"], tau[:-1], sg)[0], abs(St[-1] - q["K"]))
                    need = 0.15 * St + Vt - s["path"]  # capital needed to stay above MM
                    s["need_max"] = float(need.max()) / q["S0"]
                    s["mtm_min"] = float(s["path"].min()) / s["cap"]
                    del s["hours"]
                    s["path_w"] = None
                    sims.append(s)
                # weekly book needs hours; rebuild cheaply from stored path (hours = arange from first full hour)
                for s, q in zip(sims, qs):
                    h0 = (q["t_ref"] // vrp.H + 1) * vrp.H
                    s["hours"] = np.arange(h0, q["T"] + 1, vrp.H, dtype=np.int64)
                P, C = vrp.book(m, sims, weeks)
                for s in sims:
                    del s["hours"]
                    s["path"] = s["path"][:: 24].astype(np.float32)
                res[(tenor, hh, var)] = dict(sims=sims, P=P.astype(np.float32), C=C.astype(np.float32))
                print(cur, tenor, hh, var, len(sims), "%.0fs" % (time.time() - t_start), flush=True)
            # model-priced rule (same entries, DVOL x ratio pricing) and the random-timing pool
            qs = [q for q in Q[(tenor, False)] if q["T"] < vrp.CUT and era(q["f0"]) is not None]
            mod = []
            for q in qs:
                mq = model_quote(m, q["f0"] + 9 * vrp.H, tenor if tenor == 7 else 28, ratio[tenor], hsmed[tenor])
                if mq["T"] >= vrp.CUT:
                    continue
                s = vrp.simulate(m, mq, hh)
                mod.append((q["f0"], trade_excess(m, s, mq["t_ref"]), mq["P"], q["P"]))
            pool = []
            hours_all = np.arange(IS0 + 30 * vrp.DAY, VAL1 - 40 * vrp.DAY, vrp.H, dtype=np.int64)
            draw = RNG.choice(hours_all, size=1200 if tenor == 7 else 600, replace=False)
            for t in np.sort(draw):
                mq = model_quote(m, int(t), tenor if tenor == 7 else 28, ratio[tenor], hsmed[tenor])
                if not np.isfinite(mq["sig"]) or mq["T"] >= vrp.CUT:
                    continue
                s = vrp.simulate(m, mq, hh)
                pool.append((int(t), trade_excess(m, s, mq["t_ref"])))
            res[(tenor, hh, "model")] = mod
            res[(tenor, hh, "pool")] = pool
            print(cur, tenor, hh, "model+pool", len(mod), len(pool), "%.0fs" % (time.time() - t_start), flush=True)
    os.makedirs(OUT, exist_ok=True)
    pickle.dump(res, open(f"{OUT}/sims_{cur}.pkl", "wb"))


if __name__ == "__main__":
    main(sys.argv[1])
