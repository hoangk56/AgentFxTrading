"""Parse the fetched 8-K primary documents (untrusted text, run with python -I).
Flags filings that state a completed bitcoin purchase, and records any press release / prior announcement mentioned.
Writes research/data/btc_treasury_8k/filings_parsed.csv."""
import os, re, csv, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
R = os.path.join(D, "raw", "docs")

# completed-purchase language: "acquired / purchased (an aggregate of) approximately N bitcoin(s)"
BUY = re.compile(r"(acquired|purchased|bought)\s+(an\s+aggregate\s+of\s+|a\s+total\s+of\s+|approximately\s+|an\s+additional\s+|additional\s+){0,3}"
                 r"(approximately\s+)?([\d,\.]+)\s+(additional\s+)?(bitcoins?|BTC)", re.I)
BUY2 = re.compile(r"(purchase|acquisition|acquire|purchased|acquired)\w*\s+(of\s+)?(\$[\d\.,]+\s*(million|billion)\s+(in|of|worth\s+of)\s+|approximately\s+)?(bitcoin|BTC)", re.I)
PR = re.compile(r"(press\s+release|announced|issued\s+a\s+press)", re.I)
DATE = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+20\d\d")


def text_of(p):
    s = open(p, "rb").read().decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s)


def main():
    C = list(csv.DictReader(open(os.path.join(D, "candidates.csv"))))
    out = []
    for c in C:
        a = c["acc"].replace("-", "")
        p = os.path.join(R, f"{c['tk']}_{a}_{c['doc']}")
        if not os.path.exists(p):
            c.update(btc_n=0, buy="MISSING", btc_qty="", snippet="", pr="", dates=""); out.append(c); continue
        t = text_of(p)
        nb = len(re.findall(r"bitcoin", t, re.I))
        m = BUY.search(t)
        m2 = BUY2.search(t)
        snip = ""
        if m:
            snip = t[max(0, m.start() - 220): m.end() + 120]
        elif m2:
            snip = t[max(0, m2.start() - 220): m2.end() + 160]
        prs = [t[max(0, x.start() - 120): x.end() + 120] for x in PR.finditer(t)][:2]
        c.update(btc_n=nb, buy="Y" if m else ("y2" if m2 else ""), btc_qty=m.group(4) if m else "",
                 snippet=snip, pr=" || ".join(prs), dates=";".join(sorted(set(DATE.findall(t) and [x.group(0) for x in DATE.finditer(t)]))[:8]))
        out.append(c)
    with open(os.path.join(D, "filings_parsed.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    for c in out:
        if c["btc_n"] and int(c["btc_n"]) > 0:
            print(c["tk"], c["form"], c["acc_dt"], c["items"], "nbtc", c["btc_n"], c["buy"], c["btc_qty"])


if __name__ == "__main__":
    main()
