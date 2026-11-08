"""L2 (reading only, IS): Binance spot aggTrades of the coin's USDT (else BUSD, else BTC) pair around the perp-launch
post N and the perp's first trade P (P from round 66 N0's local launch files: only the T0 field, no perp prices).
Spot must have a daily file >= 7 d before N. Writes l2_events.json. Run with python -I."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net, pull
from pull_l1 import first_day_on_or_after, SPOT, day, H48
D = net.D
AGG = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/perp_launch/agg"


def perp_T0():
    out = {}
    for f in os.listdir(AGG):
        if f.endswith(".npz"):
            z = np.load(os.path.join(AGG, f)); out[f.rsplit("_", 1)[0]] = int(z["T0"])
    return out


def main():
    ev = json.load(open(os.path.join(D, "l2_titles.json")))
    T0 = perp_T0(); out = []
    for e in ev:
        N = e["t"] * 1000
        coin = e["coin"]; base = coin[4:] if coin.startswith("1000") else coin
        perp = coin + "USDT"
        pair = next((base + q for q in ("USDT", "BUSD", "BTC") if base + q in SPOT), None)
        if pair is None:
            print(day(N), coin, "no spot pair"); continue
        fd = first_day_on_or_after(pair, "2017-01-01")
        if fd is None or fd > day(N, -7):
            print(day(N), coin, pair, "spot too young / none", fd); continue
        P = T0.get(perp)
        if P is not None and not (N < P <= N + H48):
            P = None
        win = [(N - 3900000, N + 3900000)]; days = {day(N - 3900000), day(N), day(N + 3900000)}
        if P:
            win.append((P - 120000, P + 120000)); days |= {day(P - 120000), day(P + 120000)}
        days = sorted(d for d in days if d < "2025-01-01")
        for d in days:
            pull.get("bspot", pair, d, win)
        out.append(dict(id=e["id"], N=N, coin=coin, edited=e["edited"], src="bspot", sym=pair, X=P,
                        era="IS" if N < 1640995200000 else "VAL", year=int(day(N)[:4]), day=day(N), days=days,
                        title=e["title"]))
        print(day(N), coin, pair, "P-N min", None if P is None else round((P - N) / 60000, 1), flush=True)
    json.dump(out, open(os.path.join(D, "l2_events.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
