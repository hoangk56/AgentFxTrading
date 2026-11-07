import asyncio
import datetime
import logging
import re
import time
from typing import Dict, List, Optional, Any
from app import alerts
from app.alerts_vi import watchdog_reason_vi
from app.dashboard_alerts import is_forex_weekend
from app.docker_manager import docker_manager
from app.portfolio import get_portfolio_manager
from app.bot_controls import bot_id_for_config

logger = logging.getLogger("AgentFxTrading.Watchdog")

DEFAULT_STALE_FEED_SECONDS = 2400  # 40 min for an M15 bot: > one bar, < two bars
M15_SECONDS = 900
_PERIOD_UNIT_SECONDS = {"m": 60, "h": 3600, "d": 86400, "w": 604800}
# Health reasons (app/docker_manager.py) that mean the broker cannot be reached or refuses the login.
CONNECTION_REASONS = ("Reconnect loop:", "Login retries exhausted", "Continuous login error loop")


def reset_tick_telemetry() -> None:
    """Forget every recorded tick (used by tests)."""
    _tick_seen_at.clear()
    _tick_run_since.clear()
    _bar_seen.clear()
    _bar_advanced_at.clear()


# ---------------------------------------------------------------------------
# Bar heartbeat
#
# On 2026-09-14 a broker reconnect re-published the bar series, every cBot's OnBarClosed returned
# early, and 8 bots stopped handling bars for 3.5 hours while their containers stayed up, logged
# in, and looked healthy to the login-based checks below. The bots' tick frames carry `last_bar` -
# the last bar the bot handled - so a bot whose ticks keep flowing while that stops advancing has a
# stalled bar pipeline. Ticks stop when the market does, so a closed market never looks stalled.
# Keyed by bot_id alone.
# ---------------------------------------------------------------------------

TICK_GAP_SECONDS = 300  # a longer gap ends the tick run: market closed, or the bot was down

_tick_seen_at: Dict[str, float] = {}
_tick_run_since: Dict[str, float] = {}
_bar_seen: Dict[str, str] = {}
_bar_advanced_at: Dict[str, float] = {}


def record_bot_tick(bot_id: str, last_bar: Optional[str], now: Optional[float] = None) -> None:
    """Stamp a tick frame from `bot_id`, with the last bar it handled when the bot reports one."""
    now = time.time() if now is None else now
    previous = _tick_seen_at.get(bot_id)
    if previous is None or now - previous > TICK_GAP_SECONDS:
        _tick_run_since[bot_id] = now
    _tick_seen_at[bot_id] = now
    if last_bar and _bar_seen.get(bot_id) != last_bar:
        _bar_seen[bot_id] = last_bar
        _bar_advanced_at[bot_id] = now


def parse_bot_id(run_command: Optional[str]) -> str:
    """The --BotId a bot's docker run command passes, or "" when absent."""
    m = re.search(r'--BotId=("?)([^"\s\\]+)\1', run_command or "")
    return m.group(2) if m else ""


def _period_label(seconds: int) -> str:
    for unit, size in (("D", 86400), ("H", 3600)):
        if seconds % size == 0:
            return f"{unit}{seconds // size}"
    return f"M{seconds // 60}"


