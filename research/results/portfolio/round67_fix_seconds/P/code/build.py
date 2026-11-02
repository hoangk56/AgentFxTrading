"""Per-fix-day quote table, one tick file at a time -> data/cny_fix/cache/days.npz.

For each SAFE fix day 2016-24 with IC ticks: the pre-01:15 quote, the mid in force at the path offsets, and the
first tick at or after each fill offset (bid, ask, lag).
"""
import numpy as np

from plib import CACHE, load_fix, load_window, quote_at_or_after, quote_before

T = 1 * 3600 + 15 * 60
PATH_OFF = [-60, -30, -10, 0, 5, 10, 15, 20, 30, 60, 120, 360, 900, 1800]
# entries d, d+0.25 s, d+30 s, d+60 s; exits H, H+0.25, H+30, H+60
FILL_OFF = sorted({x for b in (5, 30, 360, 1800) for x in (b, b + 0.25, b + 30, b + 60)})


def main():
    fix = load_fix()
    days = sorted(d for d in fix if d.year >= 2016)
    rec = {"date": [], "fix": [], "pre_mid": [], "pre_age": [], "pre_spread": []}
    path = []
    fills = []  # (n_off, 3): bid, ask, lag s
    for d in days:
        w = load_window(d, T - 600, T + 1900 + 60)
        if w is None or w[0].size < 10:
            continue
        ts, b, a = w
        q = quote_before(ts, b, a, T * 1000)
        if q is None:
            continue
        rec["date"].append(d.toordinal())
        rec["fix"].append(fix[d])
        rec["pre_mid"].append((q[1] + q[2]) / 2)
        rec["pre_age"].append(T - q[0] / 1000)
        rec["pre_spread"].append(q[2] - q[1])
        pr = []
        for off in PATH_OFF:
            qq = quote_before(ts, b, a, int((T + off) * 1000))
            pr.append((qq[1] + qq[2]) / 2 if qq else np.nan)
        path.append(pr)
        fr = []
        for off in FILL_OFF:
            qq = quote_at_or_after(ts, b, a, int(round((T + off) * 1000)))
            fr.append((qq[1], qq[2], qq[0] / 1000 - (T + off)) if qq else (np.nan, np.nan, np.nan))
        fills.append(fr)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE / "days.npz", **{k: np.array(v) for k, v in rec.items()}, path=np.array(path),
             path_off=np.array(PATH_OFF, float), fills=np.array(fills), fill_off=np.array(FILL_OFF, float))
    print("days", len(rec["date"]))


if __name__ == "__main__":
    main()
