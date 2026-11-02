"""Fetch the body of selected Coincheck press / news pages (argv: press/<slug> or news/<slug>) and print the sentences
that state a start date / time (text only, no prices). Raw pages saved under raw/cc_<slug>.html."""
import sys, re, json, html, os
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import net
for path in sys.argv[1:]:
    slug = path.split("/")[-1]
    s, b = net.get(f"https://corporate.coincheck.com/{path}", save=f"cc_{slug}.html", note="GET body", tries=2, timeout=30)
    if s != 200:
        print(path, s); continue
    t = b.decode("utf-8", "replace")
    arr = json.loads(re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', t, re.S).group(1))
    strs = [x for x in arr if isinstance(x, str) and "<p" in x]
    body = max(strs, key=len) if strs else ""
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))
    hits = [m.group(0) for m in re.finditer(r"[^。]{0,60}(\d{1,2}月\d{1,2}日|本日|午前|午後|\d{1,2}[:：]\d{2}|\d{1,2}時)[^。]{0,80}", text)]
    print("==", path, len(text)); [print("   ", h.strip()[:200]) for h in hits[:6]]
