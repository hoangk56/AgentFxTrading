"""G0 pull (../HYPOTHESES_G0.md): stream data.binance.vision daily futures/um aggTrades for BTCUSDT and the
point-in-time rank 10..39 alts on sampled BTC shock days, detect real-time triggers (BTC trailing-60 s move >= 1 %),
keep only the shock windows (trades) and random-time fill snapshots, write research/data/shock_aggtrades/days/<d>.npz.

Run with `python -I pull.py <worker> <n_workers> <deadline_unix>`. Nothing dated after 2024-12-31 is requested.
Zips are never written to disk: each is inflated as a stream and the connection is closed once past the needed time.
"""
import glob, io, os, socket, sys, time, urllib.error, urllib.request, zlib
from collections import deque
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, *[".."] * 5))
D1M = os.path.join(R, "data", "binance_1m_wicks")
OUT = os.path.join(R, "data", "shock_aggtrades")
DAYS = os.path.join(OUT, "days")
LOG = os.path.join(OUT, "requests.log")
STOP = os.path.join(OUT, "STOP")
UA = {"User-Agent": "research-aggtrades/1.0"}
BASE = "https://data.binance.vision/data/futures/um/daily/aggTrades"
END = 1735689600000            # 2025-01-01 00:00 UTC, exclusive
VAL0 = 1640995200000
DAYMS = 86400000
X = 0.01
NREP = 200
WIN_PRE, WIN_POST = 150000, 10000 + 900000 + 60000   # trades kept around tau
OFFS = np.array([1, 3, 10] + [L + H for L in (1, 3, 10) for H in (60, 300, 900)]) * 1000
SEED = 66070
NMAX = 60
_last_req = [0.0]


def log(url, status, nbytes, note=""):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{status}\t{nbytes}\t{note}\n")


class NotFound(Exception):
    pass


class Stream:
    """Inflate a zip (single member) on the fly; read_until(T) parses trades until one is past T."""

    def __init__(self, url):
        self.url = url
        wait = 0.25 - (time.time() - _last_req[0])
        if wait > 0:
            time.sleep(wait)
        _last_req[0] = time.time()
        backoff = [60, 300]
        while True:
            if os.path.exists(STOP):
                raise SystemExit("STOP file")
            try:
                self.r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20)
                break
            except urllib.error.HTTPError as e:
                log(url, e.code, 0)
                if e.code == 404:
                    raise NotFound(url)
                if e.code == 403:
                    open(STOP, "w").write("403 " + url)
                    raise SystemExit("403")
                if e.code in (418, 429, 503) and backoff:
                    time.sleep(backoff.pop(0)); continue
                raise
        self.nbytes = 0; self.hdr = b""; self.dec = None; self.tail = b""; self.done = False
        self.parts = []; self.last_t = -1; self.first = True; self.t_open = time.time()

    def _parse(self, txt):
        if self.first:
            self.first = False
            if not txt[:1].isdigit():
                txt = txt[txt.index(b"\n") + 1:] if b"\n" in txt else b""
        if not txt:
            return
        a = np.loadtxt(io.BytesIO(txt), delimiter=",", usecols=(1, 2, 5, 6), ndmin=1,
                       dtype=[("p", "f8"), ("q", "f4"), ("t", "i8"), ("m", "S5")])
        if len(a):
            m = np.isin(a["m"], [b"true", b"True", b"TRUE"])
            self.parts.append((a["t"].copy(), a["p"].copy(), a["q"].copy(), m))
            self.last_t = int(a["t"][-1])

    def _feed(self, chunk):
        if self.dec is None:
            self.hdr += chunk
            if len(self.hdr) < 30:
                return
            assert self.hdr[:4] == b"PK\x03\x04"
            nl = int.from_bytes(self.hdr[26:28], "little"); el = int.from_bytes(self.hdr[28:30], "little")
            if len(self.hdr) < 30 + nl + el:
                return
            assert int.from_bytes(self.hdr[8:10], "little") == 8
            self.dec = zlib.decompressobj(-15)
            chunk = self.hdr[30 + nl + el:]
        out = self.tail + self.dec.decompress(chunk)
        if self.dec.eof:
            self.done = True
        k = out.rfind(b"\n")
        if k < 0:
            self.tail = out; return
        self.tail = out[k + 1:]
        self._parse(out[:k + 1])

    def read_until(self, T):
        while not self.done and self.last_t <= T:
            if time.time() - self.t_open > 300:          # trickling connection: socket timeout never fires
                raise TimeoutError("wall 300 s")
            chunk = self.r.read1(1 << 20)
            if not chunk:
                self.done = True
                break
            self.nbytes += len(chunk)
            self._feed(chunk)
        if self.done and self.tail.strip():
            self._parse(self.tail + b"\n"); self.tail = b""

    def close(self, status=200):
        try:
            self.r.close()
        except Exception:
            pass
        log(self.url, status, self.nbytes, "full" if self.done else "partial")

    def arrays(self):
        if not self.parts:
            z = np.zeros(0)
            return z.astype(np.int64), z, z.astype(np.float32), z.astype(bool)
        t, p, q, m = (np.concatenate(x) for x in zip(*self.parts))
        self.parts = [(t, p, q, m)]
        return t, p, q, m


