"""Build the unlock event list from the DefiLlama snapshot (schedule only, no prices), as declared in HYPOTHESES_U.md."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TU = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "token_unlocks")
PERP = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "binance", "perp_1d")
DAYS = 86400
HOLD = 1735689600
INS = {"insiders", "privateSale"}


def first_kline(sym):
    with open(os.path.join(PERP, sym + ".csv")) as f:
        next(f); line = f.readline()
    return int(float(line.split(",")[0])) // 1000 if line else None


def build(min_size=0.0, verbose=False):
    idx = {(x.get("protocolSlug") or x.get("name")): x
           for x in json.load(open(os.path.join(TU, "raw", "emissionsIndex_ds.json")))["data"]}
    rows = json.load(open(os.path.join(TU, "protocol_map.json")))
    out, dropped = [], []
    for slug, sym, gid, perps in rows:
        fn = os.path.join(TU, "emissions", slug + ".json")
        if not perps or not os.path.exists(fn):
            continue
        # choose the earliest-listed perp for this base among the matches
        cands = [(first_kline(p), p) for p in perps.split("|")]
        cands = [c for c in cands if c[0] is not None]
        if not cands:
            continue
        fk, perp = min(cands)
        ue = sorted(idx[slug]["unlockEvents"], key=lambda e: e["timestamp"])
        if not ue:
            continue
        tge = ue[0]["timestamp"]
        if fk < tge - 3 * DAYS:
            dropped.append((slug, perp, "perp older than TGE (symbol collision)"))
            continue
        d = json.load(open(fn))
        series = d["documentedData"]["data"]
        cum = {}
        for s in series:
            for p in s["data"]:
                day = p["timestamp"] // DAYS
                cum[day] = cum.get(day, 0.0) + (p.get("unlocked") or 0.0)
        cdays = np.array(sorted(cum)); cvals = np.array([cum[k] for k in cdays])
        # aggregate cliffs per UTC day
        per_day = {}
        for e in ue:
            day = e["timestamp"] // DAYS
            tot = ins = 0.0
            cats = {}
            for a in e.get("cliffAllocations", []):
                if a.get("category") == "burned":
                    continue
                amt = a.get("amount") or 0.0
                tot += amt
                cats[a.get("category")] = cats.get(a.get("category"), 0.0) + amt
                if a.get("category") in INS:
                    ins += amt
            if tot <= 0:
                continue
            pd = per_day.setdefault(day, [0.0, 0.0, {}])
            pd[0] += tot; pd[1] += ins
            for k, v in cats.items():
                pd[2][k] = pd[2].get(k, 0.0) + v
        days = sorted(per_day)
        merged = []
        for day in days:
            if merged and day - merged[-1][0] <= 3:
                m = merged[-1]; m[1] += per_day[day][0]; m[2] += per_day[day][1]
                for k, v in per_day[day][2].items():
                    m[3][k] = m[3].get(k, 0.0) + v
            else:
                merged.append([day, per_day[day][0], per_day[day][1], dict(per_day[day][2])])
        tge_day = tge // DAYS
        for day, tot, ins, cats in merged:
            if day <= tge_day + 3:
                continue
            j = np.searchsorted(cdays, day - 1, side="right") - 1
            if j < 0:
                continue
            circ = cvals[j]
            if circ <= 0:
                continue
            size = tot / circ
            if size < min_size:
                continue
            out.append(dict(slug=slug, perp=perp, day=int(day), size=float(size), ins_share=float(ins / tot),
                            first_perp_day=int(fk // DAYS), tge_day=int(tge_day), cats=cats, circ=float(circ)))
    out.sort(key=lambda e: (e["day"], e["perp"]))
    if verbose:
        for x in dropped:
            print("dropped", x)
    return out


if __name__ == "__main__":
    import datetime
    ev = build(0.0, verbose=True)
    pre = [e for e in ev if e["day"] < HOLD // DAYS]
    print("events (any size, pre-2025):", len(pre))
    for X in (0.01, 0.03):
        for lo, hi, name in ((2020, 2021, "IS 2020-21"), (2022, 2024, "VAL 2022-24")):
            sel = [e for e in pre if e["size"] >= X and lo <= datetime.datetime.utcfromtimestamp(e["day"] * DAYS).year <= hi
                   and e["day"] - 8 >= e["first_perp_day"] + 30]
            yrs = {}
            for e in sel:
                y = datetime.datetime.utcfromtimestamp(e["day"] * DAYS).year
                yrs[y] = yrs.get(y, 0) + 1
            print("X=%.0f%% %s: %d events, %d coins, by year %s" % (X * 100, name, len(sel), len({e['perp'] for e in sel}), yrs))
