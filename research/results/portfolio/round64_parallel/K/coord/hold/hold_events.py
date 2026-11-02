"""HOLD events for K2: current Upbit KRW markets (research/data/upbit/raw/market_all.json, fetched by stream K on
2026-11-01) whose coin has a Binance USDT-M perp (base+USDT, else 1000+base+USDT; stablecoins and BTC excluded; fapi
underlyingType must be COIN), first KRW candle in 2025-01-01..2026-10-25 (none before 2025), and perp first daily
kline <= L - 7 days. L = first KRW 60-min candle at or after the first daily candle. Writes upbit_hold/k2_hold_events.csv.
Prints names and dates only (no prices)."""
import calendar, csv, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k2rule as k
R = k.R
STABLE = {"USDT", "USDC", "USDE", "USD1", "USDS", "DAI", "FDUSD", "TUSD", "PYUSD", "BTC"}
mk = json.load(open(os.path.join(R, "upbit", "raw", "market_all.json")))
bases = sorted({m["market"].split("-", 1)[1] for m in mk if m["market"].startswith("KRW-")} - STABLE)
ex = json.load(open(os.path.join(R, "binance_1m_wicks_hold", "exinfo", "exchangeInfo.json")))
noncoin = {x["symbol"] for x in ex["symbols"] if x.get("underlyingType") != "COIN"}
P1 = os.path.join(R, "binance", "perp_1d")


def perp(b):
    for s in (b + "USDT", "1000" + b + "USDT"):
        if os.path.exists(os.path.join(P1, s + ".csv")) and s not in noncoin:
            return s
    return None


def perp_first(s):
    with open(os.path.join(P1, s + ".csv")) as f:
        f.readline(); return int(f.readline().split(",")[0])


def ms(x):
    return calendar.timegm(time.strptime(x, "%Y-%m-%dT%H:%M:%S")) * 1000


H0, H1 = 1735689600000, 1793318400000 - 4 * k.DAY  # L < 2026-10-26
rows = []
for b in bases:
    s = perp(b)
    if not s:
        continue
    old = k.get(f"https://api.upbit.com/v1/candles/days?market=KRW-{b}&to=2025-01-01T00:00:00Z&count=1")
    if old:
        continue
    to, first = "2026-10-29T00:00:00Z", None
    while True:
        js = k.get(f"https://api.upbit.com/v1/candles/days?market=KRW-{b}&to={to}&count=200") or []
        if not js:
            break
        first = min(ms(x["candle_date_time_utc"]) for x in js)
        if len(js) < 200:
            break
        to = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(first / 1000))
    if first is None or first < H0:
        continue
    hrs = k.get(f"https://api.upbit.com/v1/candles/minutes/60?market=KRW-{b}&to={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime((first + 28 * k.H) / 1000))}&count=28") or []
    hrs = sorted(h for h in (ms(x["candle_date_time_utc"]) for x in hrs) if h >= first)
    if not hrs:
        continue
    L, pf = hrs[0], perp_first(s)
    if not (H0 <= L < H1) or pf > L - 7 * k.DAY:
        print("skip", b, s, time.strftime("%Y-%m-%d %H:%M", time.gmtime(L / 1000)), "perp_first", time.strftime("%Y-%m-%d", time.gmtime(pf / 1000)))
        continue
    rows.append((b, s, L, pf))
    print("event", b, s, time.strftime("%Y-%m-%d %H:%M", time.gmtime(L / 1000)), flush=True)
with open(os.path.join(k.D, "k2_hold_events.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["coin", "sym", "L", "perp_first"]); w.writerows(rows)
print(len(rows), "HOLD events of", len(bases), "KRW bases")
