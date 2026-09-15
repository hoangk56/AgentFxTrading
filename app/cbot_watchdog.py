import asyncio
import calendar
import datetime
import logging
import re
import time
from typing import Dict, List, Optional, Any
from app.docker_manager import docker_manager
from app.portfolio import get_portfolio_manager

logger = logging.getLogger("AgentFxTrading.Watchdog")

# ---------------------------------------------------------------------------
# Bar-feed freshness
#
# A TMS/ORB bot pushes one snapshot per closed bar for as long as its own session
# window is open. On 2026-09-14 a broker reconnect re-published the bar series, every
# cBot's OnBarClosed returned early, and 8 bots stopped reporting for 3.5 hours while
# their containers stayed up, logged in, and looked healthy to the login-based checks
# below. record_bot_snapshot() is called by the API server on every snapshot; the loop
# then restarts a bot whose session is open, whose feed was alive, and which has since
# gone quiet for longer than a full bar cycle.
# ---------------------------------------------------------------------------

DEFAULT_STALE_FEED_SECONDS = 2400  # 40 min: > one M15 bar + LLM latency, < two bars

_snapshot_seen_at: Dict[str, float] = {}


def record_bot_snapshot(bot_key: str) -> None:
    """Stamp a snapshot received from `bot_key` ("<account_id>/<bot_id>")."""
    _snapshot_seen_at[bot_key] = time.time()


def reset_snapshot_telemetry() -> None:
    """Forget every recorded snapshot (used by tests)."""
    _snapshot_seen_at.clear()


def last_snapshot_for(bot_id: str) -> Optional[float]:
    """Newest snapshot timestamp for `bot_id`, whichever account reported it."""
    hits = [t for key, t in _snapshot_seen_at.items() if key.endswith(f"/{bot_id}")]
    return max(hits) if hits else None


def parse_session_params(run_command: Optional[str]) -> Optional[Dict[str, Any]]:
    """Extract the per-bar session window from a bot's docker run command.

    Returns None for bots that run no bar cycle (the Judas sweep bots carry no
    --OrbStartHour/--SessionEndHour) or when the command cannot be parsed.
    """
    if not run_command or "--OrbStartHour" not in run_command or "--SessionEndHour" not in run_command:
        return None

    def number(key: str) -> Optional[int]:
        m = re.search(rf'--{key}=("?)(-?\d+)\1', run_command)
        return int(m.group(2)) if m else None

    def text(key: str) -> str:
        m = re.search(rf'--{key}=("?)([^"\s\\]+)\1', run_command)
        return m.group(2) if m else ""

    start_hour, end_hour = number("OrbStartHour"), number("SessionEndHour")
    if start_hour is None or end_hour is None:
        return None

    return {
        "bot_id": text("BotId"),
        "session_name": text("SessionName") or "unknown",
        "start_hour": start_hour,
        "start_minute": number("OrbStartMinute") or 0,
        "end_hour": end_hour,
        "end_minute": number("SessionEndMinute") or 0,
        "dst_rule": text("SessionDstRule") or "None",
    }


def _nth_sunday(year: int, month: int, n: int) -> datetime.date:
    first = datetime.date(year, month, 1)
    return first + datetime.timedelta(days=(6 - first.weekday()) % 7 + (n - 1) * 7)


def _last_sunday(year: int, month: int) -> datetime.date:
    last = datetime.date(year, month, calendar.monthrange(year, month)[1])
    return last - datetime.timedelta(days=(last.weekday() + 1) % 7)


def _adjusted_hour(now_utc: datetime.datetime, base_hour: int, dst_rule: str) -> int:
    """Port of AiAgentBot.GetAdjustedHour: keep the local open hour, express it in UTC."""
    if dst_rule not in ("US", "Europe") or base_hour == 0:
        return base_hour

    year = now_utc.year
    if dst_rule == "US":
        # 2nd Sunday of March -> 1st Sunday of November
        start = datetime.datetime.combine(_nth_sunday(year, 3, 2), datetime.time(7), tzinfo=datetime.timezone.utc)
        end = datetime.datetime.combine(_nth_sunday(year, 11, 1), datetime.time(6), tzinfo=datetime.timezone.utc)
    else:
        # Last Sunday of March -> last Sunday of October
        start = datetime.datetime.combine(_last_sunday(year, 3), datetime.time(1), tzinfo=datetime.timezone.utc)
        end = datetime.datetime.combine(_last_sunday(year, 10), datetime.time(1), tzinfo=datetime.timezone.utc)

    is_dst = start <= now_utc < end
    return (base_hour - 1) % 24 if is_dst else base_hour


