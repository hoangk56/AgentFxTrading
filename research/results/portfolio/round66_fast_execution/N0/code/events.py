"""Round 66 N0: launch events = round 60's listing list (first 1d kline per base, exclusions as round 60), IS 2020-21 /
VAL 2022-24 by launch day; group NEW (no Binance spot, or spot <= 30 days before launch day) / OLD (spot > 30 days).
No prices after the first kline are read here."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R60 = os.path.join(HERE, "..", "..", "..", "round60_new_listings", "code")
sys.path.insert(0, R60)
import listings as Lm  # noqa: E402

C = Lm.C
DAY = 86400000
IS0, VAL0, END = 1577836800000, 1640995200000, 1735689600000


def events():
    syms = sorted(f[:-4] for f in os.listdir(os.path.join(C.DATA, "perp_1d")) if f.endswith(".csv"))
    sf = Lm.spot_first()
    out = []
    for s, L0 in Lm.events(syms):
        if s == "BTCUSDT":
            continue
        t = C.T0 + L0 * DAY
        if not (IS0 <= t < END):
            continue
        sp, _ = C.spot_name(s)
        ts = sf.get(sp)
        grp = "NEW" if ts is None or (t - ts) / DAY <= 30 else "OLD"
        out.append(dict(sym=s, day0=int(t), era="IS" if t < VAL0 else "VAL", group=grp,
                        year=int(str(__import__("numpy").datetime64(t, "ms"))[:4]),
                        spot_age_d=None if ts is None else (t - ts) / DAY))
    return out


if __name__ == "__main__":
    E = events()
    from collections import Counter
    print(len(E), Counter((e["era"], e["group"]) for e in E))
    print(Counter(e["year"] for e in E))
