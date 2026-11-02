"""Print bitcoin contexts of selected filings (review aid, python -I)."""
import sys, os, re, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse8k import text_of, D, R
C = list(csv.DictReader(open(os.path.join(D, "filings_parsed.csv"))))
keys = sys.argv[1:]
for c in C:
    if not any(k in c["acc_dt"] or k == c["acc"] for k in keys):
        continue
    t = text_of(os.path.join(R, f"{c['tk']}_{c['acc'].replace('-','')}_{c['doc']}"))
    print("=====", c["tk"], c["acc_dt"], c["items"], c["acc"])
    i = t.find("Item 7.01"); i = i if i >= 0 else t.find("Item 8.01")
    print(t[i:i + 900] if i >= 0 else t[:900])
