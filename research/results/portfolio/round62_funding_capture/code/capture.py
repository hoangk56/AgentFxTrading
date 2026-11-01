"""Round 62: receive extreme funding through one stamp (../HYPOTHESES.md)."""
import csv, os
import numpy as np
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "binance")
H = 3600000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000), "HOLD": (1735689600000, 1793318400000)}

def stamps(s, end):
    for sub in ("funding", "funding_window"):
        p = os.path.join(B, sub, s + ".csv")
        if os.path.exists(p):
            rows = list(csv.reader(open(p)))[1:]
            a = np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 2))
            return a[a[:, 0] <= end] if len(a) else a
    return np.zeros((0, 2))

def klines(s, end):
    p = os.path.join(B, "perp_1h", f"{s}_{end}.csv")
    if not os.path.exists(p):
        return {}
    rows = list(csv.reader(open(p)))[1:]
    return {int(float(r[0])): (float(r[1]), float(r[4])) for r in rows}

def events(s, end, tier):
    a = stamps(s, end)
    if len(a) < 2:
        return []
    k = klines(s, end)
    st_hours = set((a[:, 0] // H * H).astype(np.int64).tolist())
    interval = np.median(np.diff(a[:, 0])) / H if len(a) > 2 else 8
    cost = 0.0012 if s in ("BTCUSDT", "ETHUSDT") else 0.0020
    out = []
    for j in range(1, len(a)):
        fp, ft = a[j - 1, 1], a[j, 1]
        if abs(fp) < tier:
            continue
        Th = int(a[j, 0] // H * H)
        side = -np.sign(fp)
        need = (Th - H, Th, Th - 2 * H, Th + H)
        if any(x not in k for x in need):
            continue
        ent = k[Th - H][0]
        pre = k[Th - H][1]
        ex = k[Th][1]
        price = side * (ex / ent - 1)
        out.append(dict(sym=s, T=Th, fp=fp, ft=ft, side=side, price=price, fund=-side * ft,
                        pre=side * (pre / ent - 1), post=side * (ex / pre - 1), cost=cost,
                        wide=side * (k[Th + H][1] / k[Th - 2 * H][0] - 1) if (Th + H) in k else np.nan,
                        p1=-side * (k[Th][1] / k[Th][0] - 1) - cost,
                        interval=interval, k=k, st=st_hours))
    return out

def net(e, cm=1.0):
    return e["price"] + e["fund"] - cm * e["cost"]

def random_window(e, rng, a_rates):
    k, st = e["k"], e["st"]
    for _ in range(40):
        h = e["T"] + int(rng.integers(-72, 73)) * H
        if h == e["T"]:
            continue
        if (h - H) not in k or h not in k:
            continue
        inside = [x for x in (h,) if x in st]
        if e["interval"] > 2 and inside:
            continue
        f = sum(a_rates.get(x, 0.0) for x in inside)
        return e["side"] * (k[h][1] / k[h - H][0] - 1) - e["side"] * f - e["cost"]
    return None

def cluster_t(r, keys):
    r = np.asarray(r); keys = np.asarray(keys); mu = r.mean()
    u, inv = np.unique(keys, return_inverse=True)
    g = np.bincount(inv, weights=r - mu)
    se = np.sqrt(np.sum(g ** 2)) / len(r) * np.sqrt(len(u) / max(1, len(u) - 1))
    return mu / se


def random_p1(e, rng):
    k, st = e["k"], e["st"]
    for _ in range(40):
        h = e["T"] + int(rng.integers(-72, 73)) * H
        if h == e["T"] or h not in k:
            continue
        if e["interval"] > 2 and h in st:
            continue
        return -e["side"] * (k[h][1] / k[h][0] - 1) - e["cost"]
    return None
