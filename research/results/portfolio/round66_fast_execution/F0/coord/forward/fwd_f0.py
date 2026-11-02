"""Forward runner for PREREG F0 (../../PREREG_F0_bar_close_fade.md): fade 5 % idio 1m wicks, entered at the first
aggTrade >= the event bar's close, exit at the close of bar e+61. Forward window from FWD0 = 2026-10-30 00:00 UTC.

The registered code is reused, never edited:
- F's events: coord/hold/rule.py (`trades`, imported); F's universe: coord/hold/hold_univ.py and the 1m converter
  coord/hold/hold_pull.py are scripts with side effects at import, so their hashed source is executed with only data
  folder / date literals replaced (PATCHES below; each replaced substring must occur once, and the hash is checked);
- F0's aggTrades streamer code/pull.py + code/net.py (imported; module paths net.DATA, net.LOG, pull.NPZ redirected);
  F0's entry / fill / spread helpers from code/analyze.py (first_at, vwap_at, spread_w, clt).
Plumbing written here (no rule logic): fapi exchangeInfo, 1d klines and fundingRate pulls, fapi REST fills for daily
files data.binance.vision has not published (1m klines, aggTrades; logged in fills.csv), the manifest that re-streams
an aggTrades day file when a later event needs a window it lacks, and `events_only`, a return-free mirror of the
event selection in rule.trades used only by `progress` and by the eval gate (blind counting). `check` proves it
equals rule.trades / F0's events on already-graded data.

Data: research/data/f0_forward/ (perp_1d/, exinfo/, npz/ 1m klines, aggtrades/npz/, funding/, requests*.log, fills.csv).

Usage (python -I):
  fwd_f0.py pull       fetch / update 2026-10-30 .. yesterday (idempotent)
  fwd_f0.py progress   counts only: events, event days, months, projected date to n >= 333. Never any return.
  fwd_f0.py check      event builder vs F's HOLD trades and F0's IS / VAL events (graded periods only)
  fwd_f0.py eval       the single registered evaluation; refuses unless the PREREG's date rule is met
"""
import calendar, datetime as dt, glob, hashlib, json, os, re, sys, time, types, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
F0 = os.path.abspath(os.path.join(HERE, "..", ".."))
R = os.path.abspath(os.path.join(F0, "..", "..", "..", ".."))  # research/
FC = os.path.join(R, "results", "portfolio", "round64_parallel", "F", "coord", "hold")
sys.path.insert(0, os.path.join(F0, "code"))
sys.path.insert(1, FC)
import numpy as np  # noqa: E402
import rule  # noqa: E402  F's frozen rule (hashed)
import net  # noqa: E402  F0 polite HTTP (hashed)
import pull as f0pull  # noqa: E402  F0 aggTrades streamer (hashed)
import analyze  # noqa: E402  F0 entry / fill helpers (hashed)

MIN, DAY, HOUR, BP = 60000, 86400000, 3600000, 1e4
FWD0 = 1793318400000            # 2026-10-30 00:00 UTC, forward start (registered)
FIRST_EVAL_END = 1801440000000  # 2027-02-01 00:00 UTC: first month end after 3 full calendar months (Nov, Dec, Jan)
CAP_END = 1824854400000         # 2027-10-30 00:00 UTC: hard cap 2027-10-29 inclusive (registered)
N_REG = 333
FD = os.path.join(R, "data", "f0_forward")
NPZ1M = os.path.join(FD, "npz")
AGG = os.path.join(FD, "aggtrades")
FUND = os.path.join(FD, "funding")
FILLS = os.path.join(FD, "fills.csv")
PREREG = os.path.join(F0, "PREREG_F0_bar_close_fade.md")
FAPI = "https://fapi.binance.com/fapi/v1"
REST_WAIT_DAYS = 2  # a daily file still missing on data.binance.vision this many days later is filled from fapi

# Registered hashes (PREREG "Hashes"); every hashed file must still match before eval.
HASHED = {
    "research/results/portfolio/round66_fast_execution/F0/code/ev.py": "d3fbda578aac36fe",
    "research/results/portfolio/round66_fast_execution/F0/code/pull.py": "75107157fb6ba0cd",
    "research/results/portfolio/round66_fast_execution/F0/code/analyze.py": "934ef60959f3f457",
    "research/results/portfolio/round66_fast_execution/F0/code/net.py": "40f1ecae7fd8b010",
    "research/results/portfolio/round64_parallel/F/code/events.py": "81e007b5cd04adcb",
    "research/results/portfolio/round64_parallel/F/code/report.py": "7e3b78d6ba5476c7",
    "research/results/portfolio/round64_parallel/F/coord/hold/hold_univ.py": "84ca87404734aec6",
    "research/results/portfolio/round64_parallel/F/coord/hold/rule.py": "3811202d28136b95",
}
# Executed by the runner but not in the PREREG list (1m converter / pacing only): hash pinned here and in the note.
EXTRA_HASHED = {"research/results/portfolio/round64_parallel/F/coord/hold/hold_pull.py": "f5f8c60987059ed1"}


def q(s):
    """URL form of a symbol (some USDT-M perps have non-ASCII names, e.g. 币安人生USDT)."""
    return urllib.parse.quote(s)


def today0():
    n = dt.datetime.now(dt.timezone.utc)
    return calendar.timegm((n.year, n.month, n.day, 0, 0, 0)) * 1000


def ds(ms):
    return time.strftime("%Y-%m-%d", time.gmtime(ms / 1000))


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def repo_path(rel):
    return os.path.join(os.path.dirname(R), rel)


