"""Round 75: build the footprint cache from Binance USDT-M monthly aggTrades.

Run with the research venv and -I (downloads are untrusted data):
    research/.venv/bin/python -I research/results/portfolio/round75_order_flow/coord/code/build_fp.py BTCUSDT 2020-01 2024-12

Per month it writes research/data/footprint/<SYM>/<YYYY-MM>.npz with
  fp_key  int64   minute * 100000 + bucket, bucket = floor(1e4 * ln(price)) (1 bp log grid)
  fp_bid  float32 base qty traded by aggressive sellers in that minute and bucket (isBuyerMaker = true)
  fp_ask  float32 base qty traded by aggressive buyers
  m_min   int64   epoch minute;  m_o m_h m_l m_c float64;  m_vb m_vs float64 (aggressive buy / sell qty);  m_n int32
  big_ts int64 ms, big_p float64, big_q float64, big_side int8 (+1 aggressive buy, -1 aggressive sell):
          every aggTrade with notional >= BIG_USD
HOLD guard: months >= 2025-01 are refused unless --hold is passed (coordinator only, after a registration).
"""
import io
import os
import subprocess
import sys
import time
import zipfile

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
OUT = os.path.join(ROOT, "research", "data", "footprint")
URL = "https://data.binance.vision/data/futures/um/monthly/aggTrades/{s}/{s}-aggTrades-{m}.zip"
BIG_USD = 100_000.0
CHUNK = 192 * 1024 * 1024
KEY_MUL = 100_000


