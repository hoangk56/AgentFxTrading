"""Stream A3: first Upbit KRW 1m candle L for each event (A's pull_first walk; api.upbit.com quotation API, >= 0.3 s,
own cache research/data/upbit_spot_notice/up1m/). Fallbacks (declared in HYPOTHESES_A3.md): a sibling coin's L from
stream A's notice_events_L.csv for the same notice, else stated start + 5 min. Writes A3/events.csv (main + info)."""
import csv, json, os, sys, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/code")
import net
from events import build, bodies, AE, DAY

M = 60000
UP = os.path.join(net.D, "up1m"); os.makedirs(UP, exist_ok=True)
A_UP = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_announce/raw/up1m"
A_EV = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/notice_events_L.csv"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3"
INFO = [("JST", 1433), ("T", 2474), ("GAL", 4363)]  # declared info-only events (GAL: perp live at N, gone next day)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def page(coin, to):
    for d in (A_UP, UP):
        fn = os.path.join(d, f"{coin}_{to}.json")
        if os.path.exists(fn):
            return json.load(open(fn))
    url = f"https://api.upbit.com/v1/candles/minutes/1?market=KRW-{coin}&to={iso(to)}&count=200"
    r, s = net.opener(url)
    body = r.read() if r else b""
    if r:
        net.log(url, s, len(body), "GET"); r.close()
    js = json.loads(body) if (body and s == 200) else {"_status": s}
    json.dump(js, open(os.path.join(UP, f"{coin}_{to}.json"), "w"))
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


def main():
    rows, _ = build()
    for r in rows:
        r["set"] = "main"
    B = {d["id"]: d for d in bodies()}
    for coin, nid in INFO:
        d = B[nid]; t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        rows.append(dict(nid=nid, coin=coin, spot=coin + "USDT", N=t,
                         N_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                         stated=AE.start_time(d, coin) or "", how="info", src="trade", title=d["title"][:70], set="info"))
    sib = {}
    for x in csv.DictReader(open(A_EV)):
        if x["L1m"]:
            sib.setdefault(x["nid"], []).append((x["coin"], int(x["L1m"])))
    for r in rows:
        assert r["N"] < 1735689600000
        L, why = first(r["coin"], r["N"])
        if L is None and str(r["nid"]) in sib:
            c, L = sib[str(r["nid"])][0]; why += f"; {c}'s L (same notice)"
        elif L is None and r["stated"]:
            L = int(r["stated"]) + 300000; why += "; stated + 5 min"
        r["L"] = L; r["L_utc"] = iso(L) if L else ""; r["L_note"] = why
        r["era"] = "IS" if r["N"] < 1640995200000 else "VAL"
        print(r["coin"], r["set"], r["N_utc"], r["stated"] and iso(int(r["stated"])), r["L_utc"], why, flush=True)
    with open(os.path.join(OUT, "events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
