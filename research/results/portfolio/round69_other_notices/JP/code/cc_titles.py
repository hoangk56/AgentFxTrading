"""List Coincheck corporate news 2020-24 whose titles look like coin-listing notices (title text only, no prices)."""
import csv, re, sys
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/jp_notices"
R = list(csv.DictReader(open(D + "/coincheck_news.csv")))
kw = re.compile(r"取扱|取り扱|上場|新規|追加")
print("rows", len(R), "2020-24", sum("2020" <= r["published_at_utc"][:4] <= "2024" for r in R),
      "empty pub", sum(not r["published_at_utc"] for r in R))
import collections
print(collections.Counter(r["published_at_utc"][:4] for r in R))
for r in sorted(R, key=lambda r: r["published_at_utc"]):
    if "2020-01-01" <= r["published_at_utc"] < "2025-01-01" and kw.search(r["title"]):
        print(r["published_at_utc"], r["slug"], r["title"].replace("｜コインチェック株式会社", "")[:110])
