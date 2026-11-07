"""Vietnamese wording for the Telegram alerts (app/alerts.py).

Event alerts are written in Vietnamese where they are sent. Alerts that come from ERROR / CRITICAL log lines and the
watchdog's health reasons are translated here, for Telegram only: the log files keep their English lines. The exception
text inside a message stays as Python raised it; a line that matches no rule is sent as logged.
"""
import re
from typing import Callable, List, Tuple

LEVELS_VI = {"ERROR": "LỖI", "CRITICAL": "NGHIÊM TRỌNG"}

Rules = List[Tuple["re.Pattern[str]", Callable[["re.Match[str]"], str]]]


def _rules(pairs) -> Rules:
    return [(re.compile(p, re.DOTALL), f) for p, f in pairs]


_LOG_RULES = _rules((
    (r"^Backtest summary refresh failed: (.*)$", lambda m: f"Cập nhật tổng kết backtest lỗi: {m[1]}"),
    (r"^Backtest worker tick failed: (.*)$", lambda m: f"Vòng xử lý backtest lỗi: {m[1]}"),
    (r"^Backtest #(\d+) worker error: (.*)$", lambda m: f"Backtest #{m[1]} lỗi khi chạy: {m[2]}"),
    (r"^\[CBOT WATCHDOG\] Error checking bot '(.+?)': (.*)$", lambda m: f"[WATCHDOG] Lỗi khi kiểm tra bot '{m[1]}': {m[2]}"),
    (r"^\[CBOT WATCHDOG\] Unexpected error in loop: (.*)$", lambda m: f"[WATCHDOG] Lỗi bất ngờ trong vòng kiểm tra: {m[1]}"),
    (r"^Error reading log file (.+?): (.*)$", lambda m: f"Lỗi đọc file log {m[1]}: {m[2]}"),
    (r"^Docker is not available: (.*)$", lambda m: f"Không có Docker: {m[1]}"),
    (r"^Telemetry tick error: (.*)$", lambda m: f"Lỗi nhận giá từ bot: {m[1]}"),
    (r"^Portfolio report error: (.*)$", lambda m: f"Lỗi nhận báo cáo lệnh từ bot: {m[1]}"),
    (r"^Portfolio status error: (.*)$", lambda m: f"Lỗi đọc trạng thái danh mục: {m[1]}"),
    (r"^Dashboard accounts error: (.*)$", lambda m: f"Lỗi đọc danh sách tài khoản: {m[1]}"),
    (r"^Failed to register position: (.*)$", lambda m: f"Không ghi được lệnh mới: {m[1]}"),
    (r"^Failed to close position: (.*)$", lambda m: f"Không ghi được lệnh đóng: {m[1]}"),
    (r"^Failed to get portfolio status: (.*)$", lambda m: f"Không đọc được trạng thái danh mục: {m[1]}"),
    (r"^Unhandled error on (.*)$", lambda m: f"Lỗi chưa được xử lý ở {m[1]}"),
    (r"^HTTP (\d+) on (\S+ \S+): (.*)$", lambda m: f"HTTP {m[1]} ở {m[2]}: {m[3]}"),
))

_REASON_RULES = _rules((
    (r"^Container is (\w+)$", lambda m: f"container ở trạng thái {m[1]}"),
    (r"^Container stuck$", lambda m: "container bị treo"),
    (r"^Login retries exhausted without re-authenticating.*$", lambda m: "đã thử đăng nhập lại hết lượt mà không vào được"),
    (r"^Continuous login error loop without successful recovery$", lambda m: "lỗi đăng nhập lặp liên tục, không tự hồi phục"),
    (r"^Reconnect loop: (\d+) 'connection has been lost' in the last (\d+) lines without re-establishing$",
     lambda m: f"mất kết nối {m[1]} lần trong {m[2]} dòng log cuối mà không kết nối lại được"),
    (r"^cBot stopped itself but the container is still running$",
     lambda m: "cBot đã tự dừng nhưng container vẫn chạy, bot không còn giao dịch"),
    (r"^Ticks streaming for (\d+) min but no bar handled since (.+?) \(bar cycle is (.+)\)$",
     lambda m: f"vẫn nhận giá {m[1]} phút nhưng không xử lý nến nào từ {m[2]} (chu kỳ nến {m[3]})"),
    (r"^Backoff active \((\d+) restarts in 10m\)\. Wait (\d+)s$",
     lambda m: f"tạm ngừng tự khởi động lại ({m[1]} lần trong 10 phút), chờ {m[2]} giây"),
    (r"^Cooldown active\. Wait (\d+)s$", lambda m: f"vừa khởi động lại, chờ {m[1]} giây"),
))


def _apply(rules: Rules, text: str) -> str:
    for pattern, render in rules:
        m = pattern.match(text)
        if m:
            return render(m)
    return text


def log_alert_vi(message: str) -> str:
    """An ERROR / CRITICAL log message as Telegram shows it."""
    return _apply(_LOG_RULES, message)


def watchdog_reason_vi(reason: str) -> str:
    """A container health reason or a restart limit (app/docker_manager.py, app/cbot_watchdog.py) in Vietnamese."""
    return _apply(_REASON_RULES, reason or "")
