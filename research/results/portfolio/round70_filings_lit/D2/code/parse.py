"""Parse raw Deribit bodies to CSV (python -I). Cuts every row at ts < 2025-01-01."""
import os, json, glob, sys

ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit_funding"
HOLD = os.environ.get("D2_HOLD") == "1"  # coordinator only, after registration
CUT = 1793318400000 if HOLD else 1735689600000
RAW, SUF = ("raw_hold", "hold_") if HOLD else ("raw", "")


def funding(inst):
    rows = {}
    for p in sorted(glob.glob(os.path.join(ROOT, RAW, "funding", inst, "*.json"))):
        try:
            res = json.load(open(p)).get("result") or []
        except Exception:
            continue
        for r in res:
            t = int(r["timestamp"])
            if t < CUT:
                rows[t] = (r["index_price"], r["interest_1h"], r["interest_8h"])
    with open(os.path.join(ROOT, f"funding_{SUF}{inst}.csv"), "w") as f:
        f.write("t,index,i1h,i8h\n")
        for t in sorted(rows):
            f.write("%d,%r,%r,%r\n" % ((t,) + rows[t]))
    return len(rows)


def chart(inst):
    rows = {}
    for p in sorted(glob.glob(os.path.join(ROOT, RAW, "chart", inst, "*.json"))):
        try:
            res = json.load(open(p)).get("result") or {}
        except Exception:
            continue
        if res.get("status") != "ok":
            continue
        for k, t in enumerate(res["ticks"]):
            if t < CUT:
                rows[int(t)] = (res["open"][k], res["high"][k], res["low"][k], res["close"][k], res["volume"][k])
    with open(os.path.join(ROOT, f"chart1h_{SUF}{inst}.csv"), "w") as f:
        f.write("t,o,h,l,c,vol\n")
        for t in sorted(rows):
            f.write("%d,%r,%r,%r,%r,%r\n" % ((t,) + rows[t]))
    return len(rows)


if __name__ == "__main__":
    for inst in ("BTC-PERPETUAL", "ETH-PERPETUAL", "BTC_USDC-PERPETUAL", "ETH_USDC-PERPETUAL"):
        print(inst, "funding rows", funding(inst), "chart rows", chart(inst))
