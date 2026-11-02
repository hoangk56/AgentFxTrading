"""Round 71 FS: stream data.binance.vision daily SPOT aggTrades for the candidate crash events (../HYPOTHESES_FS.md); adapted from round 66 F0 pull.py.

Run with `python -I` (downloads are untrusted; they are never written to disk: the zip is deflate-decoded on the fly and
only rows inside the event windows are kept). Order: seed-7171 permutations of IS and VAL candidates, interleaved.
Writes research/data/spot_wicks/agg/<SYM>_<YYYY-MM-DD>.npz (t ms, p, q, m=is_buyer_maker), agg_progress.json.
"""
import json, os, struct, sys, time, zlib
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # own code dir only (python -I drops it)
import numpy as np  # noqa: E402
import net, common as C  # noqa: E402

DAY = 86400000
MIN = 60000
PRE, POST = 2 * MIN, 63 * MIN
BUDGET = float(os.environ.get("FS_BUDGET_S", 45 * 60))
FILE_WALL = 150
NPZ = os.path.join(net.DATA, "agg")
BASE = "https://data.binance.vision/data/spot/daily/aggTrades"


def order():
    z = np.load(os.path.join(C.DATA, "cand.npz"))
    E = dict(syms=list(z["syms"]), sym=z["sym"], close_e=C.T0 + (z["t"].astype(np.int64) + 1) * MIN)
    idx = np.arange(len(z["t"]))
    era = np.where(z["t"] < C.VAL0, 0, 1)
    rng = np.random.default_rng(7171)
    a = rng.permutation(idx[era == 0]); b = rng.permutation(idx[era == 1])
    out = []
    for k in range(max(len(a), len(b))):
        if k < len(a): out.append(int(a[k]))
        if k < len(b): out.append(int(b[k]))
    return E, out


