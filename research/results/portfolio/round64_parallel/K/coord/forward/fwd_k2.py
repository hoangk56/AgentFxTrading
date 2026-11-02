"""Public-data forward log for PREREG K2 (supplementary; the registered promotion needs demo trades). Same rule and
pricing as the HOLD run (coord/hold/k2rule.py: short alt perp / long BTCUSDT perp at the close of the 1m bar starting
at L + 1 h, exit 72 h later, 42 bp + real funding). Events as coord/hold/hold_events.py, with plumbing changes only:
- Upbit's market list is re-fetched each run (api.upbit.com/v1/market/all, keyless) instead of stream K's 11-01 file;
- the Binance perp age check uses fapi 1d klines (local perp_1d ends 2026-10-30): first traded day <= L - 7 d;
- window: L >= 2026-10-26 00:00 UTC (the HOLD run took L < 2026-10-26) and L + 73 h before the run time.
Appends each new graded event to research/data/upbit_fwd_k2/fwd_log.csv. Usage: python -I fwd_k2.py"""
import calendar, csv, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hold"))
import numpy as np
import k2rule as k
FD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_fwd_k2"
os.makedirs(FD, exist_ok=True)
k.LOG = open(os.path.join(FD, "requests.log"), "a", buffering=1)
STABLE = {"USDT", "USDC", "USDE", "USD1", "USDS", "DAI", "FDUSD", "TUSD", "PYUSD", "BTC"}
FWD0 = 1792972800000  # 2026-10-26 00:00 UTC
NOW = int(time.time() * 1000)
ex = json.load(open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_1m_wicks_hold/exinfo/exchangeInfo.json"))
NONCOIN = {x["symbol"] for x in ex["symbols"] if x.get("underlyingType") != "COIN"}


def ms(x):
    return calendar.timegm(time.strptime(x, "%Y-%m-%dT%H:%M:%S")) * 1000


_first = {}


def perp_first(sym):
    if sym not in _first:
        js = k.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1d&startTime=1567296000000&limit=3")
        _first[sym] = int(js[0][0]) if js else None
    return _first[sym]


def perp(b):
    for s in (b + "USDT", "1000" + b + "USDT"):
        if s in NONCOIN:
            continue
        if perp_first(s):
            return s
    return None


if __name__ == "__main__":
    mk = k.get("https://api.upbit.com/v1/market/all?isDetails=false") or []
    json.dump(mk, open(os.path.join(FD, f"market_all_{NOW}.json"), "w"))
    bases = sorted({m["market"].split("-", 1)[1] for m in mk if m["market"].startswith("KRW-")} - STABLE)
    logp = os.path.join(FD, "fwd_log.csv")
    done = {r["coin"] for r in csv.DictReader(open(logp))} if os.path.exists(logp) else set()
    new = []
    for b in bases:
        if b in done:
            continue
        old = k.get(f"https://api.upbit.com/v1/candles/days?market=KRW-{b}&to={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(FWD0 / 1000))}&count=1")
        if old:
            continue  # KRW market existed before the forward window
        js = k.get(f"https://api.upbit.com/v1/candles/days?market=KRW-{b}&count=200") or []
        if not js:
            continue
        first = min(ms(x["candle_date_time_utc"]) for x in js)
        hrs = k.get(f"https://api.upbit.com/v1/candles/minutes/60?market=KRW-{b}&to={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime((first + 28 * k.H) / 1000))}&count=28") or []
        hrs = sorted(h for h in (ms(x["candle_date_time_utc"]) for x in hrs) if h >= first)
        if not hrs:
            continue
        L = hrs[0]
        s = perp(b)
        if not s or L < FWD0 or perp_first(s) > L - 7 * k.DAY or L + 73 * k.H > NOW - 3600000:
            print("not an event (yet)", b, time.strftime("%Y-%m-%d %H:%M", time.gmtime(L / 1000)), s); continue
        x = k.trade(s, L)
        if x is None:
            print("no prices yet", b); continue
        new.append((b, s, L, x[3]))
    with open(logp, "a", newline="") as f:
        w = csv.writer(f)
        if not done:
            w.writerow(["coin", "sym", "L", "net"])
        w.writerows(new)
    allr = list(csv.DictReader(open(logp)))
    v = np.array([float(r["net"]) for r in allr])
    print(f"K2 forward log: {len(v)} events" + (f", mean {v.mean()*1e4:+.0f} bp" if len(v) else ""))
