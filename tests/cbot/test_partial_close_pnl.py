"""
Regression guard for the P&L reported when a position closes after a partial close.

On 2026-10-23 the broker stopped out the three live Gotobi shorts in slices (02:02-02:40 UTC). A partial close leaves
the position open on fewer units, and ``Positions.Closed`` then carries only the last slice: the bots reported
``pos.NetProfit`` of it (-4.60, -3.97, -24.26) while the account lost ~$690 on the three shorts; ~$660 never reached
the dashboard. Every bot now records the units a position opened with while it is open (``TrackOpenedUnits``) and
adds the earlier slices from History (``PartialClosesNet``) to the reported net.
"""


import pytest
from tests._paths import CBOT_DIR
from tests.cbot.test_exit_price_from_history import _body


BOTS = ["GotobiBot.cs", "EcbWindowBot.cs", "GoldLevelBot.cs"]
CLOSE_HANDLER = "private void OnPositionClosed(PositionClosedEventArgs args)"
# The loop each bot runs over its open positions on every tick / timer call.
MANAGE_LOOP = {
    "GotobiBot.cs": "private void CloseDueLegs(DateTime now)",
    "EcbWindowBot.cs": "private void CloseDueWindows(DateTime now)",
    "GoldLevelBot.cs": "private void ManageExits(DateTime now)",
}


@pytest.mark.parametrize("cs_name", BOTS)
def test_close_report_adds_the_earlier_slices(cs_name):
    body = _body(cs_name, CLOSE_HANDLER)
    assert "PartialClosesNet(pos)" in body, f"{cs_name} reports only the last slice of a partially closed position."
    assert "ReportPositionClosed(pos, pos.NetProfit" not in body, (
        f"{cs_name} reports pos.NetProfit, which after a stop out in slices is the last slice only."
    )


@pytest.mark.parametrize("cs_name", BOTS)
def test_opened_units_tracked_while_open(cs_name):
    body = _body(cs_name, MANAGE_LOOP[cs_name])
    assert "TrackOpenedUnits(pos)" in body, (
        f"{cs_name} never records the units its positions opened with, so PartialClosesNet finds no slice."
    )


@pytest.mark.parametrize("cs_name", BOTS)
def test_slices_are_the_earliest_deals_up_to_the_units_lost(cs_name):
    body = _body(cs_name, "private double PartialClosesNet(Position pos)")
    # The final close's own deal may or may not be in History yet: summing every deal would count it twice.
    assert "OrderBy(h => h.ClosingTime)" in body
    assert "opened - pos.VolumeInUnits" in body
