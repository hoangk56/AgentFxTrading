"""The live cBots' parameters: the [Parameter] defaults parsed from cBot/*.cs, then the live preset
(app/cbot_presets.py; synthetic crosses borrow a template symbol's), then overrides."""
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from app.cbot_presets import PRESETS
from research.lab.universe import PRESET_TEMPLATE

ROOT = Path(__file__).resolve().parents[2]
BOTS = {"flowrsi": "FlowRsiBot", "judas": "AsianRangeJudasSweepBot", "tms_orb": "AiAgentBot"}
_PARAM = re.compile(r"\[Parameter\([^\n]*?DefaultValue = ([^,)\n]+)[^\n]*\n\s*public ([\w.]+) (\w+)")


def _value(raw: str, typ: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"'):
        return raw.strip('"')
    if raw in ("true", "false"):
        return raw == "true"
    if typ == "int":
        return int(raw)
    if typ in ("double", "float"):
        return float(raw)
    return raw.split(".")[-1]          # enum member: DstRule.US -> "US"


@lru_cache(maxsize=None)
def cbot_defaults(strategy: str) -> Dict[str, Any]:
    src = (ROOT / "cBot" / f"{BOTS[strategy]}.cs").read_text()
    return {name: _value(raw, typ) for raw, typ, name in _PARAM.findall(src)}


def preset(strategy: str, symbol: str) -> dict:
    return PRESETS[(strategy, PRESET_TEMPLATE.get(symbol, symbol))]


def cbot_params(strategy: str, symbol: str, **overrides) -> Dict[str, Any]:
    p = dict(cbot_defaults(strategy))
    p.update(preset(strategy, symbol)["params"])
    p.update(overrides)
    return p
