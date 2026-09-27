"""
Bar heartbeat - 2026-09-23.

On 2026-09-14 bots stayed up and logged in but stopped handling bars. Each tick frame carries
`last_bar`, the time of the last bar the bot handled, and the watchdog restarts a bot whose ticks
flow while that stands still.
"""

import re

import pytest
from fastapi.testclient import TestClient

from app import cbot_watchdog as wd
from app.server import app
from tests._paths import CBOT_DIR

client = TestClient(app)


def _method(src: str, signature: str) -> str:
    start = src.index(signature)
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError(f"Unbalanced braces in {signature}")


def test_api_tick_records_the_bar_heartbeat():
    wd.reset_tick_telemetry()
    r = client.post("/api/tick", json={
        "bot_id": "cbot-hb-usdjpy-fix-gotobi", "account_number": "12345", "symbol": "USDJPY",
        "bid": 148.500, "ask": 148.503, "last_bar": "2026-09-24T08:45:00",
    })
    assert r.json()["status"] == "ok"
    assert wd._bar_seen["cbot-hb-usdjpy-fix-gotobi"] == "2026-09-24T08:45:00"


@pytest.mark.parametrize("cs_name", ["GotobiBot.cs", "CryptoDonchianBot.cs"])
def test_bot_stamps_every_bar_and_sends_it_with_its_ticks(cs_name):
    """
    Stamping Bars.LastBar.OpenTime repeated a value across two bars: inside OnBarClosed that is
    sometimes the closed bar and sometimes the new one. The handling time cannot repeat.
    """
    src = (CBOT_DIR / cs_name).read_text(encoding="utf-8")
    on_bar = _method(src, "protected override void OnBarClosed()")
    assert "_lastBarHandled = Server.Time" in on_bar and "Bars.LastBar" not in on_bar, on_bar
    tick = _method(src, "private void SendLiveTickTelemetry(")
    assert re.search(r"\blast_bar\s*=", tick), f"{cs_name} tick telemetry does not carry last_bar"
