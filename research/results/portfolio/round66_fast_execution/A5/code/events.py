"""Stream A5 event screen (no prices). Upbit KRW-listing notices 2020-01-01..2024-12-31 UTC, parsed with stream A's
markets() / start_time() (round65 A/code/events.py, loaded by path, read-only; perps.py from the same folder). Bodies from
the existing caches only (research/data/upbit_announce/raw/{detail,detail_event}, research/data/upbit_notices/raw/detail).
Keep a coin if: KRW market, not a stablecoin, NO Binance USDT-M perp >= 7 d old at N (A's perp_for, also the
'live on N's day' variant from A3), and a Binance perp whose FIRST trade is in [N - 7 d, N - 1 d] and which still trades at
N + 1 d. First trade = first 1m kline of research/data/perp_launch/k1m (stream N0, read-only) when present, else the first
active day of research/data/binance/perp_1d (day precision, flagged)."""
import csv, glob, json, os, re, sys, datetime as dt
import importlib.util
A_CODE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/code"
sys.path.insert(0, A_CODE)
_sp = importlib.util.spec_from_file_location("a_events", os.path.join(A_CODE, "events.py"))
AE = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AE)
import perps  # noqa: E402  (stream A's copy, read-only)
import numpy as np  # noqa: E402

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BODY_DIRS = [os.path.join(R, "upbit_announce", "raw", "detail"), os.path.join(R, "upbit_notices", "raw", "detail")]
EVD = os.path.join(R, "upbit_announce", "raw", "detail_event")
K1M = os.path.join(R, "perp_launch", "k1m")
CUT = 1735689600000
LO = 1577836800000
DAY = 86400000
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A5"


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def bodies():
    seen = {}
    for d in BODY_DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            j = json.load(open(f)); x = j.get("data", j)
            if isinstance(x, dict) and "body" in x and x.get("id") not in seen:
                seen[x["id"]] = x
    return [seen[k] for k in sorted(seen)]


_K = {}


def first_trade(sym, day_ms):
    """Precise first trade (first 1m kline open time) from N0's k1m cache if it starts on the perp_1d first day."""
    if sym not in _K:
        p = os.path.join(K1M, sym + ".npz"); _K[sym] = None
        if os.path.exists(p):
            z = np.load(p); ot, n = z["ot"], z["n"]; w = np.where(n > 0)[0]
            if len(w):
                _K[sym] = int(ot[w[0]])
    f = _K[sym]
    if f is not None and day_ms <= f < day_ms + DAY:
        return f, "k1m"
    return day_ms, "day"


def young(coin, t, SP):
    """(symbol, first trade ms, precision, span end) of a perp first trading in [t - 8 d, t] (screened finer below)."""
    out = []
    for s in (coin + "USDT", "1000" + coin + "USDT"):
        for a, b in SP.get(s, []):
            if t - 8 * DAY <= a <= t:
                f, how = first_trade(s, a)
                out.append((s, f, how, b))
    return out


def screen(coin, t, SP):
    c = AE.ALIAS.get(coin, coin)
    old = perps.perp_for(c, t, SP) or perps.perp_for(c, t, SP, need_after=-DAY)
    if old:
        return "has perp >= 7 d " + old, None
    ys = young(c, t, SP)
    if not ys:
        return "no perp in N - 8 d .. N", None
    s, f, how, b = ys[0]
    age = (t - f) / DAY
    if f > t - DAY:
        return f"perp {s} < 1 d old ({age:.2f} d, {how})", (s, f, how, b)
    if f < t - 7 * DAY:
        return f"perp {s} > 7 d ({age:.2f} d, {how})", (s, f, how, b)
    if b < t + DAY:
        return f"perp {s} stops before N + 1 d (last day {utc(b)[:10]})", (s, f, how, b)
    return "KEEP", (s, f, how, b)


def build():
    SP = perps.span(); rows = []; log = []
    src = []
    for d in bodies():
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if not (LO <= t < CUT):
            continue
        mk, how = AE.markets(d)
        for coin, m in sorted(mk.items()):
            if "KRW" not in m or coin in AE.STABLE:
                continue
            src.append((d, coin, t, how, "trade"))
    for f in sorted(glob.glob(os.path.join(EVD, "*.json"))):
        d = json.load(open(f))["data"]
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if LO <= t < CUT:
            src.append((d, re.search(r"\(([A-Z0-9]{2,10})\)", d["title"]).group(1), t, "event", "event"))
    for d, coin, t, how, sr in src:
        why, y = screen(coin, t, SP)
        log.append((d["id"], coin, utc(t), why))
        if why == "KEEP":
            s, f, fh, b = y
            st = AE.start_time(d, coin) if sr == "trade" else None
            rows.append(dict(nid=d["id"], coin=coin, perp=s, N=t, N_utc=utc(t), perp_first=f, perp_first_utc=utc(f),
                             first_prec=fh, age_d=round((t - f) / DAY, 2), stated=st or "", how=how, src=sr,
                             title=d["title"][:70]))
    rows.sort(key=lambda r: (r["N"], r["coin"]))
    return rows, log


if __name__ == "__main__":
    rows, log = build()
    with open(os.path.join(OUT, "events_screen.txt"), "w") as f:
        for x in log:
            print(*x, sep="\t", file=f)
    for x in log:
        if x[3] != "no perp in N - 8 d .. N" and not x[3].startswith("has perp"):
            print(*x, sep="\t")
    if rows:
        with open(os.path.join(OUT, "events_raw.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(len(rows), "kept of", len(log), "KRW coin-notices")
    for r in rows:
        print(r["nid"], r["coin"], r["perp"], r["N_utc"], "first", r["perp_first_utc"], r["first_prec"], r["age_d"], r["stated"], r["how"])
