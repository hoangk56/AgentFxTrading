"""Paper desk runner: computes the day's features from Dukascopy, asks the analysts (DeepSeek, OpenAI-compatible API)
for a call per symbol and records them (app/paper_desk.py). See docs/paper-desk.md for the registered terms.

    python -m app.paper_desk_runner run [--date YYYY-MM-DD] [--dry-run]    # before 07:00 UTC
    python -m app.paper_desk_runner score

Environment: DEEPSEEK_API_KEY (required for `run`), PAPER_DESK_MODEL (default deepseek-chat), PAPER_DESK_BASE_URL
(default https://api.deepseek.com), PAPER_DESK_DATA (cache directory). The key is read from the environment only and is
never written, logged or put in a prompt. A model call that fails, or answers something invalid, is recorded as
direction 0 with the reason, never skipped: leaving failures out would select the calls that survive.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from app import paper_desk, paper_desk_status
from app.dukascopy import Bar, Dukascopy, cache_dir_from_env

# Round-trip cost in bp per symbol: IC commission plus a typical spread, rounded up. Registered assumptions of the
# experiment (docs/paper-desk.md), to be replaced by measured medians; they only set the bar the calls must clear.
# Round-trip bp (long, short): spread + commission + overnight swap, measured 2026-10-29 by
# research/tools/paper_desk_costs.py (research/results/portfolio/paper_desk_costs_2026-10-29.md).
COST_BP: Dict[str, Tuple[float, float]] = {
    "EURUSD": (1.58, 0.64), "USDJPY": (0.67, 2.12), "GBPJPY": (0.92, 2.24),
    "XAUUSD": (2.55, 0.77), "US500": (0.68, 0.68), "BTCUSD": (9.29, 1.69)}
CALENDAR = Path(__file__).resolve().parent.parent / "cBot" / "seeds" / "usd_high_calendar.csv"
HISTORY_DAYS = 30
MAX_STALE_HOURS = 3
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"

ANALYSTS: Dict[str, str] = {
    "trend": "You favour continuation: trade with the recent direction when 1d, 5d and 20d returns agree and the "
             "move is large against the cost.",
    "meanrev": "You favour reversion: trade against stretched moves, when price sits at an extreme of its 20-day "
               "range and the last 24h was large against the typical daily range.",
    "risk": "You are the risk officer: you answer 0 (no trade) unless the numbers clearly justify a trade, and you "
            "answer 0 when a high-impact USD release falls inside the next 24 hours or volatility is unusual.",
}
CHIEF = "chief"

SYSTEM = (
    "You are the {role} analyst of a paper-trading experiment. You see only numbers computed from prices; do not use "
    "outside facts or news. Horizon: from 07:00 UTC today to 07:00 UTC on the next weekday. Round-trip cost for this "
    "symbol is {cost} bp, so only trade when you expect a larger move. {style}\n"
    'Reply with JSON only: {{"direction": -1 | 0 | 1, "confidence": 0..1, "rationale": "at most 200 characters"}}. '
    "0 means no trade.")

Llm = Callable[[str, str], str]     # (system, user) -> the model's text


# ---------------- features ----------------

def usd_events(first: dt.datetime, last: dt.datetime, path: Path = CALENDAR) -> List[str]:
    out = []
    if not path.exists():
        return out
    with open(path, newline="") as f:
        for row in csv.reader(r for r in f if not r.startswith("#")):
            if len(row) < 2:
                continue
            try:
                t = dt.datetime.fromisoformat(row[0]).replace(tzinfo=dt.timezone.utc)
            except ValueError:
                continue
            if first <= t < last:
                out.append(f"{row[0][11:16]} {row[1]}")
    return out


def _bp(a: float, b: float) -> float:
    return (a / b - 1.0) * 1e4


def price_at(hours: List[Bar], ts: dt.datetime, max_gap_hours: int = 2) -> Optional[float]:
    """Open of the first hourly bar starting at `ts` or up to `max_gap_hours` later, else None."""
    ms = int(ts.timestamp() * 1000)
    for bar in hours:
        if bar[0] >= ms:
            return bar[1] if bar[0] - ms <= max_gap_hours * 3600_000 else None
    return None


def features(hours: List[Bar], call_date: str, events: Optional[List[str]] = None) -> Optional[dict]:
    """Numbers the analysts see, from the hourly bars of complete UTC days, i.e. closed before 00:00 UTC of call_date.
    Dukascopy's free feed publishes a day's file only after the day is over, so nothing later exists at run time; the
    entry is 07:00 UTC, 7 hours after the last bar. None without enough bars or when the newest bar is stale."""
    entry = paper_desk.entry_time(call_date)
    asof = entry.replace(hour=0)
    ms = int(asof.timestamp() * 1000)
    h = [b for b in hours if b[0] < ms]
    if len(h) < 24 * 15 or ms - h[-1][0] > MAX_STALE_HOURS * 3600_000:
        return None                             # too little history, or the newest bar is stale
    last = h[-1][4]
    snaps = []                                  # price at 07:00 UTC of the previous calendar days, newest first
    for k in range(1, HISTORY_DAYS + 1):
        p = price_at(h, asof - dt.timedelta(days=k))
        if p is not None:
            snaps.append(p)
    if len(snaps) < 15:
        return None
    day_range = []
    for i in range(0, len(h) - 23, 24):
        chunk = h[i:i + 24]
        day_range.append(_bp(max(b[2] for b in chunk), min(b[3] for b in chunk)))
    last20 = h[-24 * 20:]
    lo, hi = min(b[3] for b in last20), max(b[2] for b in last20)
    last24 = h[-24:]
    typical = day_range[-14:]
    return {
        "ret_1d_bp": round(_bp(last, snaps[0]), 1),
        "ret_5d_bp": round(_bp(last, snaps[min(4, len(snaps) - 1)]), 1),
        "ret_20d_bp": round(_bp(last, snaps[min(19, len(snaps) - 1)]), 1),
        "range_last_24h_bp": round(_bp(max(b[2] for b in last24), min(b[3] for b in last24)), 1),
        "typical_daily_range_bp": round(sum(typical) / len(typical), 1),
        "pos_in_20d_range": round((last - lo) / (hi - lo), 2) if hi > lo else 0.5,
        "asof_utc": asof.strftime("%H:%M"),
        "hours_until_entry": round((entry - asof).total_seconds() / 3600, 1),
        "weekday": entry.strftime("%A"),
        "usd_high_impact_next_24h": events if events is not None else usd_events(entry, entry + dt.timedelta(hours=24)),
    }


# ---------------- model ----------------

def deepseek(model: str, base_url: str, api_key: str, timeout: float = 60.0) -> Llm:
    def call(system: str, user: str) -> str:
        body = json.dumps({"model": model, "temperature": 0, "max_tokens": 300,
                           "response_format": {"type": "json_object"},
                           "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.loads(res.read())["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}") from None
        except Exception as e:
            raise RuntimeError(f"{type(e).__name__}: {e}".replace(api_key, "***")) from None
    return call


def parse_answer(text: str) -> dict:
    """Validate a model answer; ValueError says why it is unusable."""
    try:
        a = json.loads(text)
        direction = a["direction"]
        if isinstance(direction, bool) or direction not in (-1, 0, 1):
            raise ValueError(f"direction {direction!r}")
        conf = a.get("confidence")
        if conf is not None:
            conf = float(conf)
            if not 0.0 <= conf <= 1.0:
                raise ValueError(f"confidence {conf}")
        return {"direction": int(direction), "confidence": conf, "rationale": str(a.get("rationale", ""))[:300]}
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        raise ValueError(f"unusable answer: {type(e).__name__}") from None


def ask(llm: Llm, role: str, style: str, symbol: str, feats: dict, extra: str = "") -> dict:
    system = SYSTEM.format(role=role, cost=round(sum(COST_BP[symbol]) / 2, 1), style=style)
    user = f"Symbol: {symbol}\nFeatures: {json.dumps(feats, sort_keys=True)}\n{extra}"
    try:
        return {**parse_answer(llm(system, user)), "error": None}
    except (RuntimeError, ValueError) as e:
        return {"direction": 0, "confidence": None, "rationale": f"ERROR: {e}", "error": str(e)}


# ---------------- run ----------------

def run_day(call_date: str, duka: Dukascopy, llm: Llm, model: str, db_target=None,
            now: Optional[dt.datetime] = None, dry_run: bool = False) -> List[dict]:
    """Ask every analyst about every symbol and record the calls. Returns what was (or would be) recorded."""
    entry = paper_desk.entry_time(call_date)
    day = entry.date()
    done = []
    already = paper_desk.recorded_symbols(call_date, db_target)
    for symbol in paper_desk.SYMBOLS:
        if symbol in already:
            continue                           # a rerun (cron retries while the price feed is down) skips what is done
        try:
            hours = duka.range(symbol, day - dt.timedelta(days=HISTORY_DAYS + 3), day - dt.timedelta(days=1))
        except RuntimeError as e:             # price feed down for this symbol: no features, so no call
            print(f"{call_date} {symbol}: price feed failed ({e}), no call", file=sys.stderr)
            continue
        feats = features(hours, call_date)
        if feats is None:
            print(f"{call_date} {symbol}: not enough data, no call", file=sys.stderr)
            continue
        answers = {r: ask(llm, r, style, symbol, feats) for r, style in ANALYSTS.items()}
        summary = "\n".join(f"{r}: {json.dumps({k: a[k] for k in ('direction', 'confidence', 'rationale')})}"
                            for r, a in answers.items())
        answers[CHIEF] = ask(llm, CHIEF, "You weigh the other analysts; you may disagree with all of them.", symbol,
                             feats, f"Other analysts:\n{summary}")
        for role, a in answers.items():
            row = {"call_date": call_date, "symbol": symbol, "analyst": f"{role}@{model}", **{
                k: a[k] for k in ("direction", "confidence", "rationale")}}
            done.append(row)
            if not dry_run:
                paper_desk.record_call(call_date, symbol, row["analyst"], a["direction"], a["confidence"],
                                       a["rationale"], feats, model, now=now, db_target=db_target)
    return done


# ---------------- score ----------------

def next_weekday(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def prev_weekday(d: dt.date) -> dt.date:
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def outcome_prices(duka: Dukascopy, cells, today: dt.date) -> Dict:
    """(call_date, symbol) -> (prev_entry, entry, exit) for cells whose exit day is over."""
    out = {}
    for call_date, symbol in cells:
        d = dt.date.fromisoformat(call_date)
        exit_day, prev_day = next_weekday(d), prev_weekday(d)
        if exit_day >= today:
            continue
        def at(day):
            return price_at(duka.day(symbol, day, today), paper_desk.entry_time(day.isoformat()))
        try:
            p = (at(prev_day), at(d), at(exit_day))
        except RuntimeError as e:
            print(f"{call_date} {symbol}: price feed failed ({e}), not scored yet", file=sys.stderr)
            continue
        if None not in p:
            out[(call_date, symbol)] = p
    return out


def format_score(result: dict) -> str:
    lines = ["name                              n   hit%   mean bp      t   verdict"]
    rows = list(result["analysts"].items()) + list(result["baselines"].items())
    for name, s in rows:
        mean = "-" if s["mean"] is None else f"{s['mean']:+.2f}"
        hit = "-" if s["hit"] is None else f"{s['hit'] * 100:.0f}"
        t = "-" if s["t"] != s["t"] else f"{s['t']:+.2f}"
        lines.append(f"{name:<30}{s['n']:>5}{hit:>7}{mean:>10}{t:>7}   {s['verdict']}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="paper_desk_runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--date", help="call date YYYY-MM-DD (default: today UTC)")
    r.add_argument("--dry-run", action="store_true")
    sub.add_parser("score")
    a = ap.parse_args(argv)

    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    paper_desk.init_schema()
    duka = Dukascopy(cache_dir_from_env())
    try:
        if a.cmd == "run":
            key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
            if not key:
                print("DEEPSEEK_API_KEY is not set", file=sys.stderr)
                return 2
            model = os.environ.get("PAPER_DESK_MODEL", DEFAULT_MODEL)
            llm = deepseek(model, os.environ.get("PAPER_DESK_BASE_URL", DEFAULT_BASE_URL), key)
            date = a.date or dt.datetime.now(dt.timezone.utc).date().isoformat()
            rows = run_day(date, duka, llm, model, dry_run=a.dry_run)
            for row in rows:
                print(f"{row['call_date']} {row['symbol']:<7} {row['analyst']:<26} {row['direction']:+d} "
                      f"{row['confidence']} {row['rationale'][:80]}")
            print(f"{len(rows)} calls {'(dry run, nothing recorded)' if a.dry_run else 'recorded'}")
        else:
            calls = paper_desk.load_calls()
            today = dt.datetime.now(dt.timezone.utc).date()
            prices = outcome_prices(duka, sorted({(c["call_date"], c["symbol"]) for c in calls}), today)
            result = paper_desk.score(calls, prices, COST_BP)
            result["scored_cells"] = len(prices)
            result["cells"] = len({(c["call_date"], c["symbol"]) for c in calls})
            paper_desk_status.save_score(result)
            print(format_score(result))
        return 0
    finally:
        duka.close()


if __name__ == "__main__":
    sys.exit(main())
