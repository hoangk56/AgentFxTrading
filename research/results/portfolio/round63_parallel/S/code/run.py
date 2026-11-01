"""Stream S engine: overnight / intraday books on the top-200 S&P 500 names (survivors), eras PRE / IS / VAL."""
import json, sys, time
import numpy as np
import onlib

t0 = time.time()
P = onlib.Panel()
D, S = P.on.shape
K = 20
NU = 200
COST = 10.0          # bp per day for USD 1 long + USD 1 short, full turnover
BORROW = 0.5 / 100 / 360 * 1e4  # bp per night on the short leg
dff = onlib.dff_by_date(P.dates)
ngt = onlib.nights(P.dates)    # nights of the overnight leg ending on row t

# universe: members, valid today, top-NU by 63-day median dollar volume through t-1
dvmed = onlib.rolling_median_dv(P.dv, 63)
cand = P.member & P.valid & np.isfinite(dvmed)
key = np.where(cand, dvmed, -np.inf)
rk = np.argsort(np.argsort(-key, axis=1), axis=1)
U = cand & (rk < NU)
print("universe size median by era:", {e: float(np.median(U[P.era_mask(e)].sum(1))) for e in onlib.ERAS})

logon = np.log1p(P.on)
def shift(x, k):
    out = np.full(x.shape, np.nan)
    if k > 0:
        out[k:] = x[:-k]
    else:
        out[:] = x
    return out

lA = np.log(P.adj)
mom = shift(lA, 21) - shift(lA, 252)     # 12-1 momentum known at close t
sig = {
    "X1a": onlib.rolling_mean_nan(logon, 21),
    "X1b": onlib.rolling_mean_nan(logon, 63),
    "X1c": onlib.rolling_mean_nan(logon, 252),
    "X2": mom,
    "X3": shift(mom, 1),                       # known before the open of t
    "X4a": shift(logon, 1),                    # previous day's overnight
    "X4b": shift(onlib.rolling_mean_nan(logon, 21), 1),
}
# leg: 'on' = hold close t -> open t+1 (realized on[t+1]); 'id' = open t -> close t (realized id[t])
leg = {"X1a": "on", "X1b": "on", "X1c": "on", "X2": "on", "X3": "id", "X4a": "id", "X4b": "id"}
side = {"X1a": 1, "X1b": 1, "X1c": 1, "X2": 1, "X3": -1, "X4a": -1, "X4b": -1}  # +1 long high signal
on_next = shift(P.on[::-1], 1)[::-1] if False else np.vstack([P.on[1:], np.full((1, S), np.nan)])
nights_next = np.append(ngt[1:], np.nan)
real = {"on": on_next, "id": P.id}

def book(s, r, Umask, k=K):
    """long top-k minus bottom-k of s within Umask (NaN signal excluded); returns daily gross (fraction), n."""
    c = Umask & np.isfinite(s)
    n = c.sum(1)
    ss = np.where(c, s, np.inf)
    order = np.argsort(ss, axis=1)              # finite ascending, inf (excluded) last
    out = np.full(D, np.nan)
    rows = np.where(n >= 5 * k)[0]
    for t in rows:
        lo = order[t, :k]; hi = order[t, n[t] - k:n[t]]
        rh = r[t, hi]; rl = r[t, lo]
        if np.isfinite(rh).sum() < k // 2 or np.isfinite(rl).sum() < k // 2:
            continue
        out[t] = np.nanmean(rh) - np.nanmean(rl)
    return out

def net_of(g, lg, sd, mult=1.0):
    x = sd * g * 1e4 - COST * mult
    if lg == "on":
        x = x - BORROW * nights_next
    return x

def stats(x, era, years=False):
    m = P.era_mask(era) & np.isfinite(x)
    v = x[m]
    r = {"n": int(m.sum()), "mean": float(v.mean()) if len(v) else np.nan, "t": float(onlib.nw_t(v)),
         "ann_sr": float(v.mean() / v.std() * np.sqrt(252)) if len(v) > 2 else np.nan}
    if years:
        ys = sorted(set(P.year[m]))
        r["years"] = {int(y): round(float(x[m & (P.year == y)].mean()), 2) for y in ys}
    return r

res = {}
gross = {}
for c in sig:
    g = book(sig[c], real[leg[c]], U)
    gross[c] = g
    gl = book(shift(sig[c], 1), real[leg[c]], U)
    row = {}
    for e in onlib.ERAS:
        row[e] = {"gross_bp": stats(side[c] * g * 1e4, e), "net": stats(net_of(g, leg[c], side[c]), e, True),
                  "net_x1.5": stats(net_of(g, leg[c], side[c], 1.5), e), "net_x2": stats(net_of(g, leg[c], side[c], 2.0), e),
                  "net_late": stats(net_of(gl, leg[c], side[c]), e)}
    res[c] = row
    print(c, leg[c], {e: (round(row[e]["gross_bp"]["mean"], 2), round(row[e]["gross_bp"]["t"], 2),
                          round(row[e]["net"]["mean"], 2), round(row[e]["net"]["t"], 2)) for e in onlib.ERAS}, flush=True)

# B1: EW universe basket overnight, excess over cash; B2 diagnostic intraday basket
def basket(r):
    rr = np.where(U, r, np.nan)
    cnt = np.isfinite(rr).sum(1)
    return np.where(cnt >= 50, np.nanmean(rr, axis=1), np.nan)
b_on = basket(on_next)
b_id = basket(P.id)
cash_bp = dff * nights_next / 360 * 1e4
B1 = {}
for e in onlib.ERAS:
    B1[e] = {"gross_bp": stats(b_on * 1e4, e, True), "excess_cash_gross": stats(b_on * 1e4 - cash_bp, e),
             "net": stats(b_on * 1e4 - 5 - cash_bp, e, True), "net_x1.5": stats(b_on * 1e4 - 7.5 - cash_bp, e),
             "net_x2": stats(b_on * 1e4 - 10 - cash_bp, e),
             "intraday_gross_bp": stats(b_id * 1e4, e, True), "cc_gross_bp": stats((b_on + np.roll(b_id, -1)) * 1e4, e)}
    print("B1", e, {k: (round(v["mean"], 2), round(v["t"], 2), round(v["ann_sr"], 2)) for k, v in B1[e].items()}, flush=True)
res["B1"] = B1

# decomposition: each X signal's book on the other leg (diagnostic)
decomp = {}
for c in sig:
    other = "id" if leg[c] == "on" else "on"
    s2 = sig[c] if other == "id" else sig[c]
    # for 'on'-leg signals (known at close t) the next intraday leg is id[t+1]
    r2 = np.vstack([P.id[1:], np.full((1, S), np.nan)]) if leg[c] == "on" else P.on  # id-leg signal at t: overnight ending t is on[t]
    g2 = book(s2, r2, U)
    decomp[c] = {e: stats(side[c] * g2 * 1e4, e) for e in onlib.ERAS}
    print("decomp", c, "other leg", {e: (round(decomp[c][e]["mean"], 2), round(decomp[c][e]["t"], 2)) for e in onlib.ERAS})
res["decomp_other_leg_gross_bp"] = decomp

np.savez_compressed("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/S/out_books.npz",
                    dates=P.dates, b_on=b_on, b_id=b_id, U=U, **{"g_" + c: gross[c] for c in sig})
json.dump(res, open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/S/out_cells.json", "w"), indent=1)
print("done %.0fs" % (time.time() - t0))
