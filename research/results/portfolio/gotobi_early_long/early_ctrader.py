"""Pre-registered test (research/results/portfolio/gotobi_early_long_2014-2019_2026-10-15.md): long leg at 17:00 (B)
vs 18:00 (A) UTC, no jitter, 2014-2019; secondary C (17:00 +/-60) vs D (18:00 +/-60). Run in ~/gotobi-early."""
import datetime, glob, json, math, os
from collections import defaultdict

RISK = 1000.0
R = os.path.expanduser("~/gotobi-early/reports")
utc = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc)


def load(v):
    files = sorted(glob.glob(f"{R}/{v}-*.json"))
    pos = defaultdict(list)
    for f in files:
        for i in json.load(open(f))["history"]["items"]:
            pos[(i["symbol"], i["direction"], i["entryTime"])].append(i)
    legs = {}
    for (sym, dirn, et), xs in pos.items():
        if sum(x["quantity"] for x in xs) <= 0.011:
            continue                                     # decoy
        day = (utc(et) + datetime.timedelta(hours=8)).date()
        legs[(sym, "long" if dirn == "buy" else "short", day)] = dict(net=sum(x["net"] for x in xs), entry=utc(et))
    return [os.path.basename(f)[:-5] for f in files], legs


def mean_t(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, m / (sd / math.sqrt(n))


data = {}
for v in "ABCD":
    files, legs = load(v)
    data[v] = legs
    longs = [l["net"] / RISK for k, l in legs.items() if k[1] == "long"]
    shorts = [l["net"] / RISK for k, l in legs.items() if k[1] == "short"]
    cover = defaultdict(int)
    for k in legs:
        cover[(k[0], k[2].year)] += 1
    print(f"{v}: {len(files)} reports, long n {len(longs)} R {mean_t(longs)[0]:+.4f} (t {mean_t(longs)[1]:+.1f}) "
          f"${sum(longs) * RISK:,.0f} | short n {len(shorts)} R {mean_t(shorts)[0]:+.4f} ${sum(shorts) * RISK:,.0f}")
    print("   legs per pair-year: " + " ".join(f"{s[:3]}{y % 100}:{n}" for (s, y), n in sorted(cover.items())))


def paired(a, b, primary):
    ka = {k: l for k, l in data[a].items() if k[1] == "long"}
    kb = {k: l for k, l in data[b].items() if k[1] == "long"}
    common = sorted(set(ka) & set(kb))
    d = {k: (kb[k]["net"] - ka[k]["net"]) / RISK for k in common}
    m, t = mean_t(list(d.values()))
    yrs, pairs = defaultdict(float), defaultdict(list)
    for k, x in d.items():
        yrs[k[2].year] += x
        pairs[k[0]].append(x)
    up = sum(v > 0 for v in yrs.values())
    print(f"\n{b} - {a} (long legs): matched {len(common)} (only {a} {len(set(ka) - set(kb))}, only {b} "
          f"{len(set(kb) - set(ka))})  mean {m:+.4f} R/leg (t {t:+.2f})  ${sum(d.values()) * RISK:+,.0f}")
    print("   by year (R summed): " + "  ".join(f"{y} {v:+.2f}" for y, v in sorted(yrs.items())) + f"  -> {up}/{len(yrs)} > 0")
    print("   by pair: " + " | ".join(f"{p} {mean_t(x)[0]:+.4f} (t {mean_t(x)[1]:+.1f})" for p, x in sorted(pairs.items())))
    if primary:
        ok = m > 0 and t >= 2.0 and up >= 4
        print(f"   PRE-REGISTERED VERDICT: {'PASS' if ok else 'FAIL'} (mean>0: {m > 0}, t>=2: {t >= 2.0}, years>=4/6: {up >= 4})")


paired("A", "B", True)
paired("D", "C", False)
