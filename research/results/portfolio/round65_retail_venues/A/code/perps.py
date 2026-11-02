"""(Copy of W/code/perps.py, unchanged.) Binance USDT-M perp availability (local perp_1d, cut at 2025-01-01; plus round 64 T's relisted first lives)."""
import csv, glob, os
import numpy as np
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
CUT = 1735689600000
DAY = 86400000


def span():
    out = {}
    for p in glob.glob(os.path.join(R, "binance", "perp_1d", "*.csv")):
        s = os.path.basename(p)[:-4]
        with open(p) as f:
            r = csv.reader(f); next(r)
            a = [(int(float(x[0])), float(x[6]) if len(x) > 6 and x[6] else 0.0) for x in r if x]
        a = [x for x in a if x[0] < CUT]
        act = [t for t, q in a if q > 0]
        if act:
            out[s] = [(act[0], act[-1])]
    p = os.path.join(R, "binance_delist", "relisted_candidates.csv")
    if os.path.exists(p):
        import datetime as dt
        for row in list(csv.DictReader(open(p))):
            f = int(dt.datetime.strptime(row["first_day"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            l = int(dt.datetime.strptime(row["last_trade_day"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            if f < CUT:
                out.setdefault(row["perp"], []).append((f, min(l, CUT - DAY)))
    return out


def perp_for(ticker, t, spans, need_before=7 * DAY, need_after=1 * DAY):
    """Perp symbol of `ticker` trading from >= need_before before t through t + need_after, else None."""
    for s in (ticker + "USDT", "1000" + ticker + "USDT"):
        for a, b in spans.get(s, []):
            if a <= t - need_before and b >= t + need_after:
                return s
    return None