# ---- patched execution of hashed scripts: only data folder / date literals change
def patches(end_ms):
    """(file, [(old, new)]): every pair differs only in string (folder) or integer (ms date) literals."""
    return {
        "hold_univ.py": [
            ('B = os.path.join(rule.R, "data", "binance", "perp_1d")',
             'B = os.path.join(rule.R, "data", "f0_forward", "perp_1d")'),
            ('OUT = os.path.join(rule.R, "data", "binance_1m_wicks_hold")',
             'OUT = os.path.join(rule.R, "data", "f0_forward")'),
            ('END = 1793318400000  # 2026-10-30 00:00 UTC exclusive', f'END = {int(end_ms)}  # forward data end, exclusive'),
            ('os.path.join(rule.R, "data", "binance_1m_wicks_hold", "exinfo", "exchangeInfo.json")',
             'os.path.join(rule.R, "data", "f0_forward", "exinfo", "exchangeInfo.json")'),
            ("sel = days >= 1735689600000", f"sel = days >= {FWD0}"),
        ],
        "hold_pull.py": [
            ('D = os.path.join(R, "data", "binance_1m_wicks_hold")', 'D = os.path.join(R, "data", "f0_forward")'),
            ("END_MIN = 1793318400000 // 60000", f"END_MIN = {int(end_ms)} // 60000"),
        ],
    }


def load_patched(fname, end_ms):
    path = os.path.join(FC, fname)
    rel = os.path.relpath(path, os.path.dirname(R))
    want = {**HASHED, **EXTRA_HASHED}.get(rel)
    if want and sha16(path) != want:
        raise SystemExit(f"{rel} does not match its registered hash {want}")
    src = open(path, encoding="utf-8").read()
    for old, new in patches(end_ms)[fname]:
        if src.count(old) != 1:
            raise SystemExit(f"{fname}: patch target found {src.count(old)} times: {old!r}")
        src = src.replace(old, new)
    mod = types.ModuleType(fname[:-3] + "_fwd"); mod.__file__ = path
    exec(compile(src, path, "exec"), mod.__dict__)
    return mod


def redirect_f0_modules():
    """F0's net / pull write under research/data/wick_aggtrades; point them at the forward folder (folders only)."""
    os.makedirs(os.path.join(AGG, "npz"), exist_ok=True)
    net.DATA = FD
    net.LOG = os.path.join(FD, "requests_net.log")
    f0pull.NPZ = os.path.join(AGG, "npz")
    rule.FUND_DIRS = [FUND]


# ---- REST helpers (fapi), through F0's net.open_url: >= 0.3 s apart, backs off on 418 / 429 / 503, stops on 403
def get_json(url, gap=0.0):
    if gap:
        time.sleep(gap)
    r = net.open_url(url, timeout=30)
    if r is None:
        net.log(url, "NONE", 0, "404 or gave up")
        return None
    try:
        body = r.read()
        used = r.headers.get("X-MBX-USED-WEIGHT-1M")
    finally:
        r.close()
    net.log(url, 200, len(body), f"weight1m={used}")
    if used and used.isdigit() and int(used) > 1200:  # half the 2,400 / min IP budget: wait for the next minute
        time.sleep(61 - time.time() % 60)
    return json.loads(body)


def log_fill(kind, sym, day, rows, note=""):
    new = not os.path.exists(FILLS)
    with open(FILLS, "a") as f:
        if new:
            f.write("utc,kind,sym,day,rows,note\n")
        f.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{kind},{sym},{day},{rows},{note}\n")


# ---- pull steps
def pull_exinfo():
    os.makedirs(os.path.join(FD, "exinfo"), exist_ok=True)
    j = get_json(f"{FAPI}/exchangeInfo")
    if not j:
        raise SystemExit("exchangeInfo failed")
    s = json.dumps(j)
    open(os.path.join(FD, "exinfo", "exchangeInfo.json"), "w").write(s)
    open(os.path.join(FD, "exinfo", f"exchangeInfo_{ds(today0())}.json"), "w").write(s)
    return j


def pull_perp_1d(ex, end_ms):
    """perp_1d/<SYM>.csv = research/data/binance/perp_1d rows < FWD0 + fapi 1d rows in [FWD0, end_ms) (complete days)."""
    src = os.path.join(R, "data", "binance", "perp_1d")
    raw = os.path.join(FD, "perp_1d_fwd"); out = os.path.join(FD, "perp_1d")
    os.makedirs(raw, exist_ok=True); os.makedirs(out, exist_ok=True)
    local = sorted(f[:-4] for f in os.listdir(src) if f.endswith("USDT.csv"))
    live = sorted(x["symbol"] for x in ex["symbols"]
                  if x.get("contractType") == "PERPETUAL" and x.get("quoteAsset") == "USDT" and x["symbol"].endswith("USDT")
                  and x.get("status") in ("TRADING", "SETTLING"))  # PENDING_TRADING has no klines yet (400)
    fails = []
    for s in sorted(set(local) | set(live)):
        rows = []
        if s in local:
            for ln in open(os.path.join(src, s + ".csv")).read().splitlines()[1:]:
                if ln and int(float(ln.split(",")[0])) < FWD0:
                    rows.append(ln)
        if s in live:
            fn = os.path.join(raw, s + ".csv")
            have = {}
            if os.path.exists(fn):
                for ln in open(fn).read().splitlines()[1:]:
                    have[int(ln.split(",")[0])] = ln
            done = [t for t in have if t + DAY <= end_ms]
            if not done or max(done) + DAY < end_ms:  # a complete day up to yesterday is missing: fetch
                if s in local:
                    start = max(done) + DAY if done else FWD0
                    url = f"{FAPI}/klines?symbol={q(s)}&interval=1d&startTime={start}&limit=499"
                else:  # new listing: its whole history (age check)
                    url = f"{FAPI}/klines?symbol={q(s)}&interval=1d&limit=499"
                k = get_json(url)
                if k is None:
                    fails.append(s)
                else:
                    for x in k:
                        if int(x[0]) + DAY <= end_ms and int(x[6]) < end_ms:
                            have[int(x[0])] = ",".join([str(int(x[0])), x[1], x[2], x[3], x[4], x[5], x[7], str(int(x[8]))])
                    with open(fn, "w") as f:
                        f.write("t,o,h,l,c,vol,qvol,n\n" + "".join(have[t] + "\n" for t in sorted(have)))
            rows += [have[t] for t in sorted(have) if (t >= FWD0 or s not in local) and t + DAY <= end_ms]
        with open(os.path.join(out, s + ".csv"), "w") as f:
            f.write("t,o,h,l,c,vol,qvol,n\n" + "".join(r_ + "\n" for r_ in rows))
    return fails


