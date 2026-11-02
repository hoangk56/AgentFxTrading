"""First Upbit KRW 1m candle (= actual KRW trading start L) for each notice event, via the public quotation API
api.upbit.com/v1/candles/minutes/1 (robots.txt 404, logged). Walks forward from the notice until candles appear, then
backward while a full page of 200 sits after the notice. Raw pages saved under research/data/upbit_announce/raw/up1m/."""
import os, sys, json, csv, datetime as dt
os.environ.setdefault("GAP", "0.3")
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, RAW
M = 60000
OUT = os.path.join(RAW, "up1m"); os.makedirs(OUT, exist_ok=True)
EV = os.path.join(os.path.dirname(__file__), "..", "notice_events.csv")


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def page(coin, to):
    fn = os.path.join(OUT, f"{coin}_{to}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    b, c = get(f"https://api.upbit.com/v1/candles/minutes/1?market=KRW-{coin}&to={iso(to)}&count=200")
    if c == 403:
        raise SystemExit("403 stop")
    js = json.loads(b) if (b and c == 200) else {"_status": c}
    json.dump(js, open(fn, "w"))
    return js


def first(coin, N):
    to = N + 200 * M
    while to <= N + 48 * 3600000:
        js = page(coin, to)
        if isinstance(js, dict):
            return None, f"status {js.get('_status')}"
        if js:
            break
        to += 180 * M
    else:
        return None, "no candles within 48 h"
    while True:
        ts = sorted(int(dt.datetime.fromisoformat(x["candle_date_time_utc"]).replace(tzinfo=dt.timezone.utc).timestamp() * 1000) for x in js)
        if ts[0] < N - M:
            return ts[0], "pre-existing KRW candle before notice"
        if len(js) < 200:
            return ts[0], "ok"
        js = page(coin, ts[0])
        if not js:
            return ts[0], "ok"


rows = list(csv.DictReader(open(EV)))
res = []
for r in rows:
    L, why = first(r["coin"], int(r["N"]))
    r["L1m"] = L or ""; r["L1m_utc"] = iso(L) if L else ""; r["L_note"] = why
    print(r["coin"], r["N_utc"], r["stated_utc"], r["L1m_utc"], why)
    res.append(r)
with open(os.path.join(os.path.dirname(__file__), "..", "notice_events_L.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
