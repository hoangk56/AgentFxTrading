"""Candidate list: Bybit USDT linear perpetuals (trading + closed) launched before 2024-11-01 and alive after
2020-01-01, mapped to spot X/USDT. Writes <root>/cands.csv (perp,spot,fac,launch,delivery)."""
import json, os, re, sys
root = sys.argv[1]
STABLE = {"USDC", "BUSD", "TUSD", "USDP", "FDUSD", "DAI", "EUR", "GBP", "AEUR", "USDE", "PAXG", "XAUT", "BTCDOM", "USTC",
          "BTC", "ETH", "USDD", "PYUSD", "BRL"}
def spot_of(base):
    m = re.match(r"^(10+)([A-Z].*)$", base)
    if m:
        return m.group(2), float(m.group(1))
    m = re.match(r"^([A-Z0-9]*[A-Z])(10+)$", base)
    if m and m.group(1) not in ("",):
        return m.group(1), float(m.group(2))
    return base, 1.0
rows = []
seen = set()
for name in ("instruments_linear.json", "instruments_linear_closed.json"):
    for x in json.load(open(os.path.join(root, name))):
        if x.get("contractType") != "LinearPerpetual" or x.get("settleCoin") != "USDT" or x.get("quoteCoin") != "USDT":
            continue
        s = x["symbol"]
        if not s.endswith("USDT") or s in seen:
            continue
        lt, dt = int(x.get("launchTime") or 0), int(x.get("deliveryTime") or 0)
        if lt >= 1730419200000 or (dt and dt < 1577836800000 + 60 * 86400000):
            continue
        b, fac = spot_of(x["baseCoin"])
        if b in STABLE or x["baseCoin"] in STABLE:
            continue
        seen.add(s)
        rows.append((s, b + "USDT", fac, lt, dt))
with open(os.path.join(root, "cands.csv"), "w") as f:
    f.write("perp,spot,fac,launch,delivery\n")
    for r in sorted(rows):
        f.write(",".join(str(v) if not isinstance(v, float) else f"{v:g}" for v in r) + "\n")
spot_now = {x["symbol"] for x in json.load(open(os.path.join(root, "instruments_spot.json")))}
print("cands", len(rows), "closed", sum(1 for r in rows if r[4]), "spot pair listed today", sum(r[1] in spot_now for r in rows))
print([r[:3] for r in rows if r[2] != 1.0])
