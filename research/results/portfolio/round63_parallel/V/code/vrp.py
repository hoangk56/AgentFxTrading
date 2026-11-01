"""Stream V engine: short delta-hedged ATM straddles on Deribit (BTC / ETH), hedged with the Binance perp.
Everything is cut at 2024-12-31 23:59:59 UTC at load. numpy only. See HYPOTHESES_V.md for the declared rules."""
import math, datetime as dt
import numpy as np

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
CUT = 1735689600000
H = 3600000
DAY = 86400000
IS_A, IS_B = "2021-03-01", "2022-07-01"
VAL_A, VAL_B = "2022-07-01", "2025-01-01"


def ms(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def ymd(t):
    return dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


# ---------------- loaders ----------------
def load_csv(fn, cols):
    a = np.genfromtxt(fn, delimiter=",", skip_header=1, usecols=cols)
    return a[a[:, 0] < CUT]


def load_perp(cur):
    a = load_csv(f"{DATA}/deribit/binance_1h/{cur}USDT.csv", (0, 1, 4))
    t = a[:, 0].astype(np.int64)
    return t, a[:, 1], a[:, 2]  # t (bar open), open, close


def load_dvol(cur):
    a = load_csv(f"{DATA}/deribit/dvol_{cur}_1h.csv", (0, 4))
    return a[:, 0].astype(np.int64), a[:, 1]  # candle open time, close


def load_funding(cur):
    a = load_csv(f"{DATA}/binance/funding/{cur}USDT.csv", (0, 1))
    return a[:, 0].astype(np.int64), a[:, 1]


def load_dff():
    out = {}
    with open(f"{DATA}/rates/DFF.csv") as fh:
        next(fh)
        for line in fh:
            d, v = line.strip().split(",")
            if d < "2025-01-01" and v not in ("", "."):
                out[d] = float(v)
    return out


def load_trades(cur, sub="fri"):
    F = ["ts", "exp", "k", "cp", "px", "amt", "dirn", "iv", "idx", "mark", "blk", "combo", "liq"]
    parts = {f: [] for f in F}
    for y in (2021, 2022, 2023, 2024):
        z = np.load(f"{DATA}/deribit/{cur}_{sub}/{y}.npz")
        m = z["ts"] < CUT
        for f in F:
            parts[f].append(z[f][m])
    return {f: np.concatenate(parts[f]) for f in F}


# ---------------- Black-Scholes (r = 0, spot) ----------------
_erf = np.vectorize(math.erf)


def ncdf(x):
    return 0.5 * (1.0 + _erf(np.asarray(x) / math.sqrt(2.0)))


def bs(S, K, tau, sig, cp):
    """tau in years; cp +1 call / -1 put. Returns price, delta."""
    S, K, tau, sig = map(np.asarray, (S, K, tau, sig))
    tau = np.maximum(tau, 1e-9)
    v = sig * np.sqrt(tau)
    d1 = (np.log(S / K) + 0.5 * v * v) / v
    d2 = d1 - v
    if cp == 1:
        return S * ncdf(d1) - K * ncdf(d2), ncdf(d1)
    return K * ncdf(-d2) - S * ncdf(-d1), ncdf(d1) - 1.0


def straddle(S, K, tau, sig):
    c, dc = bs(S, K, tau, sig, 1)
    p, dp = bs(S, K, tau, sig, -1)
    return c + p, dc + dp


def straddle_iv(P, S, K, tau):
    lo, hi = 0.01, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if straddle(S, K, tau, mid)[0] > P:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ---------------- market context ----------------
class Mkt:
    def __init__(self, cur):
        self.cur = cur
        self.pt, self.po, self.pc = load_perp(cur)
        self.pos = {int(t): i for i, t in enumerate(self.pt)}
        self.dt_, self.dv = load_dvol(cur)
        self.dpos = {int(t): i for i, t in enumerate(self.dt_)}
        self.ft, self.fr = load_funding(cur)
        self.dff = load_dff()
        self.tr = load_trades(cur)

    def px(self, t):
        """perp price at hour boundary t = open of bar starting at t."""
        return self.po[self.pos[int(t)]]

    def dvol_at(self, t):
        """DVOL known at hour boundary t: close of the candle that opened at t - 1h (fallback: last earlier)."""
        i = self.dpos.get(int(t - H))
        if i is None:
            j = np.searchsorted(self.dt_, t - H, side="right") - 1
            if j < 0:
                return np.nan
            i = j
        return self.dv[i] / 100.0

    def cash(self, t):
        d = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc)
        for k in range(10):
            s = (d - dt.timedelta(days=k)).strftime("%Y-%m-%d")
            if s in self.dff:
                return self.dff[s] / 100.0
        return np.nan

    def rv30(self, t):
        i = self.pos[int(t)]
        c = self.pc[i - 721:i]  # closes of the 721 bars ending at t -> 720 returns
        r = np.diff(np.log(c))
        return math.sqrt(np.mean(r * r) * 24 * 365)


