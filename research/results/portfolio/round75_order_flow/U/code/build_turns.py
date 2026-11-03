"""Stream U: build swing turns, unfinished flags, revisit flags and per-turn trade outcomes for one symbol.

Usage: python -I build_turns.py SYMBOL     -> U/out/turns_<SYM>.npz
Definitions: HYPOTHESES_U.md (written before any return). Uses the shared layer coord/code/fp.py unchanged.
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.dirname(HERE)
R75 = os.path.dirname(U)
spec = importlib.util.spec_from_file_location("fp", os.path.join(R75, "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)
ROOT = fp.ROOT

HS = (12, 48)
TF = 30
MAKER, TAKER = 2.0, 5.0


def funding(sym):
    a = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "funding", f"{sym}.csv"), delimiter=",",
                   skiprows=1)
    t = (a[:, 0] // 60000).astype(np.int64)  # epoch minute of the stamp
    keep = t < fp.HOLD_MIN
    t, r = t[keep], a[keep, 1]
    return t, np.r_[0.0, np.cumsum(r)]


def main(sym):
    slip = 2.0 if sym == "SOLUSDT" else 1.0
    m = fp.load_minutes(sym)
    b = fp.bars(m, TF)
    f = fp.load_fp(sym, TF)  # shared layer, BTC carry fixed by the coordinator 2026-11-03
    k = f["k"]
    fbar, top, bot, uh, ul = fp.unfinished(f)
    del f
    # the top row must contain the 1m-bar high of the 30m bar
    # align footprint bars to 30m bars
    pos = np.searchsorted(fbar, b["start"])
    pos = np.clip(pos, 0, len(fbar) - 1)
    okfp = fbar[pos] == b["start"]
    toprow_ok = (fp.bucket(b["h"]) // k == top[pos]) & okfp
    botrow_ok = (fp.bucket(b["l"]) // k == bot[pos]) & okfp
    print(sym, "k", k, "bars", len(b["start"]), "fp-aligned", okfp.mean(), "top row = high row", toprow_ok.mean(),
          "bottom row = low row", botrow_ok.mean())

    # dense 30m grid so that index windows equal time windows
    s0 = b["start"][0]
    gi = (b["start"] - s0) // TF
    G = gi[-1] + 1
    H = np.full(G, -np.inf); L = np.full(G, np.inf); C = np.full(G, np.nan); O = np.full(G, np.nan)
    H[gi], L[gi], C[gi], O[gi] = b["h"], b["l"], b["c"], b["o"]
    has = np.zeros(G, bool); has[gi] = True
    TOP = np.full(G, -1, np.int64); BOT = np.full(G, -1, np.int64)
    UH = np.zeros(G, bool); UL = np.zeros(G, bool); FPOK = np.zeros(G, bool)
    TOP[gi], BOT[gi] = top[pos], bot[pos]
    UH[gi], UL[gi], FPOK[gi] = uh[pos], ul[pos], okfp

    # 30m ATR14 (true range with previous close; requires 15 consecutive bars)
    prevc = np.r_[np.nan, C[:-1]]
    tr = np.fmax(H, prevc) - np.fmin(L, prevc)
    tr[~has] = np.nan
    csum = np.r_[0.0, np.cumsum(np.nan_to_num(tr))]
    cnt = np.r_[0, np.cumsum(np.isfinite(tr))]
    idx = np.arange(G)
    lo = np.maximum(idx - 13, 0)
    atr30 = (csum[idx + 1] - csum[lo]) / 14.0
    atr30[(cnt[idx + 1] - cnt[lo]) < 14] = np.nan
    atr30_bp = atr30 / C * 1e4

    # swing turns
    from numpy.lib.stride_tricks import sliding_window_view as swv
    cons = np.zeros(G, bool)
    hw = swv(has, 7)  # window i-4..i+2
    cons[4:G - 2] = hw.all(axis=1)
    i = np.arange(4, G - 2)
    prevmaxh = np.max(np.stack([H[i - d] for d in range(1, 5)]), axis=0)
    nextmaxh = np.maximum(H[i + 1], H[i + 2])
    prevminl = np.min(np.stack([L[i - d] for d in range(1, 5)]), axis=0)
    nextminl = np.minimum(L[i + 1], L[i + 2])
    sh = i[cons[i] & FPOK[i] & (H[i] > prevmaxh) & (H[i] > nextmaxh)]
    sl = i[cons[i] & FPOK[i] & (L[i] < prevminl) & (L[i] < nextminl)]

    # future windows on the dense grid (bars i+3 .. i+2+Hh)
    Hpad = np.r_[H, np.full(max(HS), -np.inf)]
    Lpad = np.r_[L, np.full(max(HS), np.inf)]

    # daily ATR14 from perp_1d klines (BRIEF: the 1m cache has day holes), bp of the previous close;
    # entry day D uses days D-14..D-1
    kl = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "perp_1d", f"{sym}.csv"), delimiter=",",
                    skiprows=1)
    kd = (kl[:, 0] // 86_400_000).astype(np.int64)
    D0 = kd[0]; ND = kd[-1] - D0 + 2
    DH = np.full(ND, np.nan); DL = np.full(ND, np.nan); DC = np.full(ND, np.nan)
    DH[kd - D0], DL[kd - D0], DC[kd - D0] = kl[:, 2], kl[:, 3], kl[:, 4]
    pdc = np.r_[np.nan, DC[:-1]]
    dtr = (np.fmax(DH, pdc) - np.fmin(DL, pdc)) / pdc * 1e4
    datr = np.full(ND, np.nan)
    for d in range(15, ND):
        w = dtr[d - 14:d]
        if np.isfinite(w).all():
            datr[d] = w.mean()
    # holes > 30 min in the 1m cache: a turn is dropped if its life (start of bar i-13 .. tc + 48 bars) spans one
    gap = np.diff(m["min"])
    hj = np.flatnonzero(gap > 30)
    hs, he = m["min"][hj], m["min"][hj + 1]
    print(sym, "holes > 30 min:", len(hj), "hours", round(float((gap[hj] - 1).sum()) / 60, 1))
    n_hole = 0

    ft, fcum = funding(sym)
    mm, mo, mh, ml, mc = m["min"], m["o"], m["h"], m["l"], m["c"]

    def trade(side, entry_px, start_min, end_min, tp, sl_px):
        """Minutes with start_min <= min < end_min. Returns net bp (normal fees), net bp (fees x1.5), exit minute."""
        a = np.searchsorted(mm, start_min)
        z = np.searchsorted(mm, end_min)
        if z <= a:
            return np.nan, np.nan, -1
        hh, ll = mh[a:z], ml[a:z]
        if side > 0:
            tph = hh > tp; slh = ll <= sl_px
        else:
            tph = ll < tp; slh = hh >= sl_px
        jt = np.argmax(tph) if tph.any() else 10 ** 9
        js = np.argmax(slh) if slh.any() else 10 ** 9
        if js <= jt and js < 10 ** 9:
            j = js
            px = min(sl_px, mo[a + j]) if side > 0 else max(sl_px, mo[a + j])
            px = px * (1 - side * slip / 1e4)
            fee = TAKER + TAKER
        elif jt < 10 ** 9:
            j = jt
            px = tp
            fee = TAKER + MAKER
        else:
            j = z - a - 1
            px = mc[a + j]
            fee = TAKER + TAKER
        xmin = mm[a + j]
        gross = side * (px / entry_px - 1) * 1e4
        # funding stamps in (entry minute, exit minute]
        fa = np.searchsorted(ft, start_min, side="right")
        fz = np.searchsorted(ft, xmin, side="right")
        fund = side * (fcum[fz] - fcum[fa]) * 1e4
        return gross - fee - fund, gross - 1.5 * fee - fund, xmin

    rec = {n: [] for n in ("tc", "side", "unf", "dist_bp", "atr30_bp", "datr_bp", "tp_bp", "pre_touch",
                           "rev12", "rev48", "ext12", "ext48", "era", "year")}
    for h in HS:
        for n in (f"net{h}", f"str{h}", f"late{h}", f"xm{h}"):
            rec[n] = []
    for side_turn, arr in ((+1, sh), (-1, sl)):  # +1 swing high (trade long), -1 swing low (trade short)
        for ii in arr:
            cl = C[ii + 2]
            if not np.isfinite(atr30_bp[ii + 2]):
                continue
            if side_turn > 0:
                Lr = TOP[ii]
                edge = fp.row_price(Lr, k, "low")
                if cl >= edge:
                    continue
                tp = float(fp.row_price(Lr - 1, k, "low"))
                unf = UH[ii]
                pre = max(H[ii + 1], H[ii + 2]) >= edge
            else:
                Br = BOT[ii]
                edge = fp.row_price(Br, k, "high")
                if cl <= edge:
                    continue
                tp = float(fp.row_price(Br + 1, k, "high"))
                unf = UL[ii]
                pre = min(L[ii + 1], L[ii + 2]) <= edge
            tc = int(s0 + (ii + 3) * TF)  # confirmation minute (close of bar i+2)
            lo_t, hi_t = int(s0 + (ii - 13) * TF), tc + max(HS) * TF
            q = np.searchsorted(he, lo_t, side="right")
            if q < len(hs) and hs[q] < hi_t:
                n_hole += 1
                continue
            dist = abs(edge / cl - 1) * 1e4
            rec["tc"].append(tc); rec["side"].append(side_turn); rec["unf"].append(bool(unf))
            rec["dist_bp"].append(dist); rec["atr30_bp"].append(atr30_bp[ii + 2]); rec["pre_touch"].append(pre)
            dd = tc // 1440 - D0
            rec["datr_bp"].append(datr[dd] if 0 <= dd < ND else np.nan)
            for h in HS:
                if side_turn > 0:
                    mx = Hpad[ii + 3: ii + 3 + h].max()
                    rec[f"rev{h}"].append(mx >= edge); rec[f"ext{h}"].append(mx > H[ii])
                else:
                    mn = Lpad[ii + 3: ii + 3 + h].min()
                    rec[f"rev{h}"].append(mn <= edge); rec[f"ext{h}"].append(mn < L[ii])
            rec["era"].append(0 if tc < fp.IS_END_MIN else 1)
            rec["year"].append(int(1970 + (tc // 1440) / 365.2425))
            # trade toward the level
            side = side_turn
            tpd = side * (tp / cl - 1) * 1e4
            rec["tp_bp"].append(tpd)
            for h in HS:
                if tpd <= 0:
                    rec[f"net{h}"].append(np.nan); rec[f"str{h}"].append(np.nan)
                    rec[f"late{h}"].append(np.nan); rec[f"xm{h}"].append(-1)
                    continue
                slp = cl * (1 - side * tpd / 1e4)
                n1, s1, x1 = trade(side, cl, tc, tc + h * TF, tp, slp)
                # one step late: market at the close of the 1st minute after confirmation
                a = np.searchsorted(mm, tc)
                nl = np.nan
                if a < len(mm) and mm[a] < tc + h * TF:
                    lp = mc[a]
                    if side * (tp / lp - 1) > 0 and side * (lp / slp - 1) > 0:
                        nl, _, _ = trade(side, lp, mm[a] + 1, tc + h * TF, tp, slp)
                    elif side * (lp / slp - 1) <= 0:
                        nl = np.nan  # already through the stop: no entry
                rec[f"net{h}"].append(n1); rec[f"str{h}"].append(s1); rec[f"late{h}"].append(nl)
                rec[f"xm{h}"].append(x1)
    out = {n: np.asarray(v) for n, v in rec.items()}
    order = np.argsort(out["tc"], kind="stable")
    out = {n: v[order] for n, v in out.items()}
    # calendar year exactly
    out["year"] = (out["tc"] * 60).astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970
    out["k"] = np.array(k)
    out["slip"] = np.array(slip)
    np.savez(os.path.join(U, "out", f"turns_{sym}.npz"), **out)
    print(sym, "turns dropped for a hole", n_hole)
    print(sym, "turns", len(out["tc"]), "highs", int((out["side"] > 0).sum()), "unf share", out["unf"].mean(),
          "pre_touch", out["pre_touch"].mean())


if __name__ == "__main__":
    main(sys.argv[1])
