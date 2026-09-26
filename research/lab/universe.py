"""The lab's symbols: fixed units, contract data, quote currencies and the synthetic crosses.

Real symbols take pip, tick size, commission and swaps from research/specs.py (fitted on the 2026 cTrader
reports). A synthetic cross is built from two USD legs (research/lab/feed.py); its commission is the broker's
$30 per million per side on the base currency, its swaps are the legs' swaps weighted by the legs' exposure
at 2025-26 median prices (approximate, like every swap before 2026)."""
from dataclasses import dataclass, replace
from typing import Dict, Optional, Tuple

from research.specs import SPECS, SWAPS, SymbolSpec

REAL = ("AUDJPY", "AUDUSD", "BTCUSD", "DE40", "ETHUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD",
        "UK100", "US30", "USDCAD", "USDJPY", "USTEC", "XAUUSD")
FX_REAL = ("AUDJPY", "AUDUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD", "USDCAD", "USDJPY")
INDICES = ("DE40", "UK100", "US30", "USTEC")
# (leg A, leg B, op): "mul" -> A x B, "div" -> A / B
SYNTHETIC: Dict[str, Tuple[str, str, str]] = {
    "EURGBP": ("EURUSD", "GBPUSD", "div"),
    "EURAUD": ("EURUSD", "AUDUSD", "div"),
    "GBPAUD": ("GBPUSD", "AUDUSD", "div"),
    "EURCAD": ("EURUSD", "USDCAD", "mul"),
    "GBPCAD": ("GBPUSD", "USDCAD", "mul"),
    "AUDCAD": ("AUDUSD", "USDCAD", "mul"),
    "CADJPY": ("USDJPY", "USDCAD", "div"),
}
# Real crosses rebuilt from their legs to check the method (research/lab/check_crosses.py).
CHECK_CROSSES = {"EURJPY": ("EURUSD", "USDJPY", "mul"), "GBPJPY": ("GBPUSD", "USDJPY", "mul"),
                 "AUDJPY": ("AUDUSD", "USDJPY", "mul")}
FX = FX_REAL + tuple(SYNTHETIC)
ALL = REAL + tuple(SYNTHETIC)

FIXED_UNITS = {**{s: 10_000.0 for s in FX}, "XAUUSD": 2.0, "BTCUSD": 0.1, "ETHUSD": 4.0,
               "US30": 0.2, "USTEC": 0.4, "DE40": 0.4, "UK100": 0.8}
QUOTE_CCY = {"AUDJPY": "JPY", "EURJPY": "JPY", "GBPJPY": "JPY", "USDJPY": "JPY", "CADJPY": "JPY",
             "USDCAD": "CAD", "EURCAD": "CAD", "GBPCAD": "CAD", "AUDCAD": "CAD",
             "EURGBP": "GBP", "UK100": "GBP", "EURAUD": "AUD", "GBPAUD": "AUD", "DE40": "EUR"}
# quote currency -> (conversion pair, True when that pair is quoted in USD per unit of the currency)
CONVERSION = {"JPY": ("USDJPY", False), "CAD": ("USDCAD", False), "EUR": ("EURUSD", True),
              "GBP": ("GBPUSD", True), "AUD": ("AUDUSD", True)}
# Live-preset donor for the symbols the bots do not trade.
PRESET_TEMPLATE = {"EURGBP": "EURUSD", "EURAUD": "EURUSD", "GBPAUD": "GBPUSD", "EURCAD": "EURUSD",
                   "GBPCAD": "GBPUSD", "AUDCAD": "AUDUSD", "CADJPY": "AUDJPY"}
# 2025-26 medians, used where a constant is enough (commission, swap weights, the FlowRSI SymbolSpec).
REF_PRICE = {"EURUSD": 1.16, "GBPUSD": 1.34, "AUDUSD": 0.66, "USDCAD": 1.39, "USDJPY": 154.8,
             "EURGBP": 0.865, "EURAUD": 1.76, "GBPAUD": 2.03, "EURCAD": 1.61, "GBPCAD": 1.86,
             "AUDCAD": 0.915, "CADJPY": 111.6}
