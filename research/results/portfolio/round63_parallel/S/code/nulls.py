"""Random books (1,000 per cell, net beat %) and the max-over-cells null on IS gross t (same draws)."""
import json, sys
import numpy as np
import onlib
sys.argv = ["run"]  # reuse run.py objects without re-printing much
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import run as R

D, S = R.D, R.S
K = R.K
def book_vec(s, r, Umask, k=K):
    c = Umask & np.isfinite(s)
    n = c.sum(1)
    ss = np.where(c, s, np.inf)
    order = np.argsort(ss, axis=1)
    lo = order[:, :k]
    hi_idx = np.clip(n[:, None] - k + np.arange(k)[None, :], 0, S - 1)
    hi = np.take_along_axis(order, hi_idx, axis=1)
    rl = np.take_along_axis(r, lo, axis=1); rh = np.take_along_axis(r, hi, axis=1)
    okl = np.isfinite(rl).sum(1) >= k // 2; okh = np.isfinite(rh).sum(1) >= k // 2
    with np.errstate(all="ignore"):
        g = np.nanmean(rh, 1) - np.nanmean(rl, 1)
    return np.where((n >= 5 * k) & okl & okh, g, np.nan)

# check equality with the loop version
c0 = "X1c"
gv = book_vec(R.sig[c0], R.real[R.leg[c0]], R.U)
assert np.allclose(np.nan_to_num(gv), np.nan_to_num(R.gross[c0])), "vector book differs"
rng = np.random.default_rng(63)
NDRAW = 1000
cells = list(R.sig)
eras = list(onlib.ERAS)
obs_net = {c: {e: R.res[c][e]["net"]["mean"] for e in eras} for c in cells}
obs_gt_is = {c: R.res[c]["IS"]["gross_bp"]["t"] for c in cells}
rnd_net = {c: {e: [] for e in eras} for c in cells}
rnd_gt_is = {c: [] for c in cells}
ism = R.P.era_mask("IS")
for i in range(NDRAW):
    for c in cells:
        mask = R.U & np.isfinite(R.sig[c])
        g = book_vec(rng.random((D, S)), R.real[R.leg[c]], mask)
        x = R.net_of(g, R.leg[c], 1)
        for e in eras:
            m = R.P.era_mask(e) & np.isfinite(x)
            rnd_net[c][e].append(x[m].mean())
        if i < 200:
            m = ism & np.isfinite(g)
            rnd_gt_is[c].append(onlib.nw_t(g[m]))
out = {"beat_random_net_pct": {c: {e: float(100 * np.mean(np.array(rnd_net[c][e]) < obs_net[c][e])) for e in eras} for c in cells},
       "random_net_mean_bp": {c: {e: float(np.mean(rnd_net[c][e])) for e in eras} for c in cells}}
mx = np.max(np.abs(np.array([rnd_gt_is[c] for c in cells])), axis=0)
out["maxabs_t_null_IS_gross"] = {"p50": float(np.percentile(mx, 50)), "p90": float(np.percentile(mx, 90)), "p95": float(np.percentile(mx, 95))}
out["obs_IS_gross_t"] = obs_gt_is
out["obs_max_p"] = {c: float(np.mean(mx >= abs(obs_gt_is[c]))) for c in cells}
json.dump(out, open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/S/out_nulls.json", "w"), indent=1)
print(json.dumps(out, indent=1))
