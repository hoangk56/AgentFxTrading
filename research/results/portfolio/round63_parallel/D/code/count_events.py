"""Stream D: count event types that need no announcement time (HYPOTHESES_D.md section 1-2).

S: first Binance spot kline of a base whose USDT-M perp traded >= 7 days earlier (spot listing of a perp coin).
P: last perp 1d kline before 2025 (perp delisting), counted only.

Only listing dates are read: no prices, no returns. Perps first listed >= 2025-01-01 are skipped (HOLD stays closed).
Spot first dates come from the data.binance.vision bucket listing (incl. delisted pairs).

Usage: python -I count_events.py
"""
import json, os, re, sys, time, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch import get  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "..", "..", "..", "data")
B = os.path.join(DATA, "binance")
OUT = os.path.join(DATA, "binance_announcements")
DAY = 86400000
CUT = 1735689600000  # 2025-01-01
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
QUOTES = ("USDT", "BUSD", "FDUSD", "USDC", "TUSD", "BTC", "BNB", "ETH")
EXCL = {"USDC", "BTCDOM", "DEFI", "FOOTBALL", "BLUEBIRD", "TUSD", "USDP", "FDUSD", "BUSD"}


def s3_list(prefix, delimiter="/", log=None):
    keys, marker = [], ""
    while True:
        url = f"{S3}?delimiter={delimiter}&prefix={prefix}" + (f"&marker={marker}" if marker else "")
        b = get(url, log)
        time.sleep(0.3)
        if b is None:
            return keys
        root = ET.fromstring(b)
        page = [e.find(NS + "Prefix").text for e in root.findall(NS + "CommonPrefixes")]
        page += [e.find(NS + "Key").text for e in root.findall(NS + "Contents")]
        keys += page
        if root.find(NS + "IsTruncated").text != "true" or not page:
            return keys
        marker = root.find(NS + "NextMarker").text if root.find(NS + "NextMarker") is not None else page[-1]


def perp_span(sym):
    with open(os.path.join(B, "perp_1d", sym + ".csv")) as f:
        next(f)
        rows = [l for l in f if l.strip()]
    if not rows:
        return None
    first = int(float(rows[0].split(",")[0]))
    last_pre = [int(float(r.split(",")[0])) for r in rows if int(float(r.split(",")[0])) < CUT]
    return first, (last_pre[-1] if last_pre else None), int(float(rows[-1].split(",")[0]))


def base_of(sym):
    b = sym[:-4]
    for pre in ("1000000", "1000", "1M"):
        if b.startswith(pre) and len(b) > len(pre) and not b[len(pre)].isdigit():
            return b[len(pre):], b
    return b, b


def main():
    log = open(os.path.join(OUT, "requests.log"), "a", buffering=1)
    cache = os.path.join(OUT, "spot_symbols.json")
    if os.path.exists(cache):
        spot = set(json.load(open(cache)))
    else:
        pre = s3_list("data/spot/monthly/klines/", log=log)
        spot = {p.rstrip("/").split("/")[-1] for p in pre}
        json.dump(sorted(spot), open(cache, "w"))
    print("spot symbols ever:", len(spot), flush=True)
    firsts_path = os.path.join(OUT, "spot_first_month.json")
    firsts = json.load(open(firsts_path)) if os.path.exists(firsts_path) else {}
    perps = sorted(f[:-4] for f in os.listdir(os.path.join(B, "perp_1d")) if f.endswith("USDT.csv"))
    rows = []
    for sym in perps:
        sp = perp_span(sym)
        if sp is None or sp[0] >= CUT:
            continue
        base, raw = base_of(sym)
        if base in EXCL or raw in EXCL:
            continue
        cands = sorted({b + q for b in {base, raw} for q in QUOTES} & spot)
        fm = []
        for c in cands:
            if c not in firsts:
                ks = s3_list(f"data/spot/monthly/klines/{c}/1d/", log=log)
                ms = sorted(re.findall(r"(\d{4}-\d{2})\.zip$", k)[0] for k in ks if k.endswith(".zip"))
                firsts[c] = [ms[0], ms[-1]] if ms else None
                json.dump(firsts, open(firsts_path, "w"))
            if firsts[c]:
                fm.append((firsts[c][0], c))
        rows.append((sym, sp, min(fm) if fm else None, fm))
    # exact first day for perp-first candidates (spot first month >= perp first month)
    out = []
    for sym, (p0, plast, pend), fm, allfm in rows:
        if fm is None:
            out.append((sym, p0, plast, pend, None, None))
            continue
        pm = time.strftime("%Y-%m", time.gmtime(p0 / 1000))
        if fm[0] < pm:
            out.append((sym, p0, plast, pend, fm[1], "spot_first_month_before_perp"))
            continue
        best = None  # earliest first day over every pair whose first month is the earliest month
        for m, c in allfm:
            if m != fm[0]:
                continue
            ks = s3_list(f"data/spot/daily/klines/{c}/1d/", log=log)
            ds = sorted(re.findall(r"(\d{4}-\d{2}-\d{2})\.zip$", k)[0] for k in ks if k.endswith(".zip"))
            d = ds[0] if ds else m + "-01"
            if best is None or d < best[0]:
                best = (d, c)
        out.append((sym, p0, plast, pend, best[1], best[0]))
    with open(os.path.join(OUT, "event_dates.csv"), "w") as f:
        f.write("perp,perp_first,perp_last_pre2025,perp_last_any_flag,spot_pair,spot_first_day\n")
        for sym, p0, plast, pend, sp, d0 in out:
            f.write(f"{sym},{p0},{plast},{int(pend >= CUT)},{sp or ''},{d0 or ''}\n")
    print("rows", len(out))


if __name__ == "__main__":
    main()
