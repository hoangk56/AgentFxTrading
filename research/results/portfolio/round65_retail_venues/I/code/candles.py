"""Parse each venue's candle body into (t_ms, o, h, l, c, v) rows, sorted, cut at ts < 2025-01-01."""
import json, sys, datetime as dt
CUT = 1735689600000


def parse(venue, path):
    d = json.load(open(path))
    rows = []
    if venue in ("bitkub", "btcturk"):
        if d.get("s") != "ok":
            return []
        rows = [(int(t) * 1000, float(o), float(h), float(l), float(c), float(v)) for t, o, h, l, c, v in
                zip(d["t"], d["o"], d["h"], d["l"], d["c"], d["v"])]
    elif venue == "coinone":
        rows = [(int(x["timestamp"]), float(x["open"]), float(x["high"]), float(x["low"]), float(x["close"]),
                 float(x["target_volume"])) for x in d.get("chart", [])]
    elif venue == "bitbank":
        for blk in d.get("data", {}).get("candlestick", []):
            rows += [(int(x[5]), float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4])) for x in blk["ohlcv"]]
    elif venue == "coindcx":
        rows = [(int(x["time"]), x["open"], x["high"], x["low"], x["close"], x["volume"]) for x in d] if isinstance(d, list) else []
    elif venue == "bitvavo":
        rows = [(int(x[0]), *map(float, x[1:6])) for x in d] if isinstance(d, list) else []
    elif venue == "indodax":
        rows = [(int(x["Time"]) * 1000, float(x["Open"]), float(x["High"]), float(x["Low"]), float(x["Close"]),
                 float(x["Volume"])) for x in d] if isinstance(d, list) else []
    rows = sorted(r for r in rows if r[0] < CUT)
    return rows


def fmt(t):
    return dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    v, p = sys.argv[1], sys.argv[2]
    r = parse(v, p)
    if not r:
        print(v, p.split("/")[-1], "no rows"); sys.exit()
    print(v, p.split("/")[-1], "n", len(r), "first", fmt(r[0][0]), "last", fmt(r[-1][0]), "first row", r[0][1:5])
