"""Round 71 FS: shared constants, symbol eligibility, perp listing days (../HYPOTHESES_FS.md)."""
import csv
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))  # research/
DATA = os.path.join(R, "data", "spot_wicks")
PERP = os.path.join(R, "data", "binance", "perp_1d")
OUT = os.path.join(HERE, "..", "out")
T0 = 1577836800000            # 2020-01-01
END = 1735689600000           # 2025-01-01 exclusive
VAL0_MS = 1640995200000
MIN = 60000
DAY = 86400000
NM = (END - T0) // MIN
VAL0 = (VAL0_MS - T0) // MIN
ND = (END - T0) // DAY        # days 2020-01-01..2024-12-31
BP = 1e4

STABLE = {"USDC", "BUSD", "TUSD", "USDP", "PAX", "DAI", "UST", "USTC", "FDUSD", "SUSD", "USDS", "USDSB", "EUR", "GBP",
          "AUD", "TRY", "BRL", "AEUR", "EURI", "XUSD", "USD1", "PAXG", "XAUT", "BKRW", "BIDR", "IDRT", "RUB", "UAH",
          "NGN", "ZAR", "BVND", "VAI", "USDE", "RLUSD", "PYUSD", "BFUSD", "USDF"}
EXCL_BASE = {"USDC", "BTCDOM", "DEFI", "FOOTBALL", "BLUEBIRD", "TUSD", "USDP", "FDUSD", "EUR", "BUSD", "USD1", "XUSD",
             "XAU", "XAG", "PAXG", "XAUT", "TSLA", "NVDA", "AAPL", "MSTR", "COIN", "HOOD", "AMZN", "GOOGL", "META",
             "MSFT", "CRCL", "SPY", "QQQ", "XPT", "XPD", "OIL", "CL", "NATGAS"}  # round 60 listings.EXCL_BASE


def spot_list():
    rows = list(csv.DictReader(open(os.path.join(DATA, "spot_usdt_symbols.csv"))))
    return [(r["symbol"], r["base"]) for r in rows]


def leveraged(base, bases):
    if base.endswith(("DOWN", "BULL", "BEAR")):
        return True
    return base.endswith("UP") and len(base) > 2 and (base[:-2] + "DOWN") in bases


def perp_base(sym):
    b = sym[:-4]
    for p in ("1000000", "1000", "1M"):
        if b.startswith(p) and len(b) > len(p):
            b = b[len(p):]
            break
    return {"LUNA2": "LUNA"}.get(b, b)


def perp_first_day():
    """coin base -> first perp daily-kline day index (days since 2020-01-01; negative = before 2020)."""
    out = {}
    for f in glob.glob(os.path.join(PERP, "*USDT.csv")):
        s = os.path.basename(f)[:-4]
        with open(f) as fh:
            fh.readline()
            ln = fh.readline()
        if not ln:
            continue
        d = (int(ln.split(",")[0]) - T0) // DAY
        b = perp_base(s)
        out[b] = min(out.get(b, 10 ** 6), d)
    return out


def eligible_symbols():
    """spot USDT pairs that are not stable / fiat / leveraged / excluded; with their base and first perp day."""
    L = spot_list()
    bases = {b for _, b in L}
    pf = perp_first_day()
    out = []
    for s, b in L:
        if b in STABLE or b in EXCL_BASE or leveraged(b, bases):
            continue
        out.append((s, b, pf.get(b, 10 ** 6)))
    return out


def candidate_symbols():
    """eligible pairs whose coin had no perp before 2020-01-02 (else never in the universe)."""
    return [s for s, b, d in eligible_symbols() if d > 0]
