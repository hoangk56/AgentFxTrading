"""
Regression guards from the 2026-09-23 VPS audit.

Closed volume. A partial close shrank `volume` to what was still open, and the final close left
it there: GBPJPY #674942756 opened 0.08 lots, the closed row said 0.06 lots next to the P&L of all
0.08. The bots no longer close part of a position, but open rows written before keep
initial_volume, and close_position restores it.
"""


import pytest

from app.portfolio import PortfolioManager
from tests._paths import REPO_ROOT


@pytest.fixture
def pm(tmp_path):
    return PortfolioManager(db_path=str(tmp_path / "audit.db"))


def _open(pm, symbol="ETHUSD", volume=0.4, bot_id="cbot-ethusd-h4-donchian"):
    pm.register_position(
        bot_id=bot_id, symbol=symbol, side="Sell", volume=volume, entry_price=2769.12,
        sl_pips=2506.3, tp_pips=3219.9, account_id="acct-1", ctrader_id=674939909,
    )


def _row(pm):
    conn = pm._get_conn()
    try:
        r = conn.execute("SELECT volume, initial_volume, pnl, status FROM positions").fetchone()
        return {"volume": r[0], "initial_volume": r[1], "pnl": r[2], "status": r[3]}
    finally:
        conn.close()


# --- closed volume ----------------------------------------------------------------------

def test_close_without_partial_keeps_volume(pm):
    _open(pm, volume=0.06)
    pm.close_position("cbot-ethusd-h4-donchian", "ETHUSD", exit_price=2780.0, pnl=-9.6,
                      account_id="acct-1", ctrader_id=674939909)
    assert _row(pm)["volume"] == pytest.approx(0.06)


def test_price_columns_are_widened_on_postgres():
    src = (REPO_ROOT / "app" / "portfolio.py").read_text(encoding="utf-8")
    assert "USING {col}::text::double precision" in src, (
        "float4 -> double must go through text: a direct numeric cast keeps six digits."
    )
    for col in ("volume", "entry_price", "exit_price"):
        assert f"'{col}'" in src