def log(line):
    with open(os.path.join(OUT, "requests.log"), "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + line + "\n")


def fetch(sym, month, dst):
    url = URL.format(s=sym, m=month)
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "-f", "-o", dst + ".part", "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True)
        log(f"GET {url} -> {r.stdout.strip()} rc={r.returncode}")
        if r.returncode == 0:
            chk = subprocess.run(["curl", "-s", "-f", url + ".CHECKSUM"], capture_output=True, text=True).stdout.split()
            got = subprocess.run(["shasum", "-a", "256", dst + ".part"], capture_output=True, text=True).stdout.split()
            if chk and got and chk[0] == got[0]:
                os.replace(dst + ".part", dst)
                return True
            log(f"CHECKSUM mismatch {url}")
        if "404" in r.stdout:
            return False
        time.sleep(5 * (attempt + 1))
    return False


def parse(text):
    text = text.replace("true", "1").replace("false", "0").replace("\n", ",")
    a = np.fromstring(text, sep=",")
    return a.reshape(-1, 7)


class Acc:
    def __init__(self):
        self.fp = []
        self.mins = []
        self.big = []

    def add(self, a):
        if len(a) == 0:
            return
        # A few files (SOL 2023-11) have timestamps that step back inside a chunk; the minute aggregation below needs
        # them sorted. Stable sort keeps file (aggTrade id) order inside a minute for open / close.
        a = a[np.argsort(a[:, 5], kind="stable")]
        price, qty, ts, maker = a[:, 1], a[:, 2], a[:, 5].astype(np.int64), a[:, 6]
        minute = ts // 60000
        bucket = np.floor(1e4 * np.log(price)).astype(np.int64)
        key = minute * KEY_MUL + bucket
        sell = maker > 0.5
        uk, inv = np.unique(key, return_inverse=True)
        self.fp.append((uk,
                        np.bincount(inv, weights=np.where(sell, qty, 0.0), minlength=len(uk)),
                        np.bincount(inv, weights=np.where(sell, 0.0, qty), minlength=len(uk))))
        um, first = np.unique(minute, return_index=True)
        last = np.r_[first[1:], len(minute)] - 1
        self.mins.append((um, price[first], np.maximum.reduceat(price, first), np.minimum.reduceat(price, first),
                          price[last], np.add.reduceat(np.where(sell, 0.0, qty), first),
                          np.add.reduceat(np.where(sell, qty, 0.0), first), np.diff(np.r_[first, len(minute)])))
        b = price * qty >= BIG_USD
        if b.any():
            self.big.append((ts[b], price[b], qty[b], np.where(sell[b], -1, 1).astype(np.int8)))

    def save(self, path):
        # fp_key carries into the minute field when bucket >= 1e5 (BTC above $22,026); fp.split_key undoes it.
        k = np.concatenate([x[0] for x in self.fp])
        uk, inv = np.unique(k, return_inverse=True)
        bid = np.bincount(inv, weights=np.concatenate([x[1] for x in self.fp]), minlength=len(uk))
        ask = np.bincount(inv, weights=np.concatenate([x[2] for x in self.fp]), minlength=len(uk))
        m = [np.concatenate([x[i] for x in self.mins]) for i in range(8)]
        if len(np.unique(m[0])) != len(m[0]):
            # Timestamps in a few files step back across a chunk edge: merge the pieces of a minute
            # (open of the earliest piece, close of the latest, in file order).
            order = np.argsort(m[0], kind="stable")
            m = [x[order] for x in m]
            um, first = np.unique(m[0], return_index=True)
            last = np.r_[first[1:], len(m[0])] - 1
            print(f"merged {len(m[0]) - len(um)} split minutes", flush=True)
            m = [um, m[1][first], np.maximum.reduceat(m[2], first), np.minimum.reduceat(m[3], first), m[4][last],
                 np.add.reduceat(m[5], first), np.add.reduceat(m[6], first), np.add.reduceat(m[7], first)]
        big = [np.concatenate([x[i] for x in self.big]) if self.big else np.zeros(0) for i in range(4)]
        np.savez(path + ".tmp.npz", fp_key=uk, fp_bid=bid.astype(np.float32), fp_ask=ask.astype(np.float32),
                 m_min=m[0], m_o=m[1], m_h=m[2], m_l=m[3], m_c=m[4], m_vb=m[5], m_vs=m[6], m_n=m[7].astype(np.int32),
                 big_ts=big[0].astype(np.int64), big_p=big[1], big_q=big[2], big_side=big[3].astype(np.int8))
        os.replace(path + ".tmp.npz", path)


def build_month(sym, month, raw):
    acc = Acc()
    carry = b""
    tail = None
    with zipfile.ZipFile(raw) as z, z.open(z.namelist()[0]) as f:
        first = True
        while True:
            buf = f.read(CHUNK)
            if not buf and not carry:
                break
            data = carry + buf
            if buf:
                cut = data.rfind(b"\n") + 1
                carry, data = data[cut:], data[:cut]
            else:
                carry = b""
            if first:
                first = False
                if data[:1] and not data[:1].isdigit():
                    data = data[data.find(b"\n") + 1:]
            a = parse(data.decode("ascii").strip("\n"))
            if tail is not None:
                a = np.vstack([tail, a])
            if buf:
                lm = a[-1, 5] // 60000
                keep = a[:, 5] // 60000 < lm
                tail, a = a[~keep], a[keep]
            else:
                tail = None
            acc.add(a)
            if not buf:
                break
    if tail is not None and len(tail):
        acc.add(tail)
    return acc


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    sym, m0, m1 = args
    if max(m0, m1) >= "2025-01" and "--hold" not in sys.argv:
        sys.exit("HOLD months (>= 2025-01) need --hold (coordinator only)")
    os.makedirs(os.path.join(OUT, sym), exist_ok=True)
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
    y, mo = map(int, m0.split("-"))
    while f"{y:04d}-{mo:02d}" <= m1:
        month = f"{y:04d}-{mo:02d}"
        dst = os.path.join(OUT, sym, month + ".npz")
        if not os.path.exists(dst):
            raw = os.path.join(OUT, "raw", f"{sym}-{month}.zip")
            t0 = time.time()
            if os.path.exists(raw) or fetch(sym, month, raw):
                t1 = time.time()
                build_month(sym, month, raw).save(dst)
                os.remove(raw)
                print(f"{sym} {month} dl {t1 - t0:.0f}s build {time.time() - t1:.0f}s", flush=True)
            else:
                print(f"{sym} {month} missing", flush=True)
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1


if __name__ == "__main__":
    main()
