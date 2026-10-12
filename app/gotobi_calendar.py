"""Gotobi calendar: the GotobiBot's gotobi days and its trades, by the gotobi day each position was opened for.

The rules mirror cBot/GotobiBot.cs with the presets' schedule (the cBot's defaults):
- a gotobi day is the 5th/10th/15th/20th/25th or the month's last day, a weekend one moved to the Friday before
  (GotobiBot.IsGotobi); a trading day is a gotobi day that is not in the presets' SkipDates (Japanese holidays);
- a buy entered in the long window the evening before (17:00-23:05 UTC) is the long of the next day; a sell entered
  just after that day's 00:55 UTC fix (to 01:03) is its short (GotobiBot.InferLeg);
- the bot trades a day that is not a trading day only as a decoy (camouflage), so those positions are kept apart.

The dashboard's Gotobi view (static/js/gotobi_calendar.js) draws the month; app/gotobi_calendar_api.py serves it.
"""
import calendar
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Set, Tuple

from app.cbot_presets import GOTOBI_SKIP_DATES
from app.ledger import parse_utc

BOT_SUFFIX = "-gotobi"

# GotobiBot schedule defaults: long entry 18:00 +/- 60 min jitter to 23:00 UTC the day before, fix 00:55 UTC with
# 3 grace minutes; the bot's InferLeg adds 5 minutes of slack to both windows for the fill time.
_LONG_WINDOW = (time(17, 0), time(23, 5))
_SHORT_WINDOW = (time(0, 55), time(1, 3))


def is_gotobi(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    last = calendar.monthrange(d.year, d.month)[1]
    for day in (5, 10, 15, 20, 25, last):
        moved = date(d.year, d.month, day)
        while moved.weekday() >= 5:
            moved -= timedelta(days=1)
        if moved == d:
            return True
    return False


def parse_skip_dates(text: str) -> Set[date]:
    out = set()
    for part in (text or "").replace(";", ",").replace(" ", ",").split(","):
        try:
            out.add(date.fromisoformat(part.strip()))
        except ValueError:
            continue
    return out


def skip_dates() -> Set[date]:
    return parse_skip_dates(GOTOBI_SKIP_DATES)


def is_trading_day(d: date, skips: Set[date]) -> bool:
    return is_gotobi(d) and d not in skips


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def leg_of(side: str, entry: datetime) -> Optional[Tuple[str, date]]:
    """(leg, gotobi day) of a position by its side and UTC entry time, or None outside both entry windows or for a
    weekend day (the bot never trades one, GotobiBot.PlanLeg)."""
    t = entry.time()
    if str(side or "").upper().startswith("B"):
        day = entry.date() + timedelta(days=1)
        if _LONG_WINDOW[0] <= t <= _LONG_WINDOW[1] and day.weekday() < 5:
            return "long", day
    elif _SHORT_WINDOW[0] <= t <= _SHORT_WINDOW[1]:
        return "short", entry.date()
    return None


def month_bounds(month: str) -> Tuple[date, date]:
    """First and last day of 'YYYY-MM'; ValueError when it is not one."""
    year, mon = month.split("-")
    if len(year) != 4 or len(mon) != 2:
        raise ValueError(month)
    first = date(int(year), int(mon), 1)
    if not 2000 <= first.year <= 2100:
        raise ValueError(month)
    return first, date(first.year, first.month, calendar.monthrange(first.year, first.month)[1])


def _bucket() -> Dict:
    return {"n": 0, "pnl": 0.0, "open": 0}


def _add(bucket: Dict, pos: Dict) -> None:
    bucket["n"] += 1
    if pos.get("status") == "closed":
        bucket["pnl"] = round(bucket["pnl"] + float(pos.get("pnl") or 0.0), 2)
    else:
        bucket["open"] += 1


def month_calendar(month: str, positions: Iterable[Dict], skips: Set[date], today: date,
                   vn_time=lambda ts: ts) -> Dict:
    """The weekdays of `month` with their gotobi status and the Gotobi positions of each, real and decoy apart.

    status: 'traded' (a trading day with a real position), 'scheduled' (a trading day today or later with none yet),
    'no-trade' (a past trading day without one), 'skipped' (a gotobi day in SkipDates), 'plain' (not gotobi).
    A position outside the bot's entry windows (a manual trade, say) is listed on its entry day as leg None.
    """
    first, last = month_bounds(month)
    by_day: Dict[date, List[Dict]] = {}
    for pos in positions:
        entry = parse_utc(pos.get("entry_time"))
        if entry is None:
            continue
        leg = leg_of(pos.get("side"), entry)
        day = leg[1] if leg else entry.date()
        if not first <= day <= last:
            continue
        by_day.setdefault(day, []).append({
            "id": pos.get("id"), "bot_id": pos.get("bot_id"), "account_id": pos.get("account_id"),
            "symbol": pos.get("symbol"), "side": pos.get("side"), "volume": pos.get("volume"),
            "leg": leg[0] if leg else None, "decoy": bool(leg) and not is_trading_day(day, skips),
            "status": pos.get("status"), "pnl": pos.get("pnl"),
            "entry_time": pos.get("entry_time"), "exit_time": pos.get("exit_time"),
            "entry_time_vn": vn_time(pos.get("entry_time")), "exit_time_vn": vn_time(pos.get("exit_time")),
        })

    days, totals = [], {"gotobi_days": 0, "traded_days": 0, "real_trades": 0, "real_pnl": 0.0,
                        "decoy_trades": 0, "decoy_pnl": 0.0}
    d = first
    while d <= last:
        if d.weekday() < 5:
            trades = sorted(by_day.get(d, []), key=lambda t: str(t["entry_time"]))
            real, decoy, other = _bucket(), _bucket(), _bucket()
            for t in trades:
                _add(decoy if t["decoy"] else real if t["leg"] else other, t)
            gotobi = is_gotobi(d)
            if gotobi and d in skips:
                status = "skipped"
            elif not gotobi:
                status = "plain"
            elif real["n"]:
                status = "traded"
            else:
                status = "scheduled" if d >= today else "no-trade"
            totals["gotobi_days"] += gotobi
            totals["traded_days"] += status == "traded"
            totals["real_trades"] += real["n"]
            totals["real_pnl"] = round(totals["real_pnl"] + real["pnl"], 2)
            totals["decoy_trades"] += decoy["n"]
            totals["decoy_pnl"] = round(totals["decoy_pnl"] + decoy["pnl"], 2)
            days.append({"date": d.isoformat(), "weekday": d.weekday(), "gotobi": gotobi, "skipped": d in skips,
                         "status": status, "real": real, "decoy": decoy, "other": other, "trades": trades})
        d += timedelta(days=1)
    return {"month": month, "today": today.isoformat(), "days": days, "totals": totals}
