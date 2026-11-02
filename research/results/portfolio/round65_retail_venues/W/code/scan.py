"""List (notice, ticker) pairs where the ticker appears in a candidate notice and has a Binance USDT-M perp alive at the
notice time (>= 7 d before, >= 1 d after). For manual review of event definitions; no prices are read."""
import os, re, json, glob, datetime as dt, sys
sys.path.insert(0, os.path.dirname(__file__))
import perps
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw"
SP = perps.span()
SKIP = {"KRW", "BTC", "USDT", "KST", "ERC", "ETH", "NFT", "API", "UBCI", "FAQ", "iOS", "DAPP", "DEX", "TVL", "OTP"}
out = []
for f in sorted(glob.glob(os.path.join(RAW, "detail", "*.json"))):
    d = json.load(open(f))["data"]
    t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
    if not ("2019-12" <= d["first_listed_at"][:7] <= "2024-12"):
        continue
    text = d["title"] + "\n" + d["body"]
    toks = set(re.findall(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,9})(?![A-Za-z0-9])", text)) - SKIP
    for k in sorted(toks):
        s = perps.perp_for(k, t, SP)
        if s:
            lines = [l.strip()[:110] for l in text.split("\n") if re.search(r"(?<![A-Za-z0-9])" + k + r"(?![A-Za-z0-9])", l)][:3]
            out.append((d["first_listed_at"][:16], d["id"], k, s, d["title"][:70], " | ".join(lines)))
for o in out:
    print("\t".join(map(str, o)))
