"""Vietnamese Telegram alerts (app/alerts_vi.py): log-line alerts and watchdog reasons; logs themselves stay English."""
import pytest

from app.alerts_vi import log_alert_vi, watchdog_reason_vi


@pytest.mark.parametrize("logged, sent", [
    ("Backtest #12 worker error: boom", "Backtest #12 lỗi khi chạy: boom"),
    ("[CBOT WATCHDOG] Error checking bot 'cbot-a': timeout", "[WATCHDOG] Lỗi khi kiểm tra bot 'cbot-a': timeout"),
    ("Telemetry tick error: bad float", "Lỗi nhận giá từ bot: bad float"),
    ("Failed to close position: db locked", "Không ghi được lệnh đóng: db locked"),
    ("HTTP 500 on POST /portfolio/report: {\"detail\": \"x\"}", "HTTP 500 ở POST /portfolio/report: {\"detail\": \"x\"}"),
    ("Unhandled error on GET /boom", "Lỗi chưa được xử lý ở GET /boom"),
    ("something nobody planned for", "something nobody planned for"),
])
def test_log_alerts_read_in_vietnamese(logged, sent):
    assert log_alert_vi(logged) == sent


@pytest.mark.parametrize("reason, sent", [
    ("Container is exited", "container ở trạng thái exited"),
    ("Continuous login error loop without successful recovery", "lỗi đăng nhập lặp liên tục, không tự hồi phục"),
    ("Reconnect loop: 4 'connection has been lost' in the last 200 lines without re-establishing",
     "mất kết nối 4 lần trong 200 dòng log cuối mà không kết nối lại được"),
    ("Ticks streaming for 42 min but no bar handled since 2026-10-29 12:30 (bar cycle is M15)",
     "vẫn nhận giá 42 phút nhưng không xử lý nến nào từ 2026-10-29 12:30 (chu kỳ nến M15)"),
    ("Backoff active (3 restarts in 10m). Wait 299s", "tạm ngừng tự khởi động lại (3 lần trong 10 phút), chờ 299 giây"),
    ("Cooldown active. Wait 99s", "vừa khởi động lại, chờ 99 giây"),
    ("cBot stopped itself but the container is still running", "cBot đã tự dừng nhưng container vẫn chạy, bot không còn giao dịch"),
    ("Login failed", "Login failed"),
])
def test_watchdog_reasons_read_in_vietnamese(reason, sent):
    assert watchdog_reason_vi(reason) == sent
