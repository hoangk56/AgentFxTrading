"""Stream W7: build the listing event list from metadata only (no price, no return).
Steps (all requests dated <= 2024-12; logged by net.py):
 1. Binance spot USDT pairs whose first 1d kline is 2020-01-01..2024-12-30: spot_first.csv (coins that ever had a USDT-M
    perp) plus, for the other data.binance.vision USDT symbols, the coins with a Bybit linear perp (first day from the
    first monthly 1d kline file on data.binance.vision).
 2. Drop stablecoins, leveraged tokens, stock tokens and the declared rename / swap list.
 3. New-coin filter: drop the pair if any other quote pair of the same base traded on an earlier day (first day from
    spot_first_month.json or from data.binance.vision monthly 1d files).
 4. Reference perps: Binance USDT-M perp first day (perp_1d, incl. delisted) and, if none on or before the listing
    day, the first public.bybit.com/trading dump day of the Bybit linear perp.
Output: research/data/listing_window/meta/events_meta.csv. Run with python -I."""
import csv, io, json, os, re, sys, zipfile, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
M = os.path.join(net.D, "meta")
os.makedirs(M, exist_ok=True)
CACHE = os.path.join(M, "probe_cache.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
D0, D1 = dt.date(2020, 1, 1), dt.date(2024, 12, 30)
STABLE = {"USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "PAX", "EUR", "AEUR", "GBP", "AUD", "UST", "USDS", "BKRW",
          "SUSD", "EURI", "BFUSD", "USD1", "XUSD", "RLUSD", "USDE", "PAXG", "WBTC", "WBETH", "BETH", "BNSOL"}
# Renames / token swaps / redenominations of coins already trading on Binance (declared, from memory, before data):
RENAME = {"AAVE", "EGLD", "FIRO", "BTTC", "XEC", "STRAX", "RENDER", "POL", "LUNC", "USTC", "BCH", "BEAMX", "T", "G",
          "MULTI", "OOKI", "COCOS", "DREP", "BSV", "S"}
# (list corrected ~18:29 UTC after seeing the excluded names only, before any price: ANT, GTC, ALPACA, WAXP, VIDT, QI,
#  REI, PROM, ID, NEIRO, 1000SATS, ACA, BONDLY, TORN, MDT, LUNA2 were new listings, not renames; they now go through
#  the older-pair filter)
QUOTES = ["BTC", "ETH", "BNB", "BUSD", "USDC", "TUSD", "PAX", "USDS", "FDUSD", "TRY", "EUR", "GBP", "AUD", "BRL", "RUB",
          "NGN", "BIDR", "IDRT", "UAH", "ZAR", "DAI", "BKRW", "VAI", "XRP", "TRX", "DOGE", "DOT", "JPY", "PLN", "RON",
          "ARS", "COP", "MXN", "CZK", "USDP", "AEUR", "BVND", "GYEN", "UST", "EURI"]
PREF = ["", "1000", "10000", "100000", "1000000", "1M"]


def save():
    json.dump(cache, open(CACHE, "w"))


def day(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).date()


def first_day_monthly(sym, month):
    """First day of sym's monthly 1d kline file for month 'YYYY-MM' (None if the file does not exist)."""
    assert month <= "2024-12"
    k = f"fd:{sym}:{month}"
    if k in cache:
        return None if cache[k] is None else dt.date.fromisoformat(cache[k])
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1d/{sym}-1d-{month}.zip"
    b, s = net.get(url, "meta first-day")
    v = None
    if b is not None:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            row = z.read(z.namelist()[0]).split(b"\n")[0].split(b",")
        t = int(row[0])
        if t > 1e14:
            t //= 1000
        v = day(t).isoformat()
    elif s != 404:
        raise SystemExit(f"unexpected status {s} {url}")
    cache[k] = v; save()
    return None if v is None else dt.date.fromisoformat(v)


def prev_month(m):
    y, mm = int(m[:4]), int(m[5:])
    return f"{y - 1}-12" if mm == 1 else f"{y}-{mm - 1:02d}"


def pair_first_before(sym, L, fm):
    """True if sym traded on a day before L (date)."""
    m = L.strftime("%Y-%m")
    if sym in fm:
        f0 = fm[sym][0]
        if f0 < m:
            return True
        if f0 > m:
            return False
        d = first_day_monthly(sym, m)
        return d is not None and d < L
    if first_day_monthly(sym, prev_month(m)) is not None:
        return True
    d = first_day_monthly(sym, m)
    return d is not None and d < L


def bybit_first_day(sym):
    k = f"by:{sym}"
    if k in cache:
        return None if cache[k] is None else dt.date.fromisoformat(cache[k])
    b, s = net.get(f"https://public.bybit.com/trading/{sym}/", "meta bybit dir")
    v = None
    if b is not None:
        ds = sorted(set(re.findall(rb"(\d{4}-\d{2}-\d{2})\.csv\.gz", b)))
        ds = [x.decode() for x in ds if x.decode() <= "2024-12-31"]
        v = ds[0] if ds else None
    cache[k] = v; save()
    return None if v is None else dt.date.fromisoformat(v)


def main():
    syms = set(json.load(open(os.path.join(R, "binance_announcements/spot_symbols.json"))))
    fm = json.load(open(os.path.join(R, "binance_announcements/spot_first_month.json")))
    sf = {r[0]: int(r[1]) for r in csv.reader(open(os.path.join(R, "binance/spot_first.csv"))) if len(r) > 1 and r[1].isdigit()}
    perp_first = {}
    for f in os.listdir(os.path.join(R, "binance/perp_1d")):
        with open(os.path.join(R, "binance/perp_1d", f)) as fh:
            for row in csv.reader(fh):
                if row and row[0].isdigit():
                    perp_first[f[:-4]] = int(row[0]); break
    by = set()
    for fn in ("instruments_linear.json", "instruments_linear_closed.json"):
        for x in json.load(open(os.path.join(R, "bybit_basis", fn))):
            if x.get("contractType") == "LinearPerpetual" and x.get("quoteCoin") == "USDT" and int(x["launchTime"]) < 1735689600000:
                by.add(x["symbol"])

    def perps_for(base, pool):
        core = re.sub(r"^(1000000|100000|10000|1000|1M)(?=[A-Z])", "", base)
        out = []
        for b in {base, core}:
            for p in PREF:
                s = p + b + "USDT"
                if s in pool and s not in out:
                    out.append(s)
        return out

    cands = {}
    for s, t in sf.items():
        if D0 <= day(t) <= D1:
            cands[s] = (day(t), "spot_first")
    extra = [s for s in syms if s.endswith("USDT") and s not in sf]
    for s in sorted(extra):
        b = s[:-4]
        if re.search(r"(UP|DOWN|BULL|BEAR)$", b) or b in STABLE or (b.endswith("B") and b[:-1] + "BUSDT" == s and False):
            continue
        if not perps_for(b, by):
            continue
        f0 = fm.get(s, [None])[0]
        if f0 is not None:
            if not ("2020-01" <= f0 <= "2024-12"):
                continue
            d = first_day_monthly(s, f0)
        else:
            # walk months 2020-01..2024-12 (only for Bybit-perp coins; few)
            d = None
            for y in range(2020, 2025):
                for mm in range(1, 13):
                    d = first_day_monthly(s, f"{y}-{mm:02d}")
                    if d is not None:
                        break
                if d is not None:
                    break
            if d is not None and d == dt.date(2020, 1, 1):
                d = None  # traded before 2020 (file starts on the 1st): not a 2020-24 listing
        if d is not None and D0 <= d <= D1:
            cands[s] = (d, "dbv_probe")
    rows = []
    for s, (L, src) in sorted(cands.items(), key=lambda x: x[1][0]):
        b = s[:-4]
        why = ""
        if b in STABLE or re.search(r"(UP|DOWN|BULL|BEAR)$", b):
            why = "stable/leveraged"
        elif b in RENAME:
            why = "rename/swap"
        else:
            for q in QUOTES:
                p = b + q
                if p in syms and pair_first_before(p, L, fm):
                    why = f"older pair {p}"; break
        bp = [p for p in perps_for(b, set(perp_first)) if day(perp_first[p]) <= L]
        bp_first = min((day(perp_first[p]) for p in bp), default=None)
        bpsym = min(bp, key=lambda p: perp_first[p]) if bp else ""
        bysym, by_first = "", None
        if not why and (bp_first is None or bp_first >= L):
            for p in perps_for(b, by):
                f = bybit_first_day(p)
                if f is not None and f <= L and (by_first is None or f < by_first):
                    bysym, by_first = p, f
        rows.append(dict(sym=s, L_day=L.isoformat(), src=src, excluded=why, bn_perp=bpsym,
                         bn_perp_first=bp_first.isoformat() if bp_first else "", by_perp=bysym,
                         by_first=by_first.isoformat() if by_first else ""))
    with open(os.path.join(M, "events_meta.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # counts
    from collections import Counter
    c = Counter()
    for r in rows:
        y = r["L_day"][:4]
        if r["excluded"]:
            c[(y, "excl:" + r["excluded"].split()[0])] += 1; continue
        c[(y, "new")] += 1
        if r["bn_perp_first"] and r["bn_perp_first"] <= r["L_day"]:
            c[(y, "bn_perp_on_or_before_day")] += 1
        elif r["by_first"]:
            c[(y, "bybit_only")] += 1
        else:
            c[(y, "no_hedge")] += 1
    for k in sorted(c):
        print(k, c[k])


if __name__ == "__main__":
    main()