def build_universe(end_ms):
    """executes hold_univ.py (hashed) with only its folder / date literals changed; writes f0_forward/univ_full.npz."""
    load_patched("hold_univ.py", end_ms)
    u = np.load(os.path.join(FD, "univ_full.npz"))
    return u["U"], u["rank"], [str(x) for x in u["syms"]]


def needed_1m(U, usyms, end_ms):
    """(sym, day) daily files: BTCUSDT every day; each universe coin on its days plus the day before and after."""
    need = set()
    for d in range(FWD0, end_ms, DAY):
        need.add(("BTCUSDT", d))
        di = (d - rule.H0) // DAY
        for i in np.where(U[:, di])[0]:
            for dd in (d - DAY, d, d + DAY):
                if FWD0 <= dd < end_ms:
                    need.add((usyms[i], dd))
    return sorted(need, key=lambda x: (x[1], x[0]))


def rest_1m(s, d):
    k = get_json(f"{FAPI}/klines?symbol={q(s)}&interval=1m&startTime={d}&endTime={d + DAY - 1}&limit=1500", gap=1.0)
    if not k:
        return 0
    a = np.array([[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7]), float(x[8])] for x in k])
    m = (a[:, 0] // MIN).astype(np.int64)
    np.savez_compressed(os.path.join(NPZ1M, f"{s}_{ds(d)}.npz"), m=m.astype(np.int32), o=a[:, 1].astype(np.float32),
                        h=a[:, 2].astype(np.float32), l=a[:, 3].astype(np.float32), c=a[:, 4].astype(np.float32),
                        qv=a[:, 5].astype(np.float32), n=a[:, 6].astype(np.int32))
    return len(m)


def pull_1m(need, end_ms):
    hp = load_patched("hold_pull.py", end_ms)  # hashed converter / pacing; folders + END_MIN only
    st = {"ok": 0, "cached": 0, "404": 0, "rest": 0, "missing": 0}
    t0d = today0()
    for s, d in need:
        out = os.path.join(NPZ1M, f"{s}_{ds(d)}.npz")
        if os.path.exists(out):
            st["cached"] += 1; continue
        if os.path.exists(out + ".404") and t0d - d <= REST_WAIT_DAYS * DAY:
            os.remove(out + ".404")  # recent day: not published yet, ask data.binance.vision again
        res = hp.fetch(q(s), ds(d), True)  # hold_pull puts the symbol in the URL and the file name: quote, rename
        for suf in ("", ".404"):
            qp = os.path.join(NPZ1M, f"{q(s)}_{ds(d)}.npz{suf}")
            if q(s) != s and os.path.exists(qp):
                os.replace(qp, out + suf)
        if res == 403:
            raise SystemExit("403 from data.binance.vision: stop")
        if res in (404, "skip") and not os.path.exists(out):
            if t0d - d > REST_WAIT_DAYS * DAY:
                n = rest_1m(s, d)
                if n:
                    os.remove(out + ".404") if os.path.exists(out + ".404") else None
                    log_fill("klines_1m", s, ds(d), n, "data.binance.vision 404")
                    st["rest"] += 1; continue
                log_fill("klines_1m", s, ds(d), 0, "404 and fapi empty")
            st["404" if res == 404 else "missing"] += 1
        elif os.path.exists(out):
            st["ok"] += 1
        else:
            st["missing"] += 1
    return st


def data_end(need):
    """first day (ms) from FWD0 on which a needed 1m file is not resolved (npz, or a confirmed old 404)."""
    by_day = {}
    for s, d in need:
        by_day.setdefault(d, []).append(s)
    t0d = today0(); d = FWD0
    while d in by_day:
        for s in by_day[d]:
            p = os.path.join(NPZ1M, f"{s}_{ds(d)}.npz")
            if not (os.path.exists(p) or (os.path.exists(p + ".404") and t0d - d > REST_WAIT_DAYS * DAY and s != "BTCUSDT")):
                return d
        d += DAY
    return d


def agg_jobs(ev):
    """F0 pull.jobs_for (hashed): per (sym, day) aggTrades windows [close_e - 2 min, close_e + 65 min]."""
    E = {"syms": ev["usyms"], "sym": ev["sym"], "close_e": ev["close_e"]}
    return f0pull.jobs_for(E, list(range(len(ev["t"]))))


def _manifest():
    p = os.path.join(AGG, "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def _covered(have, wins):
    return all(any(a <= lo and hi <= b for a, b in have) for lo, hi in wins)


def rest_agg(s, wins):
    """fapi aggTrades for the windows (< 1 h per time query, fromId pages after a full page); weight 20, >= 1 s apart."""
    T, P, Q, M = [], [], [], []
    for lo, hi in sorted(wins):
        a = lo
        while a <= hi:
            b = min(a + HOUR - 1, hi)
            j = get_json(f"{FAPI}/aggTrades?symbol={q(s)}&startTime={a}&endTime={b}&limit=1000", gap=1.0)
            while j:
                for x in j:
                    if a <= int(x["T"]) <= b:
                        T.append(int(x["T"])); P.append(float(x["p"])); Q.append(float(x["q"])); M.append(bool(x["m"]))
                if len(j) < 1000 or int(j[-1]["T"]) > b:
                    break
                j = get_json(f"{FAPI}/aggTrades?symbol={q(s)}&fromId={int(j[-1]['a']) + 1}&limit=1000", gap=1.0)
            a = b + 1
    o = np.argsort(np.array(T, np.int64), kind="stable")
    return (np.array(T, np.int64)[o], np.array(P)[o], np.array(Q, np.float32)[o], np.array(M, bool)[o])


def pull_agg(ev):
    jobs, _ = agg_jobs(ev)
    man = _manifest(); st = {"cached": 0, "ok": 0, "rest": 0, "404": 0, "err": 0}
    t0d = today0()
    for (s, d0), wins in sorted(jobs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        key = f"{s}_{f0pull.day_str(d0)}"
        fn = os.path.join(AGG, "npz", key + ".npz")
        old = man.get(key, {}).get("wins", [])
        if os.path.exists(fn) and _covered(old, wins):
            st["cached"] += 1; continue
        allw = sorted({tuple(w) for w in old} | {tuple(w) for w in wins})
        if os.path.exists(fn):
            os.remove(fn)  # a later event needs a window this file lacks: stream the day again with all windows
        try:
            _, res, _ = f0pull.fetch((q(s), d0), allw)
            qp = os.path.join(AGG, "npz", f"{q(s)}_{f0pull.day_str(d0)}.npz")
            if q(s) != s and os.path.exists(qp):
                os.replace(qp, fn)
        except net.Stop403 as e:
            raise SystemExit(f"403 STOP {e}")
        except Exception as e:  # noqa: BLE001  logged, retried at the next pull
            net.log(f"aggTrades {key}", "ERR", 0, repr(e)[:120]); st["err"] += 1; continue
        if res == "ok":
            man[key] = {"wins": [list(w) for w in allw], "src": "vision"}; st["ok"] += 1
        elif res == "404" and t0d - d0 * DAY > REST_WAIT_DAYS * DAY:
            T, P, Q, M = rest_agg(s, allw)
            np.savez_compressed(fn, t=T, p=P, q=Q, m=M)
            man[key] = {"wins": [list(w) for w in allw], "src": "fapi"}
            log_fill("aggTrades", s, f0pull.day_str(d0), len(T), "data.binance.vision 404"); st["rest"] += 1
        else:
            st["404"] += 1
        json.dump(man, open(os.path.join(AGG, "manifest.json"), "w"))
    return st


def pull_funding(syms, end_ms):
    """fapi fundingRate, stamps in [FWD0, end_ms), incremental; funding/<SYM>.csv (t,rate) as rule.funding_hours reads."""
    os.makedirs(FUND, exist_ok=True); fails = []
    for s in syms:
        fn = os.path.join(FUND, s + ".csv")
        have = {}
        if os.path.exists(fn):
            for ln in open(fn).read().splitlines()[1:]:
                a, b = ln.split(","); have[int(a)] = b
        t = max(have) + 1 if have else FWD0
        while t < end_ms:
            j = get_json(f"{FAPI}/fundingRate?symbol={q(s)}&startTime={t}&endTime={end_ms - 1}&limit=1000", gap=0.3)
            if j is None:
                fails.append(s); break
            for x in j:
                if FWD0 <= int(x["fundingTime"]) < end_ms:
                    have[int(x["fundingTime"])] = x["fundingRate"]
            if len(j) < 1000:
                break
            t = int(j[-1]["fundingTime"]) + 1
        with open(fn, "w") as f:
            f.write("t,rate\n" + "".join(f"{a},{have[a]}\n" for a in sorted(have)))
    return fails


# ---- events (no returns)
def events_only(D, U, RK, usyms, T0, END, syms_to_scan, cut_end):
    """Event set of rule.trades (same selection, guard, de-duplication and exit-availability drop) without computing
    any price ratio of the trade. `check` and tests/test_f0_forward.py prove equality with rule.trades."""
    NM = (END - T0) // MIN
    day_of_t = (T0 + np.arange(NM, dtype=np.int64) * MIN - rule.H0) // DAY
    rb = rule.ret1(rule.load_sym(D, "BTCUSDT", T0, NM)[0])
    S, Tt, Rr, Rk = [], [], [], []
    for s in syms_to_scan:
        if s == "BTCUSDT":
            continue
        i = usyms.index(s)
        c, o, h, l, n, qv = rule.load_sym(D, s, T0, NM)
        if np.isnan(c).all():
            continue
        r = rule.ret1(c)
        idx = np.where(~np.isnan(c), np.arange(NM), -1); np.maximum.accumulate(idx, out=idx); last = idx
        dd = np.clip(day_of_t, 0, U.shape[1] - 1)
        inU = U[i, dd]; rank = RK[i, dd]
        with np.errstate(invalid="ignore"):
            a = np.abs(r)
            m = (a >= 0.05) & inU & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)
        e = np.where(m)[0]
        e = e[(e >= 1) & (e + 2 + 60 < NM)]
        e = e[T0 + e * MIN < cut_end]
        rr = r[e]; nxt = o[e + 1]; half = c[e - 1] * (1 + rr / 2)
        g = (n[e] >= 10) & (qv[e] > 0) & ~np.isnan(nxt) & np.where(rr < 0, nxt <= half, nxt >= half)
        e = e[g]
        keep = []; lt = -10 ** 9
        for x in e:
            if x - lt > 60:
                keep.append(x); lt = x
        e = np.array(keep, dtype=np.int64)
        if len(e) == 0:
            continue
        pe = c[e + 1]; x = rule.px_at(c, last, e + 61)
        with np.errstate(invalid="ignore"):
            ok = np.isfinite(x) & np.isfinite(pe) & (pe != 0)  # rule.trades drops non-finite x / pe: data present
        e = e[ok]
        S.append(np.full(len(e), i)); Tt.append(e); Rr.append(r[e]); Rk.append(rank[e])
    cat = lambda v, dt_: np.concatenate(v) if v else np.zeros(0, dt_)  # noqa: E731
    sym, t, sig, rk = cat(S, np.int64), cat(Tt, np.int64), cat(Rr, float), cat(Rk, np.int64)
    o = np.lexsort((sym, t))
    return dict(sym=sym[o], t=t[o], r=sig[o], rank=rk[o])


def forward_events(end_ms):
    u = np.load(os.path.join(FD, "univ_full.npz"))
    U, RK, usyms = u["U"], u["rank"], [str(x) for x in u["syms"]]
    have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(NPZ1M, "*.npz"))})
    have = [s for s in have if s in usyms]
    ev = events_only(NPZ1M, U, RK, usyms, FWD0, end_ms, have, end_ms)
    ev["usyms"] = usyms
    ev["close_e"] = FWD0 + (ev["t"] + 1) * MIN
    ev["day"] = (FWD0 + ev["t"] * MIN) // DAY
    return ev, (U, RK, usyms, have)


