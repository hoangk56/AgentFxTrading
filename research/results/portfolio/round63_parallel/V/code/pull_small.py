"""Pull DVOL hourly (BTC, ETH) 2021-03..2024-12 and Binance USDT-M perp 1h klines (BTCUSDT, ETHUSDT) 2021-01..2024-12.
Every request ends <= 2024-12-31 23:59:59 UTC. Outputs CSV in research/data/deribit/."""
import json, os, fetch, numpy as np

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit"
END = 1735689599999
T0_DVOL = 1609459200000  # ask from 2021-01; series starts when it starts
T0_BIN = 1609459200000


def dvol(cur):
    rows, end = {}, END
    while True:
        u = (f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={cur}"
             f"&start_timestamp={T0_DVOL}&end_timestamp={end}&resolution=3600")
        r = json.loads(fetch.get(u, gap=0.5))["result"]
        for t, o, h, l, c in r["data"]:
            if t <= END:
                rows[t] = (o, h, l, c)
        c = r.get("continuation")
        if not r["data"] or c is None or c <= T0_DVOL:
            break
        end = c
    with open(f"{OUT}/dvol_{cur}_1h.csv", "w") as fh:
        fh.write("t,o,h,l,c\n")
        for t in sorted(rows):
            fh.write(f"{t},{','.join(str(x) for x in rows[t])}\n")
    print(cur, len(rows), min(rows), max(rows))


def kl(sym):
    os.makedirs(f"{OUT}/binance_1h", exist_ok=True)
    rows, s = [], T0_BIN
    while s < END:
        u = (f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1h&startTime={s}&endTime={END}&limit=1500")
        d = json.loads(fetch.get(u, gap=0.3))
        if not d:
            break
        rows += [r[:6] for r in d if r[0] <= END]
        s = d[-1][0] + 3600000
    with open(f"{OUT}/binance_1h/{sym}.csv", "w") as fh:
        fh.write("t,o,h,l,c,vol\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")
    print(sym, len(rows))


if __name__ == "__main__":
    for c in ("BTC", "ETH"):
        dvol(c)
    for s in ("BTCUSDT", "ETHUSDT"):
        kl(s)
