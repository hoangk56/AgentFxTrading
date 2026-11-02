"""Stream JP events, frozen in HYPOTHESES_JP.md before any price. One event per (venue, coin): N = post time of the
venue's FIRST public notice that it will list the coin (2020-24), L = post time of the venue's own "trading has
started" notice (the actual start, published at the start). Coin screen: Binance USDT-M perp whose first daily kline
<= N - 7 d and which still trades at N + 1 d (local perp_1d). Upbit overlap: the coin appears in an Upbit listing
title (stream A's listing_titles.json, any market) within 7 days of N."""
import csv, json, os, re
import numpy as np
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/jp_notices"
P1D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance/perp_1d"
UPB = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/listing_titles.json"
END = 1735689600000
DAY = 86400000
IS_END = 1640995200000

# (venue, coins, first-notice id, start-notice id); ids refer to bitbank_all.csv / coincheck_news.csv
BITBANK = [
    ("XLM", "20200910", "20200916"), ("QTUM", "202101_03", "202101_07"), ("BAT", "202103_01", "202103_03"),
    ("OMG", "202106_05", "202107_02"), ("XYM", "20210904", "20211003"), ("LINK", "275046194", "390342243"),
    ("BOBA", "589267477", "238894809"), ("MKR", "953882525", "300630689"), ("ENJ", "210278415", "501280519"),
    ("MATIC", "835797825", "218355874"), ("DOT", "614293404", "916497775"), ("DOGE", "614293404", "916497775"),
    ("FLR", "810372954", "296369657"), ("ASTR", "349559937", "593764699"), ("ADA", "431097742", "191259582"),
    ("AVAX", "681221175", "738930768"), ("AXS", "235762097", "474632791"), ("SAND", "682920796", "454865947"),
    ("OAS", "365371475", "979692342"), ("APE", "684265328", "924878620"), ("GALA", "684265328", "924878620"),
    ("CHZ", "684265328", "924878620"), ("MANA", "169709926", "205363383"), ("GRT", "", "797632065"),
    ("RNDR", "948727300", "282688480"), ("BNB", "376756918", "983746042"), ("ARB", "959507890", "251693309"),
    ("OP", "959507890", "251693309"), ("DAI", "959507890", "251693309"), ("KLAY", "959507890", "251693309"),
    ("IMX", "959507890", "251693309"), ("MASK", "257818961", ""), ("SOL", "790023809", "753695577"),
    ("CYBER", "790023809", "753695577"),
]
GRT_NOTICE = "2023-06-12T06:12:59.000Z"   # maintenance-tagged first notice (bitbank_all.csv)
MASK_START = "2024-02-08T05:23:53.000Z"   # maintenance-tagged start notice (bitbank_all.csv)
# Coincheck (corporate.coincheck.com press / news publishedAt). N = first press notice of the new coin; L = the
# later "本日より取扱いを開始" news stamp when one exists; else the start-day news stamp (CHZ / LINK); else, for
# same-day notices whose body gives no later clock time ("本日午後", "正午" already passed), L = N + 60 min (brief).
# P10 = press stamps of 2020 - mid 2021 sit at 01:00:00 UTC (10:00 JST) in 96 % of 2020 press: possibly a date-only
# placeholder; kept, flagged, and reported with and without.
CC = [  # coin, N slug (press), N iso, L iso or None (= N + 60 min), stamp class
    ("QTUM", "RwTkH-0P", "2020-02-25T01:00:00.000Z", "2020-03-12T02:57:03.000Z", "P10"),
    ("BAT", "sTLoZwss", "2020-07-13T01:00:00.000Z", "2020-07-21T03:00:47.000Z", "P10"),
    ("IOST", "rSzMt2Xd", "2020-09-01T01:00:00.000Z", "2020-09-08T03:04:51.000Z", "P10"),
    ("ENJ", "WVNlxS62", "2021-01-19T01:00:00.000Z", "2021-01-26T03:06:45.000Z", "P10"),
    ("OMG", "5WSzd4ij", "2021-04-07T01:00:00.000Z", None, "P10"),
    ("PLT", "8riNEns7", "2021-07-26T01:00:00.000Z", "2021-07-29T03:04:28.000Z", "P10"),
    ("SAND", "xW_GBJkj", "2022-05-24T03:40:01.000Z", None, "s"),
    ("DOT", "4jiGnGnC", "2022-08-23T03:09:34.000Z", "2022-09-01T04:46:24.000Z", "s"),
    ("FNCT", "7sMr4zLT", "2023-03-16T03:16:21.000Z", None, "s"),
    ("CHZ", "GQfdgLef", "2023-04-19T03:05:03.000Z", "2023-04-26T04:40:00.000Z", "s"),
    ("LINK", "GQfdgLef", "2023-04-19T03:05:03.000Z", "2023-04-26T04:40:00.000Z", "s"),
    ("DAI", "FD9iKiAt", "2023-06-16T07:10:25.000Z", "2023-06-20T05:45:11.000Z", "s"),
    ("MKR", "FD9iKiAt", "2023-06-16T07:10:25.000Z", "2023-06-20T05:45:11.000Z", "s"),
    ("MATIC", "9lr3Aq75", "2023-07-24T08:08:51.000Z", "2023-08-08T04:39:29.000Z", "s"),
    ("IMX", "B0cwfLkn", "2023-09-21T03:42:53.000Z", None, "s"),
    ("APE", "B0cwfLkn", "2023-09-21T03:42:53.000Z", None, "s"),
    ("AXS", "B0cwfLkn", "2023-09-21T03:42:53.000Z", None, "s"),
    ("WBTC", "bUO6ZDnn", "2023-10-06T08:04:54.000Z", "2023-10-11T04:31:53.000Z", "s"),
    ("AVAX", "1eXqL0l2", "2023-12-07T03:32:02.000Z", None, "s"),
    ("SHIB", "gDMWFg9B", "2023-12-14T03:31:32.000Z", None, "s"),
    ("BRIL", "845cJpb5", "2024-05-20T06:20:07.000Z", "2024-06-17T03:38:53.000Z", "s"),
    ("BC", "PMJPLO_e", "2024-10-16T02:35:34.000Z", None, "s"),
]
ALIAS = {"SHIB": "1000SHIB"}
COINCHECK = [dict(venue="coincheck", coin=c, N_iso=n, L_iso=l, stamp=k, src=sl) for c, sl, n, l, k in CC]


