"""
Forward-test status of the research candidates, from the closed trades in `positions`.

Each candidate carries the stop and promotion rules *as registered* in its own PREREG (docs/forward-candidates.md lists
the files). Nothing here chooses a threshold: a number that is not in a PREREG is not in this module. The verdict is one
of NO_DATA, CONTINUE, STOP or PROMOTE_CHECK. PROMOTE_CHECK means every promotion number this module can compute passes;
`manual` names the registered conditions it cannot read off `positions` (spread x1.5 needs the quotes, the realised
round-trip cost and the gold entry slippage need the bot's own log), so PROMOTE_CHECK is never a promotion.

Trade net, in bp, is the research's: the real fills' price move over the entry price, minus the 0.6 bp commission.
The pooled t joins the registered HOLD run, known only by (n, mean, sd), to the forward trades as independent trades.
The PREREGs cluster by day; for these bots (at most about one trade a day) the two agree closely.
"""
from __future__ import annotations

import datetime
import math
import statistics
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from app.db import get_db_connection

COMMISSION_BP = 0.6


@dataclass(frozen=True)
class Candidate:
    key: str
    label: str
    bot_suffix: str                  # bot_id ends with this (cbot_presets.STRATEGIES suffix + session slug)
    tier: str
    hold_n: int
    hold_mean: float                 # bp per trade, net
    hold_sd: float
    min_trades_stop_t: int           # trades before the pooled-t stop is read
    stop_t: float                    # stop when pooled t <= this
    min_trades_promote: int = 100
    promote_t: float = 2.5
    # Gold only: cumulative stop at 60 trades, and VAL's per-trade mean / sd for the 120-trade floor.
    stop_cum_after: Optional[int] = None
    floor_after: Optional[int] = None
    val_mean: Optional[float] = None
    val_sd: Optional[float] = None
    manual: Tuple[str, ...] = ()
    prereg: str = ""


def _sd(mean: float, n: int, t: float) -> float:
    """Per-trade sd implied by a reported mean and t over n trades."""
    return abs(mean) * math.sqrt(n) / t


# HOLD figures are the registered holdout results (n, net mean, t); the sd follows from them.
CANDIDATES: Dict[str, Candidate] = {c.key: c for c in (
    Candidate(
        key="ecb_f3", label="ECB F3 (E1 vào ngày USD-TOP)", bot_suffix="-ecb-f3", tier="RELAXED",
        hold_n=117, hold_mean=2.00, hold_sd=_sd(2.00, 117, 2.16),
        min_trades_stop_t=60, stop_t=-1.0,
        manual=("ròng > 0 khi spread x1.5", "chi phí khứ hồi TB thực tế <= 1.5 bp"),
        prereg="round24_relaxed/PREREG_R24_relaxed_hold.md; PREREG_DRAFT_C_ecb_window_variants.md"),
    Candidate(
        key="ecb_e1", label="ECB E1 (bán EURUSD 11:00-13:00 London)", bot_suffix="-ecb-e1", tier="DEMO",
        hold_n=444, hold_mean=0.64, hold_sd=_sd(0.64, 444, 0.99),
        min_trades_stop_t=100, stop_t=-1.0,
        manual=("ròng > 0 khi spread x1.5", "chi phí khứ hồi TB thực tế <= 1.5 bp"),
        prereg="round13_structural/PREREG_M_eurusd_midday.md"),
    Candidate(
        key="gold_levels", label="Vàng mốc $50 (G1-XAU50)", bot_suffix="-levels-gold50", tier="DEMO",
        hold_n=228, hold_mean=2.87, hold_sd=_sd(2.87, 228, 1.43),
        min_trades_stop_t=10 ** 9, stop_t=-1.0,   # gold has no pooled-t stop; its three stops are below
        stop_cum_after=60, floor_after=120, val_mean=3.62, val_sd=22.9,
        manual=("ròng > 0 khi spread x1.5", "trượt giá vào lệnh trung vị <= 1 x s60 sau 30 lệnh "
                "(research.tools.gold_demo_check trên <BotId>_trades.csv)"),
        prereg="round27_levels_opens/PREREG_G_gold_round50_cascade.md"),
)}


def trade_net_bp(side: str, entry: float, exit_: float, commission_bp: float = COMMISSION_BP) -> float:
    move = (exit_ - entry) if side.lower() == "buy" else (entry - exit_)
    return move / entry * 1e4 - commission_bp


