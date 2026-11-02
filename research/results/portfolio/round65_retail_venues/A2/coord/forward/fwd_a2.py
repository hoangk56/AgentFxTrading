"""Public-data forward log for PREREG A2-D5L (supplementary evidence; the registered promotion needs real fills from a
bot). Same pipeline as the HOLD run (hold_events.py / hold_pull.py / core.grade), window FWD0 = 2026-10-30 00:00 UTC
.. FWD1 = today 00:00 UTC minus 1 day (data.binance.vision daily files appear the next day). Differences, all plumbing:
- the Upbit notice list is re-fetched (api-manager.upbit.com, >= 1.5 s) back to FWD0 instead of stream W's cache;
- the Binance perp age check uses fapi 1d klines for the candidate coin (local perp_1d ends 2026-10-30), same rule
  as A's perps.perp_for: first traded day <= N - 7 d and still trading at N + 1 d.
Writes research/data/upbit_fwd_a2/: events.csv, npz/, fwd_log.csv (one row per graded event, appended once).
Usage: python -I fwd_a2.py   (re-run any time; already graded events are not re-graded)."""
import csv, datetime as dt, glob, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hold"))
import numpy as np
import core                      # A2 analyze / checks logic, net.LOG redirected below
import hold_events as HE         # get(), first(), page(); its `events` import resolves to A2's module here, so
import importlib.util            # stream A's events.py is loaded by path under its own name below
_spec = importlib.util.spec_from_file_location("a_events", os.path.join(HE.AC, "events.py"))
HE.AE = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(HE.AE)
FD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_fwd_a2"
for d in ("raw/list", "raw/detail", "raw/up1m", "raw/perp1d", "npz", "tmp"):
    os.makedirs(os.path.join(FD, d), exist_ok=True)
