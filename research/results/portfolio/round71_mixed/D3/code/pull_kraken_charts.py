"""Kraken Futures charts: 1h mark and spot (index) candles for PI_XBTUSD / PI_ETHUSD, 2021-01..2024-12 (cut < 2025)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas/kraken"
os.makedirs(OUT, exist_ok=True)
CUT = 1735689600
for sym in ["PI_XBTUSD", "PI_ETHUSD"]:
    for tt in ["mark", "spot"]:
        rows = {}
        t0 = 1609459200
        while t0 < CUT:
            t1 = min(t0 + 28 * 86400, CUT - 3600)
            d = json.loads(get("https://futures.kraken.com/api/charts/v1/%s/%s/1h?from=%d&to=%d" % (tt, sym, t0, t1),
                               gap=0.6, tries=4))
            for c in d.get("candles", []):
                t = int(c["time"])
                if t < CUT * 1000:
                    rows[t] = (c["open"], c["high"], c["low"], c["close"])
            t0 = t1 + 3600
        with open(os.path.join(OUT, "%s_%s_1h.csv" % (sym, tt)), "w") as f:
            f.write("t,o,h,l,c\n")
            for t in sorted(rows):
                f.write("%d,%s\n" % (t, ",".join(rows[t])))
        print(sym, tt, len(rows), min(rows) if rows else None, flush=True)
