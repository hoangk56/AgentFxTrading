"""Stream O2 step 1: page through the keyless announcement lists.
OKX  GET /api/v5/support/announcements?annType=announcements-new-listings&page=k (20 / page, limit 5 req / 2 s)
Bybit GET /v5/announcements/index?locale=en-US&type=new_crypto&page=k&limit=20
Raw pages saved under research/data/okx_bybit_notice/raw/pages/ (pages also hold 2025-26 rows: they are only paged
through, never parsed into events; parse.py cuts at 2025-01-01)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

P = os.path.join(net.D, "raw", "pages")
os.makedirs(P, exist_ok=True)


def okx():
    k = 1; tot = None
    while tot is None or k <= tot:
        f = os.path.join(P, f"okx_nl_{k:03d}.json")
        if not os.path.exists(f):
            b, s = net.get(f"https://www.okx.com/api/v5/support/announcements?annType=announcements-new-listings&page={k}", "okx", gap=0.6)
            if b is None:
                print("okx stop", k, s); return
            open(f, "wb").write(b)
        js = json.load(open(f))
        tot = int(js["data"][0]["totalPage"]); k += 1
    print("okx pages", tot)


def bybit():
    k = 1; tot = None
    while tot is None or (k - 1) * 20 < tot:
        f = os.path.join(P, f"bybit_nc_{k:03d}.json")
        if not os.path.exists(f):
            b, s = net.get(f"https://api.bybit.com/v5/announcements/index?locale=en-US&type=new_crypto&page={k}&limit=20", "bybit", gap=0.6)
            if b is None:
                print("bybit stop", k, s); return
            open(f, "wb").write(b)
        js = json.load(open(f))
        tot = int(js["result"]["total"])
        if not js["result"]["list"]:
            break
        k += 1
    print("bybit pages", k - 1, "total", tot)


if __name__ == "__main__":
    okx(); bybit()
