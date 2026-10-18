"""
Regression guard for X-01 (audit 2026-09-22).

``close_position`` matched on ``bot_id + symbol + status='open' + account_id`` only. The cBot has
always SENT ``ctrader_id`` in the payload, but the positions table had no such column, so it was
dropped on the floor: one close report would close EVERY open position for that (bot_id, symbol).
"""


import pytest

from app.portfolio import PortfolioManager
from tests._paths import CBOT_DIR


@pytest.fixture
def pm(tmp_path):
    manager = PortfolioManager(db_path=str(tmp_path / "identity.db"))
    for ctid, entry in ((111, 1.1000), (222, 1.1050)):
        manager.register_position(
            bot_id="eurusd-bot", symbol="EURUSD", side="Buy", volume=0.1,
            entry_price=entry, sl_pips=20.0, tp_pips=40.0, account_id="acct-1",
            ctrader_id=ctid,
        )
    return manager


def _statuses(manager):
    conn = manager._get_conn()
    try:
        rows = conn.execute(
            "SELECT ctrader_id, status FROM positions ORDER BY ctrader_id"
        ).fetchall()
        return {r[0]: r[1] for r in rows}
    finally:
        conn.close()


def test_close_only_affects_the_reported_position(pm):
    pm.close_position(
        bot_id="eurusd-bot", symbol="EURUSD", exit_price=1.1100, pnl=10.0,
        account_id="acct-1", ctrader_id=111,
    )
    statuses = _statuses(pm)
    assert statuses[111] == "closed"
    assert statuses[222] == "open", (
        "closing one position closed every open position for the same (bot_id, symbol) - "
        "this is what breaks the moment MaxPositionsAllowed goes above 1"
    )


def test_close_without_a_ctrader_id_still_works(pm):
    """Guard against over-fixing: older payloads and the legacy path must keep working."""
    assert pm.close_position(
        bot_id="eurusd-bot", symbol="EURUSD", exit_price=1.1100, pnl=10.0,
        account_id="acct-1",
    )


def test_close_position_with_ctrader_id_matches_open_position_having_null_ctrader_id(tmp_path):
    """If a position was registered without ctrader_id, closing with ctrader_id must still find and close it."""
    manager = PortfolioManager(db_path=str(tmp_path / "legacy_close.db"))
    manager.register_position(
        bot_id="hk50-bot", symbol="HK50", side="Sell", volume=0.2,
        entry_price=24858.5, sl_pips=50.0, tp_pips=100.0, account_id="acct-live",
        ctrader_id=None,
    )
    assert manager.close_position(
        bot_id="hk50-bot", symbol="HK50", exit_price=24799.7, pnl=0.59,
        account_id="acct-live", ctrader_id=347787252, close_reason="Session End",
    )
    conn = manager._get_conn()
    try:
        row = conn.execute("SELECT status, pnl, ctrader_id, close_reason FROM positions WHERE bot_id = ?", ("hk50-bot",)).fetchone()
        assert row[0] == "closed"
        assert row[1] == pytest.approx(0.59)
        assert row[2] == 347787252
        assert row[3] == "Session End"
    finally:
        conn.close()


def _rows(manager):
    conn = manager._get_conn()
    try:
        return [
            tuple(r) for r in conn.execute(
                "SELECT id, ctrader_id, status, volume, pnl FROM positions ORDER BY id"
            ).fetchall()
        ]
    finally:
        conn.close()


def test_replayed_close_does_not_close_the_next_position(pm):
    """
    A close report whose id has no open row -- replayed, or sent for a position whose
    open report never reached the server -- must not fall back to "any open position of
    the pair". That closed position 222 with 111's exit and P&L, and rewrote its
    ctrader_id to 111.
    """
    assert pm.close_position(
        bot_id="eurusd-bot", symbol="EURUSD", exit_price=1.0980, pnl=-9.7,
        account_id="acct-1", ctrader_id=111,
    )
    before = _rows(pm)

    assert not pm.close_position(
        bot_id="eurusd-bot", symbol="EURUSD", exit_price=1.0980, pnl=-9.7,
        account_id="acct-1", ctrader_id=111,
    )
    assert _rows(pm) == before, "a replayed close for 111 changed another position"


def test_close_returns_false_when_no_position_matched(tmp_path):
    """Unmatched closes must return False and not silently succeed."""
    manager = PortfolioManager(db_path=str(tmp_path / "empty.db"))
    assert not manager.close_position(
        bot_id="ghost-bot", symbol="EURUSD", exit_price=1.10, pnl=0.0,
        account_id="acct-1", ctrader_id=999,
    )



@pytest.mark.parametrize("cs_name", ["GotobiBot.cs", "EcbWindowBot.cs", "GoldLevelBot.cs"])
@pytest.mark.parametrize("action", ["open", "close"])
def test_bot_sends_ctrader_id_with_every_position_report(cs_name, action):
    """The server-side narrowing is inert unless the bot actually sends the id."""
    src = (CBOT_DIR / cs_name).read_text(encoding="utf-8")
    idx = src.index(f'action = "{action}",')
    window = src[max(0, idx - 300) : idx]
    assert "ctrader_id" in window, (
        f"{cs_name} sends action={action} without ctrader_id, so the server cannot tell "
        f"this position from any other open one for the same (bot_id, symbol)."
    )