LOG = open(os.path.join(FD, "requests.log"), "a", buffering=1)
HE.LOG = LOG
core.net.LOG = LOG
HE.DET, HE.UP1 = os.path.join(FD, "raw/detail"), os.path.join(FD, "raw/up1m")
DAY = 86400000
FWD0 = 1793318400000  # 2026-10-30 00:00 UTC
today = int(dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
FWD1 = today - DAY


def fetch_list():
    rows = {}
    for p in range(1, 60):
        fn = os.path.join(FD, "raw/list", f"p{p:04d}.json")
        b, c = HE.get(f"https://api-manager.upbit.com/api/v1/announcements?os=web&page={p}&per_page=20&category=all", 1.5)
        if not (b and c == 200):
            print("list fail", p, c); break
        open(fn, "wb").write(b)
        ns = json.loads(b)["data"]["notices"]
        for n in ns:
            rows[n["id"]] = n
        # pinned old notices sit on the first pages, so stop only when a whole page is older than FWD0
        if not ns or max(dt.datetime.fromisoformat(n["first_listed_at"]).timestamp() * 1000 for n in ns) < FWD0:
            break
    return rows


_SPAN = {}


def perp_for(ticker, t, spans=None, need_before=7 * DAY, need_after=1 * DAY):
    for s in (ticker + "USDT", "1000" + ticker + "USDT"):
        if s not in _SPAN:
            b, c = HE.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1d&startTime={t - 400 * DAY}&endTime={t + 2 * DAY}&limit=500", 0.3)
            ks = json.loads(b) if (b and c == 200) else []
            act = [int(k[0]) for k in ks if float(k[7]) > 0]
            _SPAN[s] = (act[0], act[-1]) if act else None
            json.dump(ks, open(os.path.join(FD, "raw/perp1d", f"{s}_{t}.json"), "w"))
        sp = _SPAN[s]
        if sp and sp[0] <= t - need_before and sp[1] >= t + need_after:
            return s
    return None


def build_events():
    notes = fetch_list()
    keys = ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")
    ids = []
    for i, n in notes.items():
        t = dt.datetime.fromisoformat(n["first_listed_at"]).timestamp() * 1000
        if FWD0 <= t < FWD1 and n["category"] == "거래" and any(k in n["title"] for k in keys) \
                and ("KRW" in n["title"] or "원화" in n["title"]) and "종료" not in n["title"] and "유의" not in n["title"]:
            ids.append(i)
    for i in ids:
        fn = os.path.join(HE.DET, f"{i}.json")
        if not os.path.exists(fn):
            b, c = HE.get(f"https://api-manager.upbit.com/api/v1/announcements/{i}", 1.5)
            if b and c == 200:
                open(fn, "wb").write(b)
    HE.AE.RAW, HE.AE.CUT, HE.AE.LO = HE.DET, FWD1, FWD0
    HE.perps.span = lambda: {}
    HE.perps.perp_for = perp_for
    HE.AE.perps = HE.perps
    rows, _ = HE.AE.build()
    rows = [r for r in rows if FWD0 <= r["N"] < FWD1]
    out = []
    for r in rows:
        L, why = HE.first(r["coin"], int(r["N"]))
        if L and L < r["N"]:
            continue
        if not L:
            if not r["stated"]:
                continue
            L = int(r["stated"]) + 300000
        if L + 300000 >= FWD1 + DAY:
            continue
        out.append(dict(nid=r["nid"], coin=r["coin"], perp=r["perp"], N=r["N"], L=L, N_utc=r["N_utc"],
                        day=r["N_utc"][:10], year=r["N_utc"][:4], era="FWD"))
    with open(os.path.join(FD, "events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["nid", "coin", "perp", "N", "L", "N_utc", "day", "year", "era"])
        w.writeheader(); w.writerows(out)
    return out


def pull(E):
    import pull as P
    P.TMP, P.OUT = os.path.join(FD, "tmp"), os.path.join(FD, "npz")
    jobs = {}
    for e in E:
        win = [(e["N"] - 600000, e["N"] + 1800000), (e["L"] - 600000, e["L"] + 300000)]
        for sym in (e["perp"], "BTCUSDT"):
            jobs.setdefault((sym, e["day"]), []).extend(win)
    for (sym, dayN), win in sorted(jobs.items()):
        out = os.path.join(FD, "npz", f"{sym}_{dayN}.npz")
        if os.path.exists(out):
            continue
        parts = []
        for d in sorted({str(np.datetime64(int(x), "ms"))[:10] for a, b in win for x in (a, b)}):
            zp, s = P.fetch(sym, d)
            if zp is None:
                print("MISS", sym, d, s); parts = []; break
            a = P.parse(zp)
            a[:, 2] = np.where(a[:, 2] > 1e14, np.floor(a[:, 2] / 1000), a[:, 2])
            parts.append(a)
        if not parts:
            continue
        a = np.concatenate(parts); a = a[np.argsort(a[:, 2], kind="stable")]; t = a[:, 2].astype(np.int64)
        keep = np.zeros(len(t), bool)
        for x, y in win:
            keep |= (t >= x) & (t <= y)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8))


if __name__ == "__main__":
    print("forward window", dt.datetime.fromtimestamp(FWD0 / 1000, dt.timezone.utc).date(), "..",
          dt.datetime.fromtimestamp(FWD1 / 1000, dt.timezone.utc).date(), "(exclusive)")
    E = build_events()
    pull(E)
    core.use_npz(os.path.join(FD, "npz"))
    E = [e for e in E if all(os.path.exists(os.path.join(FD, "npz", f"{s}_{e['day']}.npz")) for s in (e["perp"], "BTCUSDT"))]
    logp = os.path.join(FD, "fwd_log.csv")
    done = {(r["nid"], r["coin"]) for r in csv.DictReader(open(logp))} if os.path.exists(logp) else set()
    new = [e for e in E if (e["nid"], e["coin"]) not in done]
    if new:
        _, rows = core.grade(new, "FWD new")
        with open(logp, "a", newline="") as f:
            w = csv.writer(f)
            if not done:
                w.writerow(["nid", "coin", "perp", "N_utc", "net", "f1", "f2"])
            for x in rows:
                e = x["e"]; w.writerow([e["nid"], e["coin"], e["perp"], e["N_utc"], x["net"], x["f1"], x["f2"]])
    allr = list(csv.DictReader(open(logp))) if os.path.exists(logp) else []
    v = np.array([float(r["net"]) for r in allr])
    print(f"forward log: {len(v)} events" + (f", mean {v.mean()*1e4:+.1f} bp" if len(v) else ""))
