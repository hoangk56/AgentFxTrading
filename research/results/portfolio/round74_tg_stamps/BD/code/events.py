"""Stream BD events: parse saved t.me/s/<channel> pages (untrusted data, python -I), cut at 2025-01-01 right after
parsing, classify titles with the regexes declared in HYPOTHESES_BD.md, extract tickers.
2025-26 posts are only counted per class (no text kept or printed).
Usage: python -I events.py [channel]  -> writes BD/events_<channel>.csv and prints counts per class / year."""
import csv, glob, os, re, sys, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import parse

RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist/raw"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/BD"
CUT = 1735689600  # 2025-01-01 00:00:00 UTC
I = re.I
RX = dict(
    X=re.compile(r"\b(swap|migration|rebrand\w*|redenomination|token\s+split|rename\w*)\b", I),
    MT=re.compile(r"monitoring\s+tag", I),
    F=re.compile(r"((futures|perpetual|USD[ⓈS]?-?M|COIN-M).*\b(delist\w*|close\s+and\s+delist|settle\s+and\s+delist)"
                 r"|\bdelist\w*\b.*\b(perpetual|futures))", I),
    M=re.compile(r"\bmargin\b.*\bdelist", I),
    O=re.compile(r"(staking|\bp2p\b|flexible\s+loan|leveraged\s+tokens?|BLVT|options|\bearn\b|savings|\bloans?\b|\bconvert\b|isolated)", I),
    S=re.compile(r"\b(will\s+delist|to\s+delist|delisting\s+of|will\s+be\s+delisted|delists?)\b", I),
)
PAIRS = re.compile(r"\btrading\s+pairs?\b", I)
WILLDELIST = re.compile(r"\b[Dd]elist\s+([A-Z0-9][A-Za-z0-9 ,&]*)")
INCLUDE = re.compile(r"\b[Ii]nclude\s+([A-Z0-9][A-Za-z0-9 ,&]*)")
STOP = {"AND", "THE", "ON", "OF", "ALL", "TRADING", "PAIRS", "PAIR", "BINANCE", "WILL", "DELIST", "SPOT", "USD", "USDT",
        "BUSD", "BTC", "ETH", "BNB", "TOKENS", "TOKEN", "FROM", "AT", "IN", "TO", "A", "S", "M", "NOTICE",
        "REMOVAL", "UPDATE", "UPDATED", "CROSS", "MARGIN", "FUTURES", "PERPETUAL", "CONTRACT", "CONTRACTS"}


def title(text):
    for ln in text.split("\n"):
        if ln.strip():
            return ln.strip()
    return ""


def classify(t):
    if RX["X"].search(t):
        return "X"
    if RX["MT"].search(t):
        return "MT"
    if RX["F"].search(t):
        return "F"
    if RX["M"].search(t):
        return "M"
    if not RX["S"].search(t):
        return None
    if RX["O"].search(t):
        return "O"
    m = WILLDELIST.search(t)
    if PAIRS.search(t) and not (m and tickers_from(m.group(1))):
        return "P"
    return "S"


def tickers_from(s):
    s = re.split(r"\b(on|from|at|trading|spot|margin|futures|[Rr]emove)\b", s)[0]
    out = []
    for tok in re.split(r"[,&]|\band\b", s):
        tok = tok.strip()
        if re.fullmatch(r"[A-Z0-9]{2,12}", tok) and tok not in STOP:
            out.append(tok)
    return out


STABLE = {"BUSD", "TUSD", "USDC", "USDP", "PAX", "USDS", "USDSB", "IDRT", "BIDR", "BKRW", "EUR", "GBP", "AUD", "NGN", "RUB",
          "TRY", "UAH", "BRL", "ZAR", "DAI", "FDUSD", "AEUR", "EURI", "BVND", "IDR", "VAI", "UST", "USTC", "SUSD"}


def coins(t, body):
    if RX["F"].search(t) and not RX["X"].search(t):  # perp notices: every ticker-like word in the title
        c = [x for x in re.findall(r"(?<![-\w])([A-Z0-9]{2,12})(?![-\w])", t) if x not in STOP and x not in STABLE]
        return list(dict.fromkeys(c))
    m = (INCLUDE if RX["MT"].search(t) else WILLDELIST).search(t)
    c = tickers_from(m.group(1)) if m else []
    if not c:
        c = [x for x in re.findall(r"\(([A-Z0-9]{2,12})\)", body) if x not in STOP]
    return [x for x in dict.fromkeys(c) if x not in STABLE]


def load(ch):
    posts = {}
    for fn in glob.glob(os.path.join(RAW, ch, "*.html")):
        ps, _ = parse.parse(open(fn, "rb").read())
        for p in ps:
            if p["time"] is None:
                continue
            posts[p["id"]] = p
    return posts


def main(ch="binance_announcements"):
    posts = load(ch)
    hold = {}; rows = []
    for pid in sorted(posts):
        p = posts[pid]
        if p["time"] >= CUT:  # HOLD: count the class only, keep nothing else
            c = classify(title(p["text"]))
            hold[c] = hold.get(c, 0) + 1
            continue
        t = title(p["text"]); c = classify(t)
        rows.append(dict(id=pid, time=int(p["time"]), utc=dt.datetime.fromtimestamp(p["time"], dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                         edited=int(p["edited"]), cls=c or "", coins=" ".join(coins(t, p["text"])) if c in ("S", "F", "MT", "M") else "",
                         title=t[:300]))
    with open(os.path.join(OUT, f"events_{ch}.csv"), "w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    ids = sorted(posts)
    print(ch, "posts", len(posts), "pre-2025", len(rows), "min id", ids[0], "first", rows[0]["utc"] if rows else None)
    yrs = {}
    for r in rows:
        k = (r["utc"][:4], r["cls"] or "-"); yrs[k] = yrs.get(k, 0) + 1
    cl = ["S", "F", "M", "MT", "P", "O", "X", "-"]
    print("year  " + " ".join(f"{c:>5s}" for c in cl) + "  S-coins S-coins(not edited)")
    for y in sorted({k[0] for k in yrs}):
        sc = sum(len(r["coins"].split()) for r in rows if r["utc"][:4] == y and r["cls"] == "S")
        sce = sum(len(r["coins"].split()) for r in rows if r["utc"][:4] == y and r["cls"] == "S" and not r["edited"])
        print(y, " " + " ".join(f"{yrs.get((y, c), 0):5d}" for c in cl), f"  {sc:5d} {sce:5d}")
    print("HOLD 2025-26 class counts (count only):", {k or "-": v for k, v in sorted(hold.items(), key=lambda x: str(x[0]))})


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
