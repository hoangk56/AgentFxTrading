"""cBot/DepthLoggerBot.cs only records the order book: it runs on the live account, so it must never trade.

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build is checked on the VPS.
"""
import re

from tests._paths import CBOT_DIR

SRC = (CBOT_DIR / "DepthLoggerBot.cs").read_text(encoding="utf-8")


def _default(prop: str) -> str:
    m = re.search(r'DefaultValue = ("[^"]*"|[\w.]+)[^\]]*\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no [Parameter] default for {prop}"
    return m.group(1).strip('"')


def test_never_trades():
    for call in ("ExecuteMarketOrder", "PlaceLimitOrder", "PlaceStopOrder", "PlaceStopLimitOrder", "ClosePosition",
                 "ModifyPosition", "CancelPendingOrder", "Positions", "PendingOrders", "Trade."):
        assert call not in SRC, f"the depth logger must not touch {call}"


def test_never_calls_the_server():
    assert "HttpClient" not in SRC and "ApiUrl" not in SRC


def test_default_windows_cover_the_gotobi_minutes():
    windows = [w.split("-") for w in _default("WindowList").split(",")]
    minute = lambda s: int(s[:2]) * 60 + int(s[3:])
    for t in ("18:00", "00:55", "02:55"):
        assert any(minute(a) < minute(t) < minute(b) for a, b in windows), f"{t} UTC is not recorded"


def test_default_symbols_are_the_gotobi_pairs():
    assert set(_default("SymbolList").split(",")) == {"USDJPY", "EURJPY", "GBPJPY"}


def test_writes_under_the_mounted_home():
    assert _default("OutputDir").startswith("/root/")
