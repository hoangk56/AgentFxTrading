"""Stream WA: parse saved whale_alert_io pages (untrusted, data only) into classified events (HYPOTHESES_WA.md).
Posts with time >= 2025-01-01 are dropped right after parsing. Edited posts are dropped (counted).
Output research/data/whale_alert/events.csv: id, ts (UTC epoch s), era, kind (BI BO EI EO M B), coin, usd, src, dst.
Run with python -I."""
import csv, glob, os, re, sys, collections, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import parse

RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist/raw/whale_alert_io"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/whale_alert/events.csv"
H25 = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
I20 = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp()
V22 = dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp()
EX = ["binance", "coinbase", "kraken", "bitfinex", "bitstamp", "okex", "okx", "huobi", "htx", "gemini", "bittrex",
      "poloniex", "bithumb", "upbit", "kucoin", "bybit", "ftx", "gate", "cryptocom", "crypto.com", "bitmex", "deribit",
      "bitget", "mexc", "bitflyer", "coincheck", "bitso", "bitpanda", "liquid", "hitbtc"]
RX_T = re.compile(r"([\d,.]+)\s+#(\w+)\s+\(([\d,.]+)\s+USD\)\s+transferred from (.+?) to (.+?)\s*(?:\n|Details|$)")
RX_M = re.compile(r"([\d,.]+)\s+#(\w+)\s+\(([\d,.]+)\s+USD\)\s+(minted|burned) at (.+?)\s*(?:\n|Details|$)")


def is_ex(lbl):
    l = lbl.lower()
    return "custody" not in l and not l.startswith("unknown") and any(e in l for e in EX)


def is_unk(lbl):
    return lbl.lower().startswith("unknown")


def era(ts):
    return "pre" if ts < I20 else ("IS" if ts < V22 else "VAL")


def main():
    posts = {}
    for fn in glob.glob(os.path.join(RAW, "b*.html")):
        ps, _ = parse.parse(open(fn, "rb").read())
        for p in ps:
            if p["time"] is None or p["time"] >= H25:  # HOLD closed: drop at parse
                continue
            posts[p["id"]] = p
    st = collections.Counter(); rows = []
    for i in sorted(posts):
        p = posts[i]; st["posts_" + era(p["time"])] += 1
        if p["edited"]:
            st["edited"] += 1; continue
        tx = p["text"]
        m = RX_T.search(tx)
        if m:
            coin = m.group(2); usd = float(m.group(3).replace(",", "")); a, b = m.group(4).strip(), m.group(5).strip()
            if coin in ("BTC", "ETH"):
                c = "B" if coin == "BTC" else "E"
                if is_unk(a) and is_ex(b):
                    rows.append((i, p["time"], era(p["time"]), c + "I", coin, usd, a, b))
                elif is_ex(a) and is_unk(b):
                    rows.append((i, p["time"], era(p["time"]), c + "O", coin, usd, a, b))
                else:
                    st["flow_other_" + coin] += 1
            continue
        m = RX_M.search(tx)
        if m:
            coin = m.group(2); usd = float(m.group(3).replace(",", ""))
            if coin in ("USDT", "USDC"):
                rows.append((i, p["time"], era(p["time"]), "M" if m.group(4) == "minted" else "B", coin, usd, m.group(5).strip(), ""))
            continue
        st["unparsed"] += 1
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "ts", "era", "kind", "coin", "usd", "src", "dst"]); w.writerows(rows)
    c = collections.Counter((r[2], r[3]) for r in rows)
    c100 = collections.Counter((r[2], r[3]) for r in rows if r[5] >= 1e8)
    print(dict(st))
    for k in sorted(c):
        print(k, c[k], ">=100M", c100[k])


if __name__ == "__main__":
    main()
