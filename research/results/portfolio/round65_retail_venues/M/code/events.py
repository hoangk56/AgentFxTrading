"""Stream M event builder (no returns). Declared in ../HYPOTHESES_M.md.
1. Parse every Upbit market-addition notice title (stream W's cache, first_listed_at < 2025-01-01).
2. Candidates: (coin, notice) with BTC or USDT market in the title, 2020-01-01 <= notice < 2024-12-28, Binance USDT-M
   perp trading from >= 7 d before the notice to >= 4 d after (perps.perp_for, local perp_1d cut at 2025-01-01).
3. Upbit 60-min candles (to = notice + 8 d, count 200) for KRW-, BTC-, USDT-<coin>: first candle in the window and
   whether the market already traded before notice - 1 d. 404 = market not listed now (delisted or never).
Usage: python -I events.py probe   (writes ../probe.json)
       python -I events.py build   (writes ../events_M.csv and ../events_krw_extra.csv)"""
import csv, json, os, re, sys, time, calendar, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import titles, perps
HERE = os.path.dirname(os.path.abspath(__file__))
DAY, H = 86400000, 3600000
T0 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
TEND = int(dt.datetime(2024, 12, 28, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUT = 1735689600000
NOT = {"KRW", "BTC", "USDT", "ETH", "NFT", "BLOCKV", "UP", "TRON"}


def tickers(title):
    """Tickers inside parentheses: '(A, B)', '(name A, name B)', 'name(A)'. Market lists like '(BTC, USDT 마켓)' are skipped."""
    out = [t for t in re.findall(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,9})\(", title) if t not in NOT]
    for grp in re.findall(r"\(([^()]*)\)", title):
        if "마켓" in grp:
            continue
        for tok in re.findall(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{1,9})(?![A-Za-z0-9])", grp):
            if tok not in NOT and tok not in out:
                out.append(tok)
    return out


def markets(title):
    m = set()
    if re.search(r"KRW|원화", title):
        m.add("KRW")
    if re.search(r"BTC\s*(,|마켓)|BTC 마켓|, BTC", title) or "BTC," in title:
        m.add("BTC")
    if "USDT" in title and not re.search(r"테더\(USDT\)", title):
        m.add("USDT")
    if "ETH" in title:
        m.add("ETH")
    return m


def addition_notices():
    rows = []
    for i, (t, n) in sorted(titles.notices().items(), key=lambda x: x[1][0]):
        title = n["title"]
        if titles.ADD.search(title) and not re.search(r"종료|유의|입출금|이벤트|에어드|스테이킹|NFT|점검|루머|개선", title):
            rows.append(dict(nid=i, t=int(t.timestamp() * 1000), title=title, mk=markets(title), tk=tickers(title)))
    return rows


def ms(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%S")) * 1000


def iso(t):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t / 1000))


def candidates():
    sp = perps.span()
    out = []
    for r in addition_notices():
        if not (T0 <= r["t"] < TEND) or not ({"BTC", "USDT"} & r["mk"]):
            continue
        for c in r["tk"]:
            s = perps.perp_for(c, r["t"], sp, need_after=4 * DAY)
            if s:
                out.append(dict(coin=c, sym=s, **{k: v for k, v in r.items() if k != "tk"}))
    return out


def probe():
    import fetch
    res = {}
    cands = candidates()
    extra = [("MATIC", 1634270400000), ("POL", 1634270400000), ("AUDIO", 1637208000000), ("GAL", 1673974800000),
             ("GAL", 1720664520000), ("ALT", 1708998300000), ("OMNI", 1714714560000), ("STG", 1717054140000),
             ("BONK", 1732071300000)]
    for c, t in [(x["coin"], x["t"]) for x in cands] + extra:
        for mk in ("KRW", "BTC", "USDT"):
            key = f"{mk}-{c}@{t}"
            if key in res:
                continue
            js = fetch.get(f"https://api.upbit.com/v1/candles/minutes/60?market={mk}-{c}&to={iso(min(t + 8 * DAY, CUT))}&count=200")
            if js is None:
                res[key] = None; continue
            ts = sorted(ms(x["candle_date_time_utc"]) for x in js)
            res[key] = dict(n=len(ts), first=ts[0] if ts else None, before=bool(ts and ts[0] < t - DAY),
                            first_after=next((x for x in ts if x >= t - H), None))
        print(c, iso(t), {mk: res[f"{mk}-{c}@{t}"] for mk in ("KRW", "BTC", "USDT")}, flush=True)
    json.dump(res, open(os.path.join(HERE, "..", "probe.json"), "w"), indent=0)


if __name__ == "__main__":
    if sys.argv[1] == "cands":
        for x in candidates():
            print(x["coin"], x["sym"], iso(x["t"]), x["nid"], sorted(x["mk"]), x["title"][:70])
    elif sys.argv[1] == "probe":
        probe()


def probe_before():
    """For every market that answered 200 in probe(): is there any candle before notice - 1 h? (to = t - 1 h, count 1)"""
    import fetch
    res = json.load(open(os.path.join(HERE, "..", "probe.json")))
    out = {}
    for key, v in res.items():
        if v is None:
            continue
        m, t = key.split("@"); t = int(t)
        js = fetch.get(f"https://api.upbit.com/v1/candles/minutes/60?market={m}&to={iso(t - H)}&count=1")
        out[key] = (ms(js[0]["candle_date_time_utc"]) if js else None)
        print(key, iso(out[key]) if out[key] else "none", flush=True)
    json.dump(out, open(os.path.join(HERE, "..", "probe_before.json"), "w"), indent=0)


if __name__ == "__main__" and sys.argv[1] == "before":
    probe_before()


# ---- build (declared in ../HYPOTHESES_M.md) ----
RENAMED = {("GAL", 3266): "G"}  # BTC-GAL became BTC-G (history kept)
EXCLUDE_PRIOR_ON_UPBIT = True
# delisted markets: L from partner coin in the same notice, or from the stated opening time (WebSearch), floored to hour
PARTNER = {("SNX", 1908): "GRT"}
# mixed "KRW, BTC (A, B)" titles where B got BTC only (declared): AUDIO never had a KRW market or a KRW delisting
# notice; GAL's KRW market (KRW-G, renamed) starts 2024-07-11
BTC_ONLY = {("AUDIO", 2268), ("GAL", 3266)}
SEARCHED = {("BONK", 4574): "2024-10-22T09:00:00", ("JASMY", 4655): "2024-11-20T06:00:00"}
KRW_EXTRA = [  # K2 survivorship check: KRW listings missing from K's list (see HYPOTHESES_M.md)
    dict(coin="MATIC", sym="MATICUSDT", L="2021-10-15T06:00:00", src="KRW-POL first 60m candle (renamed market)"),
    dict(coin="OMNI", sym="OMNIUSDT", L="2024-05-03T09:00:00", src="partner ZETA KRW first 60m candle (same notice)"),
    dict(coin="STG", sym="STGUSDT", L="2024-05-30T07:00:00", src="WebSearch: 16:45 KST opening, floored"),
    dict(coin="BONK", sym="1000BONKUSDT", L="2024-11-20T03:00:00", src="WebSearch: 12:30 KST opening, floored"),
]


def build():
    pr = json.load(open(os.path.join(HERE, "..", "probe.json")))
    bf = json.load(open(os.path.join(HERE, "..", "probe_before.json")))
    import fetch
    prior_notice = {}
    for r in addition_notices():
        for c in r["tk"]:
            prior_notice.setdefault(c, r["t"])
    rows, skipped = [], []
    for x in candidates():
        c, t = x["coin"], x["t"]
        k = lambda mk: pr.get(f"{mk}-{c}@{t}")
        kb = lambda mk: bf.get(f"{mk}-{c}@{t}")
        why = None
        if c in ("USDC",):
            why = "stablecoin"
        elif prior_notice.get(c, t) < t:
            why = "earlier Upbit addition notice"
        elif any(kb(mk) for mk in ("KRW", "BTC", "USDT")):
            why = "Upbit market existed before notice"
        elif k("KRW") and k("KRW")["first_after"] is not None:
            why = "KRW added at this notice (K2 type)"
        elif k("KRW") is None and "KRW" in x["mk"] and (c, x["nid"]) not in BTC_ONLY:
            why = "KRW in title, KRW market delisted: KRW type (survivorship check)"
        if why:
            skipped.append((c, iso(t), why)); continue
        cc = RENAMED.get((c, x["nid"]), c)
        firsts = []
        for mk in ("BTC", "USDT"):
            js = fetch.get(f"https://api.upbit.com/v1/candles/minutes/60?market={mk}-{cc}&to={iso(min(t + 8 * DAY, CUT))}&count=200")
            if js:
                fa = [ms(y["candle_date_time_utc"]) for y in js if ms(y["candle_date_time_utc"]) >= t - H]
                if fa:
                    firsts.append((min(fa), mk))
        if firsts:
            L, mk = min(firsts); src = f"first {mk}-{cc} 60m candle"
        elif (c, x["nid"]) in PARTNER:
            p = PARTNER[(c, x["nid"])]
            L = pr[f"BTC-{p}@{t}"]["first_after"]; mk = "BTC"; src = f"partner {p} first BTC 60m candle"
        elif (c, x["nid"]) in SEARCHED:
            L = ms(SEARCHED[(c, x["nid"])]); mk = "USDT" if "USDT" in x["mk"] else "BTC"; src = "WebSearch opening time"
        else:
            L, mk, src = None, "BTC", "fallback"
        rows.append(dict(coin=c, sym=x["sym"], nid=x["nid"], notice=t, L=L, market=mk, src=src, title=x["title"][:70]))
    # fallback: notice + median lag (notice -> first candle) of the same year's candle-dated events, floored to the hour
    for r in rows:
        if r["L"] is None:
            yr = time.gmtime(r["notice"] / 1000).tm_year
            lags = [q["L"] - q["notice"] for q in rows if q["L"] and q["src"].startswith("first") and time.gmtime(q["notice"] / 1000).tm_year == yr]
            lag = sorted(lags)[len(lags) // 2]
            r["L"] = (r["notice"] + lag) // H * H; r["src"] = f"fallback notice + median {yr} lag {lag / H:.1f} h"
    rows = [r for r in rows if r["L"] < TEND]
    with open(os.path.join(HERE, "..", "events_M.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['coin']:8s} {r['sym']:13s} notice {iso(r['notice'])} L {iso(r['L'])} lag {(r['L'] - r['notice']) / H:5.1f} h  {r['src']}")
    print(len(rows), "M events;", "skipped:")
    for s in skipped:
        print("   ", *s)


if __name__ == "__main__" and sys.argv[1] == "build":
    build()