def parse_bar_seconds(run_command: Optional[str]) -> int:
    """Length of the chart bar the bot runs on, from its --period flag (m15, h1, ...); M15 when absent or unknown."""
    m = re.search(r'--period=("?)([mhdw])(\d+)\1', (run_command or "").lower())
    return int(m.group(3)) * _PERIOD_UNIT_SECONDS[m.group(2)] if m else M15_SECONDS


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
        # Stall episode already healed: bot_name -> the bar the bot was stuck on
        self._stale_healed: Dict[str, Any] = {}
        # Stall allowance last applied to each bot_id, shown by get_status()
        self._bar_allowance: Dict[str, int] = {}
        # Recent healing events (max 50)
        self._recent_events: List[Dict[str, Any]] = []
        self._is_running = False
        self._last_check_time: Optional[float] = None
        # Health verdict from the latest cycle: bot_name -> check_cbot_health() result. /api/bots
        # serves this instead of re-reading every container's logs on each 10 s dashboard poll.
        self._last_health: Dict[str, Dict[str, Any]] = {}

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

        fresh_health: Dict[str, Dict[str, Any]] = {}
        for config in configs:
            name = config["name"]
            try:
                health = docker_manager.check_cbot_health(name)
                fresh_health[name] = health
                if health.get("status") != "running":
                    continue

                # Only heal running containers that are stuck
                if health.get("stuck"):
                    reason = health.get("reason", "Container stuck")
                    self._restart_bot(name, reason, actions, quiet=self._is_idle_outage(config, reason))
                    continue

                feed_reason = self._bar_stall_reason(name, config.get("run_command"))
                if feed_reason:
                    self._restart_bot(name, feed_reason, actions)

            except Exception as e:
                logger.error(f"[CBOT WATCHDOG] Error checking bot '{name}': {e}")

        self._last_health = fresh_health   # whole-dict swap: readers on request threads never see a partial cycle
        self._alert_restarts(actions)
        return actions

    @staticmethod
    def _is_idle_outage(config: Dict[str, Any], reason: str) -> bool:
        """A connection failure with the market closed and no position on the bot, so nothing is at risk: IC's monthly
        cTrader maintenance takes a whole Saturday and made 61 restarts on 2026-11-07. The alerts return by themselves
        when the market opens. Positions that cannot be read count as open."""
        if not reason.startswith(CONNECTION_REASONS) or not is_forex_weekend(datetime.datetime.now(datetime.timezone.utc)):
            return False
        try:
            return get_portfolio_manager().open_position_counts().get(bot_id_for_config(config), 0) == 0
        except Exception as e:
            logger.warning(f"[CBOT WATCHDOG] Could not read open positions for '{config.get('name')}': {e}")
            return False

    @staticmethod
    def _alert_restarts(actions: List[Dict[str, Any]]) -> None:
        """One Telegram message per cycle, however many bots it restarted (a failed restart is logged as an error,
        which alerts on its own)."""
        restarted = [a for a in actions if a["success"] and not a.get("quiet")]
        if len(restarted) == 1:
            alerts.notify(f"🟠 Watchdog đã khởi động lại {restarted[0]['name']}: {watchdog_reason_vi(restarted[0]['reason'])}"
                          + alerts.bot_link(restarted[0]['name']))
        elif restarted:
            alerts.notify(f"🟠 Watchdog đã khởi động lại {len(restarted)} bot:\n"
                          + "\n".join(f"• {a['name']}: {watchdog_reason_vi(a['reason'])}" for a in restarted)
                          + alerts.bot_link())

    def last_health(self, name: str) -> Optional[Dict[str, Any]]:
        """check_cbot_health() result for `name` from the latest cycle, or None before the first one."""
        return self._last_health.get(name)

    def _restart_bot(self, name: str, reason: str, actions: List[Dict[str, Any]], quiet: bool = False) -> None:
        """Restart `name` unless rate-limited, then record the healing event. `quiet` keeps it off Telegram."""
        can_restart, limit_reason = self._can_restart(name)

        if not can_restart:
            logger.warning(
                f"[CBOT WATCHDOG] Bot '{name}' is stalled ({reason}) "
                f"but restart rate-limited: {limit_reason}"
            )
            # The cooldown right after a restart is routine (the bot is still logging in); the backoff means
            # several restarts did not help.
            if limit_reason.startswith("Backoff") and not quiet:
                alerts.notify(f"🔴 Watchdog ngừng tự khởi động lại {name} ({watchdog_reason_vi(reason)}): {watchdog_reason_vi(limit_reason)}"
                              + alerts.bot_link(name),
                              key=("watchdog-backoff", name))
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
            "message": msg,
            "quiet": quiet
        })

    def bar_allowance_seconds(self, run_command: Optional[str]) -> int:
        """How long a bot may stream ticks without handling a bar. stale_feed_seconds is sized for an M15 chart;
        a slower chart gets one of its own bars plus the same slack (an H1 chart: 60 + 25 min), so a
        bot is never called stalled while it simply waits for its next bar."""
        bar = parse_bar_seconds(run_command)
        return max(self.stale_feed_seconds, bar + self.stale_feed_seconds - M15_SECONDS)

    def _bar_stall_reason(self, name: str, run_command: Optional[str],
                          now_utc: Optional[datetime.datetime] = None) -> Optional[str]:
        """Reason when a bot keeps streaming ticks but handles no bar, else None.

        The clock starts at the later of the last bar advance and the start of the current
        tick run, so the first bar after a market reopen gets its full allowance. Latched on
        the bar the bot is stuck on: a restarted bot still warming up is not restarted again.
        """
        bot_id = parse_bot_id(run_command)
        if not bot_id or bot_id not in _bar_seen:
            return None

        now = (now_utc or datetime.datetime.now(datetime.timezone.utc)).timestamp()
        if now - _tick_seen_at[bot_id] > TICK_GAP_SECONDS:
            return None

        allowance = self.bar_allowance_seconds(run_command)
        self._bar_allowance[bot_id] = allowance
        silence = now - max(_bar_advanced_at[bot_id], _tick_run_since[bot_id])
        if silence <= allowance:
            return None

        stuck_on = _bar_seen[bot_id]
        if self._stale_healed.get(name) == stuck_on:
            return None
        self._stale_healed[name] = stuck_on

        return (
            f"Ticks streaming for {silence / 60:.0f} min but no bar handled since {stuck_on} "
            f"(bar cycle is {_period_label(parse_bar_seconds(run_command))})"
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
            # The last bar each bot handled, how long ago it advanced, last tick age.
            "bar_telemetry": {
                bot_id: {
                    "last_bar": last_bar,
                    "bar_age": round(time.time() - _bar_advanced_at[bot_id], 1),
                    "tick_age": round(time.time() - _tick_seen_at[bot_id], 1),
                    "allowance": self._bar_allowance.get(bot_id, self.stale_feed_seconds),
                }
                for bot_id, last_bar in _bar_seen.items()
            },
            "last_check": datetime.datetime.fromtimestamp(
                self._last_check_time, tz=datetime.timezone.utc
            ).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
            if self._last_check_time else None,
            "recent_events": self._recent_events[:10],
            "total_healed_events": len(self._recent_events)
        }

cbot_watchdog = CbotWatchdog()