def state():
    p = os.path.join(FD, "state.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def cmd_pull():
    os.makedirs(NPZ1M, exist_ok=True)
    redirect_f0_modules()
    end = today0()  # daily files exist up to yesterday
    if end <= FWD0:
        raise SystemExit("forward window has not started")
    print(f"pull {ds(FWD0)} .. {ds(end - DAY)}", flush=True)
    ex = pull_exinfo()
    f1 = pull_perp_1d(ex, end)
    print(f"1d klines: {len(f1)} symbols failed {f1[:10]}", flush=True)
    U, RK, usyms = build_universe(end)
    need = needed_1m(U, usyms, end)
    st1 = pull_1m(need, end)
    dend = data_end(need)
    print(f"1m files needed {len(need)}: {st1}; complete through {ds(dend - DAY)}", flush=True)
    ev, _ = forward_events(dend)
    sta = pull_agg(ev)
    print(f"aggTrades day files: {sta}", flush=True)
    fsyms = sorted({usyms[i] for d in range(FWD0, end, DAY) for i in np.where(U[:, (d - rule.H0) // DAY])[0]})
    ff = pull_funding(fsyms, end)
    print(f"funding: {len(fsyms)} universe symbols, failed {ff}", flush=True)
    json.dump({"pulled_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "end": end, "data_end": dend,
               "need_1m": len(need), "st_1m": st1, "st_agg": sta, "fail_1d": f1, "fail_funding": ff},
              open(os.path.join(FD, "state.json"), "w"), indent=1)


# ---- progress (counts only) and the evaluation date rule
def month_starts(a, b):
    """UTC month starts m with a < m <= b."""
    y, mo = time.gmtime(a / 1000)[:2]; out = []
    while True:
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
        m = calendar.timegm((y, mo, 1, 0, 0, 0)) * 1000
        if m > b:
            return out
        out.append(m)


def full_months(end_ms):
    """complete calendar months inside [FWD0, end_ms)."""
    ms = month_starts(FWD0, end_ms)
    return max(len(ms) - 1, 0) if ms else 0


def eval_gate(today_ms, dend, n_at):
    """Registered date rule. Returns (window_end, why) or (None, why). n_at(end) counts events in [FWD0, end)."""
    for m in month_starts(FWD0, CAP_END):
        if full_months(m) < 3:
            continue
        if today_ms < m or dend < m:
            return None, f"next month end to test is {ds(m - DAY)}; data complete through {ds(dend - DAY)}"
        n = n_at(m)
        if n >= N_REG:
            return m, f"first month end with n >= {N_REG} and >= 3 full months: {ds(m - DAY)} (n {n})"
    if today_ms >= CAP_END and dend >= CAP_END:
        return CAP_END, f"hard cap {ds(CAP_END - DAY)} reached (n {n_at(CAP_END)})"
    return None, f"no month end up to the cap qualifies yet; cap {ds(CAP_END - DAY)}"


def progress_lines(t, day, dend, n_agg=None):
    """counts only, never a return (blind until the single evaluation)."""
    n = len(t); days = len(np.unique(day)); span = max((dend - FWD0) / DAY, 1e-9)
    ms = sorted({ds(FWD0 + DAY * k)[:7] for k in range(int(round(span)))})
    L = [f"forward window {ds(FWD0)} .. {ds(dend - DAY)} ({span:.0f} data days)",
         f"events so far: {n}" + ("" if n_agg is None else f" (aggTrades windows on disk for {n_agg})"),
         f"day-clustered days with an event: {days}",
         f"calendar months touched: {', '.join(ms)}; full calendar months: {full_months(dend)} (need 3)"]
    if n:
        pace = n / span
        reach = FWD0 + int(np.ceil(N_REG / pace)) * DAY
        lo = max(reach, FIRST_EVAL_END)
        first = next(m for m in month_starts(FWD0, lo + 40 * DAY) if m >= lo)
        L.append(f"pace {pace * 30.44:.1f} events / month -> n >= {N_REG} projected {ds(reach)}; "
                 f"projected evaluation at month end {ds(first - DAY)}" + (" (after the cap)" if first > CAP_END else ""))
    else:
        L.append(f"pace: no event yet; n >= {N_REG} cannot be projected")
    L.append(f"registered date rule: evaluate once at the first month end with n >= {N_REG} and >= 3 full calendar "
             f"months (earliest {ds(FIRST_EVAL_END - DAY)}); hard cap {ds(CAP_END - DAY)}, then whatever n")
    return L


def cmd_progress():
    st = state()
    if not st:
        raise SystemExit("no state.json: run pull first")
    dend = int(st["data_end"])
    ev, _ = forward_events(dend)
    man = _manifest(); _, ej = agg_jobs(ev)
    n_agg = sum(all(f"{s}_{f0pull.day_str(d0)}" in man for s, d0 in ej[j]) for j in range(len(ev["t"])))
    print("\n".join(progress_lines(ev["t"], ev["day"], dend, n_agg)))
    if st.get("fail_1d") or st.get("fail_funding") or st["st_1m"].get("missing") or st["st_agg"].get("err"):
        print(f"data warnings: 1d fails {len(st.get('fail_1d', []))}, funding fails {len(st.get('fail_funding', []))}, "
              f"1m {st['st_1m']}, aggTrades {st['st_agg']}")


# ---- check (graded periods only)
def cmd_check(full_val=False):
    out = []
    # 1) HOLD: events_only on F's HOLD data == the registered HOLD run's trades (hold_trades.npz, rule.trades)
    D = os.path.join(R, "data", "binance_1m_wicks_hold")
    u = np.load(os.path.join(D, "univ_full.npz")); U, RK, usyms = u["U"], u["rank"], [str(x) for x in u["syms"]]
    T0, END = 1735689600000, 1793318400000
    have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(D, "npz", "*.npz"))})
    have = [s for s in have if s in usyms]
    t1 = time.time()
    e = events_only(os.path.join(D, "npz"), U, RK, usyms, T0, END, have, END)
    h = np.load(os.path.join(FC, "hold_trades.npz"))
    a = set(zip(e["sym"].tolist(), e["t"].tolist())); b = set(zip(h["sym"].astype(int).tolist(), h["t"].astype(int).tolist()))
    out.append(f"HOLD 2025-01-01..2026-10-29: events_only {len(a)} vs registered HOLD run {len(b)}; "
               f"identical (sym, minute): {a == b} ({time.time() - t1:.0f} s)")
    ok = a == b
    # 2) forward universe plumbing: f0_forward/univ_full.npz equals the HOLD universe on every HOLD day
    fu = os.path.join(FD, "univ_full.npz")
    if os.path.exists(fu):
        v = np.load(fu); vs = [str(x) for x in v["syms"]]
        d0, d1 = (T0 - rule.H0) // DAY, (END - rule.H0) // DAY
        bad = sum({usyms[i] for i in np.where(U[:, d])[0]} != {vs[i] for i in np.where(v["U"][:, d])[0]} for d in range(d0, d1))
        out.append(f"forward universe vs HOLD universe on {d1 - d0} HOLD days: {bad} days differ")
        ok &= bad == 0
    # 3) F0's own event set (IS / VAL, cand.npz via ev.py) vs events_only on stream F's 1m data, VAL 2024 (or all)
    import ev as f0ev
    E = f0ev.events(); z = E["z"]; idx = E["idx"]
    idx = idx[np.isfinite(z["go"][idx, 2])]  # analyze.py keeps events with an H60 exit
    Dv = os.path.join(R, "data", "binance_1m_wicks")
    uv = np.load(os.path.join(Dv, "univ.npz")); Uv, RKv, usv = uv["U"], uv["rank"], [str(x) for x in uv["syms"]]
    T0v = f0ev.T0 if full_val else 1704067200000  # 2024-01-01 (VAL year 3) unless --full
    ENDv = f0ev.END
    hv = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(Dv, "npz", "*.npz"))})
    hv = [s for s in hv if s in usv]
    t1 = time.time()
    ev2 = events_only(os.path.join(Dv, "npz"), Uv, RKv, usv, T0v, ENDv, hv, ENDv)
    a = {(usv[s], T0v + t * MIN) for s, t in zip(ev2["sym"].tolist(), ev2["t"].tolist())}
    tt = f0ev.T0 + E["t"][idx] * MIN
    b = {(E["syms"][s], int(x)) for s, x in zip(E["sym"][idx], tt) if x >= T0v + 62 * MIN}
    a = {x for x in a if x[1] >= T0v + 62 * MIN}  # first hour after a slice start: dedup history differs
    out.append(f"F0 events {ds(T0v)}..{ds(ENDv - DAY)}: events_only {len(a)} vs F0 ev.events {len(b)}; "
               f"identical: {a == b}; only here {len(a - b)}, only F0 {len(b - a)} ({time.time() - t1:.0f} s)")
    ok &= a == b
    # 4) entry plumbing: first aggTrade >= close_e from F0's aggTrades files == F0's sample_rows pa0 / pa1
    sr = np.load(os.path.join(F0, "out", "sample_rows.npz"))
    prog = json.load(open(os.path.join(R, "data", "wick_aggtrades", "progress.json")))
    rng = np.random.default_rng(1); pick = rng.choice(len(sr["j"]), size=min(60, len(sr["j"])), replace=False)
    bad = 0
    for k in pick:
        j = int(sr["j"][k])
        Tm, P, Q, M = load_trades(os.path.join(R, "data", "wick_aggtrades", "npz"), prog["ev_files"][str(j)])
        ce = int(E["close_e"][j])
        p0, _ = analyze.first_at(Tm, P, ce); p1, _ = analyze.first_at(Tm, P, ce + 1000)
        bad += not (p0 == sr["pa0"][k] and p1 == sr["pa1"][k])
    out.append(f"entry prices (first aggTrade >= close_e, +1 s) on {len(pick)} F0 sample events: {bad} differ")
    ok &= bad == 0
    print("\n".join(out)); print("CHECK", "OK" if ok else "FAILED")
    return ok


