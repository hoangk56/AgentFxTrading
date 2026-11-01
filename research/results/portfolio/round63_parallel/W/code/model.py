"""ISD-only climatology: k = SOD max - M_T given (city, season, LST hour T, drop bucket). Fitted on 2010-2021 LST days.
Also reports P(SOD max < METAR day max - m) to set the dead-bracket margin. No market data used here."""
import numpy as np, datetime as dt, json, sys
DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/kalshi_weather"
CITIES = ["NY", "CHI", "AUS", "MIA"]
KMIN, KMAX = -3, 20
def season(m): return {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2}.get(m, 3)
def dropb(d): return 0 if d <= 0 else 1 if d <= 2 else 2 if d <= 5 else 3
def load(city):
    z = np.load(f"{DATA}/isd_{city}.npz")
    return z["ts"], z["tf"], dict(zip(z["sod_day"], z["sod_max"])), int(z["off"])
def day_start_utc(day, off):  # epoch of 00:00 LST of `day`
    d = dt.date.fromisoformat(day)
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp()) - off * 3600
def state(ts, tf, t0, T, lat=600):
    """M_T and current temp from obs in [t0, t0+T h - lat]."""
    a = np.searchsorted(ts, t0); b = np.searchsorted(ts, t0 + T * 3600 - lat, side="right")
    if b - a < max(3, T // 2): return None
    seg = tf[a:b]
    return int(seg.max()), int(seg[-1])
def fit(years=(2010, 2021), hours=range(10, 24)):
    tab = {}
    stats = {}
    for c in CITIES:
        ts, tf, sod, off = load(c)
        neg = {0: 0, 1: 0, 2: 0}; n = 0
        for day, mx in sod.items():
            y = int(day[:4])
            if not (years[0] <= y <= years[1]) or mx < -100: continue
            t0 = day_start_utc(day, off)
            full = state(ts, tf, t0, 24, lat=0)
            if full is None: continue
            n += 1
            for m in neg:
                if mx < full[0] - m: neg[m] += 1
            sea = season(int(day[5:7]))
            for T in hours:
                s = state(ts, tf, t0, T)
                if s is None: continue
                k = int(np.clip(mx - s[0], KMIN, KMAX))
                key = (c, sea, T, dropb(s[0] - s[1]))
                tab.setdefault(key, np.zeros(KMAX - KMIN + 1))[k - KMIN] += 1
        stats[c] = {"days": n, **{f"P(SOD<daymax-{m})": neg[m] / max(n, 1) for m in neg}}
    return tab, stats
def prob(tab, key, lo, hi, M):
    """P(final in [lo, hi]) given M_T = M; Laplace-smoothed with 0.5 per k."""
    h = tab.get(key)
    if h is None or h.sum() < 30: return None
    p = (h + 0.5) / (h.sum() + 0.5 * len(h))
    ks = np.arange(KMIN, KMAX + 1) + M
    return float(p[(ks >= lo) & (ks <= hi)].sum())
if __name__ == "__main__":
    tab, stats = fit()
    print(json.dumps(stats, indent=1))
    for c in CITIES:
        for T in (15, 17):
            h = tab.get((c, 2, T, 0))
            if h is not None:
                print(c, "summer T", T, "drop0 n", int(h.sum()), "P(k=0)", round(h[-KMIN] / h.sum(), 3), "P(k<0)", round(h[:-KMIN].sum() / h.sum(), 4))
