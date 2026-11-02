"""Coordinator re-implementation of K2 (PREREG_DRAFT_K): short alt perp / long BTCUSDT perp, both filled at the close of
the 1m bar starting at L + 1 h (fallback up to 4 later minutes), exit at entry + 72 h, cost 42 bp, funding at real
stamps in (te + 1 min + 30 s, tx + 1 min + 30 s] as k2.fsum. Prices from public fapi 1m klines; funding from local files,
else public fapi fundingRate. Logs to research/data/upbit_nonkrw/requests.log (stream M copy; pricing logic unchanged)."""
import csv, json, os, time, urllib.request, urllib.error, datetime as dt
import numpy as np
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
D = os.path.join(R, "upbit_nonkrw"); os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
H, M, DAY = 3600000, 60000, 86400000
COST = 0.0042
_last = {}


def get(url):
    host = url.split("/")[2]
    for att in range(6):
        w = 0.3 - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script", "Accept": "application/json"}), timeout=30) as r:
                body = r.read()
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t200\t{len(body)}\n")
            return json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return None
        except Exception as e:
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None


def px(sym, t):
    js = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={t}&limit=5") or []
    for x in js:
        if t <= int(x[0]) <= t + 4 * M:
            return float(x[4])
    return np.nan


_FU = {}


def funding(sym, a, b):
    if sym not in _FU:
        rows = []
        p = os.path.join(R, "binance", "funding", sym + ".csv")
        if os.path.exists(p):
            rows = [(float(t), float(r)) for t, r in list(csv.reader(open(p)))[1:]]
        _FU[sym] = np.array(rows) if rows else np.zeros((0, 2))
    F = _FU[sym]
    have = len(F) and F[:, 0].min() <= a and F[:, 0].max() >= b - 9 * H
    if not have:  # fetch the window from fapi
        js = get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - DAY}&endTime={b + DAY}&limit=1000") or []
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js]) if js else np.zeros((0, 2))
    if not len(F):
        return 0.0
    w = (F[:, 0] > a + 30000) & (F[:, 0] <= b + 30000)
    return float(F[w, 1].sum())


def trade(sym, L, hold=72 * H, cost=COST, off=H):
    te = L + off; tx = te + hold
    ae, ax, be, bx = px(sym, te), px(sym, tx), px("BTCUSDT", te), px("BTCUSDT", tx)
    if not all(np.isfinite([ae, ax, be, bx])):
        return None
    price = -((ax / ae - 1) - (bx / be - 1))
    fund = funding(sym, te + M, tx + M) - funding("BTCUSDT", te + M, tx + M)
    return te, price, fund, price + fund - cost


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n
