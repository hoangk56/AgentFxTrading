"""Stream R library: yields, auction events, trades in yield bp (DV01 units), daily books, Newey-West t.
Inputs are the HOLD-cut copies in research/data/ust_auctions/ (asserted <= 2024-12-31 again at load)."""
import json, datetime as dt, math
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/ust_auctions"
CUT = "2024-12-31"
COST_SIDE = 0.30  # yield bp per side (declared flat, max of the futures table)
ERAS = {"PRE": (2004, 2015), "IS": (2016, 2021), "VAL": (2022, 2024)}
US_TEN = {"2-Year": "2Y", "3-Year": "3Y", "5-Year": "5Y", "7-Year": "7Y", "10-Year": "10Y", "20-Year": "20Y",
          "30-Year": "30Y", "29-Year 9-Month": "30Y"}
TEN_YEARS = {"2Y": 2, "3Y": 3, "5Y": 5, "7Y": 7, "10Y": 10, "20Y": 20, "30Y": 30, "40Y": 40}
FIN = {"US": "3M", "JP": "1Y"}


def moddur(T, y):
    if abs(y) < 1e-5:
        return T * (1 - 0.5 * y * T)
    return (1 - (1 + y / 2) ** (-2 * T)) / y


class Country:
    def __init__(self, c, rows, ecb=None):
        self.c = c
        self.dates = list(rows)
        assert max(self.dates) <= CUT
        self.idx = {d: i for i, d in enumerate(self.dates)}
        self.years = np.array([int(d[:4]) for d in self.dates])
        self.y = {}
        keys = set(k for r in rows.values() for k in r)
        for k in keys:
            self.y[k] = np.array([np.nan if rows[d].get(k) is None else rows[d][k] for d in self.dates], float)
        self.ord = np.array([dt.date.fromisoformat(d).toordinal() for d in self.dates])
        if c == "DE":
            # ECB deposit rate as financing (2014+), 0 before (file starts 2014)
            e = ecb or {}
            last, fin = 0.0, []
            for d in self.dates:
                if d in e: last = e[d]
                fin.append(last if d >= "2014-01-01" else 0.0)
            self.fin = np.array(fin)
        else:
            self.fin = self.y[FIN[c]]


def load():
    ys = json.load(open(f"{D}/yields.json"))
    ev = json.load(open(f"{D}/auctions.json"))
    assert max(ev_["d"] for ev_ in ev) <= CUT
    C = {c: Country(c, ys[c], ys["ECB"]) for c in ("US", "JP", "DE")}
    return C, ev


def events(C, ev):
    """List of dicts: c, tenor (yield key), i0 (anchor index), amt, weak flag, size flag; plus auction-day sets."""
    out, aday = [], {c: set() for c in C}
    for e in ev:
        c = e["c"]
        if e["d"] in C[c].idx:
            aday[c].add(C[c].idx[e["d"]])
        if c == "US":
            if e["tips"] or e["tenor"] not in US_TEN: continue
            ten = US_TEN[e["tenor"]]
            weakv = e.get("dealer")
        elif c == "JP":
            if e["tenor"] not in ("2Y", "5Y", "10Y", "20Y", "30Y", "40Y"): continue
            ten = e["tenor"]; weakv = e.get("tail")
        else:
            if e["tenor"] != "Bund|10 Y": continue
            ten = "10Y"; weakv = e.get("tail")
        if e["d"] not in C[c].idx: continue
        out.append(dict(c=c, ten=ten, d=e["d"], i0=C[c].idx[e["d"]], amt=e.get("amt"), wv=weakv))
    # dedupe same country/tenor/day
    seen, ded = set(), []
    for e in sorted(out, key=lambda e: (e["c"], e["ten"], e["d"])):
        k = (e["c"], e["ten"], e["d"])
        if k in seen: continue
        seen.add(k); ded.append(e)
    # size / weak vs previous-12 median of the same (country, tenor)
    hist = {}
    for e in ded:
        h = hist.setdefault((e["c"], e["ten"]), {"amt": [], "wv": []})
        pa = [x for x in h["amt"][-12:] if x is not None]
        pw = [x for x in h["wv"][-12:] if x is not None]
        e["size"] = (e["amt"] is not None and len(pa) >= 6 and e["amt"] > float(np.median(pa)))
        e["weak"] = (e["wv"] is not None and len(pw) >= 6 and e["wv"] > float(np.median(pw)))
        h["amt"].append(e["amt"]); h["wv"].append(e["wv"])
    return ded, aday


POOLS = {
    "US": lambda e: e["c"] == "US",
    "JP10": lambda e: e["c"] == "JP" and e["ten"] == "10Y",
    "DE10": lambda e: e["c"] == "DE",
    "ALL": lambda e: e["c"] == "US" or (e["c"] == "JP" and e["ten"] == "10Y") or e["c"] == "DE",
    "JPALL": lambda e: e["c"] == "JP",  # information only (cash JGBs)
}
# rule -> list of legs (entry offset, exit offset, side): side +1 = long bond (yield falls)
RULES = {
    "POST1": [(0, 1, +1)], "POST2": [(0, 2, +1)], "POST3": [(0, 3, +1)],
    "PRE5-1": [(-5, -1, -1)], "PRE5-0": [(-5, 0, -1)],
    "CYC": [(-5, 0, -1), (0, 3, +1)],
}


def leg_pieces(Cc, ten, a, legs, late=0):
    """Return (ok, gross, carry, pieces) for anchor index a. pieces: list of (date_idx, pnl) daily, gross only."""
    y = Cc.y[ten]
    n = len(y)
    gross = carry = 0.0
    pieces = []
    for (o0, o1, s) in legs:
        i0, i1 = a + o0 + late, a + o1 + late
        if i0 < 0 or i1 >= n: return False, 0, 0, []
        seg = y[i0:i1 + 1]
        if np.isnan(seg).any(): return False, 0, 0, []
        dy = np.diff(seg) * 100.0
        for k, v in enumerate(dy):
            pieces.append((i0 + 1 + k, -s * v))
        gross += -s * (seg[-1] - seg[0]) * 100.0
        f = Cc.fin[i0]
        if np.isnan(f): f = seg[0]
        md = moddur(TEN_YEARS[ten], seg[0] / 100.0)
        days = Cc.ord[i1] - Cc.ord[i0]
        carry += s * (seg[0] - f) * 100.0 * days / 365.0 / md
    return True, gross, carry, pieces


def era_of(year):
    for k, (a, b) in ERAS.items():
        if a <= year <= b: return k
    return None


def nw_t(x, lag=10):
    x = np.asarray(x, float); n = len(x)
    if n < 30: return float("nan")
    m = x.mean(); u = x - m
    g0 = (u @ u) / n
    s = g0
    for L in range(1, lag + 1):
        g = (u[L:] @ u[:-L]) / n
        s += 2 * (1 - L / (lag + 1)) * g
    return m / math.sqrt(s / n) if s > 0 else float("nan")
