"""Stream A3 event builder (no prices). Upbit KRW-listing notices 2020-01-01..2024-12-31 UTC, parsed with stream A's
markets() / start_time() (round65 A/code/events.py, imported read-only). Keeps a coin when the body puts it on the KRW
market, it is not a stablecoin, Binance has NO USDT-M perp trading >= 7 d before N (A's perp_for), and Binance has a
SPOT <COIN>USDT pair whose first kline is >= 7 d before N (research/data/binance/spot_first.csv). Bodies come only from
the existing caches research/data/upbit_announce/raw/{detail,detail_event} and research/data/upbit_notices/raw/detail."""
import csv, glob, json, os, re, sys, datetime as dt
A_CODE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/code"
sys.path.insert(0, A_CODE)
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("a_events", os.path.join(A_CODE, "events.py"))
AE = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AE)  # stream A's module, read-only
import perps  # noqa: E402

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BODY_DIRS = [os.path.join(R, "upbit_announce", "raw", "detail"), os.path.join(R, "upbit_notices", "raw", "detail")]
EVD = os.path.join(R, "upbit_announce", "raw", "detail_event")
CUT = 1735689600000
LO = 1577836800000
DAY = 86400000
SPOT_ALIAS = {"BEAM": "BEAMX"}  # Upbit ticker -> Binance base where they differ (as A)


def spot_first():
    out = {}
    for row in csv.reader(open(os.path.join(R, "binance", "spot_first.csv"))):
        if row and row[0].endswith("USDT") and row[1].strip():
            out[row[0]] = int(row[1])
    return out


def bodies():
    seen = {}
    for d in BODY_DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            j = json.load(open(f))
            x = j.get("data", j)
            if isinstance(x, dict) and "body" in x and x.get("id") not in seen:
                seen[x["id"]] = x
    return [seen[k] for k in sorted(seen)]


def build(verbose=False):
    SP = perps.span(); SF = spot_first(); rows = []; log = []
    for d in bodies():
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if not (LO <= t < CUT):
            continue
        mk, how = AE.markets(d)
        for coin, m in sorted(mk.items()):
            if "KRW" not in m or coin in AE.STABLE:
                continue
            base = SPOT_ALIAS.get(coin, coin)
            perp = perps.perp_for(AE.ALIAS.get(coin, coin), t, SP)
            # also drop a perp >= 7 d old that is live on N's day but stops within 1 d (GAL 2024-07-11, Galxe migration)
            perp = perp or perps.perp_for(AE.ALIAS.get(coin, coin), t, SP, need_after=-DAY)
            sp = base + "USDT"; f = SF.get(sp)
            st = AE.start_time(d, coin)
            why = ("has perp " + perp) if perp else ("no spot pair" if f is None else
                                                   ("spot < 7 d old" if f > t - 7 * DAY else "KEEP"))
            log.append((d["id"], coin, dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), why))
            if why == "KEEP":
                rows.append(dict(nid=d["id"], coin=coin, spot=sp, N=t,
                                 N_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                 stated=st or "", how=how, src="trade", title=d["title"][:70]))
    for f in sorted(glob.glob(os.path.join(EVD, "*.json"))):  # A's declared secondary source (2020 이벤트 notices)
        d = json.load(open(f))["data"]
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        coin = re.search(r"\(([A-Z0-9]{2,10})\)", d["title"]).group(1)
        perp = perps.perp_for(coin, t, SP); sp = coin + "USDT"; fs = SF.get(sp)
        why = ("has perp " + perp) if perp else ("no spot pair" if fs is None else ("spot < 7 d old" if fs > t - 7 * DAY else "KEEP"))
        log.append((d["id"], coin + " (event notice)", dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), why))
        if why == "KEEP" and t < CUT:
            rows.append(dict(nid=d["id"], coin=coin, spot=sp, N=t,
                             N_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                             stated="", how="event", src="event", title=d["title"][:70]))
    rows.sort(key=lambda r: (r["N"], r["coin"]))
    return rows, log


if __name__ == "__main__":
    rows, log = build()
    OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3"
    with open(os.path.join(OUT, "events_raw.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "events_screen.txt"), "w") as f:
        for x in log:
            print(*x, sep="\t", file=f)
    for x in log:
        print(*x, sep="\t")
    print(len(rows), "kept")
