"""Stream J: Upbit notice-based event lists (titles only, < 2025), matched to Binance perps that existed >= 7 days
before the notice. No prices are read.

Event types:
  krw  - KRW market additions (incl. '신규 거래지원' with KRW), compared with stream K's k2_events.csv (survivor list)
  btc  - BTC / USDT market additions without KRW in the same title
  air  - airdrop support notices for holders (지원 / 스냅샷), excluding payment-only notices (지급)
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

LIST_DIR, PERP_DIR, K2 = sys.argv[1], sys.argv[2], sys.argv[3]
CUT = datetime(2025, 1, 1, tzinfo=timezone.utc)
WEEK = 7 * 86400


def perp_first():
    out = {}
    for fn in os.listdir(PERP_DIR):
        if not fn.endswith("USDT.csv"):
            continue
        with open(os.path.join(PERP_DIR, fn)) as f:
            r = csv.reader(f)
            next(r)
            row = next(r, None)
        if row:
            base = fn[:-8]
            for pre in ("1000000", "10000", "1000", "1M"):
                if base.startswith(pre) and len(base) > len(pre) + 1:
                    base = base[len(pre):]
                    break
            t = int(row[0]) / 1000
            out[base] = min(t, out.get(base, t))
    return out


TICK = re.compile(r"\(([A-Z0-9]{2,12})(?:,\s*[^)]*)?\)")
LISTTICK = re.compile(r"\(([A-Z0-9]{2,12}(?:\s*,\s*[A-Z0-9]{2,12})+)\)")


def tickers(title):
    m = LISTTICK.search(title)
    if m:
        return [x.strip() for x in m.group(1).split(",")]
    return [m.group(1) for m in TICK.finditer(title) if m.group(1) not in ("KRW", "BTC", "USDT", "NFT")]


def main():
    pf = perp_first()
    k2 = set()
    with open(K2) as f:
        for row in csv.DictReader(f):
            k2.add(row["coin"])
    notices = {}
    for fn in sorted(os.listdir(LIST_DIR)):
        if fn.endswith(".json"):
            with open(os.path.join(LIST_DIR, fn), encoding="utf-8") as f:
                for n in json.load(f)["data"]["notices"]:
                    notices[n["id"]] = n
    ev = defaultdict(list)
    for n in notices.values():
        t = datetime.fromisoformat(n["first_listed_at"]).astimezone(timezone.utc)
        if t >= CUT or t.year < 2020:
            continue
        title = n["title"]
        add = ("추가" in title or "신규 거래지원" in title) and "마켓" in title and "연장" not in title
        if add and "KRW" in title:
            typ = "krw"
        elif add and ("BTC" in title or "USDT" in title):
            typ = "btc"
        elif re.search(r"에어드[랍롭]", title) and re.search(r"지원|스냅샷", title) and "지급" not in title:
            typ = "air"
        else:
            continue
        for c in tickers(title):
            if c in pf and pf[c] <= t.timestamp() - WEEK:
                ev[typ].append((t, c, title))
    for typ in ("krw", "btc", "air"):
        rows = sorted(ev[typ])
        by = Counter(r[0].year for r in rows)
        print(f"{typ}: {len(rows)} coin-events with a Binance perp >= 7 d old, by year {dict(sorted(by.items()))}")
        if typ == "krw":
            notk2 = [r for r in rows if r[1] not in k2]
            print(f"   not in K2's survivor list: {len(notk2)}:", ", ".join(f"{r[1]} {r[0]:%Y-%m}" for r in notk2))
        for r in rows[:: max(1, len(rows) // 6)][:6]:
            print(f"   {r[0]:%Y-%m-%d %H:%M}Z {r[1]}: {r[2]}")


if __name__ == "__main__":
    main()
