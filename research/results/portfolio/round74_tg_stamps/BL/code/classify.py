"""Classify @binance_announcements post titles (first line) with the regexes declared in HYPOTHESES_BL.md section 3.
Outputs research/data/binance_tg_listing/{l1_titles,l2_titles}.json (pre-2025, one row per coin) and prints counts per
year, including 2025-26 as counts only (hold_titles.json). Titles are untrusted text, matched as data only."""
import json, os, re, sys, datetime as dt
from collections import Counter
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_tg_listing"
L1_INC = re.compile(r"^\s*Binance (Will List|Lists|Lists New|Adds|Will Add)\b", re.I)
L1_EXC = re.compile(r"Futures|Perpetual|Margin|Launchpool|Launchpad|Convert|Earn|Savings|Staking|Pre-?Market|Alpha|"
                    r"Options|Pool|Trading Pairs|Opens Trading|Delist|Copy Trading|Loan|Simple Earn|NFT|"
                    # added 14:58 UTC after reading titles, before prices: fiat / P2P / card notices are not coin listings
                    r"Fiat|Gateway|Peer-to-peer|P2P|Purchases|Payment|Card|Buy Crypto", re.I)
L2_INC = re.compile(r"Binance Futures Will Launch .*(USD[ⓈS]-?M|USDT[- ]Margined|USDT-M).*Perpetual"
                    # added 14:58 UTC after reading titles, before prices: the 2019-20 format "Launches XXX/USDT Perpetual"
                    r"|Binance Futures (Will Launch|Launches) [A-Z0-9]+/USDT Perpetual", re.I)
L2_EXC = re.compile(r"Coin-Margined|COIN-M|Quarterly|Delivery|Pre-Market|Options|Leveraged Token", re.I)
TICK = re.compile(r"\(([A-Z0-9]{2,15})\)")
# pegged assets (stablecoins, fiat tokens, liquid-staking wrappers): no listing-demand mechanism; excluded before prices
PEGGED = {"FDUSD", "AEUR", "EURI", "UST", "BNSOL", "USDP", "TUSD", "PAX", "PAXG", "BUSD", "USDC", "DAI", "USDS", "EUR", "GBP", "AUD",
          "BIDR", "BVND", "IDRT", "NGN", "RUB", "TRY", "UAH", "BRL", "ZAR", "WBETH", "BETH", "WBTC", "USDSB", "SUSD", "TRYB", "XUSD", "USD1", "RLUSD", "BFUSD", "USDE"}


def title(text):
    return (text or "").strip().split("\n")[0].strip()


def l2_coins(t):
    """Coins named in a perp-launch title: words before 'Perpetual' after the margin type, split on , / and."""
    m0 = re.search(r"(?:Will Launch|Launches) ([A-Z0-9]+)/USDT Perpetual", t)
    if m0:
        return [m0.group(1)]
    m = re.search(r"(?:USD[ⓈS]-?M|USDT[- ]Margined|USDT-M)\s+(.*?)\s+Perpetual", t, re.I)
    if not m:
        return []
    s = re.sub(r"\(.*?\)", "", m.group(1))
    parts = re.split(r",|&|\band\b", s)
    return [p.strip().upper() for p in parts if p.strip()]


def classify(posts, key="text"):
    l1, l2 = [], []
    for p in posts:
        t = title(p[key])
        if L1_INC.search(t) and not L1_EXC.search(t):
            tk = TICK.findall(t)
            for c in dict.fromkeys(x for x in tk if x not in PEGGED):
                l1.append(dict(id=p["id"], t=p["t"], edited=p["edited"], coin=c, title=t))
        if L2_INC.search(t) and not L2_EXC.search(t):
            for c in dict.fromkeys(l2_coins(t)):
                l2.append(dict(id=p["id"], t=p["t"], edited=p["edited"], coin=c, title=t))
    return l1, l2


def dedup(ev):
    out, seen = [], {}
    for e in sorted(ev, key=lambda e: e["t"]):
        k = e["coin"]
        if k in seen and e["t"] - seen[k] < 7 * 86400:
            continue
        seen[k] = e["t"]; out.append(e)
    return out


def yr(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).year


if __name__ == "__main__":
    pre = json.load(open(os.path.join(D, "posts_pre2025.json")))
    l1, l2 = classify(pre)
    l1, l2 = dedup(l1), dedup(l2)
    json.dump(l1, open(os.path.join(D, "l1_titles.json"), "w"), indent=0)
    json.dump(l2, open(os.path.join(D, "l2_titles.json"), "w"), indent=0)
    hold = json.load(open(os.path.join(D, "hold_titles.json")))
    h1, h2 = classify(hold, key="title")
    h1, h2 = dedup(h1), dedup(h2)
    for nm, ev, hv in (("L1", l1, h1), ("L2", l2, h2)):
        c = Counter(yr(e["t"]) for e in ev); ce = Counter(yr(e["t"]) for e in ev if e["edited"])
        print(nm, "coins per year (edited):", {y: f"{c[y]} ({ce[y]})" for y in sorted(c)},
              "| posts:", len({e["id"] for e in ev}), "| HOLD 2025-01..2026-10 coins (count only):", len(hv),
              "posts:", len({e["id"] for e in hv}))
    yp = Counter(yr(p["t"]) for p in pre); print("all posts per year:", dict(sorted(yp.items())))
