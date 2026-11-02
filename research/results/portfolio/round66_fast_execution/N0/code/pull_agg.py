"""Round 66 N0: stream data.binance.vision futures/um daily aggTrades of each listing's launch day (../HYPOTHESES_N0.md).

Run with `python -I` (downloads are untrusted; zips are deflate-decoded on the fly, never written to disk). Keeps rows
from the first trade T0 to T0 + 2 h (the next day's file too if T0 + 2 h crosses midnight; never a file dated >=
2025-01-01). Writes research/data/perp_launch/agg/<SYM>_<YYYY-MM-DD>.npz (t ms, p, q, m=is_buyer_maker, T0, files).
Order: seed-6601 permutation of IS and VAL events, interleaved.
"""
import json, os, struct, sys, time, zlib
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # own code dir only
import numpy as np  # noqa: E402
import net  # noqa: E402

DAY = 86400000
H2 = 2 * 3600000
END = 1735689600000
BUDGET = float(os.environ.get("N0_BUDGET_S", 40 * 60))
FILE_WALL = 240
OUT = os.path.join(net.DATA, "agg")
BASE = "https://data.binance.vision/data/futures/um/daily/aggTrades"


def day_str(d0):
    return str(np.datetime64(int(d0), "ms"))[:10]


def stream(url, cutoff=None):
    """yields nothing; returns (T, P, Q, M, nbytes, status). cutoff None = set to first trade + 2 h."""
    r = net.open_url(url, timeout=20)
    if r is None:
        net.log(url, 404, 0, "missing")
        return None
    t0w = time.time(); nbytes = 0
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
            if time.time() - t0w > FILE_WALL:
                raise TimeoutError(f"file wall {FILE_WALL}s at {nbytes} bytes")
            c = r.read1(1 << 18)
            if not c:
                buf += dec.flush(); last_block = True
            else:
                nbytes += len(c); buf += dec.decompress(c); last_block = False
            k = buf.rfind(b"\n")
            if k < 0 and not last_block:
                continue
            block, buf = (buf, b"") if last_block else (buf[:k + 1], buf[k + 1:])
            for ln in block.split(b"\n"):
                if not ln or not ln[:1].isdigit():
                    continue
                f = ln.split(b",")
                t = int(f[5])
                if t > 1e14:
                    t //= 1000
                if cutoff is None:
                    cutoff = t + H2
                if t > cutoff:
                    done = True; break
                T.append(t); P.append(float(f[1])); Q.append(float(f[2])); M.append(f[6].strip()[:1] in (b"t", b"T", b"1"))
            if last_block:
                done = True
    finally:
        r.close()
    net.log(url, 200, nbytes, f"streamed rows={len(T)}")
    return T, P, Q, M, cutoff


def fetch(e):
    s, d0 = e["sym"], e["day0"]
    fn = os.path.join(OUT, f"{s}_{day_str(d0)}.npz")
    if os.path.exists(fn):
        return s, "cached", 0
    r1 = stream(f"{BASE}/{s}/{s}-aggTrades-{day_str(d0)}.zip")
    if r1 is None:
        return s, "404", 0
    T, P, Q, M, cutoff = r1
    files = [day_str(d0)]
    if T and cutoff >= d0 + DAY and d0 + DAY < END:
        r2 = stream(f"{BASE}/{s}/{s}-aggTrades-{day_str(d0 + DAY)}.zip", cutoff)
        if r2 is not None:
            T += r2[0]; P += r2[1]; Q += r2[2]; M += r2[3]; files.append(day_str(d0 + DAY))
        else:
            files.append("next-404")
    t = np.array(T, np.int64)
    o = np.argsort(t, kind="stable")
    tmp = fn + ".tmp.npz"
    np.savez_compressed(tmp, t=t[o], p=np.array(P)[o], q=np.array(Q, np.float32)[o], m=np.array(M, bool)[o],
                        T0=int(t.min()) if len(t) else -1, files=np.array(files))
    os.replace(tmp, fn)
    return s, "ok", len(t)


def main():
    import events
    os.makedirs(OUT, exist_ok=True)
    E = events.events()
    rng = np.random.default_rng(6601)
    a = [E[i] for i in rng.permutation([i for i, e in enumerate(E) if e["era"] == "IS"])]
    b = [E[i] for i in rng.permutation([i for i, e in enumerate(E) if e["era"] == "VAL"])]
    seq = []
    for k in range(max(len(a), len(b))):
        if k < len(a): seq.append(a[k])
        if k < len(b): seq.append(b[k])
    t0 = time.time(); status = {}; tries = {}; queue = list(range(len(seq))); pending = {}
    ex = ThreadPoolExecutor(3)
    while True:
        while len(pending) < 3 and time.time() - t0 < BUDGET and queue:
            i = queue.pop(0); tries[i] = tries.get(i, 0) + 1
            pending[ex.submit(fetch, seq[i])] = i
        if not pending:
            break
        if time.time() - t0 > BUDGET + FILE_WALL * 2 + 30:
            print("hard stop", len(pending), flush=True); break
        donef = [f for f in pending if f.done()]
        if not donef:
            time.sleep(0.05); continue
        for f in donef:
            i = pending.pop(f)
            try:
                s, st, n = f.result()
            except net.Stop403 as x:
                print("403 STOP", x, flush=True); os._exit(3)
            except Exception as x:
                print("ERR", seq[i]["sym"], repr(x)[:120], flush=True)
                net.log(seq[i]["sym"], "ERR", 0, repr(x)[:120])
                if tries[i] < 3: queue.append(i)
                continue
            status[f"{s}_{day_str(seq[i]['day0'])}"] = st
            if len(status) % 20 == 0:
                print(f"{time.time() - t0:7.0f}s events {len(status)}/{len(seq)} last {s} {st} {n}", flush=True)
    ex.shutdown(wait=False, cancel_futures=True)
    json.dump({"order": [f"{e['sym']}_{day_str(e['day0'])}" for e in seq], "status": status, "seconds": time.time() - t0},
              open(os.path.join(net.DATA, "progress_agg.json"), "w"))
    print("done", len(status), "s", time.time() - t0, flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
