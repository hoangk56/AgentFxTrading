"""End-to-end detection model for a keyless poller of t.me/s/<channel>: detection - N = true channel lag
+ preview delay (assumed 0: not observed live) + poll phase U(0, T) + HTTP response time (sampled from the probe).
True lag from whole-second stamps: L + u_post - u_N (u ~ U(0,1)), resampled until >= 0. Unmatched notices count as
misses. Env RT_FIXED=<s> replaces the probe response times. Usage: python -I e2e.py <probe.csv> <since YYYY-MM-DD> <channel> [...]"""
import os, sys, csv
import numpy as np
TG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(73)
probe, since, chs = sys.argv[1], sys.argv[2], sys.argv[3:]
rt = np.array([float(x["t_resp_s"]) for x in csv.DictReader(open(probe)) if x["status"] == "200"])
if os.environ.get("RT_FIXED"):  # sensitivity: a poller close to t.me's web servers
    rt = np.full(10, float(os.environ["RT_FIXED"]))
print(f"response time from probe: n {len(rt)} median {np.median(rt):.3f} s p90 {np.percentile(rt, 90):.3f} s")
for ch in chs:
    rows = [x for x in csv.DictReader(open(os.path.join(TG, f"lag_{ch}.csv"))) if x["N_utc"] >= since]
    L = np.array([float(x["lag"]) if x["lag"] != "" else np.nan for x in rows])
    out = []
    for T in (1.0, 1.1, 1.5, 2.0, 3.0):
        hits = []
        for _ in range(4000 // max(1, len(L) // 50)):
            ok = np.zeros(len(L), bool)
            for i, l in enumerate(L):
                if np.isnan(l):
                    continue
                while True:
                    tl = l + rng.random() - rng.random()
                    if tl >= 0:
                        break
                d = tl + rng.uniform(0, T) + rng.choice(rt)
                ok[i] = d <= 3.0
            hits.append(ok.mean())
        out.append(f"T={T:g}s: P(<=3 s) {np.mean(hits):.3f}")
    print(f"{ch} since {since}: n {len(L)}, matched {np.isfinite(L).sum()} | " + " | ".join(out))
