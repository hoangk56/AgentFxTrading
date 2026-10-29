"""Overview "Coming up" list: the next scheduled entries of the installed Gotobi and ECB window bots.

Times come from the bots' schedule defaults, not from the bots themselves:
- GotobiBot buys at 18:00 UTC (+/- 60 min jitter) the evening before a trading gotobi day and sells at the 00:55 UTC
  Tokyo fix (cBot/GotobiBot.cs Schedule parameters); trading days come from app/gotobi_calendar.py.
- EcbWindowBot sells at 11:00 London; E1 every ECB day, F3 only when 07:00 London calls the day USD-TOP
  (app/gotobi_calendar.is_ecb_day).
The gold level bot trades on price, not on a clock, so it has no entry here.

Handlers are plain `def`: FastAPI runs them in its threadpool, so the DB work never blocks the event loop.
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Set
from zoneinfo import ZoneInfo

from fastapi import APIRouter

from app import gotobi_calendar as gc
from app.accounts import get_account_registry
from app.bot_controls import bot_id_for_config
from app.cbot_presets import installed_cells
from app.portfolio import get_portfolio_manager

router = APIRouter()

LONDON = ZoneInfo("Europe/London")
_GOTOBI_LONG = time(18, 0)          # UTC, the evening before the gotobi day
_GOTOBI_FIX = time(0, 55)           # UTC, the Tokyo fix: the short's entry
_GOTOBI_JITTER_MIN = 60
_ECB_ENTRY_LONDON = time(11, 0)
_HORIZON_DAYS = 14


def upcoming_events(now: datetime, cells: Iterable[Dict], skips: Set[date], limit: int = 4) -> List[Dict]:
    """The next `limit` entries after `now` (UTC) of the installed `cells` (installed_cells rows), earliest first.

    Each: at (UTC ISO), strategy ('gotobi' / 'ecb'), rule (ECB: 'E1' / 'F3'), side ('BUY' / 'SELL'), symbols,
    conditional (F3: only on a USD-TOP day), jitter_min (the Gotobi long's +/- spread).
    """
    gotobi_symbols = sorted({c["symbol"] for c in cells if c["strategy"] == "gotobi"})
    ecb_rules = {gc.ECB_RULE_BY_STRATEGY[c["strategy"]]: c["symbol"] for c in cells
                 if c["strategy"] in gc.ECB_RULE_BY_STRATEGY}
    events = []
    today = now.date()
    for offset in range(_HORIZON_DAYS + 1):
        d = today + timedelta(days=offset)
        if gotobi_symbols and gc.is_trading_day(d, skips):
            long_at = datetime.combine(d - timedelta(days=1), _GOTOBI_LONG, tzinfo=timezone.utc)
            events.append({"at": long_at, "strategy": "gotobi", "rule": None, "side": "BUY",
                           "symbols": gotobi_symbols, "conditional": False, "jitter_min": _GOTOBI_JITTER_MIN})
            events.append({"at": datetime.combine(d, _GOTOBI_FIX, tzinfo=timezone.utc), "strategy": "gotobi",
                           "rule": None, "side": "SELL", "symbols": gotobi_symbols, "conditional": False,
                           "jitter_min": 0})
        for rule, symbol in sorted(ecb_rules.items()):
            if gc.is_ecb_day(d, rule):
                at = datetime.combine(d, _ECB_ENTRY_LONDON, tzinfo=LONDON).astimezone(timezone.utc)
                events.append({"at": at, "strategy": "ecb", "rule": rule, "side": "SELL", "symbols": [symbol],
                               "conditional": rule == "F3", "jitter_min": 0})
    # A jittered long may still come up to jitter_min after its nominal time.
    events = [e for e in events if e["at"] + timedelta(minutes=e["jitter_min"]) > now]
    events.sort(key=lambda e: (e["at"], e["rule"] or ""))
    return [{**e, "at": e["at"].isoformat()} for e in events[:limit]]


def _cells_in_scope(scope: str) -> List[Dict]:
    """Installed cells of a dashboard scope (demo / live / one account_id) whose bot nobody stopped on purpose."""
    registry = get_account_registry()
    pm = get_portfolio_manager()
    configs = {c["name"]: c for c in pm.get_cbot_configs()}
    ctrader = registry.list_ctrader_accounts()
    by_id = {a["id"]: a for a in ctrader}
    account_type: Optional[str] = scope if scope in ("demo", "live") else None
    out = []
    for cell in installed_cells(ctrader, set(configs)):
        acc = by_id[cell["account_id"]]
        if account_type is not None and acc["account_type"] != account_type:
            continue
        if account_type is None and scope != "all" and \
                registry.resolve_account_id(acc["account_number"], acc["account_type"]) != scope:
            continue
        if pm.is_bot_stopped_on_purpose(bot_id_for_config(configs[cell["name"]])):
            continue
        out.append(cell)
    return out


@router.get("/api/overview/upcoming")
def api_overview_upcoming(account_id: str = "all"):
    now = datetime.now(timezone.utc)
    return {"now": now.isoformat(), "events": upcoming_events(now, _cells_in_scope(account_id), gc.skip_dates())}
