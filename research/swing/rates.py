"""Historical short rates (FRED) and a time-varying swap model for research/swing/swing.py.

Swap per rollover as a fraction of price:
  FX BASEQUOTE : long = (r_base - r_quote)/360 - m_long,   short = (r_quote - r_base)/360 - m_short
  index, metal : long = -r_ccy/360 - m_long,               short = r_ccy/360 - m_short
  energy, crypto: IC's 2026 fraction held constant (their financing follows futures curves / exchange funding)
The markups m are fitted per symbol so the model reproduces the 2026 fraction (research/specs.SWAPS, via
swing.swap_frac) at the mean rates of the fit window 2025-09-01..2026-09-24. Symbols without a calibrated 2026
swap take the mean markup of their class. HKD has no FRED series; HIBOR tracks the USD rate under the peg, so HKD
uses the USD rate (flagged approximate).
"""
import csv
import datetime
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import numpy as np

from research.ticks import DATA_DIR

RATES_DIR = DATA_DIR / "rates"
SERIES = {"USD": "DFF", "EUR": "ECBDFR", "GBP": "IUDSOIA", "JPY": "IRSTCI01JPM156N", "AUD": "IRSTCI01AUM156N",
          "CAD": "IRSTCI01CAM156N", "CHF": "IR3TIB01CHM156N", "NZD": "IR3TIB01NZM156N"}
ALIAS = {"HKD": "USD"}
FIT_START, FIT_END = datetime.date(2025, 9, 1), datetime.date(2026, 9, 24)
DAY_MS = 86_400_000

FX_CCY = {"EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"), "USDJPY": ("USD", "JPY"), "USDCAD": ("USD", "CAD"),
          "AUDUSD": ("AUD", "USD"), "NZDUSD": ("NZD", "USD"), "USDCHF": ("USD", "CHF"), "AUDJPY": ("AUD", "JPY"),
          "EURJPY": ("EUR", "JPY"), "GBPJPY": ("GBP", "JPY")}
IDX_CCY = {"US30": "USD", "USTEC": "USD", "US500": "USD", "DE40": "EUR", "UK100": "GBP", "JP225": "JPY",
           "AUS200": "AUD", "HK50": "HKD", "XAUUSD": "USD", "XAGUSD": "USD", "XPTUSD": "USD"}
CALIBRATED_FX = ("EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD", "AUDJPY", "EURJPY", "GBPJPY")
CALIBRATED_IDX = ("US30", "USTEC", "DE40", "UK100")


def _fetch(series: str) -> Path:
    RATES_DIR.mkdir(parents=True, exist_ok=True)
    path = RATES_DIR / f"{series}.csv"
    if not path.exists():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2014-01-01"
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        if not data.startswith(b"observation_date") and not data.startswith(b"DATE"):
            raise RuntimeError(f"FRED {series}: unexpected response")
        path.write_bytes(data)
    return path


@lru_cache(maxsize=None)
def _series(ccy: str) -> Tuple[np.ndarray, np.ndarray]:
    """(UTC day numbers, rate as a fraction), forward-filled over missing values."""
    ccy = ALIAS.get(ccy, ccy)
    days, vals = [], []
    with open(_fetch(SERIES[ccy])) as fh:
        rd = csv.reader(fh)
        next(rd)
        for d, v in rd:
            try:
                x = float(v)
            except ValueError:
                continue
            days.append((datetime.date.fromisoformat(d) - datetime.date(1970, 1, 1)).days)
            vals.append(x / 100.0)
    return np.asarray(days), np.asarray(vals)


def rate(ccy: str, ms: int) -> float:
    days, vals = _series(ccy)
    k = int(np.searchsorted(days, ms // DAY_MS, side="right")) - 1
    return float(vals[max(k, 0)])


@lru_cache(maxsize=None)
def fit_rate(ccy: str) -> float:
    days, vals = _series(ccy)
    a = (FIT_START - datetime.date(1970, 1, 1)).days
    b = (FIT_END - datetime.date(1970, 1, 1)).days
    sel = (days >= a) & (days <= b)
    return float(vals[sel].mean()) if sel.any() else float(vals[-1])


def _raw_markups(symbol: str, frac_2026: Tuple[float, float]) -> Tuple[float, float]:
    fl, fs = frac_2026
    if symbol in FX_CCY:
        b, q = FX_CCY[symbol]
        d = (fit_rate(b) - fit_rate(q)) / 360.0
        return d - fl, -d - fs
    r = fit_rate(IDX_CCY[symbol]) / 360.0
    return -r - fl, r - fs


@lru_cache(maxsize=None)
def markups(symbol: str) -> Tuple[float, float]:
    from research.swing.swing import swap_frac   # 2026 fractions (calibrated or class-approximated)
    from research.specs import SWAPS
    if symbol in SWAPS:
        return _raw_markups(symbol, swap_frac(symbol)[:2])
    peers = CALIBRATED_FX if symbol in FX_CCY else CALIBRATED_IDX if symbol not in ("XAGUSD", "XPTUSD") else ("XAUUSD",)
    ms = [markups(p) for p in peers]
    return float(np.mean([m[0] for m in ms])), float(np.mean([m[1] for m in ms]))


def swap_frac_at(symbol: str, side: int, ms: int) -> float:
    """Swap per rollover as a fraction of price for a position opened at ms; None-model symbols (energies,
    crypto) keep IC's 2026 fraction."""
    from research.swing.swing import swap_frac
    if symbol in FX_CCY:
        b, q = FX_CCY[symbol]
        ml, msh = markups(symbol)
        d = (rate(b, ms) - rate(q, ms)) / 360.0
        return d - ml if side > 0 else -d - msh
    if symbol in IDX_CCY:
        ml, msh = markups(symbol)
        r = rate(IDX_CCY[symbol], ms) / 360.0
        return -r - ml if side > 0 else r - msh
    fl, fs, _ = swap_frac(symbol)
    return fl if side > 0 else fs
