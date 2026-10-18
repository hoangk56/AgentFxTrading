"""
Strategy × symbol presets for the dashboard's "Setup Instances" screen.

Gotobi (GotobiBot) trades only the three JPY pairs the research validated
(research/results/portfolio/swing_lab_v2_2026-09-27.md); the ECB window (EcbWindowBot) only EURUSD, as F3 (USD-TOP days,
research/results/portfolio/round24_relaxed/PREREG_R24_relaxed_hold.md) or E1 (every weekday,
research/results/portfolio/round13_structural/PREREG_M_eurusd_midday.md); the gold level bot (GoldLevelBot) only XAUUSD
(research/results/portfolio/round27_levels_opens/PREREG_G_gold_round50_cascade.md). So the grid has 6 cells. All 6 are
written out as `docker run` commands in docs/docker-instances.md, which tests/app/test_cbot_presets.py keeps in sync with
this module. `params`
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
    # One cBot, two rules: the suffix (and the preset's UsdTopOnly) tells them apart.
    "ecb_f3":  {"label": "ECB Window F3", "algo": "EcbWindowBot.algo",          "suffix": "-f3"},
    "ecb_e1":  {"label": "ECB Window E1", "algo": "EcbWindowBot.algo",          "suffix": "-e1"},
    "gold_levels": {"label": "Gold $50 Levels", "algo": "GoldLevelBot.algo",    "suffix": "-gold50"},
}

# Row order of the setup grid.
SYMBOLS: List[str] = ["USDJPY", "EURJPY", "GBPJPY", "EURUSD", "XAUUSD"]

_GOTOBI_SESSION = "Tokyo fix"
_ECB_SESSION = "ECB fix window"
_GOLD_SESSION = "Round levels"

# Gotobi days the bot sits out. Japanese public holidays and the 31/12 bank holiday have no Tokyo fix, and on the 45
# such days of 2016-2026 the basket lost (R -0.066, t -3.4; research/results/portfolio/gotobi_jp_holidays_2026-09-29.md).
# 2026-12-25 is the cBot's own default (the broker is closed at the fix), which a value passed in replaces. Extend the
# list each year with `python -m research.tools.gotobi_holidays --upcoming`.
GOTOBI_SKIP_DATES = "2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31"

# Broker stop = the real 3 x ATR stop instead of the cBot's random 0.8-1.0x: the tight stop cost ~1.4 % of the real
# legs' net over 2020-2026 (research/results/portfolio/gotobi_broker_stop_jitter_2026-10-15.md). The entry jitter stays.
GOTOBI_BROKER_STOP_MIN = 1.0


def _gotobi(max_spread: float, risk: float = 100.0) -> dict:
    return {"RiskPerTradeMoney": risk, "MaxSpreadPips": max_spread, "SkipDates": GOTOBI_SKIP_DATES,
            "EmergencyStopMin": GOTOBI_BROKER_STOP_MIN}


# A far broker stop for a bot or VPS that dies with a position open; the rule itself has no stop (it exits at 13:00
# London). Touched by 0.11 % (3) of E1's trades in 2016-2026; no F3 result changes at 100 pips
# (research/results/portfolio/ecb_window_cbot_2026-10-16.md).
ECB_BROKER_STOP_PIPS = 100.0


def _ecb(usd_top_only: bool, lots: float) -> dict:
    return {"UsdTopOnly": usd_top_only, "Lots": lots, "EmergencyStopPips": ECB_BROKER_STOP_PIPS}


# A far broker stop for a dead bot; the rule has none (it exits 30 minutes after the trigger). The largest adverse move
# of any 2016-2026 trade before its exit was $54 (1.1 % of the price), so no trade touches $100
# (research/results/portfolio/gold_level_cbot_2026-10-18.md).
GOLD_BROKER_STOP_USD = 100.0


def _gold(lots: float) -> dict:
    return {"Lots": lots, "EmergencyStopUsd": GOLD_BROKER_STOP_USD}


def _cell(period: str, session: str, params: dict) -> dict:
    return {"period": period, "session": session, "params": params}


# (strategy, SYMBOL) -> {"period", "session", "params"}; the 3 gotobi cells, the 2 ECB-window ones and gold.
PRESETS: Dict[Tuple[str, str], Dict] = {
    # Gotobi (GotobiBot) — research C3: the schedule and the 3 x ATR20(H1) stop are the cBot's defaults; a cell
    # sets the default $ risk per trade (never a share of equity; $100 is the research's), the entry spread cap
    # (GBPJPY quotes wider), the days with no Tokyo fix and the broker stop's lower bound.
    ("gotobi", "USDJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=3.0)),
    ("gotobi", "EURJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=3.0)),
    ("gotobi", "GBPJPY"): _cell("m15", _GOTOBI_SESSION, _gotobi(max_spread=4.0)),
    # ECB window (EcbWindowBot): sell EURUSD 11:00 -> 13:00 London; the schedule and the USD-TOP selector are the
    # cBot's defaults. F3 runs live at the minimum lot (a measurement, not a sized bet: it is a RELAXED candidate
    # that has not met its promotion rule); E1 runs on demo at 0.1 lot. Lots are fixed, never from the account.
    ("ecb_f3", "EURUSD"): _cell("m15", _ECB_SESSION, _ecb(usd_top_only=True, lots=0.01)),
    ("ecb_e1", "EURUSD"): _cell("m15", _ECB_SESSION, _ecb(usd_top_only=False, lots=0.1)),
    # Gold $50 levels (GoldLevelBot): a stop order just past a fresh $50 level, closed 30 minutes after it triggers; the
    # rule and the release calendar (cBot/seeds/usd_high_calendar.csv) are the cBot's defaults. A DEMO candidate, so it
    # runs on demo at the minimum lot (1 oz): the evidence is in bp per trade and the fills, not in dollars.
    ("gold_levels", "XAUUSD"): _cell("m15", _GOLD_SESSION, _gold(lots=0.01)),
}


def _fmt(value) -> str:
    """Render a param value the way docs/docker-instances.md writes it: true/false, bare numbers, "quoted strings"."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return f'"{value}"'


# Preset "session" label -> the token `container_name` puts after the symbol, so `docker ps` shows
# which session a bot trades without reading its --SessionName flag.
SESSION_SLUGS: Dict[str, str] = {
    _GOTOBI_SESSION: "fix",
    _ECB_SESSION: "ecb",
    _GOLD_SESSION: "levels",
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