class Fetcher:
    """Trades of one symbol from the start of day_ms, read incrementally (spills into the next day file if needed,
    never into 2025)."""

    def __init__(self, sym, day_ms):
        self.sym = sym; self.d = day_ms; self.s = None; self.res = []; self.missing = False

    def _open(self):
        ds = time.strftime("%Y-%m-%d", time.gmtime(self.d / 1000))
        url = f"{BASE}/{self.sym}/{self.sym}-aggTrades-{ds}.zip"
        for attempt in range(3):
            try:
                self.s = Stream(url); return True
            except NotFound:
                return False
            except (socket.timeout, TimeoutError, ConnectionError, OSError) as e:
                log(url, f"ERR {type(e).__name__}", 0); time.sleep(5)
        return False

    def until(self, T):
        while True:
            if self.s is None:
                if self.d >= END or self.missing:
                    return
                if not self._open():
                    self.missing = True; return
            try:
                self.s.read_until(T)
            except (socket.timeout, TimeoutError, ConnectionError, OSError, zlib.error) as e:
                self.s.close(f"ERR {type(e).__name__}")
                self.s = None; self.missing = True      # drop this coin-day rather than re-download
                return
            if not self.s.done:
                return
            self.s.close(); self.res.append(self.s.arrays()); self.s = None; self.d += DAYMS
            if self.d > T:
                return

    def finish(self):
        if self.s is not None:
            self.s.close(); self.res.append(self.s.arrays()); self.s = None

    def arrays(self):
        parts = list(self.res) + ([self.s.arrays()] if self.s is not None else [])
        if not parts:
            return None
        t, p, q, m = (np.concatenate(x) for x in zip(*parts))
        o = np.argsort(t, kind="stable")
        return t[o], p[o], q[o], m[o]


def detect(t, p, ranges):
    """Real-time triggers: first trade whose price is >= X beyond the trailing-60 s extreme; 60-min de-dup."""
    out = []; next_ok = -1
    for a, b in ranges:
        i0, i1 = np.searchsorted(t, a), np.searchsorted(t, b)
        dmin, dmax = deque(), deque()
        tt = t[i0:i1].tolist(); pp = p[i0:i1].tolist()
        for i in range(len(tt)):
            ti, pi = tt[i], pp[i]
            while dmin and pp[dmin[-1]] >= pi: dmin.pop()
            dmin.append(i)
            while dmax and pp[dmax[-1]] <= pi: dmax.pop()
            dmax.append(i)
            while tt[dmin[0]] < ti - 60000: dmin.popleft()
            while tt[dmax[0]] < ti - 60000: dmax.popleft()
            if ti < next_ok:
                continue
            lo, hi = pp[dmin[0]], pp[dmax[0]]
            if pi / lo - 1 >= X:
                out.append((ti, tt[dmin[0]], pi / lo - 1, 1, pi, lo)); next_ok = ti + 3600000
            elif pi / hi - 1 <= -X:
                out.append((ti, tt[dmax[0]], pi / hi - 1, -1, pi, hi)); next_ok = ti + 3600000
    return out


