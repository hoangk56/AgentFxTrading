"""Gotobi: gửi mọi lệnh sớm 1 phút (hoặc sớm vài giây) so với bot hiện tại, tập trung năm 2026.
Chạy: research/.venv/bin/python <file> <ticks_dir> <depth_dir>  (cwd = repo 105)

Đơn vị pip (0.01 JPY), + = phương án sớm lợi hơn. Bot: short mở tại bid lúc fix, long đóng tại bid lúc fix,
short đóng tại ask lúc 02:55. Dời tất cả đi tau giây:
  đóng long:  bid(fix+tau) - bid(fix)
  mở short:   bid(fix+tau) - bid(fix)     (cùng dấu, nên chênh ở fix tính hai lần)
  đóng short: ask(exit) - ask(exit+tau)
t_day: 3 cặp gộp trung bình mỗi ngày (3 cặp JPY cùng ngày không độc lập)."""
import datetime as dt
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, ".")
from research.swing.swing_rules import gotobi_days
from research.ticks import load_ticks
from research.tools.gotobi_holidays import no_fix_days

TICKS, DEPTH = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
PAIRS = ("USDJPY", "EURJPY", "GBPJPY")
UTC = dt.timezone.utc
HOL = no_fix_days(range(2016, 2027))
OFF = [-120, -60, -30, -15, -10, -5, -2, -1, -0.5, 0, 0.2, 0.5, 1, 2, 3, 5, 10]


def ms(d, h=0, m=0, s=0.0):
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp() * 1000 + (h * 3600 + m * 60 + s) * 1000)


def load_depth(sym, d):
    p = DEPTH / f"depth_{sym}_{d:%Y%m%d}.csv"
    if not p.exists():
        return None
    ts, b, a = [], [], []
    for line in p.read_text().splitlines()[1:]:
        f = line.split(",")
        if len(f) < 4 or not f[2] or not f[3]:
            continue
        ts.append(int(f[0]))
        b.append(float(f[2].split("|")[0].split(":")[0]))
        a.append(float(f[3].split("|")[0].split(":")[0]))
    return np.array(ts), np.array(b), np.array(a)


class Book:
    def __init__(self, sym, d):
        tk = load_ticks(sym, d, d, TICKS)
        self.src = None
        if len(tk):
            self.ts, self.b, self.a = tk.ts, tk.bid, tk.ask
            self.src = "tick"
        else:
            x = load_depth(sym, d)
            if x is not None and len(x[0]):
                self.ts, self.b, self.a = x
                self.src = "depth"

    def at(self, T):
        """Giá của tick cuối cùng tại hoặc trước T; không có tick trong 5 phút thì None."""
        i = int(np.searchsorted(self.ts, T, side="right")) - 1
        if i < 0 or T - self.ts[i] > 300_000:
            return None
        return self.b[i], self.a[i]


