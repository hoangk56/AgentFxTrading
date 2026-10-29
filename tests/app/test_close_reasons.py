"""Vietnamese close reasons on the Overview (app/close_reasons.py): every reason the three cBots send, old rows included."""
import pytest

from app.close_reasons import close_reason_vi
from tests._paths import DASHBOARD_JS


@pytest.mark.parametrize("sent, shown", [
    ("Fix exit (09:55 Tokyo)", "Thoát lúc fix (09:55 Tokyo)"),
    ("Session exit (11:55 Tokyo)", "Hết phiên (11:55 Tokyo)"),
    ("Window exit (13:00 London)", "Hết khung giờ (13:00 London)"),
    ("Hold exit (30 min after the trigger)", "Hết thời gian giữ (30 phút sau tín hiệu)"),
    ("Max hold (12 h)", "Giữ quá lâu (tối đa 12 giờ)"),
    ("Max hold (180 min)", "Giữ quá lâu (tối đa 180 phút)"),
    ("StopLoss (virtual, 3 x ATR20 H1)", "Chạm stop ảo (3 x ATR20 H1)"),
    ("StopLoss (broker guard, 100 pips)", "Chạm stop bảo vệ ở sàn (100 pips)"),
    ("StopLoss (broker guard, $100)", "Chạm stop bảo vệ ở sàn ($100)"),
    ("StopLoss (broker, 1.0-1.0 x the 3 x ATR20 H1 stop)", "Chạm stop ở sàn (1.0–1.0 x stop 3 x ATR20 H1)"),
    ("StopLoss (3 x ATR20 H1)", "Chạm stop (3 x ATR20 H1)"),
    ("Stop Loss (Trailing / Break-Even)", "Chạm stop đã dời (khoá lời / hoà vốn)"),
    ("StopLoss", "Chạm stop (SL)"),
    ("Take Profit", "Chạm chốt lời (TP)"),
    ("StopOut", "Sàn tự đóng (thiếu ký quỹ)"),
    ("Closed outside the bot (cTrader)", "Đóng ngoài bot (trong cTrader)"),
    ("Manual close (dashboard)", "Đóng tay (từ dashboard)"),
    ("Closed", "Đã đóng"),
    ("Decoy: StopLoss (virtual, 1.5 x ATR20 H1)", "Nguỵ trang: Chạm stop ảo (1.5 x ATR20 H1)"),
    ("Decoy: Session exit (11:55 Tokyo)", "Nguỵ trang: Hết phiên (11:55 Tokyo)"),
    ("Decoy: Max hold (12 h)", "Nguỵ trang: Giữ quá lâu (tối đa 12 giờ)"),
])
def test_every_bot_reason_reads_in_vietnamese(sent, shown):
    assert close_reason_vi(sent) == shown


@pytest.mark.parametrize("sent", [None, "", "Take Profit Early", "Decoy: something new"])
def test_missing_or_unknown_reasons_are_shown_as_sent(sent):
    assert close_reason_vi(sent) == sent


def test_history_carries_the_translation_and_the_overview_prefers_it(tmp_path, monkeypatch):
    import sqlite3
    import app.dashboard as dashboard_module

    db = str(tmp_path / "p.db")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE accounts (account_id TEXT, account_type TEXT, label TEXT, is_configured INTEGER)")
    conn.execute("CREATE TABLE positions (bot_id TEXT, symbol TEXT, side TEXT, volume REAL, entry_price REAL, "
                 "exit_price REAL, pnl REAL, entry_time TEXT, exit_time TEXT, sl_pips REAL, tp_pips REAL, sl_price REAL, "
                 "tp_price REAL, close_reason TEXT, account_id TEXT, status TEXT)")
    conn.execute("INSERT INTO positions VALUES ('b', 'USDJPY', 'sell', 1, 150, 149, 5, '2026-10-28 00:56:00', "
                 "'2026-10-28 02:55:00', NULL, NULL, NULL, NULL, 'Session exit (11:55 Tokyo)', 'a1', 'closed')")
    conn.commit()
    conn.close()
    monkeypatch.setattr(dashboard_module, "get_db", lambda: sqlite3.connect(db))
    item = dashboard_module.get_trade_history("a1")["items"][0]
    assert item["close_reason"] == "Session exit (11:55 Tokyo)"            # the API keeps what the bot sent
    assert item["close_reason_text"] == "Hết phiên (11:55 Tokyo)"
    assert "t.close_reason_text || t.close_reason" in DASHBOARD_JS.read_text(encoding="utf-8")