def load_trades(npz_dir, files):
    parts = []
    for fn in files:
        p = os.path.join(npz_dir, fn + ".npz")
        if os.path.exists(p):
            a = np.load(p); parts.append((a["t"], a["p"], a["q"].astype(float), a["m"]))
    if not parts:
        return (np.zeros(0, np.int64),) + (np.zeros(0),) * 2 + (np.zeros(0, bool),)
    T = np.concatenate([x[0] for x in parts]); P = np.concatenate([x[1] for x in parts])
    Q = np.concatenate([x[2] for x in parts]); M = np.concatenate([x[3] for x in parts])
    o = np.argsort(T, kind="stable")
    return T[o], P[o], Q[o], M[o]


# ---- the single registered evaluation
def registered_hashes_ok():
    bad = [f"{p} {sha16(repo_path(p))} != {h}" for p, h in {**HASHED, **EXTRA_HASHED}.items() if sha16(repo_path(p)) != h]
    me = sha16(os.path.abspath(__file__))
    txt = open(PREREG, encoding="utf-8").read()
    if me not in txt:
        bad.append(f"this runner's hash {me} is not in the PREREG")
    return bad


def result_section_empty():
    txt = open(PREREG, encoding="utf-8").read()
    m = re.search(r"\n## Forward result\n(.*)\Z", txt, re.S)
    return m is not None and m.group(1).strip() in ("", "(appended at the evaluation date)")


