"""Gross (pre-cost) t of the 6 cells, pooled IS+VAL net, Roll half-spread check at entry. Imports px (re-runs it)."""
import io, contextlib, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import px
W = px.W
for name, side, k, x in px.CELLS:
    out = []
    for era in ("IS", "VAL", None):
        m = px.sig(W, side, k) & ((W["era"] == era) if era else True)
        g = side * W["r" + x][m]; n_ = px.net(W, side, x)[m]
        sg = px.st(g); sn = px.st(n_)
        out.append(f"{era or 'ALL'} gross {sg[1]:+6.1f} t {sg[2]:+5.2f} | net {sn[1]:+6.1f} t {sn[2]:+5.2f} n {sn[0]}")
    print(f"{name:8s} " + " || ".join(out))
# Roll estimate of half-spread from aggTrade price changes, +-5 min around T
res = {"IS": [], "VAL": []}
for T, era in zip(W["T"], W["era"]):
    a, b = np.searchsorted(px.at, [(T - 5) * 60000, (T + 6) * 60000])
    p = px.ap[a:b]
    if len(p) < 10:
        continue
    d = np.diff(np.log(p))
    c = np.cov(d[1:], d[:-1])[0, 1]
    if c < 0:
        res[era].append(np.sqrt(-c) * 1e4)
for e, v in res.items():
    print(e, f"Roll half-spread at T: median {np.median(v):.2f} bp, p90 {np.quantile(v, .9):.2f}, windows {len(v)}")
# expected HOLD trades and power at VAL Sharpe
for name, side, k, x in px.CELLS:
    m = px.sig(W, side, k) & (W["era"] == "VAL")
    f = m.sum() / (W["era"] == "VAL").sum()
    sr = px.st(px.net(W, side, x)[m])[3]
    print(f"{name}: VAL trigger share {f:.2f}, HOLD n ~{95 * f:.0f}, VAL SR {sr:+.2f}, power {sr * np.sqrt(95 * f):+.2f}")
