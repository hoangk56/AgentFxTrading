"""Stream BM step 4-5: re-price B's trades on Binance 1m klines (HYPOTHESES_BM.md, fixed rules).
Entry: both legs at the open of the 1m bar starting at T + k min (k = 0, 1, 2, 5, 15; first bar within 5 min if
that minute has no bar). Exit unchanged: open of the 1m bar starting at X. Funding, costs, carry: B's values.
Writes BM/out/reprice_trades.csv and BM/out/reprice_report.txt."""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "B", "code")))
from basis import cl_t, DAY  # noqa: E402  (B's day-clustered t, unchanged)

RES = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
D = os.path.join(RES, "data", "binance_basis_1m")
OUT = os.path.join(HERE, "..", "out")
M = 60000
KS = (0, 1, 2, 5, 15)
ERAS = ("IS", "VAL", "HOLD")


def load(kind, sym, T):
    p = os.path.join(D, kind, f"{sym}_{T}.csv")
    if not os.path.exists(p):
        return None
    a = np.loadtxt(p, delimiter=",", skiprows=1, ndmin=2)
    return {int(r[0]): r for r in a} if len(a) else {}


def op(S, t):
    for j in range(6):
        r = S.get(t + j * M)
        if r is not None:
            return r[1], j
    return None, None


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "trades_b.csv"))))
    recs = []
    for r in rows:
        T, X, fac = int(r["T"]), int(r["X"]), float(r["fac"])
        P, S = load("perp", r["perp"], T), load("spot", r["spot"], T)
        rec = dict(id=int(r["id"]), era=r["era"], perp=r["perp"], T=T, X=X, hold_h=int(r["hold_h"]),
                   d_h=float(r["d_h"]), m_h=float(r["m_h"]), fund=float(r["fund"]), cost=float(r["cost"]),
                   carry=float(r["carry"]), net_b=float(r["net"]), price_b=float(r["price"]),
                   Fo_e=float(r["Fo_e"]), So_e=float(r["So_e"]), Fc_h=float(r["Fc_h"]), Sc_h=float(r["Sc_h"]),
                   have=int(bool(P) and bool(S)))
        if not rec["have"]:
            recs.append(rec); continue
        Fx, jx = op(P, X); Sx, jy = op(S, X)
        Sx = Sx * fac if Sx is not None else None
        rec.update(Fx=Fx, Sx=Sx)
        pc, sc = P.get(T - M), S.get(T - M)
        rec["Fc1"] = pc[4] if pc is not None else np.nan
        rec["Sc1"] = sc[4] * fac if sc is not None else np.nan
        p0, s0 = P.get(T), S.get(T)
        rec["sprF"] = abs(p0[1] / pc[4] - 1) if (p0 is not None and pc is not None) else np.nan
        rec["sprS"] = abs(s0[1] / sc[4] - 1) if (s0 is not None and sc is not None) else np.nan
        for k in KS:
            Fe, ja = op(P, T + k * M); Se, jb = op(S, T + k * M)
            if None in (Fe, Se, Fx, Sx):
                rec[f"net{k}"] = np.nan; continue
            Se = Se * fac
            perp_leg, spot_leg = Fx / Fe - 1, -(Sx / Se - 1)
            rec[f"Fe{k}"], rec[f"Se{k}"] = Fe, Se
            rec[f"perp{k}"], rec[f"spot{k}"] = perp_leg, spot_leg
            rec[f"net{k}"] = perp_leg + spot_leg + rec["fund"] - rec["cost"] - rec["carry"]
            rec[f"half{k}"] = int(np.log(Fe / Se) - rec["m_h"] >= rec["d_h"] / 2)
            rec[f"shift{k}"] = int(ja > 0 or jb > 0)
            # information only (not pre-declared): exit also delayed by k minutes
            Fxk, _ = op(P, X + k * M); Sxk, _ = op(S, X + k * M)
            if None not in (Fxk, Sxk):
                rec[f"netx{k}"] = (Fxk / Fe - 1) - (Sxk * fac / Se - 1) + rec["fund"] - rec["cost"] - rec["carry"]
        recs.append(rec)
    keys = sorted({k for r in recs for k in r}, key=lambda s: (s not in recs[0], s))
    with open(os.path.join(OUT, "reprice_trades.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval="")
        w.writeheader(); w.writerows(recs)
    rep = report(recs)
    open(os.path.join(OUT, "reprice_report.txt"), "w").write(rep)
    print(rep)


def col(R, k):
    return np.array([r.get(k, np.nan) for r in R], dtype=float)


def stats(x, day):
    ok = ~np.isnan(x)
    x, day = x[ok], day[ok]
    if len(x) < 3:
        return f"n {len(x)}"
    return (f"n {len(x):4d}  net {x.mean()*1e4:7.1f}  median {np.median(x)*1e4:7.1f}  t {cl_t(x, day):6.2f}"
            f"  win {np.mean(x > 0):4.0%}")


def report(recs):
    L = []
    for era in ERAS:
        R = [r for r in recs if r["era"] == era]
        H = [r for r in R if r["have"]]
        day = col(H, "T") // DAY
        L.append(f"=== {era}: trades {len(R)}, with both 1m files {len(H)} ===")
        L.append("B (1h opens, all trades): " + stats(col(R, "net_b"), col(R, "T") // DAY))
        L.append("B (1h opens, trades with 1m): " + stats(col(H, "net_b"), day))
        # reproduction of k = 0
        de = np.abs(col(H, "Fe0") / col(H, "Fo_e") - 1); ds = np.abs(col(H, "Se0") / col(H, "So_e") - 1)
        dx = np.abs(col(H, "net0") - col(H, "net_b"))
        L.append(f"k=0 vs B: perp entry within 1e-6 {np.nanmean(de < 1e-6):.1%}, spot {np.nanmean(ds < 1e-6):.1%}, "
                 f"|net0 - net_b| < 1 bp {np.nanmean(dx < 1e-4):.1%}, median |diff| {np.nanmedian(dx)*1e4:.2f} bp")
        # 1h close vs 1m close at T-1 min
        mF = np.abs(col(H, "Fc_h") / col(H, "Fc1") - 1); mS = np.abs(col(H, "Sc_h") / col(H, "Sc1") - 1)
        d1 = np.log(col(H, "Fc1") / col(H, "Sc1")) - col(H, "m_h")
        conf = d1 < -0.01
        L.append(f"1h close = 1m close(T-1): perp {np.nanmean(mF < 1e-6):.1%}, spot {np.nanmean(mS < 1e-6):.1%}; "
                 f"signal confirmed by 1m closes (d < -100 bp) {np.mean(conf):.1%}")
        for nm, v in (("perp", col(H, "sprF")), ("spot", col(H, "sprS"))):
            L.append(f"spread proxy |open(T) - close(T-1m)| {nm}: median {np.nanmedian(v)*1e4:.1f} bp, "
                     f"p75 {np.nanpercentile(v, 75)*1e4:.1f}, p90 {np.nanpercentile(v, 90)*1e4:.1f}, "
                     f"mean {np.nanmean(v)*1e4:.1f}")
        L.append("half the gap closed at entry minute: " + ", ".join(
            f"k={k} {np.nanmean(col(H, f'half{k}')):.1%}" for k in (0, 1, 5)))
        for k in KS:
            x = col(H, f"net{k}")
            L.append(f"  +{k:2d} min: " + stats(x, day) + f"  (bar shifted {np.nansum(col(H, f'shift{k}')):.0f})")
        n0, n5 = np.nanmean(col(H, "net0")), np.nanmean(col(H, "net5"))
        for k in (1, 2, 5, 15):
            L.append(f"  info, entry AND exit +{k:2d} min: " + stats(col(H, f"netx{k}"), day))
        L.append(f"  share of k=0 net kept at +5: {n5 / n0:.1%}")
        x5 = col(H, "net5")
        ok = ~np.isnan(x5)
        L.append(f"  +5 split per trade (bp): perp leg {np.nanmean(col(H, 'perp5')[ok])*1e4:.1f}, spot leg "
                 f"{np.nanmean(col(H, 'spot5')[ok])*1e4:.1f}, funding {col(H, 'fund')[ok].mean()*1e4:.1f}, costs "
                 f"-{col(H, 'cost')[ok].mean()*1e4:.1f}, carry -{col(H, 'carry')[ok].mean()*1e4:.1f}")
        pr5 = col(H, "perp5") + col(H, "spot5")
        L.append(f"  +5 price leg: mean {np.nanmean(pr5)*1e4:.1f} median {np.nanmedian(pr5)*1e4:.1f} t "
                 f"{cl_t(pr5[ok], day[ok]):.2f}; net without funding "
                 f"{np.nanmean(x5 - col(H, 'fund'))*1e4:.1f} bp")
        x15 = x5 - 0.5 * col(H, "cost")
        L.append(f"  +5 costs x1.5: " + stats(x15, day))
        for lab, w in (("confirmed by 1m close", conf), ("not confirmed", ~conf)):
            L.append(f"  +5 {lab}: " + stats(x5[w], day[w]) + f" | +0: " + stats(col(H, 'net0')[w], day[w])
                     + (f" | dates {sorted({str(np.datetime64(int(t), 'ms'))[:13] for t in col(H, 'T')[w]})}"
                        if 0 < w.sum() < 50 else ""))
        L.append(f"  +5 funding stamp crossed: " + stats(x5[col(H, 'fund') != 0], day[col(H, 'fund') != 0])
                 + f" | none: " + stats(x5[col(H, 'fund') == 0], day[col(H, 'fund') == 0]))
        y = np.asarray(col(H, "T").astype(np.int64), dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
        for yy in np.unique(y):
            w = y == yy
            L.append(f"  year {yy} +0: " + stats(col(H, 'net0')[w], day[w]) + " | +5: " + stats(x5[w], day[w]))
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