def first_side(t, p, m, targets, buyer_aggr):
    """price and delay (ms) of the first print at time >= target on one aggressor side."""
    sel = (~m) if buyer_aggr else m
    ts, ps = t[sel], p[sel]
    if len(ts) == 0:
        return np.full(targets.shape, np.nan, np.float32), np.full(targets.shape, -1, np.int32)
    j = np.searchsorted(ts, targets)
    ok = j < len(ts)
    jj = np.minimum(j, len(ts) - 1)
    pr = np.where(ok, ps[jj], np.nan).astype(np.float32)
    dl = np.where(ok, np.minimum(ts[jj] - targets, 2 ** 31 - 1), -1).astype(np.int32)
    return pr, dl


def load_btc_1m():
    ms, hs, ls = [], [], []
    for f in sorted(glob.glob(os.path.join(D1M, "npz", "BTCUSDT_*.npz"))):
        z = np.load(f); m = z["m"].astype(np.int64); k = m < END // 60000
        ms.append(m[k]); hs.append(z["h"][k].astype(float)); ls.append(z["l"][k].astype(float))
    m = np.concatenate(ms); h = np.concatenate(hs); l = np.concatenate(ls)
    o = np.argsort(m); return m[o], h[o], l[o]


def day_plan():
    m, h, l = load_btc_1m()
    cont = np.r_[False, np.diff(m) == 1]
    hh = np.maximum(h, np.r_[h[:1], h[:-1]]); ll = np.minimum(l, np.r_[l[:1], l[:-1]])
    r2 = np.where(cont, hh / ll - 1, h / l - 1)
    cand = m[r2 >= X * 0.99]                       # bar pair (cand-1, cand)
    sure = np.unique(m[h / l - 1 >= X] // 1440)
    rng = np.random.default_rng(SEED)
    isd = sure[sure * DAYMS < VAL0]; vad = sure[sure * DAYMS >= VAL0]
    isd = rng.permutation(isd)[:NMAX]; vad = rng.permutation(vad)[:NMAX]
    order = [x for pair in zip(isd, vad) for x in pair]
    return order, cand


def main():
    wid, nw, deadline = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    os.makedirs(DAYS, exist_ok=True)
    order, cand = day_plan()
    u = np.load(os.path.join(D1M, "univ.npz")); U, RK, usyms, day0 = u["U"], u["rank"], list(u["syms"]), int(u["day0"])
    have = {os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(D1M, "npz", "*.npz"))}
    rng = np.random.default_rng(SEED + 1 + wid)
    for j, dd in enumerate(order):
        if j % nw != wid:
            continue
        if time.time() > deadline or os.path.exists(STOP):
            print("deadline / stop", flush=True); break
        ds = str(np.datetime64(int(dd), "D"))
        fn = os.path.join(DAYS, ds + ".npz")
        if os.path.exists(fn):
            continue
        d_ms = int(dd) * DAYMS
        cm = cand[(cand >= dd * 1440) & (cand < (dd + 1) * 1440)]
        ranges = []
        for c in cm:
            a, b = (c - 1) * 60000, (c + 1) * 60000
            if ranges and a <= ranges[-1][1]:
                ranges[-1][1] = b
            else:
                ranges.append([a, b])
        t0 = time.time()
        # BTC up to the last candidate range end + window; then detection
        FB = Fetcher("BTCUSDT", d_ms)
        FB.until(min(ranges[-1][1] + WIN_POST, d_ms + DAYMS - 1))
        B = FB.arrays()
        if B is None or FB.missing and not len(B[0]):
            FB.finish(); print(ds, "no BTC file", flush=True); continue
        tB, pB = B[0], B[1]
        trig = [x for x in detect(tB, pB, ranges) if x[0] < d_ms + DAYMS]
        if not trig:
            FB.finish(); np.savez(fn, n_shock=0); print(ds, "no trigger", flush=True); continue
        tau = np.array([x[0] for x in trig], np.int64)
        stop = max(tau[-1] + WIN_POST, tau[0] + 3 * 3600000)
        stop_day = min(stop, d_ms + DAYMS - 1)
        stop_all = min(max(tau[-1] + WIN_POST, stop_day), END - 1)
        FB.until(stop_all); FB.finish()
        tB, pB, qB, mB = FB.arrays(); del B
        # random times: same day, inside the streamed range, >= 60 min from any trigger
        lo, hi = d_ms + 120000, stop_day - 980000
        grid = np.arange(lo, max(hi, lo), 1000, dtype=np.int64)
        if len(grid):
            grid = grid[np.all(np.abs(grid[:, None] - tau[None, :]) >= 3600000, axis=1)]
        ns = len(tau)
        rnd_t = (grid[rng.integers(0, len(grid), size=(ns, NREP))] + rng.integers(0, 1000, size=(ns, NREP))
                 if len(grid) else np.zeros((ns, NREP), np.int64))
        # coins: BTC + point-in-time rank 10..39 alts; each coin is processed then freed
        k = (d_ms - day0) // DAYMS
        nU = int(U[:, k].sum())
        rmin = 10 if nU >= 30 else 2          # small early-2020 universes: all alts except ETH (amendment 13:27 UTC)
        alts = [usyms[i] for i in np.where(U[:, k] & (RK[:, k] >= rmin) & (RK[:, k] <= 39))[0]
                if usyms[i] != "BTCUSDT" and usyms[i] in have]
        coins, ranks = [], []
        tc, tk, tt, tp, tq, tm = [], [], [], [], [], []
        RP = np.full((ns, NREP, len(alts) + 1, len(OFFS), 2), np.nan, np.float32)
        RD = np.full((ns, NREP, len(alts) + 1, len(OFFS), 2), -1, np.int32)
        for s in ["BTCUSDT"] + alts:
            if s == "BTCUSDT":
                t, p, q, m = tB, pB, qB, mB
            else:
                F = Fetcher(s, d_ms); F.until(stop_all); F.finish(); A = F.arrays()
                if A is None or len(A[0]) == 0:
                    continue
                t, p, q, m = A
            ci = len(coins)
            coins.append(s); ranks.append(0 if s == "BTCUSDT" else int(RK[usyms.index(s), k]))
            for kk in range(ns):
                a_, b_ = np.searchsorted(t, tau[kk] - WIN_PRE), np.searchsorted(t, tau[kk] + WIN_POST, "right")
                tc.append(np.full(b_ - a_, ci, np.int16)); tk.append(np.full(b_ - a_, kk, np.int16))
                tt.append(t[a_:b_]); tp.append(p[a_:b_]); tq.append(q[a_:b_]); tm.append(m[a_:b_])
            if len(grid):
                tg = rnd_t[:, :, None] + OFFS[None, None, :]
                for sd, ba in ((0, True), (1, False)):
                    pr, dl = first_side(t, p, m, tg.ravel(), ba)
                    RP[:, :, ci, :, sd] = pr.reshape(tg.shape); RD[:, :, ci, :, sd] = dl.reshape(tg.shape)
        RP = RP[:, :, :len(coins)]; RD = RD[:, :, :len(coins)]
        # BTC trailing-60 s sign at random times (last trade at t and at t - 60 s)
        jn = np.searchsorted(tB, rnd_t, "right") - 1; jp = np.searchsorted(tB, rnd_t - 60000, "right") - 1
        rb_now = pB[np.maximum(jn, 0)]; rb_60 = pB[np.maximum(jp, 0)]
        np.savez_compressed(fn, n_shock=ns, tau=tau, tau_ref=np.array([x[1] for x in trig], np.int64),
                            rB=np.array([x[2] for x in trig]), side=np.array([x[3] for x in trig], np.int8),
                            p_tau=np.array([x[4] for x in trig]), p_ref=np.array([x[5] for x in trig]),
                            coins=np.array(coins), ranks=np.array(ranks), tc=np.concatenate(tc),
                            tk=np.concatenate(tk), tt=np.concatenate(tt), tp=np.concatenate(tp),
                            tq=np.concatenate(tq), tm=np.concatenate(tm), rnd_t=rnd_t, RP=RP, RD=RD,
                            offs=OFFS, rb_now=rb_now, rb_60=rb_60, n_grid=len(grid))
        print(ds, "shocks", ns, "coins", len(coins), f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
