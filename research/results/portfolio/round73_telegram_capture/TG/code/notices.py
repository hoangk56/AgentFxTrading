"""Upbit KRW-listing notices from the read-only cache research/data/upbit_notices/raw/list_all/p*.json, using A2's
title filter (fwd_a2.build_events): category 거래, a listing keyword, KRW / 원화, not 종료, not 유의.
N = first_listed_at (seconds). Tickers = upper-case codes in parentheses of the title."""
import glob, json, re, datetime as dt, warnings
warnings.filterwarnings('ignore')
SRC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw/list_all/p*.json"
KEYS = ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")


def load():
    rows = {}
    for f in sorted(glob.glob(SRC)):
        for n in json.load(open(f))["data"]["notices"]:
            rows[n["id"]] = n
    out = []
    for i, n in rows.items():
        t = n["title"]
        if n["category"] == "거래" and any(k in t for k in KEYS) and ("KRW" in t or "원화" in t) \
                and "종료" not in t and "유의" not in t:
            N = dt.datetime.fromisoformat(n["first_listed_at"]).timestamp()
            tick = []
            for grp in re.findall(r"\(([^()]*)\)", t):
                for x in re.split(r"[,\s]+", grp):
                    x = x.strip().split("/")[0]
                    if re.fullmatch(r"[A-Z0-9]{1,12}", x) and x not in ("KRW", "BTC", "USDT", "ETH") and x not in tick:
                        tick.append(x)
            out.append(dict(id=i, title=t, N=N, tickers=tick, listed=n["listed_at"]))
    out.sort(key=lambda r: r["N"])
    return out


if __name__ == "__main__":
    E = load()
    print(len(E), "KRW-listing notices", dt.datetime.utcfromtimestamp(E[0]["N"]), dt.datetime.utcfromtimestamp(E[-1]["N"]))
    for e in E[-12:]:
        print(e["id"], dt.datetime.utcfromtimestamp(e["N"]).isoformat(), e["tickers"], e["title"][:70])
    print("no ticker:", sum(1 for e in E if not e["tickers"]))
    for e in [e for e in E if not e["tickers"]][-8:]:
        print("  ", e["id"], e["title"][:90])
    import collections
    print(collections.Counter(dt.datetime.utcfromtimestamp(e["N"]).year for e in E))
