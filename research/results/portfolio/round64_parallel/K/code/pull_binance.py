"""Binance pieces stream K needs that are not local (all ending 2024-12-31 23:59:59 UTC):
  1h perp klines for symbols with no local 1h file, funding history for symbols with no local funding file,
  BTCUSDT perp 1m monthly zips from data.binance.vision (2019-12..2024-12).
Saves under research/data/upbit/binance/. Usage: python -I pull_binance.py"""
import csv, io, json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
OUT = os.path.join(net.DATA, "binance")
END = 1735689599999
for d in ("perp_1h", "funding", "btc_1m_zip"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

print("robots data.binance.vision:", (net.get("https://data.binance.vision/robots.txt", raw=True) or b"<none>")[:300])
print("robots fapi:", (net.get("https://fapi.binance.com/robots.txt", raw=True) or b"<none>")[:300])

hit = json.load(open(os.path.join(net.DATA, "raw", "map_perp.json")))
have1h = set()
for d, f in (("binance_basis/perp_1h", lambda s: s[:-4]), ("binance/perp_1h", lambda s: s.split("_")[0]),
             ("binance_1h_full/1h", lambda s: s[:-4])):
    have1h |= {f(x) for x in os.listdir(os.path.join(R, d))}
havef = {x[:-4] for x in os.listdir(os.path.join(R, "binance_basis/funding"))} | \
        {x[:-4] for x in os.listdir(os.path.join(R, "binance/funding"))}
syms = sorted(set(hit.values()) - {"USDCUSDT"})

for s in syms:
    if s in have1h:
        continue
    p = os.path.join(OUT, "perp_1h", s + ".csv")
    if os.path.exists(p):
        continue
    rows, st = [], 1567296000000
    while st < END:
        js = net.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&startTime={st}&endTime={END}&limit=1500")
        if not js:
            break
        rows += [(x[0], x[1], x[2], x[3], x[4], x[5], x[7], x[8]) for x in js if x[0] <= END]
        st = js[-1][0] + 3600000
        if len(js) < 1500:
            break
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c", "vol", "qvol", "n"]); w.writerows(rows)
    print("1h", s, len(rows), flush=True)

for s in syms:
    if s in havef:
        continue
    p = os.path.join(OUT, "funding", s + ".csv")
    if os.path.exists(p):
        continue
    rows, st = [], 1567296000000
    while st < END:
        js = net.get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}&startTime={st}&endTime={END}&limit=1000")
        if not js:
            break
        rows += [(x["fundingTime"], x["fundingRate"]) for x in js if x["fundingTime"] <= END]
        st = js[-1]["fundingTime"] + 1
        if len(js) < 1000:
            break
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "rate"]); w.writerows(rows)
    print("funding", s, len(rows), flush=True)

for y in range(2019, 2025):
    for m in range(1, 13):
        if (y, m) < (2019, 12):
            continue
        tag = f"{y}-{m:02d}"
        p = os.path.join(OUT, "btc_1m_zip", f"BTCUSDT-1m-{tag}.zip")
        if os.path.exists(p):
            continue
        body = net.get(f"https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{tag}.zip", raw=True)
        if body:
            open(p, "wb").write(body)
        print("btc1m", tag, len(body or b""), flush=True)
print("done")