def cmd_eval():
    bad = registered_hashes_ok()
    if bad:
        raise SystemExit("refused: code differs from the registration:\n  " + "\n  ".join(bad))
    if not result_section_empty():
        raise SystemExit("refused: the PREREG 'Forward result' section is not empty (evaluation runs once)")
    st = state()
    if not st:
        raise SystemExit("refused: no forward data (run pull)")
    dend = int(st["data_end"]); now = today0()
    cache = {}

    def n_at(m):
        if m not in cache:
            cache[m] = len(forward_events(m)[0]["t"])
        return cache[m]

    W, why = eval_gate(now, dend, n_at)
    if W is None:
        raise SystemExit(f"refused: {why}")
    redirect_f0_modules()
    ev, (U, RK, usyms, have) = forward_events(W)
    T = rule.trades(NPZ1M, U, RK, usyms, FWD0, W, have, W)  # registered rule, hashed code
    o = np.lexsort((T["sym"], T["t"]))
    T = {k: v[o] for k, v in T.items()}
    if not (np.array_equal(T["sym"].astype(np.int64), ev["sym"]) and np.array_equal(T["t"].astype(np.int64), ev["t"])):
        raise SystemExit("refused: rule.trades and events_only disagree on the forward events")
    missing_f = sorted({usyms[i] for i in set(T["sym"].astype(int).tolist())} - {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(FUND, "*.csv"))})
    if missing_f:
        raise SystemExit(f"refused: funding missing for {missing_f} (run pull)")
    lines = evaluate(T, ev, usyms, W, why)
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(HERE, f"fwd_eval_output_{ds(today0())}.txt"), "w").write(txt + "\n")
    p = open(PREREG, encoding="utf-8").read()
    p = re.sub(r"\n## Forward result\n.*\Z", "\n## Forward result\n" + txt.replace("\\", "\\\\") + "\n", p, flags=re.S)
    open(PREREG, "w", encoding="utf-8").write(p)


