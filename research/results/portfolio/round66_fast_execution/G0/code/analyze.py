"""G0 analysis (../HYPOTHESES_G0.md): real-time BTC triggers, laggards at tau, taker fills on aggTrades prints.
Reads research/data/shock_aggtrades/days/*.npz (pulled by pull.py) and stream F's 1m npz for the betas (read-only,
via stream F's events.py and stream G's beta_series). Writes ../out/report.txt, ../out/cells.json,
../out/shocks_<cell>.npy (small per-shock arrays)."""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P64 = os.path.abspath(os.path.join(HERE, "..", "..", "..", "round64_parallel"))
sys.path.insert(0, os.path.join(P64, "F", "code")); sys.path.insert(0, os.path.join(P64, "G", "code"))
import events as E          # noqa: E402  (stream F loaders, read-only)
import g_events as GE       # noqa: E402  (stream G beta_series, read-only)

R = os.path.abspath(os.path.join(HERE, *[".."] * 5))
DAYS = os.path.join(R, "data", "shock_aggtrades", "days")
OUT = os.path.join(HERE, "..", "out")
BP = 1e4
VAL0 = 1640995200000
TAKER = 5e-4
LS = (1, 3, 10)
HS = (60, 300, 900)
CELLS = [("U", 1, 60), ("U", 1, 300), ("U", 1, 900), ("U", 3, 60), ("U", 3, 300), ("U", 3, 900),
         ("B", 1, 60), ("B", 1, 300)]
LATE = {1: 3, 3: 10}
ENTRY_MAX, EXIT_MAX, MID_MAX = 10000, 60000, 10000
NREP = 200
FRAME_VAL_DAYS, FRAME_IS_DAYS = 337, 387


def cname(c):
    return f"{c[0]} L{c[1]} H{c[2]}"


def off_idx(o_ms, offs):
    return int(np.where(offs == o_ms)[0][0])


def first(ts, ps, target, maxd):
    j = np.searchsorted(ts, target)
    if j < len(ts) and ts[j] - target <= maxd:
        return ps[j]
    return np.nan


def last_at(ts, ps, t, maxage=None):
    j = np.searchsorted(ts, t, "right") - 1
    if j < 0 or (maxage is not None and t - ts[j] > maxage):
        return np.nan
    return ps[j]


