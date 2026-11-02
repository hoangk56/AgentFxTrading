"""Stream W event builder (no prices). Classes from Upbit notice titles (api-manager.upbit.com, first_listed_at = post
time, KST -> UTC):
  W = 유의 종목 지정 (warning designation), D = 거래(지원) 종료 (end of trading support), U = 유의 촉구 (caution urge).
Rules declared in HYPOTHESES_W.md. Output: W/events_all.csv (every coin-notice pair 2019-12..2024-12) with a perp flag."""
import os, re, json, glob, csv, datetime as dt, sys
sys.path.insert(0, os.path.dirname(__file__))
import perps
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw"
OUT = os.path.join(os.path.dirname(__file__), "..")
DAY = 86400000
SP = perps.span()
TK = r"\(([A-Z][A-Z0-9]{1,9})\)"


def cls(title):
    t = title.replace(" ", "")
    if "유의촉구" in t:
        return None if any(k in t for k in ("스왑", "전환")) else "U"
    if "거래지원종료" in t:
        if any(k in t for k in ("사유및", "정정", "스왑", "관련안내")):
            return None
        return "D"
    if "유의종목지정" in t:
        if any(k in t for k in ("기간연장", "해제", "유지", "스왑", "전환", "추가(")):
            return None
        return "W"
    return None


def blocks(body):
    """Split a body into (ticker, text) blocks at numbered headers like '1) 코모도(KMD)' or '**1) OMG (오미세고 ...)**'."""
    lines = body.split("\n"); out = []; cur = None
    for l in lines:
        m = re.match(r"^\W*\d+\s*\)\s*(?:\*\*)?\s*([^\n]*)", l)
        tk = None
        if m:
            h = m.group(1)
            a = re.search(TK, h) or re.match(r"([A-Z][A-Z0-9]{1,9})\s*\(", h)
            tk = a.group(1) if a else None
        if tk:
            cur = [tk, ""]; out.append(cur)
        elif cur:
            cur[1] += l + "\n"
    return out


def deadline(text, title, year):
    m = re.search(r"(20\d\d)[.\-년\s]+(\d{1,2})[.\-월\s]+(\d{1,2})일?\s*(?:\([^)]*\))?\s*(\d{1,2}):(\d\d)", text)
    if m:
        y, mo, d, h, mi = map(int, m.groups())
    else:
        m = re.search(r"\((\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d\d)\)", title)
        if not m:
            return None
        mo, d, h, mi = map(int, m.groups()); y = year
    k = dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone(dt.timedelta(hours=9)))
    return int(k.timestamp() * 1000)


def build():
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "detail", "*.json"))):
        d = json.load(open(f))["data"]
        if not ("2019-12" <= d["first_listed_at"][:7] <= "2024-12") or d["category"] != "거래":
            continue
        c = cls(d["title"])
        if not c:
            continue
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        body = d["body"]
        bl = blocks(body)
        if c == "U":
            coins = [(k, "", None) for k in re.findall(TK, d["title"])]
        elif bl:
            coins = []
            for k, txt in bl:
                mk = sorted(set(re.findall(k + r"\s*/\s*(KRW|BTC|USDT)", txt)))
                if c == "D" and not re.search(r"종료\s*(예정일|일시|일정|시점)?", txt):
                    continue
                coins.append((k, ",".join(mk), deadline(txt, d["title"], int(d["first_listed_at"][:4])) if c == "D" else None))
        else:
            mk = sorted(set(re.findall(r"(?<![A-Za-z])([A-Z0-9]{2,10})\s*/\s*(KRW|BTC|USDT)", body)))
            tks = re.findall(TK, d["title"]) or sorted(set(a for a, _ in mk))
            coins = [(k, ",".join(sorted(set(b for a, b in mk if a == k))), deadline(body, d["title"], int(d["first_listed_at"][:4])) if c == "D" else None) for k in tks]
        # D notices that list the coins in prose ("A, B, C의 마켓 거래 지원 종료") but also have blocks are covered by blocks
        for k, mk, dl in coins:
            if k in ("BTC", "KRW", "USDT"):
                continue
            s = perps.perp_for(k, t, SP)
            rows.append(dict(cls=c, coin=k, t_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
                             t=t, nid=d["id"], markets=mk, deadline_utc=(dt.datetime.fromtimestamp(dl / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M") if dl else ""),
                             tdl=dl or "", perp=s or "", title=d["title"][:80]))
    rows.sort(key=lambda r: (r["t"], r["coin"]))
    return rows


def select(rows):
    """Declared filters: KRW market affected (or markets unknown) for W / D; perp alive; first per (class, coin) in 30 d."""
    keep, last = [], {}
    for r in rows:
        if not r["perp"]:
            continue
        if r["cls"] in ("W", "D") and r["markets"] and "KRW" not in r["markets"]:
            continue
        key = (r["cls"], r["coin"])
        if key in last and r["t"] - last[key] < 30 * DAY:
            continue
        last[key] = r["t"]; keep.append(r)
    return keep


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(OUT, "events_all.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    kept = select(rows)
    with open(os.path.join(OUT, "events_kept.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(kept)
    import collections
    print("all", len(rows), collections.Counter((r["cls"], r["t_utc"][:4]) for r in rows))
    print("with perp", collections.Counter((r["cls"], r["t_utc"][:4]) for r in rows if r["perp"]))
    for r in kept:
        print(r["cls"], r["coin"], r["t_utc"], r["nid"], r["markets"], r["deadline_utc"], r["perp"], r["title"][:50])