def is_forex_weekend(now_utc: datetime.datetime) -> bool:
    """FX closes Friday 21:00 UTC and reopens Sunday 21:00 UTC (mirrors get_market_sessions_info)."""
    weekday = now_utc.weekday()
    hour = now_utc.hour + now_utc.minute / 60.0
    return (weekday == 4 and hour >= 21.0) or weekday == 5 or (weekday == 6 and hour < 21.0)


def active_session_start(params: Dict[str, Any], now_utc: datetime.datetime) -> Optional[datetime.datetime]:
    """UTC start of the session instance open at `now_utc`, or None when outside the window.

    Mirrors AiAgentBot.GetSessionInfo, including the 9h fallback when SessionEndHour is 0.
    """
    start_hour = _adjusted_hour(now_utc, params["start_hour"], params["dst_rule"])
    end_hour = _adjusted_hour(now_utc, params["end_hour"], params["dst_rule"])

    start_minute = params.get("start_minute", 0)
    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + params["end_minute"]
    if params["end_hour"] == 0:
        end_minutes = start_minutes + 540
    overnight = start_minutes > end_minutes
    now_minutes = now_utc.hour * 60 + now_utc.minute
    if overnight:
        is_active = now_minutes >= start_minutes or now_minutes < end_minutes
    else:
        is_active = start_minutes <= now_minutes < end_minutes
    if not is_active:
        return None

    day = now_utc.date()
    if overnight and now_minutes < end_minutes:
        day -= datetime.timedelta(days=1)
    return datetime.datetime.combine(day, datetime.time(start_hour, start_minute), tzinfo=datetime.timezone.utc)
import time
from typing import Dict, List, Optional, Any
from app.docker_manager import docker_manager
from app.portfolio import get_portfolio_manager

logger = logging.getLogger("AgentFxTrading.Watchdog")

