"""Map DefiLlama emissions protocols (index snapshot) to Binance USDT-M perp symbols. No prices read."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "round60_new_listings", "code"))
from listings import base_of  # noqa
TU = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "token_unlocks")
PERP = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "binance", "perp_1d")
idx = json.load(open(os.path.join(TU, "raw", "emissionsIndex_ds.json")))["data"]
perps = {}
for f in sorted(os.listdir(PERP)):
    if f.endswith("USDT.csv"):
        s = f[:-4]
        perps.setdefault(base_of(s), []).append(s)
rows = []
for x in idx:
    if not x.get("unlockEvents"):
        continue
    tp = x.get("tokenPrice") or []
    sym = (tp[0].get("symbol") if tp else "") or ""
    sym = sym.upper()
    m = perps.get(sym, [])
    rows.append((x.get("protocolSlug") or x.get("name"), sym, x.get("gecko_id") or "", "|".join(m)))
json.dump(rows, open(os.path.join(TU, "protocol_map.json"), "w"), indent=0)
print(len(rows), "with events;", sum(1 for r in rows if r[3]), "mapped to a perp")
for r in rows:
    if r[3]:
        print(r)
