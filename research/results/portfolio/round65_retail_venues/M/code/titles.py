"""Stream M: list every Upbit market-addition notice title (first_listed_at < 2025-01-01) from stream W's cached list
pages (read-only). No prices. Output: ../additions_titles.csv (id, t_utc, category, title)."""
import csv, json, os, re, datetime as dt
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw/list_all"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "additions_titles.csv")
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
ADD = re.compile(r"(마켓.*(추가|오픈|신규|상장))|신규\s*거래\s*지원|거래\s*지원\s*안내|디지털\s*자산\s*추가|마켓\s*디지털")


def notices():
    seen = {}
    for fn in sorted(os.listdir(RAW)):
        if fn.endswith(".json"):
            for n in json.load(open(os.path.join(RAW, fn), encoding="utf-8"))["data"]["notices"]:
                t = dt.datetime.fromisoformat(n["first_listed_at"]).astimezone(dt.timezone.utc)
                if t < CUT:
                    seen[n["id"]] = (t, n)
    return seen


if __name__ == "__main__":
    rows = []
    for i, (t, n) in sorted(notices().items(), key=lambda x: x[1][0]):
        title = n["title"]
        if ADD.search(title) and not re.search(r"종료|연장|유의|입출금|이벤트|에어드", title):
            rows.append((i, t.strftime("%Y-%m-%d %H:%M"), n["category"], title))
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "t_utc", "category", "title"]); w.writerows(rows)
    print(len(rows))
