"""OKX: monthly funding files (module 3) 2021-09..2024-12 and 1Dutc candles for 10 USDT swaps, cut < 2025-01-01."""
import sys, os, json, io, zipfile, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas/okx"
os.makedirs(OUT, exist_ok=True)
CUT = 1735689600000
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LTC", "LINK", "BCH", "DOT"]
fams = ",".join(c + "-USDT" for c in COINS)
import datetime as _dt
def _ms(y, m): return int(_dt.datetime(y, m, 1, tzinfo=_dt.timezone.utc).timestamp() * 1000)
_starts = [(2021, 9), (2022, 5), (2023, 1), (2023, 9), (2024, 5)]
_ends = [(2022, 5), (2023, 1), (2023, 9), (2024, 5), (2025, 1)]
wins = [(_ms(*a), _ms(*b) - 1000) for a, b in zip(_starts, _ends)]
urls = []
for fam, (b, e) in [(c + "-USDT", w) for c in COINS for w in wins]:
    d = json.loads(get("https://www.okx.com/api/v5/public/market-data-history?module=3&instType=SWAP"
                       "&instFamilyList=%s&dateAggrType=monthly&begin=%d&end=%d" % (fam, b, e), gap=0.6, tries=3))
    for x in d["data"]:
        for det in x["details"]:
            for g in det["groupDetails"]:
                urls.append(g["url"])
print("files", len(urls))
fund = {c: {} for c in COINS}
for u in sorted(set(urls)):
    z = get(u, gap=0.3, tries=3)
    if z is None:
        print("missing", u); continue
    with zipfile.ZipFile(io.BytesIO(z)) as zf:
        for nm in zf.namelist():
            txt = zf.read(nm).decode("utf-8", "replace").splitlines()
            for row in csv.reader(txt[1:]):
                if len(row) < 3: continue
                inst = row[0]; c = inst.split("-")[0]
                if inst != c + "-USDT-SWAP" or c not in fund: continue
                t = int(row[2])
                if t < CUT:
                    fund[c][t] = row[1]
for c in COINS:
    with open(os.path.join(OUT, c + "_funding.csv"), "w") as f:
        f.write("t,rate\n")
        for t in sorted(fund[c]):
            f.write("%d,%s\n" % (t, fund[c][t]))
    print(c, "funding rows", len(fund[c]))
if 'fundonly' in sys.argv: sys.exit(0)
# daily candles, newest first pages; 'after' = return records older than ts
for c in COINS:
    rows = {}
    after = CUT
    while True:
        d = json.loads(get("https://www.okx.com/api/v5/market/history-candles?instId=%s-USDT-SWAP&bar=1Dutc"
                           "&after=%d&limit=100" % (c, after), gap=0.15, tries=3))["data"]
        if not d: break
        for k in d:
            t = int(k[0])
            if t < CUT: rows[t] = k
        after = min(int(k[0]) for k in d)
        if after < 1625097600000: break   # stop before 2021-07
    with open(os.path.join(OUT, c + "_1d.csv"), "w") as f:
        f.write("t,o,h,l,c,vol,volccy,volccyquote,confirm\n")
        for t in sorted(rows):
            f.write(",".join(rows[t]) + "\n")
    print(c, "candles", len(rows))
