"""Literature lookups (Crossref + OpenAlex), no e-mail / mailto sent.

Usage: python -I lit.py <log_file> <out_tsv> <queries_file>
queries_file: one query per line, "tag<TAB>query".
Writes tag, source, year, doi, title, cited_by (top 6 per source) to out_tsv; logs each request.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "research-script/1.0 (python-urllib)"


def get(url, log):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read()
            st = r.status
    except Exception as e:
        body, st = b"", f"ERR {e}"
    with open(log, "a") as f:
        f.write(f"{t}\t{url}\t{st}\t{len(body)}\tlit\n")
    time.sleep(1.0)
    try:
        return json.loads(body)
    except Exception:
        return None


def main():
    log, out, qf = sys.argv[1:4]
    rows = []
    for line in open(qf):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        tag, q = line.split("\t", 1)
        cq = urllib.parse.quote(q)
        d = get(f"https://api.crossref.org/works?query.bibliographic={cq}&rows=6&select=DOI,title,issued,is-referenced-by-count", log)
        for it in (d or {}).get("message", {}).get("items", []):
            yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
            rows.append((tag, "crossref", yr, it.get("DOI"), (it.get("title") or [""])[0], it.get("is-referenced-by-count")))
        d = get(f"https://api.openalex.org/works?search={cq}&per-page=6&select=doi,display_name,publication_year,cited_by_count", log)
        for it in (d or {}).get("results", []):
            rows.append((tag, "openalex", it.get("publication_year"), (it.get("doi") or "").replace("https://doi.org/", ""), it.get("display_name"), it.get("cited_by_count")))
    with open(out, "w") as f:
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
