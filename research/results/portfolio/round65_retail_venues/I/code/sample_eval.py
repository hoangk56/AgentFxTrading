"""For each sampled coin: venue first candle (from loc_* bodies) vs Binance perp start and Upbit K2 listing date."""
import csv, glob, json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts
from candles import parse, fmt
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research"
D = R + "/data/retail_venues"
PS = perp_starts()
K2 = {r["coin"]: int(r["L"]) for r in csv.DictReader(open(R + "/results/portfolio/round64_parallel/K/k2_events.csv"))}
DAY = 86400000
for p in sorted(glob.glob(D + "/*/loc_*")):
    v = p.split("/")[-2]
    coin = os.path.basename(p)[4:].split("_")[0].split("-")[0]
    if v in ("btcturk", "indodax"): coin = coin[:-3]
    if v == "bitkub": coin = coin.split("_")[0]
    rows = parse(v, p)
    if not rows:
        continue
    trunc = (v in ("coindcx", "indodax") and len(rows) >= 1000) or (v == "bitvavo" and len(rows) >= 1440)
    f = rows[0][0]; ps = PS[coin][0]
    ev = (not trunc) and f >= ps + 7 * DAY and 2020 <= int(fmt(f)[:4]) <= 2024
    up = K2.get(coin)
    upd = f"{(f - up) / DAY:+.0f} d vs Upbit L" if up else "no K2 Upbit event"
    print(f"{v:8s} {coin:6s} first {fmt(f)[:10]}{' (truncated: earlier)' if trunc else ''} perp {fmt(ps)[:10]} "
          f"age {(f - ps) // DAY:5d} d  event {'YES' if ev else 'no '}  {upd}")
