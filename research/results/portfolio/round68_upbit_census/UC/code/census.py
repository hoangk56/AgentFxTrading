"""Stream UC step 1 (no prices): classify every 2020-01..2024-12 Upbit notice (stream W's list cache, read-only) into
declared categories by title keyword rules, extract coins from the title, keep coins whose Binance USDT-M perp had its
first trade >= 7 d before N (minute precision from stream N0's k1m launch cache when available, else first active
perp_1d day <= N - 8 d), and still traded >= 1 d after N. KRW-listing notices (stream A's set and any title / event
that announces a market opening) are excluded. Output: UC/events_all.csv (every notice-coin row) and
UC/events_kept.csv (deduplicated: first per (category, coin) within 7 d). Rules are declared in HYPOTHESES_UC.md."""
import csv, glob, json, os, re, sys, datetime as dt, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reason import reason

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
LIST = os.path.join(R, "upbit_notices", "raw", "list_all")
UC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round68_upbit_census/UC"
ANOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/notice_events.csv"
LO, CUT = 1577836800000, 1735689600000
DAY = 86400000
IS_END = 1640995200000
ALIAS = {"BEAM": "BEAMX"}
STOP = {"KRW", "BTC", "USDT", "ERC", "NFT", "API", "PC", "IT", "KT", "POS", "IOS", "TOP", "ID", "OTP", "QR", "FAQ",
        "VASP", "PDF", "AML", "KYC", "APP", "SMS", "DAXA", "EVM", "BEP", "TRC", "SPL", "HTS", "TV", "CEO", "USD", "DEX"}

# ---- declared category rules (title, spaces removed; first match wins; order matters) ----
LISTING = re.compile(r"마켓(디지털자산|코인)?추가|신규상장|신규거래지원|거래지원(개시|예정)|마켓오픈|상장기념|마켓TOP트레이딩|원화마켓에.*추가")
CATS = [
    ("WARN", "short", re.compile(r"유의종목지정|유의촉구|거래지원종료|거래지원종료|투자유의")),
    ("SWAP", None, re.compile(r"스왑|심볼변경|리브랜딩|액면분할|티커변경|이름변경|명칭변경|마이그레이션|토큰전환|컨버전|리디노미네이션")),
    ("AIRDROP", "long", re.compile(r"(에어드[랍롭]|스테이킹|지급)(및[^\s]*)?(지원|서비스지원)(예정)?안내|스테이킹지원디지털자산추가|보유회원대상.*지원")),
    ("NETUP", None, re.compile(r"(하드포크|업그레이드|메인넷|업데이트|월렛|지갑|노드|체인전환|합병|머지)")),
    ("RESUME", None, re.compile(r"재개")),
    ("DWSUSP", "short", re.compile(r"(입출금|입금|출금|입·출금)[^\s]*(일시)?(중단|지연|제한|순단)")),
    ("TRDSUSP", None, re.compile(r"거래(일시)?(중단|정지|제한)|시장가주문|매수주문제한|주문(한시적)?제한|가격제한")),
    ("EVENT", "long", re.compile(r"이벤트")),
    ("SUPPLY", None, re.compile(r"유통량")),
]
SKIP_TITLE = re.compile(r"지급안내|지급완료|당첨|결과|보유수량|실사|이용약관|개인정보")
# addendum-1 rule (superseded by addendum 2: it matched boilerplate such as "업데이트 일자"); kept for the record
PLANNED = re.compile(r"업그레이드|하드포크|메인넷|업데이트|정기\s*점검|지갑\s*점검|노드\s*점검|월렛|마이그레이션|스왑|전환|합병|에어드[랍롭]|스냅샷")


def notices():
    rows = {}
    for f in glob.glob(os.path.join(LIST, "*.json")):
        for n in json.load(open(f))["data"]["notices"]:
            rows[n["id"]] = n
    out = []
    for n in rows.values():
        t = int(dt.datetime.fromisoformat(n["first_listed_at"]).timestamp() * 1000)
        if LO <= t < CUT and n["category"] != "NFT":
            n = dict(n, N=t); out.append(n)
    return sorted(out, key=lambda r: (r["N"], r["id"]))


def clean_title(t):
    # edit suffixes added after the post (outcome text) are removed before classification
    return re.sub(r"\s*[-–]?\s*\((완료|기간\s*연장|재개|종료|업데이트|추가|변경|수정|연기|정정|일정\s*변경)[^)]*\)\s*$", "", t).strip()


def classify(title, cat):
    s = clean_title(title).replace(" ", "")
    if cat == "거래" and LISTING.search(s) or cat == "이벤트" and LISTING.search(s):
        return "LISTING"
    if SKIP_TITLE.search(s):
        return "ROUTINE"
    for name, side, rx in CATS:
        if rx.search(s):
            if name == "NETUP" and not re.search(r"중단|지연|제한|지원|안내", s):
                continue
            return name
    return "OTHER"