def ms(iso):
    return int(np.datetime64(iso.replace("Z", ""), "ms").astype(np.int64))


def perp_ok(coin, N):
    coin = ALIAS.get(coin, coin)
    f = os.path.join(P1D, coin + "USDT.csv")
    if not os.path.exists(f):
        return None, "no perp"
    t = np.loadtxt(f, delimiter=",", skiprows=1, usecols=(0,))
    t = t[t < END]
    if not len(t) or t[0] > N - 7 * DAY:
        return None, "perp < 7 d"
    if not ((t >= N + DAY - DAY) & (t <= N + 2 * DAY)).any() and not (t > N + DAY).any():
        return None, "no trading at N + 1 d"
    return coin + "USDT", f"perp {int((N - t[0]) / DAY)} d"


def upbit(coin, N):
    for x in json.load(open(UPB)):
        t = ms(x["t_utc"].replace(" ", "T"))
        if abs(t - N) <= 7 * DAY and re.search(r"[\s(,]" + coin + r"[\s),]", " " + x["title"] + " "):
            return f"{x['id']}"
    return "-"


def screen():
    bb = {r["id"]: r["published_at_utc"] for r in csv.DictReader(open(os.path.join(D, "bitbank_all.csv")))}
    out = []
    for coin, n_id, l_id in BITBANK:
        n_iso = bb[n_id] if n_id else GRT_NOTICE
        l_iso = bb[l_id] if l_id else MASK_START
        out.append(dict(venue="bitbank", coin=coin, N_iso=n_iso, L_iso=l_iso, stamp="s", src=n_id or "GRT"))
    out += COINCHECK
    rows = []
    for e in out:
        N = ms(e["N_iso"])
        L = ms(e["L_iso"]) if e["L_iso"] else N + 3600000
        assert N < END and L < END and L > N
        perp, why = perp_ok(e["coin"], N)
        rows.append(dict(e, N=N, L=L, perp=perp, why=why, upbit=upbit(e["coin"], N)))
    return rows


def load_events():
    E = []
    for r in screen():
        if r["perp"] is None:
            continue
        r.update(era="IS" if r["N"] < IS_END else "VAL", year=r["N_iso"][:4], day=r["N_iso"][:10], Lhow="start notice")
        E.append(r)
    return E


if __name__ == "__main__":
    for r in screen():
        print(f"{r['venue']:9s} {r['coin']:6s} {r['stamp']:3s} N {r['N_iso']}  L {r['L_iso'] or 'N+60m':24s}  {(r['L']-r['N'])/3.6e6:7.1f} h  {r['why']:14s} upbit {r['upbit']}")
