"""Stream O2 event builder (no prices). Listing announcements 2020-01-01..2024-12-31 UTC from the keyless lists:
 OKX  /api/v5/support/announcements (all types, raw/pages_all) and Bybit /v5/announcements/index (type new_crypto).
Stamp N (declared in HYPOTHESES_O2.md):
 OKX:   pTime (ms, "actual time first published") when |pTime - businessPTime| <= 10 min; else businessPTime when
        pTime is a migration artefact (pTime - businessPTime > 1 d) and businessPTime has non-zero seconds (old CMS
        stamp); else dropped (stamp ambiguous).
 Bybit: dateTimestamp (s). publishTime exists only from 2024-03 and is reported as a check.
Coin: tickers in the title that map to a Binance USDT-M perp traded >= 7 d before N (perps.py logic, copied).
Output O2/events.csv."""
import csv, glob, json, os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import perps

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/okx_bybit_notice/raw"
OUTD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LO, CUT = 1577836800000, 1735689600000
MIN, DAY = 60000, 86400000
STABLE = {"USDT", "USDC", "DAI", "TUSD", "BUSD", "USDP", "PAX", "FDUSD", "USDE", "PYUSD", "USDD", "UST", "EUR", "EURT"}
STOP = {"OKX", "OKEX", "USD", "UTC", "AM", "PM", "NFT", "NFTS", "API", "BTC", "ETH", "ERC20", "BRC", "TRC20", "BEP20",
        "APY", "KOL", "VIP", "NEW", "DEX", "CEX", "AI", "ID", "ON", "OF", "TO", "THE", "AND", "FOR", "X", "II", "III", "IV",
        "VS", "BYBIT", "UTA", "P2P", "MT5", "WEB3", "SPOT", "USDC", "PERP", "PERPS", "TGE", "IEO", "IDO"} | STABLE
# Titles that are not a new spot pair / new perpetual for a coin (declared before prices)
EXCL = re.compile(r"delist|tick size|position tier|adjust|dual investment|suspen|upgrade|maintenance|copy trading|"
                  r"leveraged token|\b\d?[LS]/USDT|3L|3S|launchpad|launchpool|byvote|convert|tradfi|pre-market|premarket|"
                  r"terms|airdrop|promotion|voting|vote|result|options|loan|earn\b|savings? only|trading bot|"
                  r"grid|staking|flexible|mainnet|swap:|deposit|withdraw|resum|migration|rebrand|renam|contest|giveaway|lucky draw|"
                  r"campaign|competition|prize|carnival|x-perp|equity|stock|delay|postpone|cancel|reminder|completed|"
                  r"index|funding rate|price limit|margin tier|leverage adjustment|launch of real-time|settlement|"
                  r"call-auction|call auction|futures for|expiry|bi-monthly|quarterly|weekly", re.I)
# Exception: Bybit / OKX listing titles that carry a prize pool are still listings
LISTING = re.compile(r"\blist(?:s|ing|ed)?\b|now available|soon available|just landed|new arrivals?|new listing|"
                     r"perpetual contract|contract\b|global initial listing", re.I)
TK = r"(?=[A-Z0-9]{0,11}[A-Z])[A-Z0-9]{2,12}"


