"""Pull Upbit KRW-<coin> UNIT-minute candles (UNIT = argv[1], 240 for K1, 60 for K2 windows) backwards from 2025-01-01T00:00:00Z (exclusive) until the market's history
ends or the candle start is before the coin's floor (max(perp first day, 2019-12-20)). Writes
research/data/upbit/h1/<COIN>.csv (t_ms start UTC, o, h, l, c, krw_value, volume) ascending. Prints only counts and
first-candle times (no prices). Usage: python -I pull_upbit.py"""
import csv, json, os, sys, time, calendar
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
UNIT = int(sys.argv[1]) if len(sys.argv) > 1 else 240
OUT = os.path.join(net.DATA, f"m{UNIT}")
os.makedirs(OUT, exist_ok=True)
CUT = 1735689600000
FLOOR0 = calendar.timegm((2019, 12, 20, 0, 0, 0)) * 1000
hit = json.load(open(os.path.join(net.DATA, "raw", "map_perp.json")))


def perp_first(sym):
    with open(os.path.join(R, "binance", "perp_1d", sym + ".csv")) as f:
        f.readline()
        return int(f.readline().split(",")[0])


def iso(ms):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ms / 1000))


coins = sorted(hit, key=lambda b: (b != "BTC", b))


def one(b):
    path = os.path.join(OUT, b + ".csv")
    if os.path.exists(path):
        return
    floor = FLOOR0 if b == "BTC" else max(FLOOR0, perp_first(hit[b]) - 8 * 86400000)
    rows, to, ended = {}, CUT, False
    while to > floor:
        js = net.get(f"https://api.upbit.com/v1/candles/minutes/{UNIT}?market=KRW-{b}&to={iso(to)}&count=200")
        if js is None:
            break
        for x in js:
            t = calendar.timegm(time.strptime(x["candle_date_time_utc"], "%Y-%m-%dT%H:%M:%S")) * 1000
            if t < CUT:
                rows[t] = (t, x["opening_price"], x["high_price"], x["low_price"], x["trade_price"],
                           x["candle_acc_trade_price"], x["candle_acc_trade_volume"])
        if len(js) < 200:
            ended = True
            break
        to = min(rows) if rows else floor
    ts = sorted(rows)
    with open(path + ".tmp", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "o", "h", "l", "c", "krw", "vol"])
        for t in ts:
            w.writerow(rows[t])
    os.replace(path + ".tmp", path)
    print(b, len(ts), iso(ts[0]) if ts else "-", "history_start" if ended else "floor", flush=True)
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, coins))
print("done", flush=True)
