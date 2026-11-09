"""Stream WA seconds check (HYPOTHESES_WA.md: entries at the first aggTrade at or after post + 5 s).
fapi /aggTrades only serves the last 2 days and spot REST returns [] for old windows, so this uses data.binance.vision
USDT-M daily aggTrades for a random sample of 30 event days per era (seed 74). For every BI/BO/EI/EO/M/B event on
those days (no one-at-a-time filter) it records the first aggTrade price at or after post + 5, + 10, + 65, + 305,
+ 905, + 3605 s and the 1-minute-design entry time (next bar open after post + 5 s). Zips go to an empty tmp folder
and are deleted after parsing. Output research/data/whale_alert/secs.csv. Run with python -I."""
import csv, io, os, sys, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/whale_alert"
TMP = os.path.join(D, "tmp_agg"); os.makedirs(TMP, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
END = 1735689600
OFF = (5, 10, 65, 305, 905, 3605)
SYM = {"BI": "BTCUSDT", "BO": "BTCUSDT", "EI": "ETHUSDT", "EO": "ETHUSDT", "M": "BTCUSDT", "B": "BTCUSDT"}


def log(url, s, n):
    LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t{s}\t{n}\n")


def fetch(url, zp):
    for att in range(4):
        time.sleep(0.3)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=120)
            n = 0
            with open(zp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); n += len(b)
            log(url, r.status, n); return True
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1)); continue
            return False
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0); time.sleep(10)
    return False


def load(zp):
    with zipfile.ZipFile(zp) as z:
        raw = z.read(z.namelist()[0])
    os.remove(zp)
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(1, 5), dtype=np.float64, ndmin=2)
    t = a[:, 1]
    if t.max() > 1e14:
        t = np.floor(t / 1000)
    o = np.argsort(t, kind="stable")
    return t[o].astype(np.int64), a[o, 0]


def main():
    ev = []
    with open(os.path.join(D, "events.csv")) as f:
        for r in csv.DictReader(f):
            if r["era"] in ("IS", "VAL"):
                ev.append(dict(id=int(r["id"]), ts=float(r["ts"]), era=r["era"], kind=r["kind"], usd=float(r["usd"])))
    rng = np.random.default_rng(74)
    days = []
    for era in ("IS", "VAL"):
        ds = sorted({int(e["ts"]) // 86400 for e in ev if e["era"] == era and e["ts"] + 3700 < END})
        days += list(rng.choice(ds, 30, replace=False))
    out = os.path.join(D, "secs.csv")
    done = set()
    if os.path.exists(out):
        with open(out) as f:
            done = {(int(r["day"]), r["sym"]) for r in csv.DictReader(f)}
    new = not os.path.exists(out)
    f = open(out, "a", newline=""); w = csv.writer(f)
    if new:
        w.writerow(["day", "sym", "id", "era", "kind", "usd", "ts", "bar_t"] + [f"p{o}" for o in OFF] + ["t5", "p_bar"])
    for k, d in enumerate(sorted(days)):
        dayev = [e for e in ev if int(e["ts"]) // 86400 == d]
        for sym in ("BTCUSDT", "ETHUSDT"):
            es = [e for e in dayev if SYM[e["kind"]] == sym]
            if not es or (d, sym) in done:
                continue
            ds = dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).strftime("%Y-%m-%d")
            ds2 = dt.datetime.fromtimestamp(d * 86400 + 86400, dt.timezone.utc).strftime("%Y-%m-%d")
            ts_all = []; ps_all = []
            for dd in ([ds, ds2] if d * 86400 + 86400 < END else [ds]):  # next day for exits that cross midnight
                url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{dd}.zip"
                zp = os.path.join(TMP, "a.zip")
                if fetch(url, zp):
                    t, p = load(zp); ts_all.append(t); ps_all.append(p)
            if not ts_all:
                print("MISS", sym, ds, flush=True); continue
            t = np.concatenate(ts_all); p = np.concatenate(ps_all)
            for e in es:
                q = []
                for o in OFF:
                    j = np.searchsorted(t, int(np.ceil((e["ts"] + o) * 1000)), "left")
                    q.append(p[j] if j < len(t) else np.nan)
                j5 = np.searchsorted(t, int(np.ceil((e["ts"] + 5) * 1000)), "left")
                bar = (int(np.ceil((e["ts"] + 5) * 1000)) + 59999) // 60000 * 60000
                jb = np.searchsorted(t, bar, "left")
                w.writerow([d, sym, e["id"], e["era"], e["kind"], e["usd"], e["ts"], bar] + [f"{x:.8g}" for x in q] +
                           [int(t[j5]) if j5 < len(t) else "", f"{p[jb]:.8g}" if jb < len(t) else ""])
            f.flush()
            print(k + 1, "/", len(days), sym, ds, len(es), "events", len(t), "trades", flush=True)


if __name__ == "__main__":
    main()