def evaluate(T, ev, usyms, W, why):
    """E0a H60 (first aggTrade >= close_e, exit kline close of e+61) and the registered bars, run once."""
    n = len(T["t"]); side = -np.sign(T["r"]); cost = T["cost"]
    ce = FWD0 + (T["t"].astype(np.int64) + 1) * MIN; day = (FWD0 + T["t"].astype(np.int64) * MIN) // DAY
    _, ej = agg_jobs(ev)
    x = np.full(n, np.nan); f = np.zeros(n)
    pa0, pa1, pv0, xv, sp1 = (np.full(n, np.nan) for _ in range(5))
    NM = (W - FWD0) // MIN
    for s in np.unique(T["sym"].astype(int)):
        q = np.where(T["sym"].astype(int) == s)[0]
        c = rule.load_sym(NPZ1M, usyms[s], FWD0, NM)[0]
        idx = np.where(~np.isnan(c), np.arange(NM), -1); np.maximum.accumulate(idx, out=idx)
        x[q] = rule.px_at(c, idx, T["t"][q].astype(np.int64) + 61)
        f[q] = side[q] * rule.fund(rule.funding_hours(usyms[s]), ce[q].astype(float), ce[q] + 61.0 * MIN)
    for k in range(n):
        Tm, P, Q, M = load_trades(os.path.join(AGG, "npz"), [f"{s}_{f0pull.day_str(d0)}" for s, d0 in ej[k]])
        c0 = int(ce[k])
        if not len(Tm) or Tm[-1] < c0 + 62 * MIN:
            continue
        mine = M == (side[k] < 0)
        pa0[k], _ = analyze.first_at(Tm, P, c0); pa1[k], _ = analyze.first_at(Tm, P, c0 + 1000)
        pv0[k] = analyze.vwap_at(Tm, P, Q, c0, mine); xv[k] = analyze.vwap_at(Tm, P, Q, c0 + 61 * MIN, ~mine)
        sp1[k] = analyze.spread_w(Tm, P, Q, M, c0, c0 + 1000)
    use = np.isfinite(pa0) & np.isfinite(x)
    net0 = side * (x / pa0 - 1) - f - cost
    net1 = side * (x / pa1 - 1) - f - cost
    real = side * (xv / pv0 - 1) - f - 10 / BP
    j = np.where(use)[0]
    m, t, sd, nn = analyze.clt(net0[j], day[j])
    m15, t15, _, _ = analyze.clt(net0[j] - 0.5 * cost[j], day[j])
    j1 = j[np.isfinite(net1[j])]; m1, t1, _, n1 = analyze.clt(net1[j1], day[j1])
    jr = j[np.isfinite(real[j])]; mr, tr, _, nr = analyze.clt(real[jr], day[jr])
    jo = j[np.argsort(ce[j], kind="stable")]; hlf = len(jo) // 2
    mh1 = analyze.clt(net0[jo[:hlf]], day[jo[:hlf]])[0]; mh2 = analyze.clt(net0[jo[hlf:]], day[jo[hlf:]])[0]
    g1 = m > 0 and t >= 2.0
    g2 = m15 > 0 and m1 > 0 and mr > 0
    g3 = mh1 > 0 and mh2 > 0
    cr = T["r"][j] < 0
    cs = {}
    for k in j:
        cs[usyms[int(T["sym"][k])]] = cs.get(usyms[int(T["sym"][k])], 0) + net0[k]
    dsum = {}
    for k in j:
        dsum[int(day[k])] = dsum.get(int(day[k]), 0) + net0[k]
    tot = net0[j].sum()
    L = [f"Forward evaluation run {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC by fwd_f0.py eval "
         f"(sha {sha16(os.path.abspath(__file__))}); window {ds(FWD0)} .. {ds(W - DAY)}; {why}",
         f"- events {n}; with aggTrades for the entry {len(j)} (excluded {n - len(j)}); days {len(np.unique(day[j]))}; "
         f"n vs registered {N_REG}: {len(j)}",
         f"- E0a H60 net {m * BP:+.1f} bp, day-clustered t {t:.2f}, median {np.median(net0[j]) * BP:+.1f}, "
         f"S {m / sd:.3f}",
         f"- x1.5 costs {m15 * BP:+.1f} (t {t15:.2f}); 1 s late (E1) {m1 * BP:+.1f} (t {t1:.2f}, n {n1}); "
         f"$10k taker VWAP both legs {mr * BP:+.1f} (t {tr:.2f}, n {nr})",
         f"- halves by event count: {mh1 * BP:+.1f} / {mh2 * BP:+.1f}",
         f"- crash n {cr.sum()} {np.mean(net0[j][cr]) * BP if cr.any() else float('nan'):+.1f} / spike n {(~cr).sum()} "
         f"{np.mean(net0[j][~cr]) * BP if (~cr).any() else float('nan'):+.1f}",
         f"- top-5 coins share of net {sum(sorted(cs.values())[-5:]) / tot:.3f}; top-5 days {sum(sorted(dsum.values())[-5:]) / tot:.3f}",
         f"- first-second half-spread median {np.nanmedian(sp1[j]) / 2 * BP:.1f} bp vs model 3h median "
         f"{np.median(3 * (cost[j] - 10 / BP) / 4) * BP:.1f} bp",
         f"- bar 1 (net > 0, t >= 2.0): {g1}; bar 2 (x1.5, E1, $10k fills > 0): {g2}; bar 3 (both halves > 0): {g3}",
         f"- **{'PASS: LIVE candidate (user decides on a bot)' if (g1 and g2 and g3) else 'FAIL: dropped'}**"]
    return L


def main(argv):
    if not argv or argv[0] not in ("pull", "progress", "check", "eval"):
        raise SystemExit(__doc__)
    if argv[0] == "pull":
        cmd_pull()
    elif argv[0] == "progress":
        cmd_progress()
    elif argv[0] == "check":
        sys.exit(0 if cmd_check("--full" in argv) else 1)
    else:
        cmd_eval()


if __name__ == "__main__":
    main(sys.argv[1:])
