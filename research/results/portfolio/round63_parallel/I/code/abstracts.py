"""Fetch abstracts from OpenAlex by DOI (no mailto). Usage: python -I abstracts.py <log> <doi> ..."""
import json, sys, time, urllib.request
from datetime import datetime, timezone
UA = "research-script/1.0 (python-urllib)"
log = sys.argv[1]
for doi in sys.argv[2:]:
    url = f"https://api.openalex.org/works/https://doi.org/{doi}?select=display_name,publication_year,abstract_inverted_index,authorships"
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            b = r.read(); st = r.status
    except Exception as e:
        b, st = b"", f"ERR {e}"
    open(log, "a").write(f"{t}\t{url}\t{st}\t{len(b)}\tabstract\n")
    time.sleep(1)
    if not b:
        print(doi, st); continue
    d = json.loads(b)
    inv = d.get("abstract_inverted_index") or {}
    words = sorted((p, w) for w, ps in inv.items() for p in ps)
    au = ", ".join(a["author"]["display_name"] for a in d.get("authorships", [])[:4])
    print(f"### {doi} | {d.get('display_name')} ({d.get('publication_year')}) | {au}\n{' '.join(w for _, w in words)[:1400]}\n")
