"""Kalshi K1 (Addendum A): favourite at the ask, hold to settlement, INXD + HIGHNY sample, 2023 IS / 2024 VAL."""
import sys, os, json, glob, collections, datetime as dt, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import cash, ctstat, FRICTION

K = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/kalshi"
CUT = 1735689600


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


markets = []
for fn in glob.glob(K + "/ev/*.json"):
    for m in json.load(open(fn)):
        c = ts(m["close_time"])
        if c >= CUT or m.get("result") not in ("yes", "no"):
            continue
        cf_ = f"{K}/candles/{m['ticker']}.json"
        if not os.path.exists(cf_):
            continue
        try:
            cs = json.load(open(cf_)).get("candlesticks") or []
        except Exception:
            continue
        rows = []
        for x in cs:
            t = int(x["end_period_ts"])
            if t >= CUT:
                continue
            b, a = fnum((x.get("yes_bid") or {}).get("close")), fnum((x.get("yes_ask") or {}).get("close"))
            rows.append((t, b, a))
        rows.sort()
        m["c"] = c
        m["q"] = rows
        m["series"] = m["event_ticker"].split("-")[0]
        markets.append(m)
print("kalshi markets loaded", len(markets), collections.Counter((m["series"], dt.datetime.fromtimestamp(m["c"], dt.timezone.utc).year) for m in markets))


def quote_at(m, t):
    last = None
    for row in m["q"]:
        if row[0] <= t:
            last = row
        else:
            break
    if last is None or last[0] < t - 3 * 3600:
        return None
    return last


def run(T, thr, fee_mult=1.0, late=0, mid=False, maxspread=None):
    ev = collections.defaultdict(list)
    for m in markets:
        t = m["c"] - T + late
        q = quote_at(m, t)
        if q is None:
            continue
        _, b, a = q
        if b is None or a is None or a <= 0 or a > 1 or b < 0 or a < b:
            continue
        if maxspread is not None and a - b > maxspread + 1e-9:
            continue
        cand = []
        ya, na = a, 1 - b
        if mid:
            ya = na = None
            mm = (a + b) / 2
            ya, na = mm, 1 - mm
        if thr <= ya <= 0.98:
            cand = ("yes", ya, (a + b) / 2)
        elif thr <= na <= 0.98:
            cand = ("no", na, 1 - (a + b) / 2)
        if not cand:
            continue
        side, p, pmid = cand
        fee = 0.07 * p * (1 - p) * fee_mult
        pay = 1.0 if m["result"] == side else 0.0
        r = pay / (p + fee) - 1 - FRICTION - cash(t, m["c"])
        ev[m["event_ticker"]].append((r, p, pmid, m["c"], side))
    out = []
    for e, lst in ev.items():
        c = max(x[3] for x in lst)
        out.append(dict(ret=float(np.mean([x[0] for x in lst])), day=dt.datetime.fromtimestamp(c, dt.timezone.utc).date(),
                        year=dt.datetime.fromtimestamp(c, dt.timezone.utc).year, series=e.split("-")[0],
                        p=float(np.mean([x[1] for x in lst])), pm=float(np.mean([x[2] for x in lst])),
                        cost=[(x[1], 0.07 * x[1] * (1 - x[1]) * fee_mult) for x in lst], n=len(lst), side=lst[0][4]))
    return out


rng = np.random.default_rng(63)
for T in (6 * 3600, 24 * 3600):
    for thr in (0.80, 0.90):
        evs = run(T, thr)
        for y in (2023, 2024):
            s = [e for e in evs if e["year"] == y]
            if not s:
                print(f"K1 T{T // 3600}h thr{thr} {y}: n 0")
                continue
            m, t = ctstat([e["ret"] for e in s], [e["day"] for e in s])
            # calibration null at the PAID price (spread + fee charged): outcome ~ Bernoulli(paid price)
            P = [c for e in s for c in e["cost"]]
            sims = []
            idx = np.cumsum([0] + [e["n"] for e in s])
            pp = np.array([c[0] for c in P])
            ff = np.array([c[1] for c in P])
            for _ in range(2000):
                w = rng.random(len(pp)) < pp
                x = w / (pp + ff) - 1 - FRICTION
                sims.append(np.mean([x[idx[i]:idx[i + 1]].mean() for i in range(len(s))]))
            sims = np.array(sims)
            pv = (np.sum(sims >= m) + 1) / 2001
            sdm = sims.std()
            ser = collections.Counter(e["series"] for e in s)
            by = {k: round(100 * np.mean([e["ret"] for e in s if e["series"] == k]), 2) for k in ser}
            x15 = [e for e in run(T, thr, fee_mult=1.5) if e["year"] == y]
            late = [e for e in run(T, thr, late=3600) if e["year"] == y]
            print(f"K1 T{T // 3600:2d}h thr{thr:.2f} {y}: n {len(s):3d} mean {100 * m:+.2f}% t_cl {t:+.2f} z_net {m / sdm:+.2f} "
                  f"p(cal) {pv:.3f} paid {np.mean([e['p'] for e in s]):.3f} mid {np.mean([e['pm'] for e in s]):.3f} "
                  f"| fee x1.5 {100 * np.mean([e['ret'] for e in x15]):+.2f}% | +1h {100 * np.mean([e['ret'] for e in late]):+.2f}% | by series {dict(ser)} {by}")

print("\n--- POST-HOC (not declared; info only): same rule, only brackets with yes_ask - yes_bid <= 4c at entry ---")
for T in (6 * 3600, 24 * 3600):
    for thr in (0.80, 0.90):
        evs = run(T, thr, maxspread=0.04)
        parts = []
        for y in (2023, 2024):
            s_ = [e for e in evs if e["year"] == y]
            if s_:
                m, t = ctstat([e["ret"] for e in s_], [e["day"] for e in s_])
                parts.append(f"{y}: n {len(s_)} mean {100 * m:+.2f}% t {t:+.2f} paid {np.mean([e['p'] for e in s_]):.3f} mid {np.mean([e['pm'] for e in s_]):.3f}")
        print(f"K1 T{T // 3600:2d}h thr{thr:.2f} spread<=4c | " + " | ".join(parts))
