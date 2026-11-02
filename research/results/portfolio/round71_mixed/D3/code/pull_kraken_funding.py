"""Kraken Futures hourly/4h funding history. The endpoint returns the full history incl. 2025-26: rows with
timestamp >= 2025-01-01 are dropped in memory; the raw body is never written to disk."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas/kraken"
os.makedirs(OUT, exist_ok=True)
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
for sym in ["PI_XBTUSD", "PI_ETHUSD", "PF_XBTUSD", "PF_ETHUSD"]:
    b = get("https://futures.kraken.com/derivatives/api/v3/historical-funding-rates?symbol=" + sym, gap=1.0, tries=3)
    j = json.loads(b)
    rows = []
    for r in j.get("rates", []):
        t = dt.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
        if t < CUT:
            rows.append((int(t.timestamp() * 1000), r["fundingRate"], r["relativeFundingRate"]))
    del j, b
    with open(os.path.join(OUT, sym + "_funding.csv"), "w") as f:
        f.write("t,abs_rate,rel_rate\n")
        for x in rows:
            f.write("%d,%r,%r\n" % x)
    print(sym, len(rows), rows[0][0] if rows else None, rows[-1][0] if rows else None)
