"""Stream A4 event builder (no prices). Upbit KRW-listing notices 2020-01-01..2024-12-31 UTC, parsed with stream A's
markets() / start_time() (round65 A/code/events.py, loaded by path under another name, read-only; bodies from the same
caches as A3). Keeps a coin when the body puts it on the KRW market, it is not a stablecoin, Binance has NO USDT-M perp
>= 7 d old at N (A's perp_for, plus A3's 'live on N's day' variant, so the set is disjoint from A / A2), and Bybit has
a USDT linear perpetual with launchTime <= N - 7 d and not delivered before N + 1 d (instruments-info snapshots in
research/data/bybit_basis/, trading + closed; read-only). The dump directory listing check is in probe.py."""
import csv, glob, json, os, re, sys, datetime as dt
import importlib.util
A_CODE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/code"
_sp = importlib.util.spec_from_file_location("a_events", os.path.join(A_CODE, "events.py"))
AE = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AE)  # stream A's module, read-only
_pp = importlib.util.spec_from_file_location("a_perps", os.path.join(A_CODE, "perps.py"))
PP = importlib.util.module_from_spec(_pp); _pp.loader.exec_module(PP)

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BODY_DIRS = [os.path.join(R, "upbit_announce", "raw", "detail"), os.path.join(R, "upbit_notices", "raw", "detail")]
EVD = os.path.join(R, "upbit_announce", "raw", "detail_event")
CUT = 1735689600000
LO = 1577836800000
DAY = 86400000


def bybit_linear():
    out = {}
    for fn in ("instruments_linear.json", "instruments_linear_closed.json"):
        for x in json.load(open(os.path.join(R, "bybit_basis", fn))):
            if x.get("quoteCoin") != "USDT" or x.get("contractType") != "LinearPerpetual":
                continue
            m = re.fullmatch(r"(10*)?([A-Z0-9]+)", x["baseCoin"])
            if not m:
                continue
            dl = int(x["deliveryTime"] or 0)
            out.setdefault(m.group(2), []).append((x["symbol"], int(x["launchTime"]), dl, x["status"]))
            if m.group(1):
                out.setdefault(x["baseCoin"], []).append((x["symbol"], int(x["launchTime"]), dl, x["status"]))
    return out


def bybit_for(coin, t, BY):
    for sym, lt, dl, st in BY.get(coin, []):
        if lt <= t - 7 * DAY and (dl == 0 or dl >= t + DAY):
            return sym, lt
    return None, (min(x[1] for x in BY[coin]) if coin in BY else None)


def bodies():
    seen = {}
    for d in BODY_DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            j = json.load(open(f))
            x = j.get("data", j)
            if isinstance(x, dict) and "body" in x and x.get("id") not in seen:
                seen[x["id"]] = x
    return [seen[k] for k in sorted(seen)]


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def build():
    SP = PP.span(); BY = bybit_linear(); rows = []; log = []
    items = []
    for d in bodies():
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if not (LO <= t < CUT):
            continue
        mk, how = AE.markets(d)
        for coin, m in sorted(mk.items()):
            if "KRW" in m and coin not in AE.STABLE:
                items.append((d, t, coin, how, "trade"))
    for f in sorted(glob.glob(os.path.join(EVD, "*.json"))):  # A's declared secondary source (2020 이벤트 notices)
        d = json.load(open(f))["data"]
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if LO <= t < CUT:
            items.append((d, t, re.search(r"\(([A-Z0-9]{2,10})\)", d["title"]).group(1), "event", "event"))
    for d, t, coin, how, src in items:
        bc = AE.ALIAS.get(coin, coin)
        perp = PP.perp_for(bc, t, SP) or PP.perp_for(bc, t, SP, need_after=-DAY)
        bsym, blt = bybit_for(coin, t, BY)
        if perp:
            why = "has Binance perp " + perp
        elif bsym is None:
            why = "no Bybit perp" if blt is None else f"Bybit perp launched {utc(blt)[:10]} (< 7 d before N or later)"
        else:
            why = "KEEP"
        log.append((d["id"], coin, utc(t), why))
        if why == "KEEP":
            rows.append(dict(nid=d["id"], coin=coin, bsym=bsym, launch=blt, launch_utc=utc(blt), N=t, N_utc=utc(t),
                             stated=AE.start_time(d, coin) or "" if src == "trade" else "", how=how, src=src,
                             title=d["title"][:70]))
    rows.sort(key=lambda r: (r["N"], r["coin"]))
    return rows, log


if __name__ == "__main__":
    rows, log = build()
    OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A4"
    with open(os.path.join(OUT, "events_raw.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "events_screen.txt"), "w") as f:
        for x in log:
            print(*x, sep="\t", file=f)
    for x in log:
        if not x[3].startswith("has Binance"):
            print(*x, sep="\t")
    print(len(rows), "kept;", sum(x[3].startswith("has Binance") for x in log), "with a Binance perp")
