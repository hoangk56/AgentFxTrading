"""Stream A event builder (no prices). KRW-market listing notices 2020-01-01..2024-12-31 (UTC) from Upbit notice bodies
(api-manager.upbit.com, first_listed_at = original post time, KST -> UTC). Per coin: markets from the body (HTML table,
'- KRW 마켓 : A, B', '- X : KRW, BTC 마켓', else '원화 마켓에 X 추가/상장' -> all title coins KRW). Keeps coins with a KRW
market, not a stablecoin, whose Binance USDT-M perp traded >= 7 d before the notice (W/perps.py logic). Output
A/notice_events.csv. L (first KRW 1m candle) is added by pull_first.py."""
import os, re, json, glob, csv, datetime as dt, sys
sys.path.insert(0, os.path.dirname(__file__))
import perps
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_announce/raw/detail"
OUT = os.path.join(os.path.dirname(__file__), "..")
CUT = 1735689600000
LO = 1577836800000  # 2020-01-01
ALIAS = {"BEAM": "BEAMX"}  # Upbit ticker -> Binance perp base where they differ
STABLE = {"USDT", "USDC", "DAI", "TUSD", "BUSD", "USDP", "PAX"}
TK = r"((?=[A-Z0-9]{0,9}[A-Z])[A-Z0-9]{1,10})"


def markets(d):
    b, title = d["body"].replace("\xa0", " ").replace("\r", ""), d["title"]
    out = {}
    k = b.find("<table")
    if k >= 0:
        tb = b[k:b.find("</table>", k)]
        for name, mk in re.findall(r"<td>([^<]*)</td>\s*<td>([^<]*)</td>", tb):
            m = re.search(r"\(" + TK + r"\)", name)
            if m and re.search(r"KRW|BTC|USDT", mk):
                out[m.group(1)] = set(re.findall(r"KRW|BTC|USDT", mk))
        if out:
            return out, "table"
    for l in b.split("\n"):
        s = l.strip().lstrip("-").strip()
        m = re.match(r"^((?:KRW|BTC|USDT)(?:\s*,\s*(?:KRW|BTC|USDT))*)\s*마켓\s*:\s*(.+)$", s)
        if m and not re.search(r"\d[,.]\d|\d\s*(원|KRW|BTC|USDT)\b|→", m.group(2)):
            for t in re.findall(r"\b" + TK + r"\b", re.sub(r"\([^)]*\)", "", m.group(2))):
                out.setdefault(t, set()).update(re.findall(r"KRW|BTC|USDT", m.group(1)))
            continue
        m = re.match(r"^" + TK + r"\s*:\s*((?:KRW|BTC|USDT)[ ,A-Z마켓]*마켓)\s*$", s)
        if m:
            out.setdefault(m.group(1), set()).update(re.findall(r"KRW|BTC|USDT", m.group(2)))
    if out:
        return out, "lines"
    if re.search(r"(원화\s*마켓(, BTC 마켓)?|KRW[, A-Z]*마켓)에[^\n]*(추가|상장)", b):
        mk = {"KRW"} | ({"BTC"} if re.search(r"KRW, BTC 마켓에|원화마켓, BTC 마켓에", b) else set())
        tks = re.findall(r"[ (,]" + TK + r"(?=[,)])", "(" + title.split("(", 1)[1] if "(" in title else "")
        tks = [t for t in tks if t not in ("KRW", "BTC", "USDT")]
        return {t: set(mk) for t in tks}, "prose"
    return out, "none"


def start_time(d, coin):
    """Stated trading start (KST) for the coin if the body gives one (latest stated value wins: postponements are
    posted above the original text, so the first match in the body is the newest). Returns ms UTC or None."""
    b = d["body"].replace("\xa0", " ").replace("\r", ""); y = int(d["first_listed_at"][:4])
    pats = [r"(?:연기된|변경된|변경\s*:)\s*[^\n]*?(20\d\d)-(\d\d)-(\d\d)[^\n\d]*(\d{1,2}):(\d\d)",
            r"거래지원 개시 시점\s*:\s*(20\d\d)-(\d\d)-(\d\d)[^\n\d]*?(\d{1,2}):(\d\d)"]
    for p in pats:
        m = re.search(p, b)
        if m:
            Y, Mo, D, h, mi = map(int, m.groups()); break
    else:
        m = None
        k = b.find("<table")
        if k >= 0:
            tb = b[k:b.find("</table>", k)]
            for row in re.findall(r"<tr>(.*?)</tr>", tb, flags=re.S):
                if "(" + coin + ")" in row:
                    m = re.search(r"(\d{1,2})월\s*(\d{1,2})일\s*(\d{1,2})시(?:\s*(\d{1,2})분)?", row)
            if m:
                Mo, D, h = map(int, m.groups()[:3]); mi = int(m.group(4) or 0); Y = y
        if not m:
            return None
    return int(dt.datetime(Y, Mo, D, h, mi, tzinfo=dt.timezone(dt.timedelta(hours=9))).timestamp() * 1000)


def build():
    SP = perps.span(); rows = []; skipped = []
    for f in sorted(glob.glob(os.path.join(RAW, "*.json")), key=lambda x: int(os.path.basename(x)[:-5])):
        d = json.load(open(f))["data"]
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        if not (LO <= t < CUT):
            continue
        mk, how = markets(d)
        for coin, m in sorted(mk.items()):
            if "KRW" not in m:
                skipped.append((d["id"], coin, "no KRW market")); continue
            if coin in STABLE:
                skipped.append((d["id"], coin, "stablecoin")); continue
            s = perps.perp_for(ALIAS.get(coin, coin), t, SP)
            st = start_time(d, coin)
            r = dict(nid=d["id"], coin=coin, N=t, N_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                     stated=st or "", stated_utc=dt.datetime.fromtimestamp(st / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M") if st else "",
                     perp=s or "", how=how, title=d["title"][:70])
            (rows if s else skipped).append(r if s else (d["id"], coin, "no perp >= 7 d before N"))
    # Declared secondary source: 2020 KRW opens whose 거래 notice is absent from the list but whose 이벤트 notice
    # ("원화마켓 오픈 ... 이벤트") is present; first_listed_at of the event notice is used as N (flag src=event).
    EV = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_announce/raw/detail_event"
    for f in sorted(glob.glob(os.path.join(EV, "*.json"))):
        d = json.load(open(f))["data"]
        t = int(dt.datetime.fromisoformat(d["first_listed_at"]).timestamp() * 1000)
        coin = re.search(r"\(([A-Z0-9]{2,10})\)", d["title"]).group(1)
        s = perps.perp_for(coin, t, SP)
        if s and t < CUT:
            rows.append(dict(nid=d["id"], coin=coin, N=t, N_utc=dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                             stated="", stated_utc="", perp=s, how="event", title=d["title"][:70]))
    for r in rows:
        r.setdefault("src", "event" if r["how"] == "event" else "trade")
    rows.sort(key=lambda r: (r["N"], r["coin"]))
    return rows, skipped


if __name__ == "__main__":
    rows, skipped = build()
    with open(os.path.join(OUT, "notice_events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r["nid"], r["coin"], r["N_utc"], r["stated_utc"], r["perp"], r["how"], r["title"][:45])
    print(len(rows), "kept;", len(skipped), "skipped")
    for s in skipped:
        print("  skip", s)
