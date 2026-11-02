"""Coincheck corporate PRESS pages (corporate.coincheck.com/press/<slug>; derived from pull_coincheck.py by sed: same parser, own csv).
robots allows /news, disallows only /2017-2021/, /archive, /en, ...). For each page keep slug, title,
publishedAt / createdAt / updatedAt (CMS _meta of the post) and the first 400 chars of visible text, only if
publishedAt < 2025-01-01 (rows >= 2025 are dropped unprinted). Raw HTML is not kept (size); parse = untrusted data."""
import sys, re, os, csv, html, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import net
SM = os.path.join(net.D, "raw", "corporate.coincheck.com_sitemap-dynamic_sitemap-dynamic-cHJlc3MvOnNsdWc.xml")
OUT = os.path.join(net.D, "coincheck_press.csv")
done = set()
if os.path.exists(OUT):
    done = {r["slug"] for r in csv.DictReader(open(OUT))}
skipped = os.path.join(net.D, "coincheck_press_skipped.txt")
if os.path.exists(skipped):
    done |= set(open(skipped).read().split())
locs = re.findall(r"<loc>https://corporate.coincheck.com/press/([^<]+)</loc>", open(SM).read())
new = not os.path.exists(OUT)
f = open(OUT, "a", newline=""); w = csv.writer(f)
if new:
    w.writerow(["slug", "published_at_utc", "created_at_utc", "updated_at_utc", "title", "text"])
sk = open(skipped, "a")
meta = re.compile(r'\{"project":(\d+),"publishedAt":(\d+),"createdAt":(\d+),.*?"updatedAt":(\d+)\}')
n = 0
for slug in locs:
    if slug in done:
        continue
    s, b = net.get(f"https://corporate.coincheck.com/press/{slug}", note="GET press", tries=3, timeout=30)
    n += 1
    if s != 200:
        sk.write(slug + "\n"); continue
    t = b.decode("utf-8", "replace")
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
    pub = cr = up = ""
    if m:
        try:
            arr = json.loads(m.group(1))
            # first post-level _meta after the page's dynamicData key: the dict with publishedAt + schema + uid
            # the post's own _meta is the last such dict (earlier ones are its category / tag records)
            ms = [x for x in arr if isinstance(x, dict) and "publishedAt" in x and "uid" in x and "schema" in x]
            if ms:
                x = ms[-1]
                def val(i):
                    v = arr[x[i]]
                    return v[1] if isinstance(v, list) and len(v) == 2 and v[0] == "Date" else str(v)
                pub, cr, up = val("publishedAt"), val("createdAt"), val("updatedAt")
        except Exception as e:
            pub = "ERR"
    title = html.unescape(re.findall(r"<title>(.*?)</title>", t, re.S)[0]) if "<title>" in t else ""
    if pub and pub != "ERR" and pub >= "2025-01-01":
        sk.write(slug + "\n"); continue
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))[:400]
    w.writerow([slug, pub, cr, up, title, text]); f.flush()
    if n % 50 == 0:
        print("done", n, flush=True)
print("finished", n, flush=True)
