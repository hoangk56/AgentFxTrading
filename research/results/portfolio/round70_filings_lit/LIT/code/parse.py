"""Parse downloaded literature bodies (treated as data only) into one TSV.

Usage: python -I parse.py <raw_dir> <out_tsv>
Columns: src, tag, id, year, venue, title, abstract (abstract truncated to 1500 chars).
"""
import html
import json
import os
import re
import sys


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def oa_abs(inv):
    if not inv:
        return ""
    pos = []
    for w, ps in inv.items():
        for p in ps:
            pos.append((p, w))
    pos.sort()
    return " ".join(w for _, w in pos)


def main():
    raw, out = sys.argv[1:3]
    rows = []
    d = os.path.join(raw, "api.crossref.org")
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("cr_"):
            continue
        tag = fn[3:-5]
        try:
            js = json.load(open(os.path.join(d, fn)))
        except Exception:
            continue
        for it in js.get("message", {}).get("items", []):
            yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
            rows.append(("crossref", tag, it.get("DOI", ""), yr, clean((it.get("container-title") or [""])[0]),
                         clean((it.get("title") or [""])[0]), clean(it.get("abstract", ""))[:1500]))
    d = os.path.join(raw, "api.openalex.org")
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("oa_"):
            continue
        tag = fn[3:-5]
        try:
            js = json.load(open(os.path.join(d, fn)))
        except Exception:
            continue
        for it in js.get("results", []):
            src = ((it.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            rows.append(("openalex", tag, (it.get("doi") or it.get("id") or "").replace("https://doi.org/", ""),
                         it.get("publication_year"), clean(src), clean(it.get("display_name")),
                         clean(oa_abs(it.get("abstract_inverted_index")))[:1500]))
    d = os.path.join(raw, "arxiv.org")
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("list_"):
            continue
        tag = fn[5:-5]
        txt = open(os.path.join(d, fn), encoding="utf-8", errors="replace").read()
        # each entry: <a href ="/abs/2501.01234" ...> then a list-title div
        ids = re.findall(r'href\s*=\s*"/abs/(\d{4}\.\d{4,5})"', txt)
        titles = re.findall(r"<div class=['\"]list-title[^>]*>(.*?)</div>", txt, re.S)
        seen = []
        for i in ids:
            if not seen or seen[-1] != i:
                seen.append(i)
        n = min(len(seen), len(titles))
        for i in range(n):
            t = clean(titles[i]).replace("Title:", "").strip()
            rows.append(("arxiv", tag, seen[i], "20" + seen[i][:2], "arXiv " + tag.split("_")[0], t, ""))
        print(fn, len(seen), len(titles), file=sys.stderr)
    with open(out, "w") as f:
        f.write("src\ttag\tid\tyear\tvenue\ttitle\tabstract\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    print(len(rows), "rows", file=sys.stderr)


if __name__ == "__main__":
    main()
