"""Stream S: mua stablecoin khi X/USDT chiết khấu, bán khi về lại (HYPOTHESES_S.md).

Chạy: research/.venv/bin/python -I peg.py   (đọc research/data/binance_stables/npz/1m, cắt < 2025-01-01)
"""
import csv
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research"
NPZ = os.path.join(ROOT, "data/binance_stables/npz/1m")
OUT = os.path.join(ROOT, "results/portfolio/round64_parallel/S/out")
CUT = 1735689600000
DAY = 86400000
VAL0 = 1640995200000  # 2022-01-01
ZERO_FEE0 = {"default": 1688169600000, "FDUSDUSDT": 1690329600000}  # 2023-07-01, FDUSD 2023-07-26
PAIRS = ["USDCUSDT", "BUSDUSDT", "TUSDUSDT", "PAXUSDT", "USDPUSDT", "FDUSDUSDT", "DAIUSDT", "USDSUSDT",
         "USDSBUSDT"]
DEEP = {"USDCUSDT", "BUSDUSDT", "FDUSDUSDT"}
KS = [10, 30, 100]
HS = [1, 7]
FEE = 10e-4


def ymd(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def load_pairs():
    out = {}
    for p in PAIRS:
        f = os.path.join(NPZ, p + ".npz")
        if not os.path.exists(f):
            continue
        z = np.load(f)
        m = z["t"] < CUT
        out[p] = {"t": z["t"][m], "c": z["c"][m], "n": z["n"][m], "qv": z["qv"][m], "h": z["h"][m], "l": z["l"][m],
                  "v": z["v"][m], "tbb": z["tbb"][m], "tbq": z["tbq"][m]}
    return out


def load_dff():
    days, vals = [], []
    with open(os.path.join(ROOT, "data/rates/DFF.csv")) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            try:
                v = float(row[1])
            except ValueError:
                continue
            d = datetime.strptime(row[0], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days.append(int(d.timestamp() * 1000))
            vals.append(v / 100.0)
    return np.array(days), np.array(vals)


DFF_T, DFF_V = load_dff()


def cash(t_ms, hold_days):
    i = np.clip(np.searchsorted(DFF_T, t_ms, side="right") - 1, 0, len(DFF_V) - 1)
    return DFF_V[i] * hold_days / 365.0


def next_traded(n, i):
    """Nến đầu tiên từ i có giao dịch (nến rỗng: giá đóng chỉ là giá cũ)."""
    N = len(n)
    while i < N and n[i] == 0:
        i += 1
    return i


def taker_px(d, i, side):
    """Giá trung bình của lệnh taker cùng chiều trong nến i (hoặc nến kế tiếp có lệnh như vậy, tối đa 10 nến).

    Mua: tbq / tbb; bán: (qv - tbq) / (v - tbb). Không có thì lấy giá xấu nhất của nến i."""
    N = len(d["t"])
    for j in range(i, min(i + 10, N)):
        if side == "buy" and d["tbb"][j] > 0:
            px = d["tbq"][j] / d["tbb"][j]
        elif side == "sell" and d["v"][j] - d["tbb"][j] > 0:
            px = (d["qv"][j] - d["tbq"][j]) / (d["v"][j] - d["tbb"][j])
        else:
            continue
        if abs(px / d["c"][j] - 1) < 0.05:
            return float(px)
    return float(d["h"][i] if side == "buy" else d["l"][i])


def simulate(sym, d, k, H, late=0):
    t, c, n = d["t"], d["c"], d["n"]
    N = len(t)
    disc = 1.0 - c
    sig = np.flatnonzero(disc >= k * 1e-4)
    back = np.flatnonzero(disc <= k * 0.5e-4)
    trades = []
    i = 0
    while True:
        j = np.searchsorted(sig, i)
        if j >= len(sig):
            break
        s = sig[j]
        e = next_traded(n, s + 1 + late)
        if e >= N:
            break
        # ngắt quãng dữ liệu (mã ngừng giao dịch): không vào nếu nến vào cách tín hiệu > 1 giờ
        if t[e] - t[s] > 3600000:
            i = e
            continue
        tstop = np.searchsorted(t, t[e] + H * DAY)
        jb = np.searchsorted(back, e + 1)
        x = back[jb] if jb < len(back) else N
        if x < tstop:
            xb = next_traded(n, x + 1 + late)
            how = "revert"
        else:
            xb = next_traded(n, tstop + late)
            how = "time"
        gap = False
        if xb >= N:
            xb = N - 1
            how = "end"
        # dữ liệu đứt giữa lệnh (> 1 ngày không có nến): thoát ở nến cuối trước chỗ đứt
        seg = np.diff(t[e:xb + 1])
        if len(seg) and seg.max() > DAY:
            xb = e + int(np.argmax(seg > DAY))
            how = "gap"
            gap = True
        hold_days = (t[xb] - t[e]) / DAY
        trades.append({"sym": sym, "sig": int(s), "e": int(e), "x": int(xb), "te": int(t[e]), "tx": int(t[xb]),
                       "pe": float(c[e]), "px": float(c[xb]), "pe_hi": float(d["h"][e]), "px_lo": float(d["l"][xb]),
                       "pe_tk": taker_px(d, e, "buy"), "px_tk": taker_px(d, xb, "sell"), "d_sig": float(disc[s]), "d_e": float(disc[e]),
                       "hold": hold_days, "how": how, "gap": gap})
        i = xb + 1
    return trades


def costs(tr, mult=1.0, zero_fee=False):
    hs = 0.5e-4 if tr["sym"] in DEEP else 1.0e-4
    z0 = ZERO_FEE0.get(tr["sym"], ZERO_FEE0["default"])
    fee_e = 0.0 if (zero_fee and tr["te"] >= z0) else FEE
    fee_x = 0.0 if (zero_fee and tr["tx"] >= z0) else FEE
    return mult * (fee_e + fee_x + 2 * hs)


def net(tr, mult=1.0, zero_fee=False, excess=True, fill="close"):
    """fill: close = giá đóng + nửa spread proxy (đã khai báo); taker = giá TB của taker cùng chiều trong nến
    (đã gồm spread, chỉ cộng phí); worst = cao nhất nến vào / thấp nhất nến ra (chỉ cộng phí)."""
    fees = costs(tr, 1.0, zero_fee) - 2 * (0.5e-4 if tr["sym"] in DEEP else 1e-4)
    if fill == "close":
        r = tr["px"] / tr["pe"] - 1.0 - costs(tr, mult, zero_fee)
    elif fill == "taker":
        r = tr["px_tk"] / tr["pe_tk"] - 1.0 - mult * fees
    else:
        r = tr["px_lo"] / tr["pe_hi"] - 1.0 - mult * fees
    if excess:
        r -= cash(tr["te"], tr["hold"])
    return r


def episodes(trs):
    """Gộp lệnh mọi mã có [vào, ra] (đệm 24 h) chồng nhau thành một đợt."""
    if not trs:
        return np.array([], dtype=int)
    order = np.argsort([tr["te"] for tr in trs])
    lab = np.empty(len(trs), dtype=int)
    g, end = -1, -10**18
    for idx in order:
        a, b = trs[idx]["te"] - DAY, trs[idx]["tx"] + DAY
        if a > end:
            g += 1
            end = b
        else:
            end = max(end, b)
        lab[idx] = g
    return lab


def cl_t(r, lab):
    n = len(r)
    if n < 2:
        return float("nan"), 0
    m = r.mean()
    G = len(np.unique(lab))
    if G < 2:
        return float("nan"), G
    S = np.bincount(lab, weights=r - m)
    var = G / (G - 1) * (S ** 2).sum() / n ** 2
    return float(m / np.sqrt(var)) if var > 0 else float("nan"), G


def stats(trs, **kw):
    if not trs:
        return {"n": 0, "G": 0, "mean": float("nan"), "t": float("nan")}
    r = np.array([net(tr, **kw) for tr in trs])
    lab = episodes(trs)
    t, G = cl_t(r, lab)
    ep = np.bincount(lab, weights=r)
    sh_ep = ep.mean() / ep.std(ddof=1) if len(ep) > 1 and ep.std(ddof=1) > 0 else float("nan")
    sh_tr = r.mean() / r.std(ddof=1) if len(r) > 1 and r.std(ddof=1) > 0 else float("nan")
    return {"n": len(r), "G": G, "mean": float(r.mean()), "t": t, "sh_ep": float(sh_ep), "sh_tr": float(sh_tr),
            "ep_pos": int((ep > 0).sum()), "sum": float(r.sum()), "ep": ep}


def era_of(tr):
    return "IS" if tr["te"] < VAL0 else "VAL"


def year_of(tr):
    return datetime.fromtimestamp(tr["te"] / 1000, tz=timezone.utc).year


def random_bench(data, trs, ndraw=2000, mode="uniform", k=None, rng=None, **kw):
    """Phân phối mean net của lệnh ngẫu nhiên (cùng mã, cùng kỷ, cùng số nến giữ, cùng phí)."""
    if not trs:
        return None
    rng = rng or np.random.default_rng(64)
    means = np.zeros(ndraw)
    for tr in trs:
        d = data[tr["sym"]]
        t, c = d["t"], d["c"]
        hb = tr["x"] - tr["e"]
        lo, hi = (0, np.searchsorted(t, VAL0)) if era_of(tr) == "IS" else (np.searchsorted(t, VAL0), len(t))
        hi = max(lo + 1, hi - hb - 1)
        if mode == "uniform":
            pool = None
        else:
            disc = 1.0 - c[lo:hi]
            de = tr["d_e"]
            b_lo = k * 1e-4 if de < 2 * k * 1e-4 else (2 * k * 1e-4 if de < 4 * k * 1e-4 else 4 * k * 1e-4)
            b_hi = 2 * b_lo if b_lo < 4 * k * 1e-4 else 1.0
            pool = lo + np.flatnonzero((disc >= b_lo) & (disc < b_hi))
            if len(pool) == 0:
                pool = None
        idx = rng.integers(lo, hi, ndraw) if pool is None else pool[rng.integers(0, len(pool), ndraw)]
        gross = c[np.minimum(idx + hb, len(c) - 1)] / c[idx] - 1.0
        hold = (t[np.minimum(idx + hb, len(t) - 1)] - t[idx]) / DAY
        cst = costs(tr, kw.get("mult", 1.0), kw.get("zero_fee", False))
        cs = cash(tr["te"], hold) if kw.get("excess", True) else 0.0
        means += gross - cst - cs
    return means / len(trs)


def main():
    os.makedirs(OUT, exist_ok=True)
    data = load_pairs()
    print("pairs:", {p: (ymd(int(v["t"][0])), ymd(int(v["t"][-1])), len(v["t"])) for p, v in data.items()})
    cells = {}
    for k in KS:
        for H in HS:
            for late in (0, 1):
                trs = []
                for p, d in data.items():
                    trs.extend(simulate(p, d, k, H, late))
                trs.sort(key=lambda x: x["te"])
                cells[(k, H, late)] = trs
    return data, cells


if __name__ == "__main__":
    main()