COMMISSION_PER_SIDE = 30e-6          # USD per USD of base notional
# Real / synthetic mean-spread ratio measured on EURJPY, GBPJPY, AUDJPY (research/lab/check_crosses.py,
# 2026-09-25: 1.55, 1.22, 1.26; mid difference < 0.1 bp): the broker's crosses are wider than the legs imply.
SYNTH_SPREAD_FACTOR = 1.26


@dataclass(frozen=True)
class Instrument:
    symbol: str
    pip: float
    tick_size: float
    units: float              # the lab's fixed volume in cTrader units
    comm_per_unit: float      # USD per unit, round trip
    quote_ccy: str
    swap_long: float          # USD per unit per rollover
    swap_short: float
    triple_weekday: int
    cross: Optional[Tuple[str, str, str]] = None

    @property
    def synthetic(self) -> bool:
        return self.cross is not None

    def mirrored(self) -> "Instrument":
        """Prices mirrored: a long position now earns what a short one did."""
        return replace(self, swap_long=self.swap_short, swap_short=self.swap_long)

    def spec(self) -> SymbolSpec:
        """research.specs.SymbolSpec for the FlowRSI simulator (constant USD per quote). A synthetic cross is
        named after its preset donor: the simulator looks swaps up by name for its own running net, which the lab
        does not use (it rebuilds P&L from the fills)."""
        if self.symbol in SPECS:
            return SPECS[self.symbol]
        pair, direct = CONVERSION[self.quote_ccy]
        usd_per_quote = REF_PRICE[pair] if direct else 1.0 / REF_PRICE[pair]
        return SymbolSpec(PRESET_TEMPLATE[self.symbol], self.pip, self.tick_size, 1000, 1000, self.comm_per_unit,
                          usd_per_quote)


def _base_usd(symbol: str) -> float:
    return {"EUR": REF_PRICE["EURUSD"], "GBP": REF_PRICE["GBPUSD"], "AUD": REF_PRICE["AUDUSD"],
            "CAD": 1.0 / REF_PRICE["USDCAD"]}[symbol[:3]]


def _synthetic_swaps(symbol: str) -> Tuple[float, float]:
    """(long, short) USD per unit. One unit long of the cross = w_a units of leg A and w_b of leg B (sign = side)."""
    a, b, op = SYNTHETIC[symbol]
    if op == "mul":                   # EURCAD = EURUSD x USDCAD: long 1 EURUSD and EURUSD-worth of USDCAD
        w_a, w_b = 1.0, REF_PRICE[a]
    elif symbol == "CADJPY":          # USDJPY / USDCAD: long and short 1/USDCAD of each leg
        w_a, w_b = 1.0 / REF_PRICE["USDCAD"], -1.0 / REF_PRICE["USDCAD"]
    else:                             # EURGBP = EURUSD / GBPUSD: long 1 EURUSD, short EURGBP-worth of GBPUSD
        w_a, w_b = 1.0, -REF_PRICE[symbol]

    def leg(sym: str, w: float, long_cross: bool) -> float:
        long_rate, short_rate, _ = SWAPS[sym]
        return abs(w) * (long_rate if (w > 0) == long_cross else short_rate)

    return leg(a, w_a, True) + leg(b, w_b, True), leg(a, w_a, False) + leg(b, w_b, False)


def instrument(symbol: str) -> Instrument:
    if symbol in SPECS:
        s = SPECS[symbol]
        long_rate, short_rate, triple = SWAPS[symbol]
        return Instrument(symbol, s.pip, s.tick_size, FIXED_UNITS[symbol], s.comm_per_unit,
                          QUOTE_CCY.get(symbol, "USD"), long_rate, short_rate, triple)
    if symbol in SYNTHETIC:
        jpy = symbol.endswith("JPY")
        long_rate, short_rate = _synthetic_swaps(symbol)
        return Instrument(symbol, 0.01 if jpy else 0.0001, 0.001 if jpy else 0.00001, FIXED_UNITS[symbol],
                          2 * COMMISSION_PER_SIDE * _base_usd(symbol), QUOTE_CCY[symbol], long_rate, short_rate, 2,
                          SYNTHETIC[symbol])
    raise KeyError(symbol)
