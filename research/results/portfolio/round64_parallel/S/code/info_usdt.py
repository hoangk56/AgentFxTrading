"""Thông tin: chiết khấu của chính USDT qua chéo BTC (BTCBUSD / BTCUSDC vs BTCUSDT, nến 1h), chỉ IS / VAL.

Chạy: research/.venv/bin/python -I info_usdt.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import peg  # noqa: E402

H1 = os.path.join(peg.ROOT, "data/binance_stables/npz/1h")


def load(sym):
    z = np.load(os.path.join(H1, sym + ".npz"))
    m = z["t"] < peg.CUT
    return z["t"][m], z["c"][m]


def main():
    tb, cb = load("BTCUSDT")
    data = peg.load_pairs()
    out = []
    for cross, direct in (("BTCBUSD", "BUSDUSDT"), ("BTCUSDC", "USDCUSDT"), ("BTCTUSD", "TUSDUSDT")):
        f = os.path.join(H1, cross + ".npz")
        if not os.path.exists(f):
            continue
        tx, cx = load(cross)
        common, ia, ib = np.intersect1d(tb, tx, return_indices=True)
        # giá X theo USDT suy từ BTC: BTCUSDT / BTCX; > 1 nghĩa là USDT rẻ (chiết khấu)
        implied = cb[ia] / cx[ib]
        d = data.get(direct)
        corr = gap = float("nan")
        if d is not None:
            # giá đóng 1m của nến cuối mỗi giờ (open time = giờ + 59 phút)
            j = np.searchsorted(d["t"], common + 59 * 60000)
            ok = (j < len(d["t"])) & (d["t"][np.minimum(j, len(d["t"]) - 1)] == common + 59 * 60000)
            dc = d["c"][j[ok]]
            gap = np.median(np.abs(implied[ok] - dc)) * 1e4
            corr = np.corrcoef(implied[ok] - 1, dc - 1)[0, 1]
        for era, m in (("IS", common < peg.VAL0), ("VAL", common >= peg.VAL0)):
            if m.sum() == 0:
                continue
            u = implied[m] - 1  # USDT chiết khấu so với X
            out.append(f"{cross} vs BTCUSDT {era}: hours {m.sum()}, implied USDT discount vs {cross[3:]} median "
                       f"{np.median(u) * 1e4:+.1f} bp, p5 {np.percentile(u, 5) * 1e4:+.1f}, p95 "
                       f"{np.percentile(u, 95) * 1e4:+.1f}, hours > +30 bp {np.mean(u > 3e-3) * 100:.2f} %, "
                       f"< -30 bp {np.mean(u < -3e-3) * 100:.2f} %, max {u.max() * 1e4:+.0f}, min {u.min() * 1e4:+.0f}")
        out.append(f"   cross vs direct {direct} close at the same hour: corr {corr:.3f}, median |gap| {gap:.1f} bp")
    text = "\n".join(out)
    print(text)
    with open(os.path.join(peg.OUT, "usdt_cross.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