def clt(x, cl):
    x = np.asarray(x, float); cl = np.asarray(cl)
    k = np.isfinite(x); x, cl = x[k], cl[k]
    n = len(x)
    if n < 3:
        return np.nan, np.nan, np.nan, n, 0
    m = x.mean(); e = x - m
    u, inv = np.unique(cl, return_inverse=True)
    S = np.bincount(inv, weights=e)
    G = len(u)
    v = (S ** 2).sum() / n ** 2 * (G / max(G - 1, 1))
    sr = m / x.std(ddof=1) if x.std(ddof=1) > 0 else np.nan
    return m, m / np.sqrt(v) if v > 0 else np.nan, sr, n, G


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DAYS, "*.npz")))
    days = []
    for f in files:
        z = np.load(f)
        if int(z["n_shock"]) > 0 and len(z["coins"]) > 1:
            days.append((os.path.basename(f)[:10], dict(z)))
    n_days_all = len(files)
    n_days_trig = sum(1 for f in files if int(np.load(f)["n_shock"]) > 0)
    # betas: 7-day 1m OLS on BTC, at the trigger minute and the random minutes
    need = {}
    for ds, z in days:
        mins = list((z["tau"] - E.T0) // E.MIN) + list(((z["rnd_t"].ravel() - E.T0) // E.MIN))
        for s in z["coins"][1:]:
            need.setdefault(str(s), set()).update(int(m) for m in mins)
    cB = E.load_sym("BTCUSDT")[0]; rB = E.ret1(cB); del cB
    BETA = {}
    for s, mins in need.items():
        c = E.load_sym(s)[0]
        b = GE.beta_series(E.ret1(c), rB)
        mm = np.array(sorted(mins)); mm = mm[(mm >= 0) & (mm < E.NM)]
        BETA[s] = dict(zip(mm.tolist(), b[mm].tolist()))
        del c, b
    # ---- per shock, per laggard
    rows = []      # one row per laggard trade
    shocks = []    # one per shock
    for ds, z in days:
        coins = [str(c) for c in z["coins"]]; offs = z["offs"]
        tc, tk, tt, tp, tm = z["tc"], z["tk"], z["tt"], z["tp"], z["tm"]
        for k in range(int(z["n_shock"])):
            tau, tref, rb, side = int(z["tau"][k]), int(z["tau_ref"][k]), float(z["rB"][k]), int(z["side"][k])
            if tau + 10000 + 900000 + EXIT_MAX >= 1735689600000:
                continue
            mk = (tk == k)
            selB = mk & (tc == 0)
            bt, bp, bm = tt[selB], tp[selB], tm[selB]
            btc_buy = (bt[~bm], bp[~bm]); btc_sell = (bt[bm], bp[bm])
            minute = (tau - E.T0) // E.MIN
            lag_idx = []
            n_elig = 0
            for ci in range(1, len(coins)):
                s = coins[ci]
                beta = BETA.get(s, {}).get(int(minute), np.nan)
                if not np.isfinite(beta) or beta < GE.BETA_MIN:
                    continue
                sel = mk & (tc == ci)
                t, p, m = tt[sel], tp[sel], tm[sel]
                if len(t) < 2:
                    continue
                p_ref = last_at(t, p, tref, 30000); p_now = last_at(t, p, tau)
                if not (np.isfinite(p_ref) and np.isfinite(p_now)):
                    continue
                n_elig += 1
                u = (p_now / p_ref - 1) - beta * rb
                if not (np.sign(u) == -side and abs(u) > 0.5 * abs(beta * rb)):
                    continue
                buy = (t[~m], p[~m]); sell = (t[m], p[m])
                own_in, own_out = (buy, sell) if side > 0 else (sell, buy)
                rec = dict(day=ds, k=k, tau=tau, era=int(tau >= VAL0), year=int(ds[:4]), sym=s, ci=ci, beta=beta,
                           u=side * u, rank=int(z["ranks"][ci]), side=side)
                for L in LS:
                    te = tau + L * 1000
                    pe = first(*own_in, te, ENTRY_MAX)
                    pb, ps_ = first(*buy, te, MID_MAX), first(*sell, te, MID_MAX)
                    mid_e = (pb + ps_) / 2
                    rec[f"pe{L}"] = pe; rec[f"mide{L}"] = mid_e; rec[f"qs{L}"] = (pb - ps_) / mid_e
                    # BTC hedge: opposite direction to the alt
                    hb_in, hb_out = (btc_sell, btc_buy) if side > 0 else (btc_buy, btc_sell)
                    peB = first(*hb_in, te, ENTRY_MAX)
                    rec[f"peB{L}"] = peB
                    rec[f"midB{L}"] = (first(*btc_buy, te, MID_MAX) + first(*btc_sell, te, MID_MAX)) / 2
                    for H in HS:
                        tx = te + H * 1000
                        px = first(*own_out, tx, EXIT_MAX)
                        mid_x = (first(*buy, tx, MID_MAX) + first(*sell, tx, MID_MAX)) / 2
                        pxB = first(*hb_out, tx, EXIT_MAX)
                        midxB = (first(*btc_buy, tx, MID_MAX) + first(*btc_sell, tx, MID_MAX)) / 2
                        g = side * (px / pe - 1)
                        sc = side * (pe / mid_e - 1) + (-side) * (px / mid_x - 1)     # spread paid, round trip
                        hB = -side * (pxB / peB - 1)
                        scB = (-side) * (peB / rec[f"midB{L}"] - 1) + side * (pxB / midxB - 1)
                        rec[f"gU{L}_{H}"] = g; rec[f"scU{L}_{H}"] = sc
                        rec[f"gB{L}_{H}"] = g + beta * hB; rec[f"scB{L}_{H}"] = sc + beta * scB
                        rec[f"gmid{L}_{H}"] = side * (mid_x / mid_e - 1)
                rows.append(rec); lag_idx.append((ci, s))
            shocks.append(dict(day=ds, k=k, tau=tau, era=int(tau >= VAL0), year=int(ds[:4]), side=side, rb=rb,
                               n_elig=n_elig, lag=lag_idx, zi=len(shocks), rnd=(z["rnd_t"][k], z["RP"][k],
                               z["RD"][k], z["rb_now"][k], z["rb_60"][k], offs)))
    nsh = len(shocks)
    # ---- per-shock nets per cell
    def net_of(r, leg, L, H, mult=1.0, med=None):
        g = r[f"g{leg}{L}_{H}"]
        tk = 2 * TAKER * (1 + (r["beta"] if leg == "B" else 0))
        if mult == 1.0:
            return g - tk
        sc = r[f"sc{leg}{L}_{H}"]
        if not np.isfinite(sc):
            sc = med
        return g - tk - (mult - 1) * (tk + sc)

    real_isT = {}
    sh_day = np.array([s["day"] for s in shocks]); sh_era = np.array([s["era"] for s in shocks])
    sh_year = np.array([s["year"] for s in shocks])
    # rows need shock index
    key = {(s["day"], s["k"]): s["zi"] for s in shocks}
    for r in rows:
        r["zi"] = key[(r["day"], r["k"])]
    L_ = []
    summary = {}
    rnd_means = {}
    for c in CELLS:
        leg, L, H = c
        cs = {}
        for tag, LL, mult in (("base", L, 1.0), ("x1.5", L, 1.5), ("late", LATE[L], 1.0)):
            scs = np.array([r[f"sc{leg}{LL}_{H}"] for r in rows], float)
            med = float(np.nanmedian(scs)) if np.isfinite(scs).any() else 0.0
            acc = [[] for _ in range(nsh)]
            for r in rows:
                v = net_of(r, leg, LL, H, mult, med)
                if np.isfinite(v):
                    acc[r["zi"]].append(v)
            per = np.array([np.mean(a) if a else np.nan for a in acc]); ntr = np.array([len(a) for a in acc])
            cs[tag] = (per, ntr, med)
        per, ntr, med = cs["base"]
        # per-trade nets (for per-trade Sharpe)
        trn = np.array([net_of(r, leg, L, H) for r in rows]); tre = np.array([r["era"] for r in rows])
        trd = np.array([r["day"] for r in rows])
        d = {}
        for en, nm in ((0, "IS"), (1, "VAL")):
            m = sh_era == en
            mu, t, sr, n, G = clt(per[m], sh_day[m])
            mt = (tre == en) & np.isfinite(trn)
            _, tt_, srt, nt, _ = clt(trn[mt], trd[mt])
            d[nm] = dict(net=mu * BP, t=t, S=sr, n=n, days=G, trades=int(ntr[m].sum()), S_trade=srt,
                         x15=clt(cs["x1.5"][0][m], sh_day[m])[0] * BP, x15_t=clt(cs["x1.5"][0][m], sh_day[m])[1],
                         late=clt(cs["late"][0][m], sh_day[m])[0] * BP, late_t=clt(cs["late"][0][m], sh_day[m])[1])
            gs = np.array([r[f"g{leg}{L}_{H}"] for r in rows])[tre == en]
            sc = np.array([r[f"sc{leg}{L}_{H}"] for r in rows])[tre == en]
            d[nm]["gross_trade"] = float(np.nanmean(gs) * BP) if len(gs) else np.nan
            d[nm]["spread_rt_mean"] = float(np.nanmean(sc) * BP) if np.isfinite(sc).any() else np.nan
            d[nm]["spread_rt_med"] = float(np.nanmedian(sc) * BP) if np.isfinite(sc).any() else np.nan
        d["years"] = {}
        for y in range(2020, 2025):
            m = sh_year == y
            d["years"][y] = clt(per[m], sh_day[m])[0] * BP if m.any() else np.nan
        summary[cname(c)] = d
        real_isT[cname(c)] = d["IS"]["t"]
        np.save(os.path.join(OUT, f"shocks_{leg}_L{L}_H{H}.npy"),
                np.c_[np.array([s["tau"] for s in shocks]), sh_era, per, ntr])
    # ---- random benchmark (same coins, same day, side = BTC trailing-60 s sign, same L / H, fills, costs)
    RN = {cname(c): np.full((nsh, NREP), np.nan) for c in CELLS}
    rspread = {"IS": [], "VAL": []}
    for s in shocks:
        if not s["lag"]:
            continue
        rt, RP, RD, bnow, b60, offs = s["rnd"]
        if not np.any(rt):
            continue
        rside = np.sign(bnow / b60 - 1)
        rmin = (rt - E.T0) // E.MIN
        for c in CELLS:
            leg, L, H = c
            ie, ix = off_idx(L * 1000, offs), off_idx((L + H) * 1000, offs)
            acc = np.zeros(NREP); cnt = np.zeros(NREP)
            for ci, sym in s["lag"]:
                beta_r = np.array([BETA[sym].get(int(mm), np.nan) for mm in rmin])
                long_ = rside > 0
                pe = np.where(long_, RP[:, ci, ie, 0], RP[:, ci, ie, 1]); de = np.where(long_, RD[:, ci, ie, 0], RD[:, ci, ie, 1])
                px = np.where(long_, RP[:, ci, ix, 1], RP[:, ci, ix, 0]); dx = np.where(long_, RD[:, ci, ix, 1], RD[:, ci, ix, 0])
                ok = (de >= 0) & (de <= ENTRY_MAX) & (dx >= 0) & (dx <= EXIT_MAX) & (rside != 0)
                g = rside * (px / pe - 1)
                tk = 2 * TAKER
                if leg == "B":
                    peB = np.where(long_, RP[:, 0, ie, 1], RP[:, 0, ie, 0]); deB = np.where(long_, RD[:, 0, ie, 1], RD[:, 0, ie, 0])
                    pxB = np.where(long_, RP[:, 0, ix, 0], RP[:, 0, ix, 1]); dxB = np.where(long_, RD[:, 0, ix, 0], RD[:, 0, ix, 1])
                    ok &= (deB >= 0) & (deB <= ENTRY_MAX) & (dxB >= 0) & (dxB <= EXIT_MAX) & np.isfinite(beta_r)
                    g = g + beta_r * (-rside) * (pxB / peB - 1)
                    tk = tk * (1 + np.nan_to_num(beta_r))
                v = np.where(ok, g - tk, 0.0)
                acc += v; cnt += ok
                if c == CELLS[0]:
                    mb = (RD[:, ci, ie, 0] >= 0) & (RD[:, ci, ie, 0] <= MID_MAX) & (RD[:, ci, ie, 1] >= 0) & (RD[:, ci, ie, 1] <= MID_MAX)
                    mb &= np.abs(RD[:, ci, ie, 0] - RD[:, ci, ie, 1]) <= 500     # both prints within 0.5 s
                    mid = (RP[:, ci, ie, 0] + RP[:, ci, ie, 1]) / 2
                    qs = (RP[:, ci, ie, 0] - RP[:, ci, ie, 1]) / mid
                    rspread["VAL" if s["era"] else "IS"].extend((qs[mb] * BP).tolist())
            with np.errstate(invalid="ignore"):
                RN[cname(c)][s["zi"]] = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    maxnull = np.full(NREP, -np.inf)
    for c in CELLS:
        nm = cname(c); per = np.load(os.path.join(OUT, f"shocks_{c[0]}_L{c[1]}_H{c[2]}.npy"))[:, 2]
        for en, en_nm in ((0, "IS"), (1, "VAL")):
            m = (sh_era == en) & np.isfinite(per)
            rm = np.nanmean(RN[nm][m], axis=0)
            summary[nm][en_nm]["rand_mean"] = float(np.nanmean(rm) * BP) if np.isfinite(rm).any() else np.nan
            summary[nm][en_nm]["rand_pct"] = float(np.mean(rm < np.nanmean(per[m])) * 100) if np.isfinite(rm).any() else np.nan
        m = (sh_era == 0)
        for rep in range(NREP):
            x = RN[nm][m, rep]
            t = clt(x, sh_day[m])[1]
            if np.isfinite(t):
                maxnull[rep] = max(maxnull[rep], t)
    # ---- report
    L_.append(f"days pulled {n_days_all}, with a trigger {n_days_trig}, used (trigger + alts) {len(days)}")
    L_.append(f"shocks {nsh} (IS {(sh_era == 0).sum()}, VAL {(sh_era == 1).sum()}); with >= 1 laggard "
              f"IS {sum(1 for s in shocks if s['lag'] and s['era'] == 0)}, VAL {sum(1 for s in shocks if s['lag'] and s['era'] == 1)}; "
              f"laggard rows {len(rows)}; median eligible alts / shock {np.median([s['n_elig'] for s in shocks]):.0f}")
    for y in range(2020, 2025):
        L_.append(f"  {y}: shocks {(sh_year == y).sum()}, with laggard {sum(1 for s in shocks if s['lag'] and s['year'] == y)}")
    L_.append("")
    hdr = ("cell | IS net (t) S n days trades | VAL net (t) S n days trades | S_trade I/V | years | x1.5 I/V | "
           "late I/V | rand % I/V (rand mean) | gross/trade I/V | spread rt mean/med I | V")
    L_.append(hdr)
    for c in CELLS:
        d = summary[cname(c)]; I, V = d["IS"], d["VAL"]
        L_.append(f"{cname(c)} | {I['net']:+.1f} ({I['t']:+.2f}) {I['S']:+.3f} {I['n']} {I['days']} {I['trades']} | "
                  f"{V['net']:+.1f} ({V['t']:+.2f}) {V['S']:+.3f} {V['n']} {V['days']} {V['trades']} | "
                  f"{I['S_trade']:+.3f}/{V['S_trade']:+.3f} | "
                  + " ".join(f"{d['years'][y]:+.0f}" for y in range(2020, 2025)) +
                  f" | {I['x15']:+.1f}/{V['x15']:+.1f} | {I['late']:+.1f}/{V['late']:+.1f} | "
                  f"{I.get('rand_pct', np.nan):.0f}/{V.get('rand_pct', np.nan):.0f} ({I.get('rand_mean', np.nan):+.1f}/{V.get('rand_mean', np.nan):+.1f}) | "
                  f"{I['gross_trade']:+.1f}/{V['gross_trade']:+.1f} | {I['spread_rt_mean']:.1f}/{I['spread_rt_med']:.1f} | "
                  f"{V['spread_rt_mean']:.1f}/{V['spread_rt_med']:.1f}")
    best = max(CELLS, key=lambda c: np.nan_to_num(real_isT[cname(c)], nan=-9))
    mx = real_isT[cname(best)]
    fin = maxnull[np.isfinite(maxnull)]
    L_.append("")
    L_.append(f"IS-best cell: {cname(best)} (IS t {mx:+.2f}); max-over-8 random IS t: median {np.median(fin):+.2f}, "
              f"p95 {np.percentile(fin, 95):+.2f}, share below real {np.mean(fin < mx) * 100:.0f} %")
    nV = summary[cname(best)]["VAL"]["n"]
    n_val_days_sampled = len({s["day"] for s in shocks if s["era"] == 1})
    if n_val_days_sampled:
        nV_full = nV / n_val_days_sampled * FRAME_VAL_DAYS
        nH = nV_full * 22 / 36
        for c in CELLS:
            S = summary[cname(c)]["VAL"]["S"]
            summary[cname(c)]["power"] = S * np.sqrt(nH) if np.isfinite(S) else np.nan
        L_.append(f"HOLD pace: VAL shocks with laggards {nV} on {n_val_days_sampled} sampled VAL days -> ~{nV_full:.0f} in "
                  f"the full VAL frame -> ~{nH:.0f} in 22 HOLD months; power = S_VAL x sqrt({nH:.0f})")
        L_.append("power per cell: " + ", ".join(f"{cname(c)} {summary[cname(c)]['power']:+.2f}" for c in CELLS))
    for en in ("IS", "VAL"):
        q = np.array(rspread[en])
        if len(q):
            L_.append(f"random-minute quoted-spread proxy (same coins, t+1 s, first ask print - first bid print, both within 0.5 s of each other) {en}: "
                      f"mean {q.mean():.1f} bp, median {np.median(q):.1f} bp, n {len(q)}")
    qs1 = np.array([r["qs1"] for r in rows], float); er = np.array([r["era"] for r in rows])
    for en, nm in ((0, "IS"), (1, "VAL")):
        q = qs1[(er == en) & np.isfinite(qs1)] * BP
        if len(q):
            L_.append(f"shock quoted-spread proxy at tau+1 s ({nm}, laggards): mean {q.mean():.1f} bp, median "
                      f"{np.median(q):.1f} bp, n {len(q)}")
    # information: hedged mid path of laggards from tau (where the catch-up happens)
    for en, nm in ((0, "IS"), (1, "VAL")):
        sel = [r for r in rows if r["era"] == en]
        if not sel:
            continue
        parts = [f"resid at tau {np.mean([r['u'] for r in sel]) * BP:+.1f}"]
        for L in LS:
            for H in HS:
                v = np.array([r[f"gmid{L}_{H}"] for r in sel], float)
                parts.append(f"mid L{L} H{H} {np.nanmean(v) * BP:+.1f}")
        L_.append(f"info laggard rows {nm} (unhedged, gross mid-to-mid): " + " | ".join(parts))
    txt = "\n".join(L_)
    open(os.path.join(OUT, "report.txt"), "w").write(txt + "\n")
    json.dump(summary, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)
    print(txt)


if __name__ == "__main__":
    main()
