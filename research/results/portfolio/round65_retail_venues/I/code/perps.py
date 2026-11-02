"""Binance USDT-M perp start per base coin, from local research/data/binance/perp_1d (first row; cut ts < 2025)."""
import os, glob

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
CUT = 1735689600000  # 2025-01-01 UTC ms


def perp_starts():
    out = {}
    for p in glob.glob(os.path.join(R, "binance", "perp_1d", "*.csv")):
        sym = os.path.basename(p)[:-4]
        if not sym.endswith("USDT"):
            continue
        with open(p) as f:
            f.readline(); first = f.readline()
        if not first:
            continue
        t = int(first.split(",")[0])
        if t >= CUT:
            continue
        base = sym[:-4]
        for pre in ("1000000", "10000", "1000", "1M"):
            if base.startswith(pre) and len(base) > len(pre) + 1:
                base = base[len(pre):]; break
        if base not in out or t < out[base][0]:
            out[base] = (t, sym)
    return out


if __name__ == "__main__":
    ps = perp_starts(); print(len(ps), list(ps.items())[:5])
