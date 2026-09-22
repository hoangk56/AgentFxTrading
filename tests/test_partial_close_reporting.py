"""
Regression guard for C-03 (audit 2026-09-22): partial closes never reached the DB.

``Positions.Closed`` does not fire on a PARTIAL close, and neither bot reported
one. When the position finally closed, ``ReportPositionClosed`` sent
``pos.NetProfit`` of the REMAINDER while the DB row still carried the original
volume -- so the profit banked at break-even vanished from every statistic.

Observed on GBPJPY #674345493 (22/09):

    05:15:30  open  0.09 lots
    08:16:09  [Partial Close] 0.02 lots at Break-Even   <- no report sent
    08:41:55  closed, PnL 38.27                          <- only the 0.07

DB row: volume 0.09, pnl 38.27. AiAgentBot closes 50% at BE, so the dashboard
under-reported half the winning leg of every winning trade, systematically.

The fix needs no schema change: ``pnl`` is NULL while a position is open and the
``daily_stats`` view only reads ``status = 'closed'``, so the open row can bank
realised partial P&L and the final close adds to it.
"""

from pathlib import Path

import pytest

from app.portfolio import PortfolioManager

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def pm(tmp_path):
    manager = PortfolioManager(db_path=str(tmp_path / "partial.db"))
    manager.register_position(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        side="Sell",
        volume=0.09,
        entry_price=195.40,
        sl_pips=20.0,
        tp_pips=40.0,
        account_id="acct-1",
    )
    return manager


def _row(manager):
    conn = manager._get_conn()
    try:
        cur = conn.execute(
            "SELECT volume, pnl, status FROM positions WHERE bot_id = ? AND symbol = ?",
            ("gbpjpy-all-flowrsi", "GBPJPY"),
        )
        r = cur.fetchone()
        return {"volume": r[0], "pnl": r[1], "status": r[2]}
    finally:
        conn.close()


# ── server side: the position row must track the partial ──

def test_partial_close_reduces_volume_and_banks_realised_pnl(pm):
    ok = pm.record_partial_close(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        remaining_volume=0.07,
        realized_pnl=12.00,
        account_id="acct-1",
    )
    assert ok
    row = _row(pm)
    assert row["status"] == "open", "a partial close must not close the position"
    assert row["volume"] == pytest.approx(0.07), (
        "volume still shows the original size, so risk and exposure read high"
    )
    assert row["pnl"] == pytest.approx(12.00), (
        "profit realised at break-even was not banked on the row"
    )


def test_final_close_adds_to_the_banked_partial(pm):
    pm.record_partial_close(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        remaining_volume=0.07,
        realized_pnl=12.00,
        account_id="acct-1",
    )
    pm.close_position(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        exit_price=194.10,
        pnl=38.27,
        account_id="acct-1",
    )
    row = _row(pm)
    assert row["status"] == "closed"
    assert row["pnl"] == pytest.approx(50.27), (
        "the final close overwrote the banked partial instead of adding to it - "
        "this is the 38.27-instead-of-50.27 bug from the GBPJPY trade"
    )


def test_close_without_any_partial_is_unaffected(pm):
    """Guard against over-fixing: the ordinary path must report exactly what it reports."""
    pm.close_position(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        exit_price=194.10,
        pnl=38.27,
        account_id="acct-1",
    )
    assert _row(pm)["pnl"] == pytest.approx(38.27)


def test_banked_partial_stays_out_of_daily_stats_until_the_position_closes(pm):
    pm.record_partial_close(
        bot_id="gbpjpy-all-flowrsi",
        symbol="GBPJPY",
        remaining_volume=0.07,
        realized_pnl=12.00,
        account_id="acct-1",
    )
    conn = pm._get_conn()
    try:
        total = conn.execute("SELECT COALESCE(SUM(total_pnl), 0) FROM daily_stats").fetchone()[0]
    finally:
        conn.close()
    assert total == pytest.approx(0.0), (
        "an open position's banked partial leaked into daily_stats"
    )


def test_partial_close_on_an_unknown_position_is_rejected(pm):
    assert not pm.record_partial_close(
        bot_id="gbpjpy-all-flowrsi",
        symbol="EURUSD",
        remaining_volume=0.07,
        realized_pnl=12.00,
        account_id="acct-1",
    ), "a partial close for a symbol with no open row must not silently succeed"


# ── cBot side: both bots must actually send the report ──

@pytest.mark.parametrize(
    "cs_name,anchor",
    [
        ("FlowRsiBot.cs", "[Partial Close]"),
        ("AiAgentBot.cs", "[Partial Close]"),
    ],
)
def test_bot_reports_the_partial_close(cs_name, anchor):
    src = (ROOT / "cBot" / cs_name).read_text(encoding="utf-8")
    idx = src.index(anchor)
    window = src[max(0, idx - 1200) : idx + 1200]
    assert "ReportPartialClose" in window, (
        f"{cs_name} closes part of the position without reporting it. "
        f"Positions.Closed does not fire on a partial, so the realised profit never "
        f"reaches the DB and the row keeps its original volume."
    )


@pytest.mark.parametrize("cs_name", ["FlowRsiBot.cs", "AiAgentBot.cs"])
def test_bot_sends_partial_close_action(cs_name):
    src = (ROOT / "cBot" / cs_name).read_text(encoding="utf-8")
    assert '"partial_close"' in src, (
        f"{cs_name} does not send action=partial_close to /portfolio/report"
    )


@pytest.mark.parametrize("cs_name", ["FlowRsiBot.cs", "AiAgentBot.cs"])
def test_realised_pnl_comes_from_the_booked_deal(cs_name):
    """The DB stores money, so it must be the booked P&L (commission + swap), not an estimate."""
    src = (ROOT / "cBot" / cs_name).read_text(encoding="utf-8")
    idx = src.index("ReportPartialClose(")
    window = src[max(0, idx - 2000) : idx]
    assert "History.LastOrDefault" in window, (
        f"{cs_name} reports an estimated realised P&L. The booked HistoricalTrade "
        f"carries commission and swap; the NetProfit delta does not."
    )
    assert "pnlBeforePartial" in window, (
        f"{cs_name} has no fallback for when History is not yet populated."
    )


def test_ai_agent_bot_imports_linq_for_the_history_lookup():
    src = (ROOT / "cBot" / "AiAgentBot.cs").read_text(encoding="utf-8")
    assert "using System.Linq;" in src, (
        "AiAgentBot uses History.LastOrDefault but does not import System.Linq - "
        "this will not compile."
    )
