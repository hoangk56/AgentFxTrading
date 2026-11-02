"""Per-channel lag table over fixed windows, from TG/lag_<channel>.csv (written by analyze.py).
Also extracts sub-second detection stamps printed in posts (CLWfeed 'Detected (UTC): ...Z', coin_listing 'HH:MM:SS.mmm').
Usage: python -I summary.py"""
import os, sys, re, csv, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import analyze
TG = analyze.OUT
START = {"upbit_news": "2025-08-20"}  # 'Channel created' 2025-05-02, first real post 2025-08-20 (public launch 08-22)
CH = [c for c in ("upbit_news", "newlistingsfeed", "coin_listing", "CLWfeed", "BWEnews") if os.path.exists(os.path.join(TG, f"lag_{c}.csv"))]


def row(ch, lo, hi="9999"):
    r = [x for x in csv.DictReader(open(os.path.join(TG, f"lag_{ch}.csv"))) if lo <= x["N_utc"] < hi]
    if not r:
        return None
    L = np.array([float(x["lag"]) for x in r if x["lag"] != ""]); n = len(r); pos = L[L >= 0]
    q = lambda p: np.percentile(pos, p) if len(pos) else np.nan
    return n, len(L), q(50), q(80), q(90), (pos <= 2).sum() / n, (pos <= 3).sum() / n, int((L < 0).sum()), int((L > 60).sum())


print("| channel | window (N, UTC) | notices | matched | median s | p80 s | p90 s | <=2 s | <=3 s | before N | >60 s |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for ch in CH:
    first = min(x["N_utc"] for x in csv.DictReader(open(os.path.join(TG, f"lag_{ch}.csv"))))
    for lo, lab in ((START.get(ch, first[:10]), "channel start"), ("2025-08-20", "since 2025-08-20"),
                    ("2026-01-01", "2026"), ("2026-06-16", "since 2026-06-16")):
        s = row(ch, lo)
        if s:
            n, m, md, p8, p9, l2, l3, b, o = s
            print(f"| {ch} | {lab} ({lo}..) | {n} | {m} ({m / n:.0%}) | {md:.0f} | {p8:.0f} | {p9:.1f} | {l2:.0%} | {l3:.0%} | {b} | {o} |")

# sub-second detection stamps
N = {e["id"]: e["N"] for e in analyze.notices.load()}
for ch, pat in (("CLWfeed", r"Detected \(UTC\):\s*(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)Z"), ("coin_listing", r"(?m)^(\d\d:\d\d:\d\d\.\d{3})\s*$")):
    P = {p["id"]: p for p in analyze.posts(ch)}
    dn, pd = [], []
    for x in csv.DictReader(open(os.path.join(TG, f"lag_{ch}.csv"))):
        if x["post"] == "":
            continue
        p = P[int(x["post"])]; m = re.search(pat, p["text"])
        if not m:
            continue
        s = m.group(1)
        if "T" in s:
            d = dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp()
        else:
            day = dt.datetime.fromtimestamp(p["time"], dt.timezone.utc).date().isoformat()
            d = dt.datetime.fromisoformat(f"{day}T{s}").replace(tzinfo=dt.timezone.utc).timestamp()
            if d > p["time"] + 1:
                d -= 86400
        dn.append(d - N[int(x["nid"])]); pd.append(p["time"] - d)
    if dn:
        dn, pd = np.array(dn), np.array(pd)
        print(f"{ch}: {len(dn)} matched posts with a sub-second detection stamp; detect - N: median {np.median(dn):.3f} "
              f"p80 {np.percentile(dn, 80):.3f} p90 {np.percentile(dn, 90):.3f} min {dn.min():.3f} max {dn.max():.3f} s; "
              f"Telegram stamp - detect: median {np.median(pd):.3f} p90 {np.percentile(pd, 90):.3f} s")
