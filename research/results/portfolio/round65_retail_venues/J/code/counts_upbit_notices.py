"""Stream J: count Upbit notice titles by type, first_listed_at < 2025-01-01 KST-aware (titles only, no prices).

Reads stream W's cached list pages (read-only): research/data/upbit_notices/raw/list_all/p*.json.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

D = sys.argv[1]
CUT = datetime(2025, 1, 1, tzinfo=timezone.utc)

PATTERNS = {
    "KRW market addition": re.compile(r"KRW\s*마켓.*추가|원화\s*마켓.*추가|KRW.*디지털\s*자산\s*추가"),
    "BTC market addition": re.compile(r"BTC\s*마켓.*추가"),
    "USDT market addition": re.compile(r"USDT\s*마켓.*추가"),
    "airdrop / snapshot": re.compile(r"에어드랍|에어드롭|스냅샷|airdrop", re.I),
    "deposit/withdraw suspension": re.compile(r"입출금.*(일시\s*)?중단"),
    "warning designation": re.compile(r"유의\s*종목\s*지정"),
    "trading support end": re.compile(r"거래\s*지원\s*종료"),
    "network upgrade / hard fork": re.compile(r"하드\s*포크|업그레이드|메인넷"),
    "token swap": re.compile(r"스왑|전환"),
}


def main():
    seen = set()
    cnt = defaultdict(Counter)
    ex = defaultdict(list)
    for fn in sorted(os.listdir(D)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(D, fn), encoding="utf-8") as f:
            d = json.load(f)
        for n in d.get("data", {}).get("notices", []):
            if n["id"] in seen:
                continue
            seen.add(n["id"])
            t = datetime.fromisoformat(n["first_listed_at"]).astimezone(timezone.utc)
            if t >= CUT:
                continue
            title = n["title"]
            for k, p in PATTERNS.items():
                if p.search(title):
                    cnt[k][t.year] += 1
                    if len(ex[k]) < 4 and t.year in (2021, 2022, 2023, 2024):
                        ex[k].append(f"{t:%Y-%m-%d %H:%M}Z {title}")
    for k in PATTERNS:
        print(f"{k}: {dict(sorted(cnt[k].items()))}")
        for e in ex[k]:
            print("    ", e)


if __name__ == "__main__":
    main()
