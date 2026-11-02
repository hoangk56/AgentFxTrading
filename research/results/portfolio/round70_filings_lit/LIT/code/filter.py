"""Mechanism-word filter over parsed records (declared in HYPOTHESES_LIT before reading results).

Usage: python -I filter.py <all_tsv> <out_tsv>
Keeps a record if title+abstract has >= 1 mechanism word (retail / announcement / rule flow / settlement) and the
record is 2025+; dedups by lower-cased title. arXiv rows have titles only, so for them a mechanism word OR a venue
word suffices.
"""
import re
import sys

MECH = r"retail|robinhood|individual investor|attention|announce|listing|delist|airdrop|launch|liquidat|deleverag|" \
       r"margin call|forced|rebalanc|leveraged etf|inclusion|index (addition|deletion|reconstitution)|unlock|" \
       r"vesting|mint|redemption|creation|funding rate|settlement|expir|pin|oracle|resolution|auction|" \
       r"pump|meme|0dte|zero.day|order imbalance|order flow|price pressure|flow"
VENUE = r"crypto|bitcoin|btc|ethereum|token|perpetual|binance|coinbase|upbit|hyperliquid|polymarket|kalshi|" \
        r"prediction market|etf|option|futures|stablecoin|defi|exchange"
NOISE = r"covid|esg|carbon|climate|portfolio optimi|deep learning|llm|large language|neural|reinforcement|" \
        r"insurance|bank lending|mortgage|tax evasion"


def main():
    src, out = sys.argv[1:3]
    seen, kept, n = set(), [], 0
    hdr = None
    for line in open(src, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if hdr is None:
            hdr = p
            continue
        n += 1
        s, tag, rid, yr, venue, title, ab = (p + [""] * 7)[:7]
        try:
            if int(str(yr)[:4]) < 2025:
                continue
        except ValueError:
            continue
        key = re.sub(r"\W+", "", title.lower())
        if not key or key in seen:
            continue
        txt = (title + " " + ab).lower()
        if re.search(NOISE, title.lower()):
            continue
        m = re.search(MECH, txt)
        v = re.search(VENUE, txt)
        ok = (m and v) if s != "arxiv" else (m or v)
        if not ok:
            continue
        seen.add(key)
        kept.append(p)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\t".join(hdr) + "\n")
        for p in kept:
            f.write("\t".join(p) + "\n")
    print(n, "in,", len(kept), "kept", file=sys.stderr)


if __name__ == "__main__":
    main()
