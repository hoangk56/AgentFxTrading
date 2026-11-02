"""Find the first Bithumb KRW 60-min candle of every Bithumb KRW coin with a Binance USDT-M perp, plus a probe of
delisted visibility. All requests end at to=2025-01-01T08:59:59 KST (= 2024-12-31 23:59:59 UTC) or earlier.
Usage: python -I pull_events.py first | probe | btc"""
import csv, json, os, sys, time, calendar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bnet
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BD = os.path.join(R, "bithumb")
API = "https://api.bithumb.com/v1/candles/"
TO_MAX = "2025-01-01T08:59:59"  # KST
CUT = 1735689600000
H, DAY, KST = 3600000, 86400000, 9 * 3600000


def perps():
    return {f[:-4]: f[:-4] for f in os.listdir(os.path.join(R, "binance", "perp_1d")) if f.endswith("USDT.csv")}


def mapsym(coin, P):
    for pre in ("", "1000", "1000000", "1M"):
        s = pre + coin + "USDT"
        if s in P:
            return s
    return None


def ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%S")) * 1000


def kst(ms):  # ms UTC -> KST string for `to`
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime((ms + KST) / 1000))


def candles(kind, coin, to, count):
    js = bnet.get(f"{API}{kind}?market=KRW-{coin}&to={to}&count={count}")
    if isinstance(js, dict):
        return js  # error object
    return [x for x in (js or []) if ts(x["candle_date_time_utc"]) < CUT]


def first(coin):
    m = candles("months", coin, TO_MAX, 200)
    if isinstance(m, dict) or not m:
        return dict(status="none" if not isinstance(m, dict) else m.get("error", {}).get("message", "err"))
    if len(m) >= 200:
        return dict(status="months_full")
    m0 = min(ts(x["candle_date_time_utc"]) for x in m)
    d = candles("days", coin, kst(min(m0 + 33 * DAY, CUT - 1000)), 40)
    if isinstance(d, dict) or not d:
        return dict(status="nodays", m0=m0)
    d = sorted(d, key=lambda x: ts(x["candle_date_time_utc"]))
    d0 = d[0]
    t0 = ts(d0["candle_date_time_utc"])
    h = candles("minutes/60", coin, kst(min(t0 + DAY, CUT - 1000)), 24)
    if isinstance(h, dict) or not h:
        return dict(status="nohours", m0=m0, d0=t0)
    h = sorted(h, key=lambda x: ts(x["candle_date_time_utc"]))
    return dict(status="ok", m0=m0, d0=t0, L=ts(h[0]["candle_date_time_utc"]), d0_close=d0["trade_price"],
                d0_open=d0["opening_price"], d0_prev=d0.get("prev_closing_price"), d0_krw=d0["candle_acc_trade_price"],
                h0_krw=h[0]["candle_acc_trade_price"], h0_open=h[0]["opening_price"], h0_close=h[0]["trade_price"],
                n_month=len(m))


if __name__ == "__main__":
    mode = sys.argv[1]
    P = perps()
    mk = json.load(open(os.path.join(BD, "raw", "market_all.json")))
    krw = sorted(x["market"][4:] for x in mk if x["market"].startswith("KRW-"))
    if mode == "first":
        rows = []
        for c in krw:
            s = mapsym(c, P)
            if not s or c == "BTC":
                continue
            r = first(c); r.update(coin=c, sym=s)
            rows.append(r); print(c, s, r.get("status"), time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["L"] / 1000)) if "L" in r else "", flush=True)
        keys = ["coin", "sym", "status", "m0", "d0", "L", "d0_open", "d0_close", "d0_prev", "d0_krw", "h0_open", "h0_close", "h0_krw", "n_month"]
        with open(os.path.join(BD, "first_candles.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in rows]
    elif mode == "probe":
        base = set()
        for s in P:
            b = s[:-4]
            for pre in ("1000000", "1000", "1M"):
                if b.startswith(pre) and len(b) > len(pre):
                    b = b[len(pre):]; break
            base.add(b)
        miss = sorted(base - set(krw))
        out = []
        for c in miss:
            js = bnet.get(f"{API}months?market=KRW-{c}&to={TO_MAX}&count=1")
            st = "found" if isinstance(js, list) and js else (js.get("error", {}).get("message") if isinstance(js, dict) else "empty")
            out.append((c, st)); print(c, st, flush=True)
        with open(os.path.join(BD, "probe_delisted.csv"), "w", newline="") as f:
            csv.writer(f).writerows([("coin", "status")] + out)
    elif mode == "btc":
        rows, to = [], TO_MAX
        while True:
            d = candles("days", "BTC", to, 200)
            if isinstance(d, dict) or not d:
                break
            rows += [(ts(x["candle_date_time_utc"]), x["trade_price"]) for x in d]
            t0 = min(ts(x["candle_date_time_utc"]) for x in d)
            if t0 < 1575158400000:  # 2019-12-01
                break
            to = kst(t0 - 1000)
        rows = sorted(set(rows))
        with open(os.path.join(BD, "btc_days.csv"), "w", newline="") as f:
            csv.writer(f).writerows([("t", "close")] + rows)
        print(len(rows), "btc days")
