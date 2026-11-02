"""Real-money R per trade of a live research algorithm sized by risk (Gotobi C3), for the research screen.

The forward trackers in app/forward_status.py cover the bp rules; an R rule that went straight to real money has no
tracker, so its "Chạy thật" bar would stay empty. This reads its bots' closed live trades instead.

R of a trade = signed price move / stop distance, from the real fills: spread is in, commission is not. Only real legs
count: a Gotobi leg is real when it falls in an entry window of a trading gotobi day (the Calendar screen's rule,
app/gotobi_calendar.py) and its close reason is not a decoy's; decoys and anything else are left out, not counted as
skipped. A trade without a stop distance or a price is skipped and counted.
"""
import re
from typing import Dict, List, Optional

from app.close_reasons import DECOY_PREFIX
from app.db import get_db_connection
from app.forward_status import forward_t
from app.gotobi_calendar import is_trading_day, leg_of, skip_dates
from app.ledger import parse_utc

_BRACES = re.compile(r"\{([^{}]*)\}")


def expand_bots(pattern: Optional[str]) -> List[str]:
    """Shell-style brace expansion of a registry `bot` field: "a-{x,y}-b" -> ["a-x-b", "a-y-b"]."""
    text = str(pattern or "").strip()
    if not text:
        return []
    m = _BRACES.search(text)
    if not m:
        return [text]
    return [name for part in m.group(1).split(",")
            for name in expand_bots(text[:m.start()] + part.strip() + text[m.end():])]


def pip_size(symbol: str) -> float:
    return 0.01 if "JPY" in str(symbol or "").upper() else 0.0001


def trade_r(row: Dict) -> Optional[float]:
    """The trade's R from its fills and stop distance; None without a stop or a price."""
    try:
        entry, exit_, sl = float(row["entry_price"]), float(row["exit_price"]), float(row.get("sl_pips") or 0)
    except (TypeError, ValueError, KeyError):
        return None
    if sl <= 0 or entry <= 0 or exit_ <= 0:
        return None
    sign = 1.0 if str(row.get("side") or "").lower().startswith("b") else -1.0
    return (exit_ - entry) * sign / (sl * pip_size(row.get("symbol")))


def _real_leg(row: Dict, skips) -> bool:
    if str(row.get("close_reason") or "").startswith(DECOY_PREFIX):
        return False
    if "gotobi" not in str(row.get("bot_id") or "").lower():
        return True
    entry = parse_utc(row.get("entry_time"))
    leg = leg_of(row.get("side"), entry) if entry else None
    return bool(leg) and is_trading_day(leg[1], skips)


def live_r_status(bot_pattern: Optional[str], since: Optional[str], db_target=None) -> Dict:
    """{n, mean, forward_t, skipped} over the bots' closed trades on live accounts, exited on or after `since`."""
    bots = expand_bots(bot_pattern)
    out = {"n": 0, "mean": None, "forward_t": None, "skipped": 0}
    if not bots:
        return out
    sql = ("SELECT bot_id, symbol, side, entry_price, exit_price, sl_pips, entry_time, exit_time, close_reason "
           "FROM positions WHERE status = 'closed' AND bot_id IN (" + ", ".join("?" for _ in bots) + ") "
           "AND account_id IN (SELECT account_id FROM accounts WHERE account_type = 'live' AND is_configured = 1)")
    params: List = list(bots)
    if since:
        sql += " AND exit_time >= ?"
        params.append(since)
    conn = get_db_connection(db_target)
    try:
        rows = [dict(r) for r in conn.execute(sql + " ORDER BY exit_time", params).fetchall()]
    finally:
        conn.close()
    skips = skip_dates()
    values = []
    for row in rows:
        if not _real_leg(row, skips):
            continue
        r = trade_r(row)
        if r is None:
            out["skipped"] += 1
        else:
            values.append(r)
    if values:
        out.update(n=len(values), mean=sum(values) / len(values), forward_t=forward_t(values))
    return out
