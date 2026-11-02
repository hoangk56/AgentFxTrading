"""CLWfeed posts carry 'Detected (UTC): <iso µs>': compare detection and Telegram post time with N for matched
Upbit KRW-listing notices. Usage: python -I clw_detect.py"""
import os, sys, re, csv, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import analyze
r = analyze.match("CLWfeed", True)
P = {p["id"]: p for p in analyze.posts("CLWfeed")}
N = {e["id"]: e["N"] for e in analyze.notices.load()}
det, post = [], []
for x in r["rows"]:
    if x["post"] == "":
        continue
    p = P[int(x["post"])]
    m = re.search(r"Detected \(UTC\):\s*([0-9T:\-.]+)Z", p["text"])
    d = dt.datetime.fromisoformat(m.group(1)).replace(tzinfo=dt.timezone.utc).timestamp() if m else None
    n = N[int(x["nid"])]
    det.append(d - n if d else np.nan); post.append(p["time"] - n)
    print(x["N_utc"], x["tickers"], "detect-N", round(d - n, 3) if d else None, "post-N", p["time"] - n,
          "post-detect", round(p["time"] - d, 3) if d else None)
det = np.array(det); det = det[~np.isnan(det)]
print("detect-N s: n", len(det), "median", np.median(det).round(3), "p80", np.percentile(det, 80).round(3),
      "p90", np.percentile(det, 90).round(3), "max", det.max().round(3))
