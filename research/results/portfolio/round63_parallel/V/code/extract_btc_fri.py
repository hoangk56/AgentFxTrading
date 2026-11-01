"""Extract BTC option trades in Friday 07:30-10:00 UTC windows (2021-03-05..2024-12-27) from round 34's monthly npz
(read-only) into research/data/deribit/BTC_fri/<year>.npz, the same layout as the ETH pull. Also keeps a daily
08:00-09:00 window sample (BTC_daily/<year>.npz) to check the scaled-iv mark-to-market."""
import os, glob, datetime as dt, numpy as np

SRC = "/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r34/D/data/BTC"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit"
CUT = 1735689600000
F = ["ts", "exp", "k", "cp", "px", "amt", "dirn", "iv", "idx", "mark", "blk", "combo", "liq"]

for y in (2021, 2022, 2023, 2024):
    fri, day = {f: [] for f in F}, {f: [] for f in F}
    for fn in sorted(glob.glob(f"{SRC}/{y}??.npz")):
        if y == 2021 and int(fn[-6:-4]) < 3:
            continue
        z = np.load(fn)
        ts = z["ts"]
        keep_ts = ts < CUT
        d = ts // 1000
        wd = ((d // 86400) + 3) % 7  # 0 = Monday (1970-01-01 was a Thursday)
        sod = d % 86400
        mf = keep_ts & (wd == 4) & (sod >= 7.5 * 3600) & (sod < 10 * 3600)
        md = keep_ts & (sod >= 8 * 3600) & (sod < 9 * 3600)
        for f in F:
            fri[f].append(z[f][mf]); day[f].append(z[f][md])
    for name, dd in (("BTC_fri", fri), ("BTC_daily", day)):
        os.makedirs(f"{OUT}/{name}", exist_ok=True)
        np.savez_compressed(f"{OUT}/{name}/{y}.npz", **{f: np.concatenate(dd[f]) for f in F})
    print(y, sum(len(a) for a in fri["ts"]), sum(len(a) for a in day["ts"]))
