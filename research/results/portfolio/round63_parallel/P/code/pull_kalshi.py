"""Kalshi replication pull (Addendum A of HYPOTHESES_P.md). Keyless public API.
1) list historical markets of INXD and HIGHNY by event ticker per random day; keep close 2023-01-01..2024-12-31.
2) sample up to 150 events per series x era (Random(63)); for each bracket market pull hourly candles
   [close - 27 h, close - 5 h] (both entry times inside; end < 2025)."""
import sys, os, json, random, collections, datetime as dt, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/kalshi"
os.makedirs(OUT + "/candles", exist_ok=True)
B = "https://api.elections.kalshi.com/trade-api/v2"
net.MIN_GAP["api.elections.kalshi.com"] = 0.5
LO, HI = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc), dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
KEEP = ("ticker", "event_ticker", "close_time", "result", "status", "open_time", "volume", "settlement_value")


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def event_markets(series, d):
    """The historical endpoint ignores series_ticker, so query by event ticker <SERIES>-YYMONDD."""
    e = f"{series}-{d.year % 100:02d}{MON[d.month - 1]}{d.day:02d}"
    fn = f"{OUT}/ev/{e}.json"
    if os.path.exists(fn):
        return json.load(open(fn))
    s, b = net.get(f"{B}/historical/markets?event_ticker={e}&limit=100")
    if s != 200:
        return []
    rows = []
    for m in json.loads(b).get("markets") or []:
        try:
            c = ts(m["close_time"])
        except Exception:
            continue
        if LO <= c < HI:  # drop 2025+ at load, unprinted
            rows.append({k: m.get(k) for k in KEEP})
    json.dump(rows, open(fn, "w"))
    return rows


def candles(m):
    fn = f"{OUT}/candles/{m['ticker']}.json"
    if os.path.exists(fn):
        return "skip"
    c = int(ts(m["close_time"]).timestamp())
    st, en = c - 27 * 3600, min(c - 5 * 3600, int(HI.timestamp()) - 1)
    s, b = net.get(f"{B}/historical/markets/{m['ticker']}/candlesticks?start_ts={st}&end_ts={en}&period_interval=60")
    if s != 200:
        return f"fail {s}"
    open(fn, "wb").write(b)
    return "ok"


def main():
    os.makedirs(OUT + "/ev", exist_ok=True)
    todo = []
    for series in ("INXD", "HIGHNY"):
        for era in (2023, 2024):
            days = [dt.date(era, 1, 1) + dt.timedelta(days=i) for i in range(366 if era == 2024 else 365)]
            if series == "INXD":
                days = [d for d in days if d.weekday() < 5]
            random.Random(63).shuffle(days)
            got = 0
            for d in days:
                if got >= (30 if series == "INXD" else 150):
                    break
                ms = event_markets(series, d)
                if ms:
                    got += 1
                    todo += ms
            print(series, era, "events with markets", got, flush=True)
    print(len(todo), "markets to pull", flush=True)
    with cf.ThreadPoolExecutor(1) as ex:
        res = list(ex.map(candles, todo))
    print(collections.Counter(r.split()[0] for r in res), flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    try:
        main()
    except net.Stop as e:
        print("STOP", e, flush=True)
