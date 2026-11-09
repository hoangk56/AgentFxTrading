"""Stream CL events: listing posts for Bithumb (KRW), Coinbase (announcement / retail-live), Robinhood and other venues
from @coin_listing (2017-10..) and @newlistingsfeed (2024-03..), timed by the Telegram post stamp T.
Every post is cut at T < 2025-01-01 right after parsing (load.posts). hold_counts() counts 2025-01..2026-10-29 titles
by class only (no times, coins or prices kept or printed).
Classes (regexes declared in HYPOTHESES_CL.md):
  BH   Bithumb KRW listing (notice relays "will list" / "listing/airdrop event ... (상장 예정|추가 예정)", market posts
       "X/KRW listed on Bithumb", newlistingsfeed "$X listed on Bithumb spot", [BITHUMB] "$X listed on Bithumb");
       BTC-market-only notices dropped.
  CBA  Coinbase first announcement ("Coinbase Pro will list", "is launching on Coinbase Pro", roadmap additions,
       "Coinbase will add support for", newlistingsfeed "added to Coinbase roadmap", stated-time "listed on Coinbase
       spot: <date> at <time> UTC").
  CBL  Coinbase retail go-live ("is now available on Coinbase", "now live on coinbase.com", "trades are live",
       newlistingsfeed "listed on Coinbase( spot)" / "added to Coinbase spot" without a stated future time).
  RH   Robinhood ("Robinhood Listed", "listed on Robinhood").
  OTH  Huobi "will list", Kraken listing, KuCoin listing posts (pooled).
Coinbase International futures, custody, staking, airdrop-only and Bithumb Global posts are not events.
Event = first post of (class, coin) with no post of the same (class, coin) in the 180 days before; the coin's Binance
USDT-M perp must have traded from <= T - 7 d through T + 1 d (round 65 A's perps.perp_for)."""
import csv, os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/code")
import load

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/CL"
IS0, VAL0, CUT = 1577836800, 1640995200, 1735689600
SKIP = {"BTC", "KRW", "USDT", "USD", "ETH", "BNB", "EUR", "GBP", "USDC", "DAI", "UST", "GUSD", "EUROC", "EURC", "PAX",
        "BUSD", "TUSD", "WBTC", "WLUNA", "TBTC", "WCFG", "MSOL", "LSETH", "CBETH", "QCAD", "GYEN", "MUSD", "PYUSD",
        "DAO", "NFT", "ERC", "SPL", "API", "UTC", "PT", "ET", "AM", "PM", "IOS", "THE", "AND", "NONE", "X", "ID"}

R_CB_INTL = re.compile(r"Coinbase International", re.I)
R_CB_NOISE = re.compile(r"Custody|Staking|staking|article|Coinbase Pro API|BTCAUCTION|Auction|offline|REMINDER|"
                        r"Experimental label here|Learn more", re.I)
R_CBA = re.compile(r"Coinbase Pro will list|launching on Coinbase Pro|Coinbase lists|Coinbase will list: ACH|"
                   r"Coinbase Pro will List|added to the roadmap|added to Coinbase roadmap|Coinbase Roadmap|"
                   r"Coinbase will add support for|listed on Coinbase spot: \w+ \d+ at", re.I)
R_CBL = re.compile(r"is now available on Coinbase|are now available on Coinbase|are are now available on Coinbase|"
                   r"now live on https|trades are live|listed on Coinbase spot$|listed on Coinbase$|"
                   r"added to Coinbase spot", re.I)
R_BH_NOTICE = re.compile(r"Bithumb will list|Bithumb listing/airdrop event")
R_BH_LISTWORD = re.compile(r"상장 예정|추가 예정|신규 상장|원화 마켓|to be listed|new listing", re.I)
R_BH_MARKET = re.compile(r"^([A-Z0-9]+)/KRW listed on Bithumb$")
R_BH_NLF = re.compile(r"listed on Bithumb spot|\] \$\S+ listed on Bithumb$")
R_RH = re.compile(r"Robinhood Listed|listed on Robinhood", re.I)
R_OTH = re.compile(r"Huobi will list|Kraken listing|Kucoin will list|KuCoin will list|Kucoin listing|KuCoin listing")


def tickers(text, head):
    s = set(re.findall(r"\$([A-Z0-9]{2,12})\b", head)) | set(re.findall(r"#([A-Z0-9]{2,12})\b", head))
    s |= set(re.findall(r"\(+([A-Z0-9]{2,12})\)+", head))
    if not s:
        s = set(re.findall(r"\(([A-Z0-9]{2,12})\)", text))
    if not s:  # "Coinbase will add support for METIS, MONA, MEDIA, and AST with ..."
        m = re.search(r"will add support for (.+?) (with|on) ", text)
        if m:
            s = set(re.findall(r"\b([A-Z0-9]{2,10})\b", m.group(1)))
    return sorted(x for x in s if x not in SKIP and not x.isdigit())


