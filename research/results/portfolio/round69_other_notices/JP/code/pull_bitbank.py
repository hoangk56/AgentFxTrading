"""Pull bitbank's お知らせ list (bitbank.cc/blog/tags/information?page=N, robots allows /blog) and keep
(id, publishedAt, title, summary) for notices dated 2019-12-01 <= t < 2025-01-01. Pages whose rows are all
>= 2025 are not kept on disk and their rows are never written or printed. Parsed as untrusted data."""
import sys, re, os, csv, html
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import net
# argv: none = the お知らせ tag list (59 pages); "all" = the full blog index (109 pages, every tag)
ALL = len(sys.argv) > 1 and sys.argv[1] == "all"
OUT = os.path.join(net.D, "bitbank_all.csv" if ALL else "bitbank_notices.csv")
rows = []
pat = re.compile(r'href="/blog/articles/([^"]+)"><div[^>]*linkCover.*?dateTime="([^"]+)".*?blog/tags/([a-z]+)".*?__title">(.*?)</p>.*?__content">(.*?)</p>', re.S)
for p in range(15 if ALL else 1, 110 if ALL else 60):
    u = f"https://bitbank.cc/blog?page={p}" if ALL else f"https://bitbank.cc/blog/tags/information?page={p}"
    s, b = net.get(u, note="GET list")
    if s != 200:
        print("page", p, s); continue
    t = b.decode("utf-8", "replace")
    recs = pat.findall(t)
    keep = [r for r in recs if "2019-12-01" <= r[1] < "2025-01-01"]
    if keep:
        open(os.path.join(net.D, "raw", f"bitbank_{'all' if ALL else 'list'}_p{p:03d}.html"), "wb").write(b)
    rows += [(i, d, html.unescape(ti), html.unescape(c)[:300], tg) for i, d, tg, ti, c in keep]
    old = [r for r in recs if r[1] < "2025-01-01"]
    print("page", p, "records", len(recs), "kept", len(keep), "min<2025", min([r[1] for r in old], default="-"))
    if recs and max(r[1] for r in recs) < "2019-12-01":
        break
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "published_at_utc", "title", "summary", "tag"]); w.writerows(rows)
print("rows", len(rows))
