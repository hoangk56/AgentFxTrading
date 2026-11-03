"""Stream CF report: tables from out/<SYM>_real.npz and out/<SYM>_rand.npz -> out/report.txt.
    research/.venv/bin/python -I report.py BTCUSDT ETHUSDT [SOLUSDT]"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
NDAYS = 1827
IS_END = 731  # day index of 2022-01-01
YEARS = np.array([(np.datetime64("2020-01-01") + np.timedelta64(d, "D")).astype("datetime64[Y]").astype(int) + 1970
                  for d in range(NDAYS)])
CELLS = [f"{c}|{t}" for c in ("C3_0.2", "C3_0.4", "C4", "none") for t in ("TPV", "2R")]
INFO = ["nonemkt|TPV", "nonemkt|2R"]


def ct(S, n):
    """Day-clustered t of the per-trade mean from per-day sums S and counts n (arrays over days)."""
    N = n.sum()
    if N < 3:
        return np.nan
    m = S.sum() / N
    g = (n > 0).sum()
    r = S - n * m
    v = (r ** 2).sum() / N ** 2 * g / max(g - 1, 1)
    return m / np.sqrt(v) if v > 0 else np.nan


def daysum(tr, col=3, adj=None):
    S = np.zeros(NDAYS)
    n = np.zeros(NDAYS)
    if len(tr):
        d = tr[:, 1].astype(int)
        x = tr[:, col] if adj is None else adj
        np.add.at(S, d, x)
        np.add.at(n, d, 1)
    return S, n


def era_mask(era):
    d = np.arange(NDAYS)
    return {"IS": d < IS_END, "VAL": d >= IS_END, "ALL": d >= 0}[era]


def stats(trs, era):
    """trs: list of trade arrays (one per symbol). Pooled stats in one era."""
    tr = np.concatenate([t for t in trs if len(t)]) if any(len(t) for t in trs) else np.zeros((0, 7))
    em = era_mask(era)
    tr = tr[em[tr[:, 1].astype(int)]] if len(tr) else tr
    if len(tr) < 3:
        return dict(n=len(tr), bp=np.nan, R=np.nan, t=np.nan, sd=np.nan, st=np.nan, wr=np.nan)
    S, n = daysum(tr)
    Ss, _ = daysum(tr, adj=tr[:, 3] - 0.5 * tr[:, 4])
    R = tr[:, 3] / tr[:, 5]
    return dict(n=len(tr), bp=tr[:, 3].mean(), R=R.mean(), t=ct(S, n), sd=tr[:, 3].std(ddof=1),
                st=ct(Ss, n), stbp=(tr[:, 3] - 0.5 * tr[:, 4]).mean(), wr=(tr[:, 3] > 0).mean(), tr=tr)


def years(trs):
    tr = np.concatenate([t for t in trs if len(t)])
    y = YEARS[tr[:, 1].astype(int)]
    return {int(yy): (int((y == yy).sum()), tr[y == yy, 3].mean()) for yy in np.unique(y)}


def main():
    syms = sys.argv[1:]
    real = {s: np.load(os.path.join(OUT, f"{s}_real.npz")) for s in syms}
    rand = {s: np.load(os.path.join(OUT, f"{s}_rand.npz")) for s in syms}
    L = []
    p = L.append
    p(f"Stream CF report, symbols {', '.join(syms)}; net bp per trade after fees, slippage, funding; t clustered by UTC day")
    p("")
    # random pooled
    sums = sum(rand[s]["sums"] for s in syms)
    cnts = sum(rand[s]["cnts"] for s in syms)
    G = sums.shape[0]
    rt = {}
    for era in ("IS", "VAL"):
        em = era_mask(era)
        rt[era] = np.array([[ct(sums[g, c][em], cnts[g, c][em]) for c in range(len(CELLS))] for g in range(G)])
    p(f"== Pooled, base execution ({G} random draws) ==")
    hdr = (f"{'cell':14s} {'era':4s} {'n':>5s} {'bp':>7s} {'R':>7s} {'t':>6s} {'win':>5s} {'x1.5 bp':>8s} "
           f"{'x1.5 t':>6s} {'late bp':>8s} {'late t':>6s} {'rand pct':>8s} {'rand t med':>10s}")
    p(hdr)
    res = {}
    for ci, cell in enumerate(CELLS + INFO):
        for era in ("IS", "VAL"):
            b = stats([real[s][cell + "|base"] for s in syms], era)
            lt = stats([real[s][cell + "|late"] for s in syms], era)
            res[(cell, era)] = b
            if ci < len(CELLS):
                pct = 100 * np.nanmean(rt[era][:, ci] < b["t"])
                med = np.nanmedian(rt[era][:, ci])
            else:
                pct, med = np.nan, np.nan
            p(f"{cell:14s} {era:4s} {b['n']:5d} {b['bp']:7.2f} {b['R']:7.3f} {b['t']:6.2f} {b['wr']:5.2f} "
              f"{b.get('stbp', np.nan):8.2f} {b['st']:6.2f} {lt['bp']:8.2f} {lt['t']:6.2f} {pct:8.1f} {med:10.2f}")
    p("")
    best = max(CELLS, key=lambda c: res[(c, "IS")]["t"])
    mx = np.nanmax(rt["IS"], axis=1)
    p(f"Best real cell on IS: {best} t {res[(best, 'IS')]['t']:.2f}; max-over-8-cells random IS t: median "
      f"{np.median(mx):.2f}, 95th {np.percentile(mx, 95):.2f}; real best beats {100 * np.mean(mx < res[(best, 'IS')]['t']):.1f} %")
    p("")
    p("== Power at VAL size (mean / sd per trade x sqrt(VAL n x 22 / 36)) and years ==")
    for cell in CELLS + INFO:
        v = res[(cell, "VAL")]
        pw = v["bp"] / v["sd"] * np.sqrt(v["n"] * 22 / 36) if v["n"] > 2 else np.nan
        yy = years([real[s][cell + "|base"] for s in syms])
        pos = sum(1 for _, (n, m) in yy.items() if m > 0)
        p(f"{cell:14s} power {pw:6.2f}  years +{pos}/{len(yy)}  " +
          "  ".join(f"{y}: {m:+.1f} ({n})" for y, (n, m) in yy.items()))
    p("")
    p("== Per symbol, base ==")
    for s in syms:
        for cell in CELLS + INFO:
            row = []
            for era in ("IS", "VAL"):
                b = stats([real[s][cell + "|base"]], era)
                row.append(f"{era} n {b['n']:5d} bp {b['bp']:7.2f} t {b['t']:6.2f}")
            p(f"{s:8s} {cell:14s} " + "  |  ".join(row))
    p("")
    p("== Exit mix (pooled ALL, base): stop / TP / time ==")
    for cell in CELLS + INFO:
        tr = np.concatenate([real[s][cell + "|base"] for s in syms])
        bc = np.bincount(tr[:, 6].astype(int), minlength=3) / len(tr)
        p(f"{cell:14s} stop {bc[0]:.2f} tp {bc[1]:.2f} time {bc[2]:.2f}  median R {np.median(tr[:, 5]):.1f} bp")
    p("")
    p("== Random benchmark per cell: pooled t distribution (median / 90th / 95th) ==")
    for ci, cell in enumerate(CELLS):
        for era in ("IS", "VAL"):
            x = rt[era][:, ci]
            p(f"{cell:14s} {era:4s} median {np.nanmedian(x):6.2f}  p90 {np.nanpercentile(x, 90):6.2f}  "
              f"p95 {np.nanpercentile(x, 95):6.2f}")
    txt = "\n".join(L)
    with open(os.path.join(OUT, "report_" + "_".join(s[:3] for s in syms) + ".txt"), "w") as fh:
        fh.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
