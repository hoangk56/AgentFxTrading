import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas/raw/okx"
for fam, b, e in [("BTC-USDT", 1609459200000, 1633046399000), ("BTC-USDT", 1672531200000, 1696118399000),
                  ("BTC-USDT", 1704067200000, 1727740799000), ("BTC-USD", 1609459200000, 1633046399000)]:
    u = ("https://www.okx.com/api/v5/public/market-data-history?module=3&instType=SWAP&instFamilyList=%s"
         "&dateAggrType=monthly&begin=%d&end=%d" % (fam, b, e))
    d = get(u, gap=0.6, tries=2)
    open(os.path.join(R, "probe_mdh_%s_%d.json" % (fam, b)), "wb").write(d)
    j = json.loads(d)
    for x in j["data"]:
        for det in x["details"]:
            for g in det["groupDetails"]:
                print(fam, g["filename"], g["sizeMB"], g["url"])
        if not x["details"]:
            print(fam, b, "empty")
