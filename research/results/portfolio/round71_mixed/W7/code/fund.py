"""Stream W7: funding stamps of each reference perp over [listing day, listing day + 3 d), endTime <= 2024-12-31 23:59:59.
Binance fapi /fapi/v1/fundingRate and Bybit v5 /v5/market/funding/history (public, keyless). Saved to
research/data/listing_window/funding/{bn,by}_<SYM>.csv (t,rate). Run with python -I."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
F = os.path.join(D, "funding"); os.makedirs(F, exist_ok=True)
END = 1735689600000 - 1
rows = list(csv.DictReader(open(os.path.join(D, "meta", "pull_list.csv"))))
for e in rows:
    d0 = int(np.datetime64(e["L_day"], "ms").astype(np.int64)); d1 = min(d0 + 3 * 86400000, END)
    for leg, sym in (("bn", e["bn_perp"]), ("by", e["by_perp"])):
        if not sym:
            continue
        p = os.path.join(F, f"{leg}_{sym}.csv")
        have = {}
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                have[int(r["t"])] = r["rate"]
        if leg == "bn":
            url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={d0}&endTime={d1}&limit=1000"
        else:
            url = (f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={sym}"
                   f"&startTime={d0}&endTime={d1}&limit=200")
        b, s = net.get(url, "funding")
        if b is None:
            print("MISS", leg, sym, s); continue
        j = json.loads(b)
        if leg == "bn":
            for x in j:
                if int(x["fundingTime"]) < END:
                    have[int(x["fundingTime"])] = x["fundingRate"]
        else:
            if j.get("retCode") != 0:
                print("RET", sym, j.get("retCode"), j.get("retMsg")); continue
            for x in j["result"]["list"]:
                if int(x["fundingRateTimestamp"]) < END:
                    have[int(x["fundingRateTimestamp"])] = x["fundingRate"]
        with open(p, "w") as f:
            f.write("t,rate\n")
            for t in sorted(have):
                f.write(f"{t},{have[t]}\n")
        print(leg, sym, e["L_day"], len(have), flush=True)