def mt(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    n = len(xs)
    if n < 3:
        return n, float("nan"), float("nan")
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return n, m, (m / (sd / math.sqrt(n)) if sd else float("nan"))


def per_day(cells):
    g = defaultdict(list)
    for (_, d), v in cells.items():
        g[d].append(v)
    return {d: sum(v) / len(v) for d, v in g.items()}


def boot(vals, n=20000):
    a = np.array(vals)
    r = np.random.default_rng(7)
    m = a[r.integers(0, len(a), (n, len(a)))].mean(axis=1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


# ---------------- A. tick theo giây ----------------
days = [d for d in gotobi_days(dt.date(2025, 1, 1), dt.date(2026, 11, 5)) if d not in HOL]
fix = defaultdict(dict)    # tau -> {(sym, d): pips bid(fix+tau)-bid(fix)}
sc = defaultdict(dict)     # tau -> {(sym, d): pips ask(exit)-ask(exit+tau)}
spr = defaultdict(lambda: defaultdict(list))   # (year, sym) -> tau -> spread
srcs = defaultdict(int)
for sym in PAIRS:
    for d in days:
        bk = Book(sym, d)
        if bk.src is None:
            continue
        p0 = bk.at(ms(d, 0, 55))
        if p0 is None:
            continue
        srcs[(d.year, bk.src)] += 1
        for tau in OFF:
            p = bk.at(ms(d, 0, 55, tau))
            if p:
                fix[tau][(sym, d)] = (p[0] - p0[0]) * 100
                spr[(d.year, sym)][tau].append((p[1] - p[0]) * 100)
        e0 = bk.at(ms(d, 2, 55))
        if e0 is None or ms(d, 2, 55) > bk.ts[-1]:
            continue
        for tau in OFF:
            p = bk.at(ms(d, 2, 55, tau))
            if p:
                sc[tau][(sym, d)] = (e0[1] - p[1]) * 100


def sel(cells, y):
    return {k: v for k, v in cells.items() if k[1].year == y}


print("nguồn (năm, loại) -> số cặp-ngày:", dict(srcs))
for y in (2026, 2025):
    print(f"\n=== {y}: dời so với 00:55:00 / 02:55:00, pip mỗi cặp-ngày, + = sớm/muộn hơn lại lợi ===")
    print("tau(s)   n  bid(fix+tau)-bid(fix) t_day | n  đóng short t_day | tổng 3 việc (2xfix+đóng short) t_day | spread U/E/G")
    for tau in OFF:
        fx, cl = sel(fix[tau], y), sel(sc[tau], y)
        a = mt(list(per_day(fx).values()))
        b = mt(list(per_day(cl).values()))
        keys = set(fx) & set(cl)
        tot = {k: 2 * fx[k] + cl[k] for k in keys}
        c = mt(list(per_day(tot).values()))
        sp = " ".join(f"{np.mean(spr[(y, s)][tau]):.2f}" for s in PAIRS if spr[(y, s)][tau])
        print(f"{tau:+6.1f} {a[0]:3d} {a[1]:+7.2f} {a[2]:+5.1f} | {b[0]:3d} {b[1]:+7.2f} {b[2]:+5.1f} | {c[1]:+7.2f} {c[2]:+5.1f} | {sp}")

print("\n=== 2026, sớm 60 s so với bot có cùng độ trễ d ===")
fx60, cl60 = sel(fix[-60], 2026), sel(sc[-60], 2026)
keys = set(fx60) & set(cl60)
tot = {k: 2 * fx60[k] + cl60[k] for k in keys}
pd_ = per_day(tot)
vals = list(pd_.values())
print(f"n ngày {len(vals)}, TB {np.mean(vals):+.2f}p/cặp-ngày, t_day {mt(vals)[2]:+.2f}, CI95 {boot(vals)[0]:+.2f}..{boot(vals)[1]:+.2f}, "
      f"ngày > 0: {sum(v > 0 for v in vals)}/{len(vals)}")
for s in PAIRS:
    x = [v for k, v in tot.items() if k[0] == s]
    print(f"  {s}: {np.mean(x):+.2f}p (n {len(x)})")
print("  theo việc: đóng long " + f"{np.mean(list(fx60.values())):+.2f}p, mở short như vậy, đóng short {np.mean(list(cl60.values())):+.2f}p")
print("  theo tháng: " + " ".join(f"{m:02d}:{np.mean([v for d, v in pd_.items() if d.month == m]):+.1f}" for m in sorted({d.month for d in pd_})))
print("  từng ngày: " + " ".join(f"{d:%m-%d}:{v:+.1f}" for d, v in sorted(pd_.items())))
trim = sorted(vals)[2:-2]
print(f"  bỏ 2 ngày cao nhất + 2 thấp nhất: {np.mean(trim):+.2f}p; trung vị {np.median(vals):+.2f}p")
print("\nthay vì 60 s, sớm đúng bằng độ trễ (t = bid đã có sẵn lúc tau<0 so với fill muộn d giây):")
for early in (-0.2, -0.5, -1, -2):
    tau = early
    if tau not in fix:
        continue
    print(f"  sớm {abs(tau)} s: {mt(list(per_day(sel(fix[tau], 2026)).values()))[1]:+.2f}p mỗi chiều ở fix")
print("\nfill trễ d giây so với 00:55:00 (2026), chi phí mỗi chiều ở fix, âm = fill trễ làm bán thấp hơn:")
for tau in (0.2, 0.5, 1, 2, 3, 5, 10):
    a = mt(list(per_day(sel(fix[tau], 2026)).values()))
    print(f"  +{tau}s: {a[1]:+.2f}p t_day {a[2]:+.1f}")

# ---------------- B. m1 từng năm, có stop ----------------
D = pathlib.Path("research/data/m1")
gross = defaultdict(lambda: defaultdict(dict))  # variant -> leg -> {(sym,d): pips}
placebo = {}
for sym in PAIRS:
    z = np.load(D / f"{sym}.npz")
    t, h, l, c, ca = z["ts"], z["h"], z["l"], z["c"], z["ca"]
    hr = t // 3_600_000
    uh, ih = np.unique(hr, return_index=True)
    H = np.maximum.reduceat(h, ih)
    L = np.minimum.reduceat(l, ih)
    last = np.append(ih[1:], len(t)) - 1
    C = c[last]
    tr = np.maximum(H[1:] - L[1:], np.maximum(np.abs(H[1:] - C[:-1]), np.abs(L[1:] - C[:-1])))
    uh1 = uh[1:]

    def atr(T):
        k = int(np.searchsorted(uh1 + 1, T // 3_600_000, side="right"))
        return float(tr[k - 20:k].mean()) if k >= 20 else None

    def px(T, ask=False):
        i = int(np.searchsorted(t, T, side="left")) - 1
        if i < 0 or T - (t[i] + 60_000) > 300_000:
            return None
        return ca[i] if ask else c[i]

    def long_pnl(E, T):
        i = int(np.searchsorted(t, E, side="left"))
        if i >= len(t) or t[i] > T - 3_600_000 * 1.9:
            return None
        en = ca[i]
        a = atr(int(t[i]))
        if a is None:
            return None
        stop = en - 3 * a
        j = int(np.searchsorted(t, T - 60_000, side="right"))
        k = i + 1 + np.flatnonzero(l[i + 1:j] <= stop)[:1]
        if k.size:
            return (stop - en) * 100
        x = px(T)
        return None if x is None else (x - en) * 100

    def short_pnl(To, Tc):
        en = px(To)
        ex = px(Tc, True)
        a = atr(To)
        if en is None or ex is None or a is None:
            return None
        stop = en + 3 * a
        i, j = int(np.searchsorted(t, To, side="left")), int(np.searchsorted(t, Tc - 60_000, side="right"))
        if ((h[i:j] + (ca[i:j] - c[i:j])) >= stop).any():
            return (en - stop) * 100
        return (en - ex) * 100

    for d in gotobi_days(dt.date(2016, 1, 5), dt.date(2026, 9, 24)):
        if d in HOL:
            continue
        d0 = ms(d)
        for name, sh in (("bot", 0), ("som60", -60_000)):
            lp = long_pnl(d0 - 6 * 3_600_000 + sh, d0 + 55 * 60_000 + sh)
            sp = short_pnl(d0 + 55 * 60_000 + sh, d0 + 175 * 60_000 + sh)
            if lp is not None:
                gross[name]["long"][(sym, d)] = lp
            if sp is not None:
                gross[name]["short"][(sym, d)] = sp
    # placebo: ngày thường, không stop
    allg = set(gotobi_days(dt.date(2016, 1, 5), dt.date(2026, 9, 24)))
    d = dt.date(2016, 1, 5)
    pl = {}
    while d <= dt.date(2026, 9, 24):
        if d.weekday() < 5 and d not in allg and d not in HOL:
            d0 = ms(d)
            a, b, x, y = px(d0 + 54 * 60_000), px(d0 + 55 * 60_000), px(d0 + 174 * 60_000, True), px(d0 + 175 * 60_000, True)
            if None not in (a, b, x, y):
                pl[(sym, d)] = 2 * (a - b) * 100 + (y - x) * 100
        d += dt.timedelta(days=1)
    placebo[sym] = pl

print("\n=== m1 2016-09/2026, CÓ stop 3xATR, dời cả mở long; pip mỗi cặp-ngày (long+short gộp) ===")
print("năm   n   bot     sớm60   sớm60-bot  t_day  | long -bot  short -bot | placebo ngày thường")
all_pl = {k: v for s in PAIRS for k, v in placebo[s].items()}
rows = []
for y in range(2016, 2027):
    tot = {}
    parts = {}
    for leg in ("long", "short"):
        A, B = gross["bot"][leg], gross["som60"][leg]
        ks = [k for k in A if k in B and k[1].year == y]
        parts[leg] = np.mean([B[k] - A[k] for k in ks])
        for k in ks:
            tot.setdefault(k, [0.0, 0.0])
            tot[k][0] += A[k]
            tot[k][1] += B[k]
    dd = per_day({k: v[1] - v[0] for k, v in tot.items()})
    base = np.mean([v[0] for v in tot.values()])
    var = np.mean([v[1] for v in tot.values()])
    a = mt(list(dd.values()))
    pp = mt(list(per_day({k: v for k, v in all_pl.items() if k[1].year == y}).values()))
    rows.append(a[1])
    print(f"{y} {a[0]:3d} {base:+7.2f} {var:+7.2f} {var - base:+7.2f} {a[2]:+6.1f} | {parts['long']:+7.2f} {parts['short']:+7.2f} | {pp[1]:+6.2f} (t {pp[2]:+.1f})")
print(f"năm sớm60 hơn bot: {sum(r > 0 for r in rows)}/{len(rows)}")
d26 = defaultdict(float)
for leg in ("long", "short"):
    A, B = gross["bot"][leg], gross["som60"][leg]
    for k in A:
        if k in B and k[1].year == 2026:
            d26[k] += B[k] - A[k]
pd26 = per_day(d26)
print("2026 m1 có stop từng ngày: " + " ".join(f"{d:%m-%d}:{v:+.1f}" for d, v in sorted(pd26.items())))
v26 = sorted(pd26.values())
print(f"2026 m1 có stop bỏ ngày cao nhất: {mt(v26[:-1])}; CI95 {boot(list(pd26.values()))}")
for e, ys in (("2016-2025", range(2016, 2026)), ("2020-2026", range(2020, 2027))):
    tot = {}
    for leg in ("long", "short"):
        A, B = gross["bot"][leg], gross["som60"][leg]
        for k in A:
            if k in B and k[1].year in ys:
                tot[k] = tot.get(k, 0.0) + B[k] - A[k]
    a = mt(list(per_day(tot).values()))
    print(f"{e}: sớm60-bot {a[1]:+.2f}p/cặp-ngày, t_day {a[2]:+.2f}, n ngày {a[0]}")