def pooled_t(hold_n: int, hold_mean: float, hold_sd: float, values: Sequence[float]) -> float:
    """t of the mean over HOLD (summary) plus forward trades, as independent trades."""
    n = hold_n + len(values)
    if n < 3:
        return float("nan")
    total = hold_n * hold_mean + sum(values)
    mean = total / n
    ss = hold_sd ** 2 * (hold_n - 1) + hold_n * (hold_mean - mean) ** 2
    ss += sum((v - mean) ** 2 for v in values)
    sd = math.sqrt(ss / (n - 1))
    return mean / (sd / math.sqrt(n)) if sd > 0 else float("nan")


def forward_t(values: Sequence[float]) -> Optional[float]:
    """t of the forward values alone (mean over its standard error), rounded to 2; None under 2 values or no spread.
    The research screen grades a real run on this, never on pooled_t, which already carries the HOLD run's t."""
    if len(values) < 2:
        return None
    sd = statistics.stdev(values)
    return round(statistics.fmean(values) / (sd / math.sqrt(len(values))), 2) if sd > 0 else None


def evaluate(cand: Candidate, nets: Sequence[float]) -> dict:
    """Verdict for one candidate from its forward trades' net bp, oldest first."""
    n = len(nets)
    out = {"key": cand.key, "label": cand.label, "tier": cand.tier, "n": n, "manual": list(cand.manual),
           "prereg": cand.prereg, "reasons": []}
    if n == 0:
        return {**out, "verdict": "NO_DATA", "mean": None, "cum": 0.0, "pooled_t": pooled_t(
            cand.hold_n, cand.hold_mean, cand.hold_sd, []), "forward_t": None, "hold_n": cand.hold_n}
    cum = sum(nets)
    pt = pooled_t(cand.hold_n, cand.hold_mean, cand.hold_sd, nets)
    out.update(mean=cum / n, cum=cum, pooled_t=pt, forward_t=forward_t(nets), hold_n=cand.hold_n)

    if cand.stop_cum_after is not None and n >= cand.stop_cum_after and cum < 0:
        out["reasons"].append(f"sau {cand.stop_cum_after} lệnh, tổng ròng {cum:+.1f} bp < 0")
    if cand.floor_after is not None and n >= cand.floor_after:
        floor = n * cand.val_mean - 1.5 * cand.val_sd * math.sqrt(n)
        out["floor"] = floor
        if cum < floor:
            out["reasons"].append(f"sau {cand.floor_after} lệnh, tổng ròng {cum:+.1f} bp thấp hơn "
                                  f"tổng kỳ vọng trừ 1.5 sd ({floor:+.1f})")
    if n >= cand.min_trades_stop_t and pt <= cand.stop_t:
        out["reasons"].append(f"sau {cand.min_trades_stop_t} lệnh, t gộp {pt:+.2f} <= {cand.stop_t}")
    if out["reasons"]:
        return {**out, "verdict": "STOP"}

    if pt >= cand.promote_t and n >= cand.min_trades_promote:
        return {**out, "verdict": "PROMOTE_CHECK"}
    need = []
    if n < cand.min_trades_promote:
        need.append(f"cần thêm {cand.min_trades_promote - n} lệnh")
    if not pt >= cand.promote_t:
        need.append(f"t gộp {pt:+.2f} < {cand.promote_t}")
    out["reasons"] = need
    return {**out, "verdict": "CONTINUE"}


def load_dated_nets(cand: Candidate, db_target=None) -> List[Tuple[Optional[str], float]]:
    """(exit time, net bp) of every closed trade whose bot_id ends with the candidate's suffix, oldest entry first."""
    conn = get_db_connection(db_target)
    try:
        rows = conn.execute(
            "SELECT side, entry_price, exit_price, exit_time FROM positions "
            "WHERE status = 'closed' AND exit_price IS NOT NULL AND entry_price > 0 AND bot_id LIKE ? "
            "ORDER BY entry_time", (f"%{cand.bot_suffix}",)).fetchall()
    finally:
        conn.close()
    return [(r["exit_time"], trade_net_bp(r["side"], r["entry_price"], r["exit_price"])) for r in rows]