def fridays(a, b):
    d = dt.datetime.fromisoformat(a).replace(tzinfo=dt.timezone.utc)
    while d.weekday() != 4:
        d += dt.timedelta(days=1)
    e = dt.datetime.fromisoformat(b).replace(tzinfo=dt.timezone.utc)
    while d < e:
        yield int(d.timestamp() * 1000)
        d += dt.timedelta(days=7)


# ---------------- entry quotes from trades ----------------
def entry_quote(m, f0, tenor, late=False):
    """f0 = Friday 00:00 UTC ms. Returns dict or None. Pricing window 08:00-09:00 (late: 09:00-10:00)."""
    w0 = f0 + (9 if late else 8) * H
    t_ref = w0 + H // 2
    tr = m.tr
    a, b = np.searchsorted(tr["ts"], [w0, w0 + H])
    if b - a < 5:
        return None
    sl = slice(a, b)
    ts, ex, kk, cp = tr["ts"][sl], tr["exp"][sl], tr["k"][sl], tr["cp"][sl]
    px, mk, iv, ix = tr["px"][sl], tr["mark"][sl], tr["iv"][sl], tr["idx"][sl]
    j = np.argmin(np.abs(ts - t_ref))
    S0 = ix[j]
    exps = np.unique(ex[ex > t_ref + DAY])
    if tenor == 7:
        T = f0 + 7 * DAY + 8 * H
        if T not in exps:
            return None
    else:
        days = (exps - (f0 + 8 * H)) / DAY
        ok = (days >= 21) & (days <= 35)
        if not ok.any():
            return None
        T = int(exps[ok][np.argmin(np.abs(days[ok] - 28))])
    me = ex == T
    ks = np.unique(kk[me])
    K = ks[np.argmin(np.abs(ks - S0))]
    tau0 = (T - t_ref) / DAY / 365.0
    near = me & (np.abs(np.log(kk / S0)) < 0.1) & np.isfinite(mk) & (mk > 0)
    hs = float(np.median(np.abs(px[near] - mk[near]) / mk[near])) if near.sum() >= 3 else np.nan
    legs, route = {}, []
    atm = me & (np.abs(np.log(kk / S0)) < 0.05) & np.isfinite(iv)
    iv_atm = float(np.median(iv[atm])) / 100.0 if atm.sum() >= 1 else np.nan
    for c in (1, -1):
        ml = me & (kk == K) & (cp == c) & np.isfinite(mk)
        if ml.any():
            idxs = np.where(ml)[0]
            q = idxs[np.argmin(np.abs(ts[idxs] - t_ref))]
            sig_q = iv[q] / 100.0 if np.isfinite(iv[q]) and iv[q] > 0 else (iv_atm if np.isfinite(iv_atm) else 0.8)
            _, dl = bs(ix[q], K, (T - ts[q]) / DAY / 365.0, sig_q, c)
            legs[c] = mk[q] * ix[q] + float(dl) * (S0 - ix[q])
            route.append("mark")
        elif np.isfinite(iv_atm):
            legs[c] = float(bs(S0, K, tau0, iv_atm, c)[0])
            route.append("iv")
        else:
            return None
    P = legs[1] + legs[-1]
    return dict(f0=f0, t_ref=t_ref, T=T, S0=S0, K=K, P=P, Pc=legs[1], Pp=legs[-1], hs=hs, route=route,
                sig=straddle_iv(P, S0, K, tau0), iv_atm=iv_atm, dvol=m.dvol_at(w0))


