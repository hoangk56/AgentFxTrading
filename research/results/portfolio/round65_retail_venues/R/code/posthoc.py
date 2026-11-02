"""Post-hoc information only (after the declared books): the reversed rhythm (short high-share in the Korean day,
long at night) = minus A-FLIP. Not a declared cell, cannot be promoted from this stream."""
import os
import numpy as np
import r
f = open(os.path.join(r.OUTD, "r_posthoc.txt"), "w")
yrs = r.year_of_day()
TA, kA = r.terc(r.XA)
M0 = r.prep(0)
z = r.run_cell("A-FLIP", TA, kA, None, None, M0)
g = -z["gross"]; fu = -z["fund"]
turn = z["cost"] / 1.0      # taker+spread cost of the flip; turnover in $ = sum |dW|
# turnover per day: recompute with unit cost
c0 = r.HS.copy(); r.HS[:] = 0.0
zt = r.run_cell("A-FLIP", TA, kA, None, None, M0)   # cost now = 5 bp x turnover
r.HS[:] = c0
tv = zt["cost"] / 0.0005
print("Reversed A-FLIP (short high-share 00-15 UTC, long 15-24), per day per $1 of one side, bp", file=f)
for en, ee in (("IS", r.r.IS), ("VAL", r.r.VAL)):
    m = r.era(ee) & z["ok"]
    sg = r.tst(g[m]); st = r.tst(g[m] + fu[m] - z["cost"][m]); sm = r.tst(g[m] + fu[m] - 0.0002 * tv[m])
    print(f"{en}: n {sg['n']} gross {1e4*sg['mean']:+.1f} (t {sg['t']:+.2f}), turnover {tv[m].mean():.2f} $/day, "
          f"net taker+spread {1e4*st['mean']:+.1f} (t {st['t']:+.2f}), net at 2 bp maker no spread {1e4*sm['mean']:+.1f} "
          f"(t {sm['t']:+.2f}, ann SR {sm['sr']*np.sqrt(365):+.2f})", file=f)
print("gross by year:", " ".join(f"{y}:{1e4*g[(yrs==y)&z['ok']].mean():+.1f}" for y in range(2020, 2025)), file=f)
print("maker-net by year:", " ".join(f"{y}:{1e4*(g+fu-0.0002*tv)[(yrs==y)&z['ok']].mean():+.1f}" for y in range(2020, 2025)), file=f)
# split: day part and night part of the reversed rhythm, gross
for nm, R_ in (("day 00-15 (short high/long low)", -M0["RD"]), ("night 15-24 (long high/short low)", M0["RN"])):
    W = TA / np.maximum(kA, 1)[:, None]; W[~z["ok"]] = 0
    x = (W * R_).sum(1)
    print(nm, " ".join(f"{en} {1e4*x[r.era(ee)&z['ok']].mean():+.1f} (t {r.tst(x[r.era(ee)&z['ok']])['t']:+.2f})"
                       for en, ee in (("IS", r.r.IS), ("VAL", r.r.VAL))), file=f)
f.close()
print(open(os.path.join(r.OUTD, "r_posthoc.txt")).read())

# size control (information): same universe A, terciles by trailing 30-day perp quote volume (small = "high" leg),
# and share terciles within each volume half
import warnings
QD = r.D["QD"]
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    tv30 = np.full(QD.shape, np.nan)
    c = np.concatenate([np.zeros((QD.shape[0], 1)), np.cumsum(np.nan_to_num(QD), axis=1)], axis=1)
    d = np.arange(30, QD.shape[1]); tv30[:, 30:] = (c[:, d] - c[:, d - 30]) / 30
f = open(os.path.join(r.OUTD, "r_posthoc.txt"), "a")
def rev_flip(X, label):
    T, k = r.terc(X)
    zz = r.run_cell("A-FLIP", T, k, None, None, M0)
    g2 = -zz["gross"]
    print(label, " ".join(f"{en} gross {1e4*g2[r.era(ee)&zz['ok']].mean():+.1f} (t {r.tst(g2[r.era(ee)&zz['ok']])['t']:+.2f})"
                         for en, ee in (("IS", r.r.IS), ("VAL", r.r.VAL))), file=f)
rev_flip(np.where(r.EA, -np.log(tv30.T), np.nan), "size control: reversed flip, terciles by -log(30d volume) in universe A:")
# share residual on log volume per day (rank share after removing size)
LS_ = np.log(np.where(r.EA, r.S.T, np.nan)); LV = np.log(tv30.T)
res = np.full(LS_.shape, np.nan)
for dd in range(LS_.shape[0]):
    m = np.isfinite(LS_[dd]) & np.isfinite(LV[dd])
    if m.sum() >= 9:
        b = np.polyfit(LV[dd, m], LS_[dd, m], 1); res[dd, m] = LS_[dd, m] - np.polyval(b, LV[dd, m])
rev_flip(res, "share net of size: reversed flip, terciles by residual of log share on log volume:")
f.close()
print(open(os.path.join(r.OUTD, "r_posthoc.txt")).read())
