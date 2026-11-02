"""Stream O2: fetch the OKX article page of each OKX event (www.okx.com/help/<slug>, allowed by robots.txt) to read the
stated trading start. Saved raw under research/data/okx_bybit_notice/raw/bodies/. Bybit article pages
(announcements.bybit.com -> 301 to www.bybit.com, unreachable from this machine) are not fetched: Bybit events use a
time stated in the title, else N + 60 min (declared)."""
import csv, hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

B = os.path.join(net.D, "raw", "bodies")
os.makedirs(B, exist_ok=True)
EV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "events.csv")


def path(url):
    return os.path.join(B, hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")


if __name__ == "__main__":
    urls = sorted({r["url"] for r in csv.DictReader(open(EV)) if r["venue"] == "OKX"})
    for u in urls:
        p = path(u)
        if os.path.exists(p):
            continue
        b, s = net.get(u, "okx-body", gap=0.8)
        if b is None:
            print("MISS", s, u); continue
        open(p, "wb").write(b)
    print("bodies", len(urls))
