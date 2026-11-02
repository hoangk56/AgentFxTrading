"""Summarise the probe bodies (shape only; every file is <= 2024-12). Run with python -I."""
import io
import json
import os
import sys
import zipfile

RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/scout_ib/raw"
CUT_MS = 1735689600000  # 2025-01-01 00:00 UTC
CUT_US = CUT_MS * 1000


def kline_zip(path):
    with zipfile.ZipFile(path) as z:
        name = z.namelist()[0]
        txt = z.read(name).decode().strip().splitlines()
    rows = [r.split(",") for r in txt if r and r[0].isdigit()]
    t = [int(r[0]) for r in rows]
    t = [x // 1000 if x > 1e14 else x for x in t]  # microsecond files -> ms
    assert max(t) < CUT_MS
    c = [float(r[4]) for r in rows]
    qv = [float(r[7]) for r in rows]
    n = [int(r[8]) for r in rows]
    return len(rows), min(t), max(t), min(c), max(c), sum(qv) / len(qv), sum(n) / len(n)


def main():
    bdv = os.path.join(RAW, "data.binance.vision")
    for f in sorted(os.listdir(bdv)):
        p = os.path.join(bdv, f)
        if f.endswith(".zip"):
            n, t0, t1, cmin, cmax, qv, nt = kline_zip(p)
            print(f"{f}: rows {n}, close min {cmin:.5f} max {cmax:.5f}, mean quote vol/day {qv:,.0f}, trades/day {nt:,.0f}")
        elif f.endswith(".head"):
            print(f, open(p).read().strip().replace("\n", "; "))
    cb = json.load(open(os.path.join(RAW, "api.exchange.coinbase.com", "cbeth_eth_2023.json")))
    ts = [r[0] for r in cb]
    assert max(ts) < CUT_MS / 1000
    closes = [r[4] for r in cb]
    print(f"CBETH-ETH daily: {len(cb)} candles, close min {min(closes):.5f} max {max(closes):.5f}, "
          f"mean volume {sum(r[5] for r in cb) / len(cb):,.0f} cbETH/day")
    h = json.load(open(os.path.join(RAW, "status.coinbase.com", "history_p16.json")))
    months = h.get("months", [])
    print("status history page 16 months:", [(m.get("name"), m.get("year"), len(m.get("incidents", []))) for m in months])
    kw = ("transfer", "trading", "available", "launch", "listing", "now live")
    hits = []
    for m in months:
        for inc in m.get("incidents", []):
            nm = inc.get("name", "")
            if any(k in nm.lower() for k in kw):
                hits.append((m.get("year"), m.get("name"), nm[:90], inc.get("timestamp", "")[:40] if isinstance(inc.get("timestamp"), str) else ""))
    print(f"listing-like incident titles: {len(hits)}")
    for x in hits[:12]:
        print("  ", x)
    if months and months[0].get("incidents"):
        print("incident keys:", sorted(months[0]["incidents"][0].keys()))


if __name__ == "__main__":
    sys.exit(main())
