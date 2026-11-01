"""Stream P analysis: P1 (favourite-longshot) and P2 (settlement window) on Polymarket 2023 (IS) / 2024 (VAL).
Run with research/.venv python -I. Reads research/data/polymarket/{markets.json, raw_prices/}. numpy only.
Rules exactly as declared in ../HYPOTHESES_P.md."""
import json, os, sys, glob, datetime as dt, collections, math
import numpy as np

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket"
DFF = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/rates/DFF.csv"
CUT = 1735689600  # 2025-01-01: nothing at or after is loaded
H = 3600
DAY = 86400
FRICTION = 0.0005


def ymd(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).date()


def load_dff():
    r = {}
    for line in open(DFF).read().splitlines()[1:]:
        d, v = line.split(",")
        try:
            r[dt.date.fromisoformat(d)] = float(v) / 100
        except ValueError:
            pass
    return r


DFFR = load_dff()


_D0 = dt.date(2014, 1, 1).toordinal()
_RATE = []
_v = 0.0
for _o in range(_D0, dt.date(2026, 12, 31).toordinal() + 1):
    _v = DFFR.get(dt.date.fromordinal(_o), _v)
    _RATE.append(_v)
_CUM = np.concatenate([[0.0], np.cumsum(_RATE)])


def cash(t0, t1):
    """Cash return (act/360) from t0 to t1: mean daily DFF over the calendar days touched x days / 360."""
    if t1 <= t0:
        return 0.0
    a, b = ymd(t0).toordinal() - _D0, ymd(t1).toordinal() - _D0
    avg = (_CUM[b + 1] - _CUM[a]) / (b - a + 1)
    return float(avg) * (t1 - t0) / DAY / 360


def half_spread(p, mult):
    return (0.01 if p < 0.96 else 0.005) * mult


def load_universe():
    R = json.load(open(DATA + "/markets.json"))
    out = []
    drop = collections.Counter()
    for r in R:
        if not (r["ob"] and len(r["tokens"]) == 2 and r["vol"] >= 1000 and r["closed"] < CUT):
            continue
        f = r["final"]
        if len(f) != 2 or not (sorted(f) == [0.0, 1.0] or f == [0.5, 0.5]):
            drop["bad_final"] += 1
            continue
        fn = f"{DATA}/raw_prices/{r['id']}_0.json"
        if not os.path.exists(fn):
            drop["no_file"] += 1
            continue
        try:
            h = json.load(open(fn)).get("history", [])
        except Exception:
            drop["bad_json"] += 1
            continue
        h = [(int(x["t"]), float(x["p"])) for x in h if int(x["t"]) < CUT]
        if not h:
            drop["empty_hist"] += 1
            continue
        h.sort()
        r["ts"] = np.array([x[0] for x in h], dtype=np.int64)
        r["px"] = np.array([x[1] for x in h])
        out.append(r)
    return out, drop


def price_at(r, t):
    i = np.searchsorted(r["ts"], t, side="right") - 1
    if i < 0 or r["ts"][i] < t - 6 * H:
        return None
    return float(r["px"][i])


def era_of(t):
    y = ymd(t).year
    return {2023: "IS", 2024: "VAL"}.get(y, "PRE" if y < 2023 else None)


# ---------- trade generators: return list of dict(market, tok, p, t_entry) -------------
def p1_trade(r, T, thr, side, late=0):
    t = r["end"] - T + late
    if not (r["closed"] > t + H):
        return None
    p0 = price_at(r, t)
    if p0 is None:
        return None
    for tok, p in ((0, p0), (1, 1 - p0)):
        if thr <= p + 1e-9 and p <= 0.98 + 1e-9:
            if side == "all" or (side == "Y" and tok == 0) or (side == "N" and tok == 1):
                return dict(tok=tok, p=p, t=t)
    return None


def p2a_trade(r, L, late=0):
    t = r["end"] + L + late
    if not (r["closed"] > t + H):
        return None
    p0 = price_at(r, t)
    if p0 is None:
        return None
    for tok, p in ((0, p0), (1, 1 - p0)):
        if 0.90 - 1e-9 <= p < 0.99 - 1e-9:
            return dict(tok=tok, p=p, t=t)
    return None


def p2b_trade(r, late=0):
    lo, hi = r["end"] - 7 * DAY, min(r["closed"], r["end"] + 4 * DAY)
    m = (r["ts"] >= lo) & (r["ts"] < hi)
    ts, px = r["ts"][m], r["px"][m]
    hit = np.nonzero((px >= 0.95 - 1e-9) | (px <= 0.05 + 1e-9))[0]
    if len(hit) == 0:
        return None
    tau = int(ts[hit[0]])
    tok = 0 if px[hit[0]] >= 0.95 - 1e-9 else 1
    t = tau + H + late
    if not (t < r["closed"] - H):
        return None
    p0 = price_at(r, t)
    if p0 is None:
        return None
    p = p0 if tok == 0 else 1 - p0
    if 0.95 - 1e-9 <= p < 0.99 - 1e-9:
        return dict(tok=tok, p=p, t=t)
    return None


def ret(r, tr, mult=1.0, fill=None):
    p = tr["p"]
    pay = r["final"][tr["tok"]]
    cost_p = fill if fill is not None else p + half_spread(p, mult)
    cost_p = min(cost_p, 0.9999)
    return pay / cost_p - 1 - FRICTION - cash(tr["t"], r["closed"])


# ---------- event aggregation + clustered t ---------------------------------------------
def aggregate(rows):
    """rows: list of (market, trade, return). -> arrays per event: ret, cluster day, era, year, cat."""
    ev = collections.defaultdict(list)
    for r, tr, x in rows:
        ev[r["event"]].append((r, tr, x))
    out = []
    for e, lst in ev.items():
        cmax = max(r["closed"] for r, _, _ in lst)
        out.append(dict(event=e, ret=float(np.mean([x for _, _, x in lst])), day=ymd(cmax), era=era_of(cmax),
                        year=ymd(cmax).year, q=f"{ymd(cmax).year}Q{(ymd(cmax).month - 1) // 3 + 1}",
                        cat=lst[0][0]["cat"], n=len(lst), p=float(np.mean([tr["p"] for _, tr, _ in lst])),
                        days=float(np.mean([(r["closed"] - tr["t"]) / DAY for r, tr, _ in lst]))))
    return out


def ctstat(x, g):
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return float(np.mean(x)) if n else float("nan"), float("nan")
    m = x.mean()
    cl = collections.defaultdict(float)
    for xi, gi in zip(x, g):
        cl[gi] += xi - m
    G = len(cl)
    if G < 2:
        return m, float("nan")
    se = math.sqrt(sum(v * v for v in cl.values()) * G / (G - 1)) / n
    return m, (m / se if se > 0 else float("nan"))


def summarize(evs, era):
    s = [e for e in evs if e["era"] == era]
    m, t = ctstat([e["ret"] for e in s], [e["day"] for e in s])
    return dict(n=len(s), mean=m, t=t, sd=float(np.std([e["ret"] for e in s])) if s else float("nan"),
                hit=float(np.mean([e["ret"] > 0 for e in s])) if s else float("nan"),
                p=float(np.mean([e["p"] for e in s])) if s else float("nan"),
                days=float(np.mean([e["days"] for e in s])) if s else float("nan"))


def fmt(d):
    return f"n {d['n']:5d}  mean {100 * d['mean']:+7.3f} %  t {d['t']:+6.2f}  sd {100 * d['sd']:6.2f} %  p {d['p']:.3f}  hold {d['days']:5.2f} d"
