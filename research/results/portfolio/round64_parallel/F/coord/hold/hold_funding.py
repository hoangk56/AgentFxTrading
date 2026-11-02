"""Funding history 2025-01-01..2026-10-29 for HOLD pull_list symbols absent from research/data/binance/funding, from the
public keyless fapi /fapi/v1/fundingRate (robots.txt only blocks named search bots). >= 0.25 s apart, back off on
418 / 429, stop on 403. Writes research/data/binance_1m_wicks_hold/funding/<SYM>.csv (t,rate). Run with python -I."""
import csv, json, os, time, urllib.request, urllib.error, datetime as dt
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks_hold"); OUT = os.path.join(D, "funding"); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(D, "requests.log"), "a")
S, E = 1735689600000, 1793318400000
syms = sorted({r["sym"] for r in csv.DictReader(open(os.path.join(D, "pull_list.csv")))})
syms = [s for s in syms if not os.path.exists(os.path.join(R, "data", "binance", "funding", s + ".csv"))]
for s in syms:
    rows, t = [], S
    while t < E:
        url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}&startTime={t}&endTime={E - 1}&limit=1000"
        for att in range(5):
            time.sleep(0.3)
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=30) as r:
                    body = r.read()
                log.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},200,{len(body)}\n"); log.flush()
                j = json.loads(body); break
            except urllib.error.HTTPError as e:
                log.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{e.code},0\n"); log.flush()
                if e.code == 403:
                    raise SystemExit("403: stop")
                time.sleep(30 * (att + 1)); j = None
        if not j:
            break
        rows += [(int(x["fundingTime"]), x["fundingRate"]) for x in j]
        if len(j) < 1000:
            break
        t = int(j[-1]["fundingTime"]) + 1
    with open(os.path.join(OUT, s + ".csv"), "w") as f:
        f.write("t,rate\n")
        for a, b in rows:
            if a < E:
                f.write(f"{a},{b}\n")
    print(s, len(rows), flush=True)
