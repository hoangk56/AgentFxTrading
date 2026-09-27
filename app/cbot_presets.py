"""
Strategy × symbol presets for the dashboard's "Setup Instances" screen.

Gotobi (GotobiBot) trades only the three JPY pairs the research validated
(research/results/portfolio/swing_lab_v2_2026-09-27.md) and Crypto Donchian (CryptoDonchianBot, research C1,
forward test) only BTCUSD and ETHUSD, so the grid has 5 cells. All 5 are written out as `docker run` commands
in docs/docker-instances.md, which tests/app/test_cbot_presets.py keeps in sync with this module. `params`
holds only the strategy-tuned flags. Infrastructure flags (credentials, symbol, period, BotId, ApiUrl,
AccountLabel) are emitted by `build_run_command`, so a preset never knows which account runs it.
"""
from typing import Collection, Dict, Iterable, List, Tuple

DEFAULT_IMAGE = "ghcr.io/spotware/ctrader-console:latest"
# The bots derive every server URL from this one (/api/tick, /portfolio/report, /api/cbot/commands) by
# replacing or stripping the trailing /trade, so the suffix stays although the server has no /trade route.
API_URL = "http://127.0.0.1:8000/trade"

STRATEGIES: Dict[str, Dict[str, str]] = {
    "gotobi":  {"label": "Gotobi Fix",  "algo": "GotobiBot.algo",               "suffix": "-gotobi"},
    "donchian": {"label": "Crypto Donchian", "algo": "CryptoDonchianBot.algo",   "suffix": "-donchian"},
}

# Row order of the setup grid.
SYMBOLS: List[str] = ["USDJPY", "EURJPY", "GBPJPY", "BTCUSD", "ETHUSD"]

_GOTOBI_SESSION = "Tokyo fix"
_DONCHIAN_SESSION = "H4 breakout"


def _gotobi(max_spread: float, risk: float = 50.0) -> dict:
    return {"RiskPerTradeMoney": risk, "MaxSpreadPips": max_spread}


def _cell(period: str, session: str, params: dict) -> dict:
    return {"period": period, "session": session, "params": params}


# (strategy, SYMBOL) -> {"period", "session", "params"}; 3 gotobi + 2 donchian cells.
PRESETS: Dict[Tuple[str, str], Dict] = {
    # Gotobi (GotobiBot) — research C3: the schedule and the 3 x ATR20(H1) stop are the cBot's defaults; a cell
    # sets the default $ risk per trade (never a share of equity) and the entry spread cap (GBPJPY quotes wider).
    ("gotobi", "USDJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=3.0)),
    ("gotobi", "EURJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=3.0)),
    ("gotobi", "GBPJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=4.0)),
    # Crypto Donchian (CryptoDonchianBot) — research C1, which failed its 2025-26 holdout: a small forward-test bot.
    # Channels, stop, lot scaling and the spread cap (a share of the stop, so no pips) are the cBot's defaults; a
    # cell sets only the default $ risk per trade (x0.5..2 by breakout strength, never a share of equity). $100 is the
    # research's; much less does not size BTCUSD: its minimum 0.01 BTC already risks ~$30-40 at a 3 x ATR(H4) stop.
    # The chart is H1: the bot builds UTC-aligned H4 bars from H1 (the broker's H4 bars start at its 21/22:00 UTC day).
    ("donchian", "BTCUSD"): _cell("h1", _DONCHIAN_SESSION, {"RiskPerTradeMoney": 100.0}),
    ("donchian", "ETHUSD"): _cell("h1", _DONCHIAN_SESSION, {"RiskPerTradeMoney": 100.0}),
}


def _fmt(value) -> str:
    """Render a param value the way the README writes it: true/false, bare numbers, "quoted strings"."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return f'"{value}"'


# Preset "session" label -> the token `container_name` puts after the symbol, so `docker ps` shows
# which session a bot trades without reading its --SessionName flag.
SESSION_SLUGS: Dict[str, str] = {
    _GOTOBI_SESSION: "fix",
    _DONCHIAN_SESSION: "h4",
}


def container_name(slug: str, strategy: str, symbol: str) -> str:
    session = SESSION_SLUGS[PRESETS[(strategy, symbol)]["session"]]
    return f"cbot-{slug}-{symbol.lower()}-{session}{STRATEGIES[strategy]['suffix']}"


def describe_cell(strategy: str, symbol: str, account_label: str) -> str:
    return f"{STRATEGIES[strategy]['label']} {symbol} {PRESETS[(strategy, symbol)]['period']} — {account_label}"


def build_run_command(account: dict, strategy: str, symbol: str, project_root: str, ctrader_home: str,
                      image: str = DEFAULT_IMAGE) -> str:
    """Single-line `docker run` for one preset cell. `account` needs slug, ctid_email, account_number, label, pwd_file."""
    preset = PRESETS[(strategy, symbol)]
    name = container_name(account["slug"], strategy, symbol)
    parts = [
        "docker", "run", "-d", "--name", name, "--restart", "unless-stopped", "--network", "host",
        "-v", f"{project_root}:/workspace", "-v", f"{ctrader_home}:/root",
        image, "run", f"/workspace/cBot/{STRATEGIES[strategy]['algo']}",
        f"--ctid={account['ctid_email']}", f"--pwd-file={account['pwd_file']}", f"--account={account['account_number']}",
        f"--symbol={symbol}", f"--period={preset['period']}", "--full-access",
        f'--BotId="{name}"', f'--ApiUrl="{API_URL}"', f'--AccountLabel="{account["label"]}"',
    ]
    parts += [f"--{key}={_fmt(value)}" for key, value in preset["params"].items()]
    return " ".join(parts)


def installed_cells(accounts: Iterable[dict], config_names: Collection[str]) -> List[dict]:
    """Preset cells that already have a cbot_configs row, attributed to the account whose slug named them.

    One row per (cell, account): the same cell can be installed for several accounts. Configs not
    named by `container_name` (hand-written, or from a since-deleted account) are not reported.
    Ordered by the grid (PRESETS order) then by `accounts` order, so the UI needs no sorting.
    """
    accounts = list(accounts)
    rows = []
    for (strategy, symbol) in PRESETS:
        for account in accounts:
            name = container_name(account["slug"], strategy, symbol)
            if name in config_names:
                rows.append({
                    "symbol": symbol, "strategy": strategy, "name": name,
                    "account_id": account["id"], "account_label": account["label"],
                    "account_type": account["account_type"],
                })
    return rows


def presets_payload() -> dict:
    """What GET /api/setup/presets returns: the grid, without params."""
    return {
        "strategies": STRATEGIES,
        "symbols": SYMBOLS,
        "cells": [
            {"symbol": symbol, "strategy": strategy, "period": cell["period"], "session": cell["session"]}
            for (strategy, symbol), cell in PRESETS.items()
        ],
    }
