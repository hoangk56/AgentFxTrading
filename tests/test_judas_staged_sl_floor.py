"""
Regression guard for C-08 (audit 2026-09-22): sniper entries bypassed the SL floor.

``ExecuteDecision`` clamps the AI's stop up to an anti-stop-hunt floor
(``max(AiSlMinFloorPips, 0.8 * ATR)``) and sizes the volume from the clamped
value. ``ExecuteStagedMarketOrder`` -- the Anti-FOMO sniper path, on by default
via ``enableWickRetracementHunting`` -- then RECOMPUTES ``slPips`` from
``decision.new_sl_price`` against the pulled-back price and never re-applies the
floor, while still using ``_stagedVolumeUnits`` sized for the original stop.

XAUUSD: AI proposes 210p, staging clamps to 200p and sizes volume for 200p.
Price pulls back 150p, the sniper fires, and the recomputed stop is ~60p -- deep
inside the noise the floor exists to avoid, on a position sized for 200p.

Volume is linear in 1/slPips, so a stop cut to 30% of the sized distance carries
roughly 3x the intended risk.
"""

from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AsianRangeJudasSweepBot.cs"


def _src() -> str:
    return CS_PATH.read_text(encoding="utf-8")


def _method_body(signature: str) -> str:
    src = _src()
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
    raise AssertionError(f"Unbalanced braces in {signature!r}")


FLOOR_HELPER = "GetEffectiveSlFloorPips"


def test_sl_floor_is_a_shared_helper():
    src = _src()
    assert f"private double {FLOOR_HELPER}()" in src, (
        f"The anti-stop-hunt floor is still computed inline. Extract it as "
        f"{FLOOR_HELPER}() so every order path applies the same floor."
    )


def test_staged_sniper_reapplies_the_sl_floor():
    body = _method_body("private void ExecuteStagedMarketOrder(TradeType tradeType)")
    recompute_idx = body.index("Recalculate SL/TP pips relative to actual executed entry price")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    region = body[recompute_idx:order_idx]
    assert FLOOR_HELPER in region, (
        "ExecuteStagedMarketOrder recomputes slPips against the pulled-back price but "
        "never re-applies the ATR/AiSlMinFloorPips floor - the anti-stop-hunt guard "
        "disappears exactly when price is closest to the stop."
    )


def test_staged_sniper_resizes_volume_when_the_stop_changes():
    body = _method_body("private void ExecuteStagedMarketOrder(TradeType tradeType)")
    recompute_idx = body.index("Recalculate SL/TP pips relative to actual executed entry price")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    region = body[recompute_idx:order_idx]
    assert "volume =" in region, (
        "volume is still _stagedVolumeUnits, sized for the stop distance computed at "
        "STAGING time. After the stop is recomputed the dollar risk no longer matches "
        "what the risk engine intended."
    )
    assert "_stagedSlPips" in region, (
        "The resize must be relative to the staged stop distance the volume was sized for."
    )


def test_execute_decision_uses_the_same_helper():
    body = _src()
    decision_idx = body.index("Safety Guard: Dynamic ATR & Minimum SL Floor")
    region = body[decision_idx : decision_idx + 900]
    assert FLOOR_HELPER in region, (
        "ExecuteDecision must use the shared floor helper, otherwise the two paths can "
        "drift apart again."
    )


def test_staged_resize_is_logged():
    body = _method_body("private void ExecuteStagedMarketOrder(TradeType tradeType)")
    recompute_idx = body.index("Recalculate SL/TP pips relative to actual executed entry price")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    assert "Print(" in body[recompute_idx:order_idx], (
        "A staged order whose stop and volume were adjusted must say so in the log."
    )