class CbotWatchdog:
    """
    Automatic Health Monitor & Self-Healing Watchdog for cTrader cBot containers.
    Detects unrecovered broker disconnection and login failure loops,
    automatically restarting affected containers with rate-limiting and backoff.
    """

    def __init__(
        self,
        check_interval_seconds: int = 60,
        cooldown_seconds: int = 120,
        max_restarts_in_window: int = 3,
        window_seconds: int = 600,
        backoff_cooldown_seconds: int = 300,
        stale_feed_seconds: int = DEFAULT_STALE_FEED_SECONDS
    ):
        self.check_interval_seconds = check_interval_seconds
        self.cooldown_seconds = cooldown_seconds
        self.max_restarts_in_window = max_restarts_in_window
        self.window_seconds = window_seconds
        self.backoff_cooldown_seconds = backoff_cooldown_seconds
        self.stale_feed_seconds = stale_feed_seconds

        # Per-bot restart timestamps: bot_name -> list of float timestamps
        self._restart_history: Dict[str, List[float]] = {}
        # Session instance already healed for a stalled bar feed: bot_name -> session start
        self._stale_healed: Dict[str, datetime.datetime] = {}
        # Recent healing events (max 50)
        self._recent_events: List[Dict[str, Any]] = []
        self._is_running = False
        self._last_check_time: Optional[float] = None

    def _now_gmt7_str(self) -> str:
        dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _can_restart(self, name: str) -> tuple[bool, str]:
        now = time.time()
        history = self._restart_history.get(name, [])
        # Prune older than window_seconds
        history = [t for t in history if now - t <= self.window_seconds]
        self._restart_history[name] = history

        if not history:
            return True, "OK"

        last_restart = history[-1]
        elapsed_since_last = now - last_restart

        if len(history) >= self.max_restarts_in_window:
            if elapsed_since_last < self.backoff_cooldown_seconds:
                remaining = int(self.backoff_cooldown_seconds - elapsed_since_last)
                return False, f"Backoff active ({len(history)} restarts in 10m). Wait {remaining}s"
        elif elapsed_since_last < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - elapsed_since_last)
            return False, f"Cooldown active. Wait {remaining}s"

        return True, "OK"

    def _record_restart(self, name: str, reason: str, success: bool, message: str):
        now = time.time()
        if name not in self._restart_history:
            self._restart_history[name] = []
        self._restart_history[name].append(now)

        event = {
            "timestamp": self._now_gmt7_str(),
            "bot_name": name,
            "reason": reason,
            "success": success,
            "message": message
        }
        self._recent_events.insert(0, event)
        if len(self._recent_events) > 50:
            self._recent_events.pop()

    def check_and_heal(self) -> List[Dict[str, Any]]:
        """
        Inspect all configured cBots and auto-heal any stuck containers.
        Returns list of actions taken.
        """
        self._last_check_time = time.time()
        actions = []

        if not docker_manager.is_available:
            return actions

        pm = get_portfolio_manager()
        configs = pm.get_cbot_configs()

        for config in configs:
            name = config["name"]
            try:
                health = docker_manager.check_cbot_health(name)
                if health.get("status") != "running":
                    continue

                # Only heal running containers that are stuck
                if health.get("stuck"):
                    self._restart_bot(name, health.get("reason", "Container stuck"), actions)
                    continue

                feed_reason = self._stale_feed_reason(name, config.get("run_command"))
                if feed_reason:
                    self._restart_bot(name, feed_reason, actions)

            except Exception as e:
                logger.error(f"[CBOT WATCHDOG] Error checking bot '{name}': {e}")

        return actions

    def _restart_bot(self, name: str, reason: str, actions: List[Dict[str, Any]]) -> None:
        """Restart `name` unless rate-limited, then record the healing event."""
        can_restart, limit_reason = self._can_restart(name)

        if not can_restart:
            logger.warning(
                f"[CBOT WATCHDOG] Bot '{name}' is stalled ({reason}) "
                f"but restart rate-limited: {limit_reason}"
            )
            return

        logger.warning(
            f"[CBOT WATCHDOG] Auto-healing bot '{name}' -> "
            f"Reason: {reason}. Triggering restart..."
        )

        res = docker_manager.restart_container(name, timeout=15)
        success = res.get("success", False)
        msg = res.get("message", "")

        if success:
            logger.info(
                f"[CBOT WATCHDOG] Bot '{name}' successfully restarted and recovered."
            )
        else:
            logger.error(
                f"[CBOT WATCHDOG] Failed to restart bot '{name}': {msg}"
            )

        self._record_restart(name, reason, success, msg)
        actions.append({
            "name": name,
            "reason": reason,
            "success": success,
            "message": msg
        })

    def _stale_feed_reason(
        self,
        name: str,
        run_command: Optional[str],
        now_utc: Optional[datetime.datetime] = None
    ) -> Optional[str]:
        """Reason when a running bot stopped pushing bar snapshots mid-session, else None.

        A cBot pushes a snapshot per closed bar only while its own session window is
        open, so silence only means something inside that window and outside the FX
        weekend. A per-session latch keeps a broker holiday (everyone legitimately
        silent) from turning into a restart loop.
        """
        params = parse_session_params(run_command)
        if params is None or not params["bot_id"]:
            return None

        if now_utc is None:
            now_utc = datetime.datetime.now(datetime.timezone.utc)
        if is_forex_weekend(now_utc):
            return None

        session_start = active_session_start(params, now_utc)
        if session_start is None:
            return None

        last_seen = last_snapshot_for(params["bot_id"])
        if last_seen is None:
            return None

        silence = now_utc.timestamp() - last_seen
        if silence <= self.stale_feed_seconds:
            return None

        if self._stale_healed.get(name) == session_start:
            return None
        self._stale_healed[name] = session_start

        return (
            f"No bar snapshot for {silence / 60:.0f} min during the "
            f"'{params['session_name']}' session (bar cycle is M15)"
        )

    async def run_loop(self):
        """Background monitoring loop."""
        self._is_running = True
        logger.info(
            f"[CBOT WATCHDOG] Started cBot Watchdog service "
            f"(interval={self.check_interval_seconds}s, cooldown={self.cooldown_seconds}s)"
        )

        while self._is_running:
            try:
                # Run inspection in thread to avoid blocking event loop on docker IO
                await asyncio.to_thread(self.check_and_heal)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CBOT WATCHDOG] Unexpected error in loop: {e}")

            try:
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break

        logger.info("[CBOT WATCHDOG] cBot Watchdog service stopped.")

    def stop(self):
        self._is_running = False

    def get_status(self) -> Dict[str, Any]:
        """Status summary for dashboard API."""
        return {
            "is_running": self._is_running,
            "check_interval_seconds": self.check_interval_seconds,
            "stale_feed_seconds": self.stale_feed_seconds,
            # Age of the last snapshot per bot, so the detector is observable from the dashboard.
            "feed_telemetry": {
                key: round(time.time() - seen_at, 1) for key, seen_at in _snapshot_seen_at.items()
            },
            "last_check": datetime.datetime.fromtimestamp(
                self._last_check_time, tz=datetime.timezone.utc
            ).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
            if self._last_check_time else None,
            "recent_events": self._recent_events[:10],
            "total_healed_events": len(self._recent_events)
        }

cbot_watchdog = CbotWatchdog()