def fmt(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def kind(title):
    return "perp" if re.search(r"perpetual|perp\b|\bswap\b|contract", title, re.I) else "spot"


def tickers(title):
    t = title.replace("\xa0", " ").replace("（", "(").replace("）", ")").replace("、", "/")
    # OKX perp titles: "... and List Perpetual for SAND/PERP": only the coins after "Perpetual (Swap) for"
    m = re.search(r"(?:list|listing)\s+(?:usdt-margined\s+|coin-margined\s+)?perpetual(?:\s+swaps?)?\s+(?:&\s*futures\s+)?for\s+(.+)$", t, re.I)
    if m:
        seg = re.split(r"\s+(?:and enable|along with|crypto,|crypto\b)", m.group(1))[0]
        return [x for x in re.findall(r"\b" + TK + r"\b", seg) if x not in STOP]
    pair = re.findall(r"\b(" + TK + r")(?:-PERP)?/(?:USDT|USDC|BTC|ETH|SOL|EUR)\b", t)
    if pair:  # Bybit "New Listing: X/USDT -- prize pool of Y": the pair's base only
        return [x for x in pair if x not in STOP][:1] if "prize" in t.lower() else [x for x in pair if x not in STOP]
    paren = re.findall(r"\(\s*(" + TK + r")\s*\)", t)
    if paren:
        return [x for x in paren if x not in STOP]
    out = []
    for x in re.findall(r"\b(" + TK + r")(?:/USDT|USDT|USD)?\b", re.sub(r"\([^)]*\)", "", t)):
        if x in STOP or x.isdigit():
            continue
        out.append(x)
    return out


def base(x):
    for suf in ("USDT", "USD"):
        if x.endswith(suf) and len(x) > len(suf) + 1:
            return x[: -len(suf)]
    return x


def okx_rows():
    rows = []
    for p in sorted(glob.glob(os.path.join(D, "pages_all", "okx_all_*.json"))):
        rows += json.load(open(p))["data"][0]["details"]
    seen, out = set(), []
    for r in rows:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        pt, bz = int(r["pTime"]), int(r["businessPTime"])
        if abs(pt - bz) <= 10 * MIN:
            N, src = pt, "pTime"
        elif pt - bz > DAY and bz % MIN != 0:
            N, src = bz, "bizPTime"
        else:
            N, src = None, "ambiguous"
        ref = N if N is not None else bz
        if not (LO <= ref < CUT):
            continue
        out.append(dict(venue="OKX", title=r["title"], url=r["url"], N=N, src=src, aux=pt, ann=r["annType"]))
    return out


def bybit_rows():
    rows = []
    for p in sorted(glob.glob(os.path.join(D, "pages", "bybit_nc_*.json"))):
        rows += json.load(open(p))["result"]["list"]
    out = []
    for r in rows:
        N = int(r["dateTimestamp"])
        if not (LO <= N < CUT):
            continue
        out.append(dict(venue="Bybit", title=r["title"], url=r["url"], N=N, src="dateTimestamp",
                        aux=r.get("publishTime") or "", ann="|".join(r.get("tags") or [])))
    return out


def build():
    SP = perps.span()
    ev, rej = [], []
    for a in okx_rows() + bybit_rows():
        title = a["title"]
        if a["N"] is None:
            rej.append((a, "stamp ambiguous")); continue
        if not LISTING.search(title) or (EXCL.search(title) and not re.search(r"new listing|will list|to list|lists\b", title, re.I)):
            rej.append((a, "not a listing")); continue
        if EXCL.search(title) and re.search(r"delist|tick size|position tier|adjust|dual investment|suspen|tradfi|pre-market|x-perp|equity|leveraged token|copy trading|convert|launchpool|launchpad|byvote|options|futures for|expiry", title, re.I):
            rej.append((a, "not a listing")); continue
        tks = list(dict.fromkeys(base(x) for x in tickers(title)))
        hit = False
        for c in tks:
            if c in STOP:
                continue
            p = perps.perp_for(c, a["N"], SP)
            if p:
                ev.append(dict(venue=a["venue"], coin=c, perp=p, kind=kind(title), N=a["N"], N_utc=fmt(a["N"]),
                               src=a["src"], aux=a["aux"], title=title, url=a["url"])); hit = True
        if not hit:
            rej.append((a, "no Binance perp >= 7 d" if tks else "no ticker"))
    ev.sort(key=lambda e: e["N"])
    # same coin within the previous 24 h (any venue): keep the first only (windows would overlap)
    keep, last = [], {}
    for e in ev:
        if e["coin"] in last and e["N"] - last[e["coin"]] < DAY:
            e["dup"] = 1
        else:
            e["dup"] = 0
            last[e["coin"]] = e["N"]
        keep.append(e)
    for e in keep:
        y = int(e["N_utc"][:4]); e["year"] = y; e["era"] = "IS" if y <= 2021 else "VAL"; e["day"] = e["N_utc"][:10]
    return keep, rej


if __name__ == "__main__":
    ev, rej = build()
    cols = ["venue", "coin", "perp", "kind", "N", "N_utc", "src", "aux", "era", "year", "day", "dup", "title", "url"]
    with open(os.path.join(OUTD, "events.csv"), "w") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); [w.writerow(e) for e in ev]
    with open(os.path.join(OUTD, "events_rejected.csv"), "w") as f:
        w = csv.writer(f); w.writerow(["venue", "N_or_aux", "src", "reason", "title"])
        for a, why in rej:
            w.writerow([a["venue"], a["N"] or a["aux"], a["src"], why, a["title"]])
    import collections
    c = collections.Counter((e["venue"], e["era"], e["kind"], e["dup"]) for e in ev)
    for k, v in sorted(c.items()):
        print(k, v)
    print("rejected", collections.Counter((a["venue"], why) for a, why in rej))
