"""Stream R: copy round 41 auctions and round 46 yield files into research/data/ust_auctions/, HOLD cut at parse.
Every row dated > 2024-12-31 is dropped before anything else; only counts are printed. Run with python -I."""
import csv, json, glob, datetime as dt, sys
OLD = "/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/ust_auctions"
RATES = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/rates"
CUT = dt.date(2024, 12, 31)


def num(s):
    try:
        v = float(s)
        return v
    except Exception:
        return None


ys = {"US": {}, "JP": {}, "DE": {}, "ECB": {}}
for f in sorted(glob.glob(f"{OLD}/r46/P/web/ust/par_*.csv")):
    rd = csv.reader(open(f, encoding="utf-8-sig")); h = next(rd)
    for r in rd:
        d = dt.datetime.strptime(r[0], "%m/%d/%Y").date()
        if d > CUT: continue
        row = dict(zip(h, r))
        ys["US"][str(d)] = {k.replace(" Yr", "Y").replace(" Mo", "M"): num(row.get(k)) for k in
                            ("3 Mo", "2 Yr", "3 Yr", "5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr")}
rd = csv.reader(open(f"{OLD}/r46/P/web/mof/jgbcme_all.csv", encoding="shift_jis", errors="replace"))
next(rd); h = next(rd)
for r in rd:
    try: d = dt.datetime.strptime(r[0].strip(), "%Y/%m/%d").date()
    except Exception: continue
    if d > CUT or d.year < 2003: continue
    row = dict(zip(h, r))
    ys["JP"][str(d)] = {k: num(row.get(k)) for k in ("1Y", "2Y", "5Y", "10Y", "20Y", "30Y", "40Y")}
for r in csv.reader(open(f"{OLD}/r46/P/web/bbk/r10.csv", encoding="utf-8-sig")):
    try: d = dt.date.fromisoformat(r[0])
    except Exception: continue
    if d > CUT or d.year < 2003: continue
    v = num(r[1]) if len(r) > 1 else None
    if v is not None: ys["DE"][str(d)] = {"10Y": v}
for r in csv.reader(open(f"{RATES}/ECBDFR.csv")):
    try: d = dt.date.fromisoformat(r[0])
    except Exception: continue
    if d > CUT: continue
    v = num(r[1])
    if v is not None: ys["ECB"][str(d)] = v
for c in ys:
    assert max(ys[c]) <= "2024-12-31"
    ys[c] = dict(sorted(ys[c].items()))
json.dump(ys, open(f"{OUT}/yields.json", "w"))
ev = json.load(open(f"{OLD}/r41/A/out/auctions.json"))
assert max(e["d"] for e in ev) <= "2024-12-31"
json.dump(ev, open(f"{OUT}/auctions.json", "w"))
print({c: (len(v), min(v), max(v) <= "2024-12-31") for c, v in ys.items()}, "auctions", len(ev))
