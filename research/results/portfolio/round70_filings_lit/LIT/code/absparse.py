"""Print title, submission date and abstract from saved arxiv.org/abs pages (data only).

Usage: python -I absparse.py <file> [<file> ...]
"""
import html
import re
import sys


def cl(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


for fn in sys.argv[1:]:
    t = open(fn, encoding="utf-8", errors="replace").read()
    ti = re.search(r'<h1 class="title mathjax">(.*?)</h1>', t, re.S)
    ab = re.search(r'<blockquote class="abstract mathjax">(.*?)</blockquote>', t, re.S)
    dt = re.search(r"\[Submitted on ([^\]]*)\]", t)
    print("==", fn.split("/")[-1], cl(ti.group(1) if ti else ""), "|", dt.group(1) if dt else "")
    print(cl(ab.group(1) if ab else "")[:1300])
    print()