def spans():
    """perp -> (first trade ms, last active day ms). Minute precision from N0's k1m (first bar with trades)."""
    out = {}
    for p in glob.glob(os.path.join(R, "binance", "perp_1d", "*.csv")):
        s = os.path.basename(p)[:-4]
        with open(p) as f:
            r = csv.reader(f); next(r)
            a = [(int(float(x[0])), float(x[6]) if len(x) > 6 and x[6] else 0.0) for x in r if x]
        act = [t for t, q in a if q > 0 and t < CUT]
        if act:
            out[s] = [act[0] + DAY, act[-1], "1d"]  # day precision: assume launch at the end of the first day
    for p in glob.glob(os.path.join(R, "perp_launch", "k1m", "*.npz")):
        s = os.path.basename(p)[:-4]
        z = np.load(p)
        ot, n = z["ot"], z["n"]
        k = np.where(n > 0)[0]
        if len(k) and s in out and ot[k[0]] < CUT:
            out[s][0] = int(ot[k[0]]); out[s][2] = "1m"
    return out


def perp_for(tk, t, SP):
    b = ALIAS.get(tk, tk)
    for s in (b + "USDT", "1000" + b + "USDT"):
        if s in SP:
            a, z, how = SP[s]
            if a <= t - 7 * DAY and z >= t + DAY:
                return s, (t - a) / DAY, how
    return None, None, None


def coins(title, SP):
    t = clean_title(title)
    tk = re.findall(r"\(([A-Z][A-Z0-9]{1,9})\)", t)
    bare = re.findall(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,9})(?![A-Za-z0-9])", re.sub(r"\([^)]*\)", " ", t))
    tk += [b for b in bare if (b + "USDT") in SP or ("1000" + b + "USDT") in SP or ALIAS.get(b, "") + "USDT" in SP]
    seen = []
    for k in tk:
        if k not in STOP and k not in seen:
            seen.append(k)
    return seen


def build(body_dir=None):
    SP = spans()
    A_nids = {int(r["nid"]) for r in csv.DictReader(open(ANOT))}
    rows = []
    for n in notices():
        c = "LISTING" if n["id"] in A_nids else classify(n["title"], n["category"])
        cs = coins(n["title"], SP)
        if c == "DWSUSP" and body_dir:
            bp = os.path.join(body_dir, f"{n['id']}.json")
            if os.path.exists(bp):
                body = json.load(open(bp))["data"]["body"]
                rs, _ = reason(body)
                # addendum 2: reason sentence of the original notice (reason.py), not boilerplate words
                if rs == "PLANNED":
                    c = "NETUP"
                elif rs == "CHAIN" or re.search(r"네트워크\s*점검", _):
                    c = "DWSUSP"
                else:
                    c = "DWWALLET"
        side = dict((a, b) for a, b, _ in CATS).get(c) if c != "DWWALLET" else None
        base = dict(nid=n["id"], N=n["N"], N_utc=dt.datetime.fromtimestamp(n["N"] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    cat=c, side=side or "", ucat=n["category"], ncoins=len(cs), title=n["title"][:90])
        if not cs:
            rows.append(dict(base, coin="", perp="", age_d="", how=""))
        for k in cs:
            s, age, how = perp_for(k, n["N"], SP)
            rows.append(dict(base, coin=k, perp=s or "", age_d=f"{age:.2f}" if age else "", how=how or ""))
    return rows


def dedupe(rows):
    keep, last = [], {}
    for r in rows:
        if not r["perp"] or r["cat"] in ("LISTING", "ROUTINE") or r["perp"] == "BTCUSDT":
            continue
        k = (r["cat"], r["perp"])
        if k in last and r["N"] - last[k] < 7 * DAY:
            continue
        last[k] = r["N"]; keep.append(r)
    return keep


def era(N):
    return "IS" if N < IS_END else "VAL"


if __name__ == "__main__":
    bd = os.path.join(R, "upbit_census", "raw", "detail")
    rows = build(bd if os.path.isdir(bd) else None)
    F = list(rows[0])
    with open(os.path.join(UC, "events_all.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=F); w.writeheader(); w.writerows(rows)
    kept = dedupe(rows)
    with open(os.path.join(UC, "events_kept.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=F); w.writeheader(); w.writerows(kept)
    nn = collections.Counter(); seen = set()
    for r in rows:
        if r["nid"] not in seen:
            seen.add(r["nid"]); nn[(r["cat"], r["N_utc"][:4])] += 1
    cats = ["LISTING", "ROUTINE"] + [c for c, _, _ in CATS] + ["DWWALLET", "OTHER"]
    print("notices per category and year (2020..2024)")
    for c in cats:
        print(f"  {c:8s}", [nn[(c, str(y))] for y in range(2020, 2025)])
    ck = collections.Counter((r["cat"], r["N_utc"][:4]) for r in kept)
    days = collections.defaultdict(set)
    for r in kept:
        days[(r["cat"], era(r["N"]))].add(r["N_utc"][:10])
    print("kept coin-events with perp >= 7 d (per year 2020..2024; IS / VAL; IS / VAL days)")
    for c in cats[2:]:
        y = [ck[(c, str(y))] for y in range(2020, 2025)]
        print(f"  {c:8s} {y} IS {sum(y[:2])} VAL {sum(y[2:])} days {len(days[(c,'IS')])}/{len(days[(c,'VAL')])}")
