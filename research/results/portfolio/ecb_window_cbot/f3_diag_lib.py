# F3 / E1 rebuilt from IC M1 (research/data/m1) to pin the cBot's conventions. Not a registered test: the eras below
# were all opened before (IS/VAL/HOLD). Variants:
#   ref   : the registered rule (mid prices, M1 quote = last bar with X-10min <= ts < X)
#   bidh1 : the cBot's selector: bid close of the H1 bar that ends at X (bar opening X-1h), no staleness window
# Also reports the stop-loss tail of E1 (adverse excursion in pips over 11:00-13:00 London from M1 high/low).
import datetime as dt, math, zoneinfo, numpy as np
UTC = dt.timezone.utc; NY = zoneinfo.ZoneInfo("America/New_York"); LON = zoneinfo.ZoneInfo("Europe/London")
MIN = 60_000
D = {s: np.load(f"research/data/m1/{s}.npz") for s in ("EURUSD", "USDJPY", "USDCHF")}


def ms(d, h, m, tz):
    return int(dt.datetime(d.year, d.month, d.day, h, m, tzinfo=tz).timestamp() * 1000)


def q_mid(s, X, back=10):
    z = D[s]; i = np.searchsorted(z["ts"], X, "left") - 1
    if i < 0 or z["ts"][i] < X - back * MIN:
        return None
    return (z["c"][i] + z["ca"][i]) / 2, z["c"][i], z["ca"][i]


def q_bid_h1(s, X):
    """bid close of the H1 bar [X-1h, X): last M1 bar with ts in [X-60min, X)."""
    z = D[s]; i = np.searchsorted(z["ts"], X, "left") - 1
    if i < 0 or z["ts"][i] < X - 60 * MIN:
        return None
    return z["c"][i]


def prev_wkd(d):
    p = d - dt.timedelta(days=1)
    while p.weekday() >= 5:
        p -= dt.timedelta(days=1)
    return p


def xmas(d):
    return (d.month == 12 and d.day >= 24) or (d.month == 1 and d.day <= 1)


D0, D1 = dt.date(2016, 1, 4), dt.date(2026, 9, 24)
WKD = [D0 + dt.timedelta(days=i) for i in range((D1 - D0).days + 1)]
WKD = [d for d in WKD if d.weekday() < 5]


def U_series(kind):
    U = np.full(len(WKD), np.nan)
    for i, d in enumerate(WKD):
        a, b = ms(prev_wkd(d), 18, 0, NY), ms(d, 7, 0, LON)
        v = []
        for s in ("USDJPY", "USDCHF"):
            if kind == "ref":
                pa, pb = q_mid(s, a), q_mid(s, b)
                if pa is None or pb is None:
                    break
                v.append(math.log(pb[0] / pa[0]))
            else:
                pa, pb = q_bid_h1(s, a), q_bid_h1(s, b)
                if pa is None or pb is None:
                    break
                v.append(math.log(pb / pa))
        if len(v) == 2:
            U[i] = np.mean(v)
    return U


def select(U, q=67, hist=250, mn=60):
    sel = np.zeros(len(U), bool)
    for i in range(len(U)):
        h = U[max(0, i - hist):i]; h = h[~np.isnan(h)]
        if len(h) >= mn and not np.isnan(U[i]):
            sel[i] = U[i] >= np.percentile(h, q)
    return sel


def e1(d):
    A, B = ms(d, 11, 0, LON), ms(d, 13, 0, LON)
    a, b = q_mid("EURUSD", A), q_mid("EURUSD", B)
    if a is None or b is None:
        return None
    net = -(b[2] / a[1] - 1) * 1e4 - 0.6
    z = D["EURUSD"]; k = (z["ts"] >= A) & (z["ts"] < B)
    mae = (z["h"][k].max() + (b[2] - b[1]) - a[1]) / 1e-4 if k.any() else np.nan   # short: ask high vs sell price, pips
    return net, mae



def q_gen(s, X, win, kind):
    z = D[s]; i = np.searchsorted(z["ts"], X, "left") - 1
    if i < 0 or z["ts"][i] < X - win * MIN:
        return None
    return z["c"][i] if kind == "bid" else (z["c"][i] + z["ca"][i]) / 2

def U_gen(win, kind):
    U = np.full(len(WKD), np.nan)
    for i, d in enumerate(WKD):
        a, b = ms(prev_wkd(d), 18, 0, NY), ms(d, 7, 0, LON)
        v = []
        for s in ("USDJPY", "USDCHF"):
            pa, pb = q_gen(s, a, win, kind), q_gen(s, b, win, kind)
            if pa is None or pb is None: break
            v.append(math.log(pb / pa))
        if len(v) == 2: U[i] = np.mean(v)
    return U

ref = select(U_gen(10, "mid"))
for win, kind in ((15, "mid"), (10, "bid"), (15, "bid")):
    s = select(U_gen(win, kind))
    diff = [d for d, a, b in zip(WKD, ref, s) if a != b]
    wd = [sum(d.weekday() == k for d in diff) for k in range(5)]
    print(f"{kind} {win} min: days differing from the registered selector {len(diff)} of {int(ref.sum())} selected; by weekday {wd}")