# ---------------- simulate one position ----------------
def simulate(m, q, hedge_h, cost_mult=1.0, lag=0, hs_default=0.02, fee_cap=True):
    """Short 1 straddle (1 coin per leg) at quote q, hedge every hedge_h hours with the perp from the first full hour
    after t_ref (+lag hours execution delay), unwind and settle at T. Returns dict with per-hour P&L path (MTM)."""
    S0, K, T, P = q["S0"], q["K"], q["T"], q["P"]
    hs = q["hs"] if np.isfinite(q["hs"]) else hs_default
    t_ref = q["t_ref"]
    h0 = (t_ref // H + 1) * H  # first full hour after pricing
    hours = np.arange(h0, T + 1, H, dtype=np.int64)
    S = np.array([m.px(t) for t in hours])
    dv0 = q["dvol"]
    # option premium and entry costs
    fee = sum(min(0.0003 * S0, 0.125 * leg) if fee_cap else 0.0003 * S0 for leg in (q["Pc"], q["Pp"]))
    sell = P * (1 - hs * cost_mult)
    cash = sell - fee * cost_mult
    # hedge schedule
    n = len(hours)
    pos = np.zeros(n)  # perp position held during [hours[i], hours[i+1])
    cur, traded = 0.0, 0.0
    sig_t = np.empty(n)
    for i in range(n - 1):
        dvt = m.dvol_at(hours[i])
        sig_t[i] = q["sig"] * (dvt / dv0 if np.isfinite(dvt) and np.isfinite(dv0) and dv0 > 0 else 1.0)
        reb_i = i - lag
        if reb_i >= 0 and (reb_i % hedge_h == 0):
            tdec = hours[reb_i]
            sd = sig_t[reb_i]
            _, dlt = straddle(S[reb_i], K, (T - tdec) / DAY / 365.0, sd)
            target = float(dlt)  # short straddle delta = -dlt; hedge = +dlt
            traded += abs(target - cur) * S[i]
            cash -= 0.0005 * abs(target - cur) * S[i] * cost_mult
            cur = target
        pos[i] = cur
    sig_t[-1] = sig_t[-2] if n > 1 else q["sig"]
    # unwind at T
    cash -= 0.0005 * abs(cur) * S[-1] * cost_mult
    traded += abs(cur) * S[-1]
    hedge_pnl = np.concatenate([[0.0], np.cumsum(pos[:-1] * np.diff(S))])
    # funding on the perp hedge
    fund = np.zeros(n)
    fi = np.searchsorted(m.ft, [h0 + 1, T])  # stamps with h0 < tf < T (hedge unwound at T)
    for j in range(fi[0], fi[1]):
        k = int((m.ft[j] - h0) // H)
        if 1 <= k < n:
            fund[k:] += -pos[k - 1] * m.fr[j] * S[k]
    # option liability path (model) and settlement
    tau = (T - hours) / DAY / 365.0
    V = np.append(straddle(S[:-1], K, tau[:-1], sig_t[:-1])[0], abs(S[-1] - K))
    intr = abs(S[-1] - K)
    dfee = min(0.00015 * S[-1], 0.125 * intr) if intr > 0 else 0.0
    # P&L path: cash received - liability + hedge + funding; final adds settlement fees and unwind
    path = cash - V + hedge_pnl + fund
    path[-1] -= dfee * cost_mult
    # entry MTM jump: at h0 the liability is V[0]
    final = path[-1]
    return dict(hours=hours, path=path, final=final, prem=sell, P=P, intr=intr, hedge=hedge_pnl[-1], fund=fund[-1],
                traded=traded, fee=fee, S0=S0, T=T, cap=0.5 * S0)


# ---------------- book ----------------
def book(m, sims, weeks):
    """Weekly book (Friday 08:00 -> Friday 08:00 marks) from positions. weeks = sorted Friday 00:00 ms.
    Returns arrays pnl, cap per week and per-position weekly contribution matrices."""
    nw = len(weeks)
    marks = np.array(weeks, dtype=np.int64) + 8 * H
    P = np.zeros((len(sims), nw))
    C = np.zeros((len(sims), nw))
    for r, s in enumerate(sims):
        hrs, path = s["hours"], s["path"]
        # cumulative P&L at each mark (0 before entry, final after expiry)
        prev = 0.0
        for w in range(nw):
            a, b = marks[w], marks[w] + 7 * DAY
            if b <= hrs[0] - H or a >= s["T"]:
                continue
            if b >= s["T"]:
                v = s["final"]
            else:
                i = int((b - hrs[0]) // H)
                v = path[min(max(i, 0), len(path) - 1)]
            P[r, w] = v - prev
            prev = v
            C[r, w] = s["cap"]
    return P, C


def excess(m, weeks, P, C):
    """weekly excess return on deployed capital."""
    pnl, cap = P.sum(0), C.sum(0)
    rc = np.array([m.cash(w) for w in weeks])
    ex = np.where(cap > 0, (pnl - cap * rc * 7 / 360) / np.where(cap > 0, cap, 1), np.nan)
    return ex, pnl, cap


def nw_t(x, lags=4):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 5:
        return np.nan
    mu = x.mean()
    e = x - mu
    g = np.dot(e, e) / n
    for l in range(1, lags + 1):
        g += 2 * (1 - l / (lags + 1)) * np.dot(e[l:], e[:-l]) / n
    return mu / math.sqrt(g / n) if g > 0 else np.nan