def jobs_for(E, seq):
    """symbol-day jobs in order of first need; each job has the windows of all events on that symbol-day."""
    jobs = {}; ev_jobs = {}
    for j in seq:
        s = E["syms"][E["sym"][j]]; ce = int(E["close_e"][j])
        lo, hi = ce - PRE, ce + POST
        need = []
        for d0 in range(lo // DAY, hi // DAY + 1):
            key = (s, int(d0))
            if key not in jobs:
                jobs[key] = []
            jobs[key].append((max(lo, d0 * DAY), min(hi, (d0 + 1) * DAY - 1)))
            need.append(key)
        ev_jobs[j] = need
    return jobs, ev_jobs


def day_str(d):
    return str(np.datetime64(int(d) * DAY, "ms"))[:10]


def fetch(key, wins):
    s, d = key
    ds = day_str(d)
    fn = os.path.join(NPZ, f"{s}_{ds}.npz")
    if os.path.exists(fn):
        return key, "cached", 0
    url = f"{BASE}/{s}/{s}-aggTrades-{ds}.zip"
    w = np.array(sorted(wins), np.int64)
    wlo, cutoff = int(w[:, 0].min()), int(w[:, 1].max())
    r = net.open_url(url, timeout=20)
    tstart = time.time()
    if r is None:
        net.log(url, 404, 0, "missing")
        return key, "404", 0
    nbytes = 0
    T, P, Q, M = [], [], [], []
    try:
        head = b""
        while len(head) < 30:
            c = r.read(30 - len(head))
            if not c: break
            head += c
        nbytes += len(head)
        sig, ver, flag, meth, _, _, _, csz, usz, nl, xl = struct.unpack("<IHHHHHIIIHH", head)
        if sig != 0x04034B50 or meth != 8:
            raise ValueError(f"zip header sig {sig:x} method {meth}")
        skip = nl + xl
        while skip > 0:
            c = r.read(skip); nbytes += len(c); skip -= len(c)
            if not c: break
        dec = zlib.decompressobj(-15)
        buf = b""; done = False
        while not done:
            if time.time() - tstart > FILE_WALL:
                raise TimeoutError(f"file wall deadline {FILE_WALL}s at {nbytes} bytes")
            c = r.read1(1 << 18)
            if not c:
                buf += dec.flush(); done = True
            else:
                nbytes += len(c); buf += dec.decompress(c)
            k = buf.rfind(b"\n")
            if k < 0 and not done:
                continue
            block, buf = (buf, b"") if done else (buf[:k + 1], buf[k + 1:])
            lines = block.split(b"\n")
            # fast skip: last full line before the first window start
            last = None
            for ln in reversed(lines):
                if ln and ln[:1].isdigit():
                    last = ln; break
            if last is None:
                continue
            tl = int(last.split(b",")[5])
            if tl < wlo:
                continue
            for ln in lines:
                if not ln or not ln[:1].isdigit():
                    continue
                f = ln.split(b",")
                t = int(f[5])
                if t > cutoff:
                    done = True; break
                if t < wlo:
                    continue
                if np.any((w[:, 0] <= t) & (t <= w[:, 1])):
                    T.append(t); P.append(float(f[1])); Q.append(float(f[2])); M.append(f[6].strip()[:1] in (b"t", b"T"))
    finally:
        r.close()
    net.log(url, 200, nbytes, f"streamed rows={len(T)}")
    tmp = fn + ".tmp.npz"
    np.savez_compressed(tmp, t=np.array(T, np.int64), p=np.array(P), q=np.array(Q, np.float32), m=np.array(M, bool))
    os.replace(tmp, fn)
    return key, "ok", nbytes


def main():
    os.makedirs(NPZ, exist_ok=True)
    E, seq = order()
    jobs, ev_jobs = jobs_for(E, seq)
    keys = []
    for j in seq:
        for k in ev_jobs[j]:
            if k not in keys: keys.append(k)
    t0 = time.time(); status = {}; tot = 0
    queue = list(keys); tries = {}; fmap = {}
    ex = ThreadPoolExecutor(3)
    if True:
        pending = set()
        while True:
            while len(pending) < 3 and time.time() - t0 < BUDGET and queue:
                k = queue.pop(0); tries[k] = tries.get(k, 0) + 1
                fu = ex.submit(fetch, k, jobs[k]); pending.add(fu); fmap[fu] = k
            if not pending:
                break
            if time.time() - t0 > BUDGET + FILE_WALL + 30:
                print("hard stop with", len(pending), "pending", flush=True); break
            donef = [f for f in pending if f.done()]
            if not donef:
                time.sleep(0.05); continue
            for f in donef:
                pending.discard(f)
                try:
                    k, st, nb = f.result()
                except net.Stop403 as e:
                    print("403 STOP", e, flush=True); os._exit(3)
                except Exception as e:  # keep going; retried once at the end of the queue
                    k = fmap[f]
                    net.log(f"{BASE}/{k[0]}/{k[0]}-aggTrades-{day_str(k[1])}.zip", "ERR", 0, repr(e)[:120])
                    print("ERR", k, repr(e), flush=True)
                    if tries[k] < 3: queue.append(k)
                    continue
                status[f"{k[0]}_{day_str(k[1])}"] = st; tot += nb
                if len(status) % 20 == 0:
                    print(f"{time.time() - t0:7.0f}s files {len(status)}/{len(keys)} MB {tot / 1e6:.0f}", flush=True)
    ex.shutdown(wait=False, cancel_futures=True)
    done_ev = [j for j in seq if all(status.get(f"{k[0]}_{day_str(k[1])}") in ("ok", "cached", "404") for k in ev_jobs[j])]
    json.dump({"order": seq, "done_events": done_ev, "status": status, "seconds": time.time() - t0, "bytes": tot,
               "ev_files": {str(j): [f"{k[0]}_{day_str(k[1])}" for k in ev_jobs[j]] for j in done_ev}},
              open(os.path.join(net.DATA, "agg_progress.json"), "w"))
    print("done events", len(done_ev), "files", len(status), "MB", tot / 1e6, "s", time.time() - t0, flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
