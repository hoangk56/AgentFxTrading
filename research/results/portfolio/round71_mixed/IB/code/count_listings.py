"""Count Binance spot USDT listings per year (2020-24) and whether a USDT-M perp existed before the spot opened.
Metadata only (first-kline dates); no price or return. Run with python -I."""
import csv
import os
from datetime import datetime, timezone

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance"
CUT = 1735689600000
STABLE = {"USDCUSDT", "BUSDUSDT", "TUSDUSDT", "FDUSDUSDT", "USDPUSDT", "DAIUSDT", "PAXUSDT", "EURUSDT", "AEURUSDT"}
perp_first = {}
for f in os.listdir(os.path.join(R, "perp_1d")):
    with open(os.path.join(R, "perp_1d", f)) as fh:
        rd = csv.reader(fh)
        for row in rd:
            if row and row[0].isdigit():
                perp_first[f[:-4]] = int(row[0])
                break
by = {}
for row in csv.reader(open(os.path.join(R, "spot_first.csv"))):
    if not row or not row[1].isdigit():
        continue
    sym, t = row[0], int(row[1])
    if t >= CUT or sym in STABLE or any(k in sym for k in ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")):
        continue
    y = datetime.fromtimestamp(t / 1000, timezone.utc).year
    if y < 2020:
        continue
    p = perp_first.get(sym)
    k = "perp_before" if p is not None and p < t else ("perp_within_7d" if p is not None and p - t < 7 * 86400000 else "no_perp_7d")
    by.setdefault(y, {}).setdefault(k, 0)
    by[y][k] += 1
for y in sorted(by):
    tot = sum(by[y].values())
    print(y, tot, by[y])
