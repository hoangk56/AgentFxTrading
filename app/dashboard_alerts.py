"""Overview alert strip: what an investor must look at before anything else.

Pure function over data the dashboard already has (open positions, watchdog status), so it is
testable without a running bot. The watchdog restarts stuck bots on its own; this only makes
that visible, and flags the one case it cannot heal: an open position nobody is pricing.
"""
import datetime
import re
from typing import Any, Dict, List

# A bot ticks every few seconds, so ten minutes without a price on an open position means nobody watches its stop.
STALE_PRICE_SECONDS = 600
# Watchdog restarts older than this are history, not an alert.
RECENT_RESTART_SECONDS = 3600


_LIVE_TOKEN = re.compile(r"(^|[-_])live([-_]|$)", re.IGNORECASE)


def bot_mode(bot_id: str) -> str:
    """'live' or 'demo' from a bot id (cbot-live-live-eurusd-..., cbot-demo-demo-...), as the Bots tab does by name."""
    return "live" if _LIVE_TOKEN.search(bot_id or "") else "demo"


def filter_by_mode(alerts: List[Dict[str, str]], mode: str) -> List[Dict[str, str]]:
    """Keep the alerts of one trading mode; ones about no bot (docker) always stay."""
    return [a for a in alerts if a.get("kind") == "docker_down" or bot_mode(a.get("bot", "")) == mode]


def tag_modes(alerts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Label each alert with its trading mode ('all' for Docker itself) and the container its buttons act on.

    The Overview lists Real and Demo alerts together since the 2026-11-01 redesign. Containers are named after
    their --BotId, so the bot id stands in where the caller did not give the container name.
    """
    for alert in alerts:
        if alert.get("kind") == "docker_down":
            alert["mode"] = "all"
            continue
        alert["mode"] = bot_mode(alert.get("bot", ""))
        alert.setdefault("container", alert.get("bot", ""))
    return alerts


def _minutes(seconds: float) -> int:
    return max(1, round(seconds / 60))


def _event_age_seconds(event: Dict[str, Any], now_gmt7: datetime.datetime):
    try:
        stamp = datetime.datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
    except (KeyError, TypeError, ValueError):
        return None
    return (now_gmt7 - stamp).total_seconds()


def build_alerts(positions: List[Dict[str, Any]], watchdog: Dict[str, Any], forex_weekend: bool,
                 now_gmt7: datetime.datetime, down_bots: List[Dict[str, str]] = (),
                 docker_missing: bool = False) -> List[Dict[str, str]]:
    """Alerts for the strip, critical first. ``now_gmt7`` is naive GMT+7 (the watchdog's clock).

    ``down_bots``: configured bots whose container is not running and that the owner did not stop on purpose.
    """
    alerts: List[Dict[str, str]] = []

    # A dead container is real on the weekend too: nobody manages its stops, and it will not be there on Sunday night.
    if docker_missing:
        alerts.append({"level": "crit", "kind": "docker_down", "bot": "docker",
                       "message": "Không có Docker: không kiểm tra, chạy hay khởi động lại bot được"})
    for bot in down_bots:
        if bot.get("status") == "error":
            message = "không đọc được trạng thái container (lỗi Docker): kiểm tra Docker daemon, bot có thể đã dừng"
        else:
            # The Overview row carries the Chạy button; Dừng (to keep it off on purpose) is on the Bot screen.
            message = (f"container đang ở trạng thái {bot.get('status', 'not running')} mà không ai dừng; "
                       "muốn để tắt thì bấm Dừng ở màn Bot")
        alert = {"level": "crit", "kind": "bot_stopped", "bot": bot["bot_id"], "message": message}
        if bot.get("container"):
            alert["container"] = bot["container"]
        alerts.append(alert)

    # A restart the watchdog could not complete is real even with the market closed.
    seen_bots = set()
    for event in watchdog.get("recent_events", []):
        bot = event.get("bot_name")
        age = _event_age_seconds(event, now_gmt7)
        if bot in seen_bots or age is None or age < 0 or age > RECENT_RESTART_SECONDS:
            continue
        seen_bots.add(bot)
        if event.get("success"):
            if not forex_weekend:
                alerts.append({"level": "warn", "kind": "restarted", "bot": bot,
                               "message": f"watchdog đã khởi động lại {_minutes(age)} phút trước ({event.get('reason', 'stuck')})"})
        else:
            alerts.append({"level": "crit", "kind": "restart_failed", "bot": bot,
                           "message": f"watchdog khởi động lại THẤT BẠI {_minutes(age)} phút trước: {event.get('message', '')}".rstrip(": ")})

    if not forex_weekend:
        for position in positions:
            age = position.get("price_age_seconds")
            if isinstance(age, (int, float)) and age > STALE_PRICE_SECONDS:
                alerts.append({"level": "crit", "kind": "stale_price", "bot": position.get("bot_id") or "",
                               "message": f"lệnh {position.get('symbol', '')} đang mở mà không có giá {_minutes(age)} phút"})
        for bot, telemetry in watchdog.get("bar_telemetry", {}).items():
            if telemetry.get("bar_age", 0) > telemetry.get("allowance", float("inf")):
                alerts.append({"level": "warn", "kind": "feed_stalled", "bot": bot,
                               "message": f"không có nến mới {_minutes(telemetry['bar_age'])} phút (watchdog sẽ khởi động lại)"})

    alerts.sort(key=lambda a: a["level"] != "crit")
    return alerts