def load_nets(cand: Candidate, db_target=None) -> List[float]:
    """Net bp of every closed trade whose bot_id ends with the candidate's suffix, oldest entry first."""
    return [net for _, net in load_dated_nets(cand, db_target)]


def forward_status(db_target=None, keys: Optional[Iterable[str]] = None) -> List[dict]:
    """evaluate() per candidate, plus `dated`: [(exit time, net bp)] for the research screen's periods."""
    out = []
    for k in keys or CANDIDATES:
        dated = load_dated_nets(CANDIDATES[k], db_target)
        out.append({**evaluate(CANDIDATES[k], [net for _, net in dated]), "dated": dated})
    return out


GOLD_CALENDAR = Path(__file__).resolve().parent.parent / "cBot" / "seeds" / "usd_high_calendar.csv"
CALENDAR_WARN_DAYS = 21


def calendar_guard(today: Optional[datetime.date] = None, path: Path = GOLD_CALENDAR) -> Optional[dict]:
    """The gold bot stops arming after the seed's `# valid_through=` day (a funding-lapse guard, see
    research/tools/usd_high_calendar_seed.py). Returns that day and the days left, or None when the line is missing."""
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                if "valid_through=" in line:
                    day = datetime.date.fromisoformat(line.split("valid_through=", 1)[1].strip())
                    return {"valid_through": day.isoformat(), "days_left": (day - today).days}
    except (OSError, ValueError):
        pass
    return None


ALERT_VERDICTS = {"STOP": "🔴", "PROMOTE_CHECK": "🟢"}
ALERT_VERDICTS_VI = {"STOP": "DỪNG", "PROMOTE_CHECK": "ĐỦ ĐIỀU KIỆN XÉT"}   # as the Research view's trackers word them
CHECK_INTERVAL_SECONDS = 3600


class ForwardAlerts:
    """Tells Telegram once when a candidate's verdict turns STOP or PROMOTE_CHECK (a change from what the last check
    saw). The last verdicts live in memory only, so a server restart repeats an alert for a candidate that is still in
    one of those states; alerts are off until TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set."""

    def __init__(self, notify):
        self._notify = notify
        self._last: Dict[str, str] = {}

    def check(self, statuses: Iterable[dict]) -> List[str]:
        sent = []
        for s in statuses:
            verdict = s["verdict"]
            if verdict in ALERT_VERDICTS and self._last.get(s["key"]) != verdict:
                lines = [f"{ALERT_VERDICTS[verdict]} Kiểm chứng {ALERT_VERDICTS_VI[verdict]}: {s['label']}",
                         f"{s['n']} lệnh kiểm chứng, TB ròng {s['mean']:+.2f} bp, t gộp {s['pooled_t']:+.2f}"]
                lines += s["reasons"]
                if verdict == "PROMOTE_CHECK":
                    lines.append("Chưa kiểm ở đây: " + "; ".join(s["manual"]))
                sent.append("\n".join(lines))
                self._notify(sent[-1], key=("forward", s["key"], verdict))
            self._last[s["key"]] = verdict
        return sent

    def check_calendar(self, guard: Optional[dict]) -> Optional[str]:
        """Warn (once a day per state) when the gold seed's valid_through is close or past: the bot stops arming then."""
        if guard is None or guard["days_left"] > CALENDAR_WARN_DAYS:
            return None
        day = guard["valid_through"]
        left = guard["days_left"]
        text = (f"🟠 Lịch mốc giá vàng còn hiệu lực đến {day} (còn {left} ngày)" if left >= 0 else
                f"🔴 Lịch mốc giá vàng đã hết hạn ngày {day}: bot không còn đặt lệnh chờ") \
            + ". Dựng lại cBot/seeds/usd_high_calendar.csv (research/tools/usd_high_calendar_seed.py) khi biết" \
              " kết quả funding tháng 12, rồi deploy lại bot."
        self._notify(text, key=("forward", "calendar", day, datetime.date.today().isoformat()))
        return text

    async def run_loop(self, interval: float = CHECK_INTERVAL_SECONDS):
        import asyncio
        import logging
        from app.portfolio import get_portfolio_manager
        while True:
            try:
                statuses = await asyncio.to_thread(lambda: forward_status(get_portfolio_manager().db_path))
                self.check(statuses)
                self.check_calendar(calendar_guard())
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logging.getLogger(__name__).warning(f"[FORWARD] status check failed: {e}")
            await asyncio.sleep(interval)