def classify(text):
    """-> (class, [tickers]) or None. Header = first line (plus the second for coin_listing article relays)."""
    lines = text.strip().split("\n")
    head = lines[0].strip()
    if R_CB_INTL.search(text):
        return None
    if R_BH_NOTICE.search(head) and "Global" not in head:
        if not R_BH_LISTWORD.search(text):
            return None  # airdrop / trading events of coins already listed
        if re.search(r"BTC 마켓", text) and not re.search(r"원화|KRW", text):
            return None  # BTC-market-only listing
        return "BH", tickers(text, head)
    m = R_BH_MARKET.match(head)
    if m:
        return "BH", [m.group(1)]
    if R_BH_NLF.search(head) and "Global" not in head:
        return "BH", tickers(text, head)
    if "Coinbase" in text or "coinbase" in text:
        if R_CB_NOISE.search(head) and not R_CBA.search(head):
            return None
        if R_CBA.search(text.split("\n")[0]) or (R_CBA.search(text) and "Coinbase tweet" in head):
            return "CBA", tickers(text, head)
        if R_CBL.search(head) or R_CBL.search(text[:300]):
            return "CBL", tickers(text, head)
        return None
    if R_RH.search(head):
        return "RH", tickers(text, head)
    if R_OTH.search(head):
        return "OTH", tickers(text, head)
    return None


def raw_events(posts_fn=load.posts):
    rows = []
    for ch in ("coin_listing", "newlistingsfeed"):
        for p in posts_fn(ch):
            c = classify(p["text"])
            if not c or not c[1]:
                continue
            for tk in c[1]:
                rows.append(dict(ch=ch, pid=p["id"], T=int(p["time"]), cls=c[0], coin=tk, edited=p["edited"],
                                 head=p["text"].split("\n")[0][:120]))
    rows.sort(key=lambda r: (r["T"], r["ch"], r["pid"]))
    return rows


def first_posts(rows):
    last = {}; out = []
    for r in rows:
        k = (r["cls"], r["coin"])
        if k not in last or r["T"] - last[k] > 180 * 86400:
            out.append(dict(r))
        last[k] = r["T"]
    return out


def build():
    import perps
    spans = perps.span()
    ev = []
    for r in first_posts(raw_events()):
        if r["T"] < IS0 or r["T"] >= CUT:
            continue
        sym = perps.perp_for(r["coin"], r["T"] * 1000, spans)
        r["perp"] = sym or ""
        r["era"] = "IS" if r["T"] < VAL0 else "VAL"
        u = dt.datetime.fromtimestamp(r["T"], dt.timezone.utc)
        r["year"], r["day"] = u.year, u.strftime("%Y-%m-%d")
        ev.append(r)
    return ev


def hold_counts():
    """Counts of first posts per class in 2025-01-01..2026-10-29 (titles only; no perp check, nothing else kept)."""
    rows = []
    for ch in ("coin_listing", "newlistingsfeed"):
        for i, (text, ed) in enumerate(load.hold_titles(ch)):
            c = classify(text)
            if c and c[1]:
                for tk in c[1]:
                    rows.append((c[0], tk))
    from collections import Counter
    return Counter(k for k, _ in set(rows))  # distinct (class, coin) pairs: a lower bound on 30-day first posts


if __name__ == "__main__":
    ev = build()
    with open(os.path.join(OUT, "events_all.csv"), "w") as f:
        w = csv.DictWriter(f, fieldnames=list(ev[0].keys())); w.writeheader(); w.writerows(ev)
    E = [e for e in ev if e["perp"]]
    for e in E:
        e["T"] = e["T"] * 1000  # ms for pull / analyze
    with open(os.path.join(OUT, "events.csv"), "w") as f:
        w = csv.DictWriter(f, fieldnames=list(E[0].keys())); w.writeheader(); w.writerows(E)
    from collections import Counter
    c = Counter((e["cls"], e["year"], bool(e["perp"])) for e in ev)
    print("class  year  posts(first per coin)  with perp>=7d")
    for cls in ("BH", "CBA", "CBL", "RH", "OTH"):
        for y in range(2020, 2025):
            n0, n1 = c[(cls, y, False)], c[(cls, y, True)]
            if n0 + n1:
                print(f"{cls:4s} {y} {n0+n1:5d} {n1:5d}")
    print("events with perp", len(E))
