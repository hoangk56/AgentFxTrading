"""HOLD events for PREREG A2-D5L (names and times only, no prices). Same pipeline as stream A, window moved:
1. titles from stream W's notice list (research/data/upbit_notices/raw/list_all, read-only), A's scan.py keys, category
   거래, first_listed_at in 2025-01-01..2026-10-29 UTC; KRW / 원화 in the title, no 종료 / 유의 (A's pull_detail.py filter);
2. bodies from W's cache if present, else api-manager.upbit.com/api/v1/announcements/<id> at >= 1.5 s (robots: no rules);
3. A/code/events.py markets() / start_time() / build() with CUT = 2026-10-30, LO = 2025-01-01 and perps.CUT = 2026-10-30
   (Binance perp traded >= 7 d before N); rows with N < 2025-01-01 dropped;
4. L = first Upbit KRW 1m candle, A/code/pull_first.py first() logic verbatim (api.upbit.com, 0.3 s);
   fallbacks as A2/code/events.py: a sibling coin's L in the same notice, else stated start + 5 min, else drop;
   rows with L < N (pre-existing KRW market) dropped.
Writes research/data/upbit_hold_a2/hold_events.csv. Run with python -I."""
import csv, datetime as dt, glob, json, os, shutil, sys, time, urllib.request, urllib.error
AC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/code"
sys.path.insert(0, AC)
import perps
import events as AE
HD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_hold_a2"
RAW = os.path.join(HD, "raw"); DET = os.path.join(RAW, "detail"); UP1 = os.path.join(RAW, "up1m")
for d in (DET, UP1):
    os.makedirs(d, exist_ok=True)
LOG = open(os.path.join(HD, "requests.log"), "a", buffering=1)
W = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw"
HOLD0, END = 1735689600000, 1793318400000
M = 60000
_last = {}


def get(url, gap):
    host = url.split("/")[2]
    for att in range(5):
        w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script", "Accept": "application/json"}), timeout=30) as r:
                b = r.read(); LOG.write(f"{ts}\t{url}\t{r.status}\t{len(b)}\n"); return b, r.status
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return None, e.code
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None, "fail"


def titles():
    keys = ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")
    lo = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc); hi = dt.datetime(2026, 10, 30, tzinfo=dt.timezone.utc)
    rows = {}
    for f in sorted(glob.glob(os.path.join(W, "list_all", "p*.json"))):
        for n in json.load(open(f))["data"]["notices"]:
            t = dt.datetime.fromisoformat(n["first_listed_at"]).astimezone(dt.timezone.utc)
            if lo <= t < hi and n["category"] == "거래" and any(k in n["title"] for k in keys):
                rows[n["id"]] = n
    return [i for i, n in rows.items() if ("KRW" in n["title"] or "원화" in n["title"]) and "종료" not in n["title"] and "유의" not in n["title"]]


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def page(coin, to):  # A/code/pull_first.py page(), own cache
    fn = os.path.join(UP1, f"{coin}_{to}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    b, c = get(f"https://api.upbit.com/v1/candles/minutes/1?market=KRW-{coin}&to={iso(to)}&count=200", 0.3)
    js = json.loads(b) if (b and c == 200) else {"_status": c}
    json.dump(js, open(fn, "w"))
    return js


def first(coin, N):  # A/code/pull_first.py first(), verbatim logic
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


if __name__ == "__main__":
    ids = titles()
    print(len(ids), "candidate notices")
    for i in ids:
        fn = os.path.join(DET, f"{i}.json")
        if os.path.exists(fn):
            continue
        src = os.path.join(W, "detail", f"{i}.json")
        if os.path.exists(src):
            shutil.copy(src, fn); continue
        b, c = get(f"https://api-manager.upbit.com/api/v1/announcements/{i}", 1.5)
        if b and c == 200:
            open(fn, "wb").write(b)
        else:
            print("detail fail", i, c)
    AE.RAW, AE.CUT, AE.LO = DET, END, HOLD0
    perps.CUT = END
    rows, skipped = AE.build()
    rows = [r for r in rows if r["N"] >= HOLD0]
    for r in rows:
        L, why = first(r["coin"], int(r["N"]))
        r["L1m"], r["L_note"] = (L or ""), why
    byn = {}
    for r in rows:
        if r["L1m"] and r["L1m"] >= r["N"]:
            byn.setdefault(r["nid"], []).append(r["L1m"])
    out = []
    for r in rows:
        if r["L1m"] and r["L1m"] < r["N"]:
            print("drop (pre-existing KRW market)", r["coin"], r["N_utc"]); continue
        if r["L1m"]:
            L, how = r["L1m"], "candle"
        elif byn.get(r["nid"]):
            L, how = byn[r["nid"]][0], "sibling L"
        elif r["stated"]:
            L, how = int(r["stated"]) + 300000, "stated+5m"
        else:
            print("drop (no L)", r["coin"], r["N_utc"]); continue
        out.append(dict(nid=r["nid"], coin=r["coin"], perp=r["perp"], N=r["N"], L=L, Lhow=how, N_utc=r["N_utc"],
                        day=r["N_utc"][:10], year=r["N_utc"][:4], era="HOLD"))
    with open(os.path.join(HD, "hold_events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for r in out:
        print(r["coin"], r["perp"], r["N_utc"], r["Lhow"], round((r["L"] - r["N"]) / 60000), "min to L")
    print(len(out), "HOLD events;", len(skipped), "skipped rows (incl. pre-2025)")
