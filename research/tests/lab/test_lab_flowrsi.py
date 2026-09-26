from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.bars import build_bars  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies.flowrsi import flowrsi  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.screen import params_for  # noqa: E402
from research.signals import Market, build  # noqa: E402
from research.sim import make_levels, place_order, run_account  # noqa: E402
from research.specs import SPECS, flowrsi_params  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402


def test_place_order_with_fixed_units_skips_the_risk_sizing():
    p = flowrsi_params("XAUUSD")
    spec = SPECS["XAUUSD"]
    assert place_order(1, 2900.0, 2930.0, 2915.0, 2915.2, 100.0, spec, p) is None      # min-lot guard at $100
    units, sl, tp = place_order(1, 2900.0, 2930.0, 2915.0, 2915.2, 100.0, spec, p, fixed_units=2.0)
    assert units == 2.0 and sl == pytest.approx(2900.0) and tp == pytest.approx(2930.0)


@needs_ticks
def test_flowrsi_adapter_matches_the_replica_with_fixed_units():
    t = load_ticks("EURUSD", date(2025, 3, 1), date(2025, 4, 15))
    ch = Chunk("EURUSD", "real", 2025, t, day_ms(date(2025, 3, 10)), day_ms(date(2025, 4, 10)), instrument("EURUSD"))
    ctx = Ctx(ch, "FLOWRSI")
    flowrsi(ctx, "C0", "X2")
    spec, p = SPECS["EURUSD"], params_for("EURUSD", "C0", "X2")
    m = Market(build_bars(t, 15), build_bars(t, 60), build_bars(t, 240))
    sig = build("C0", m, spec, p).copy()
    sig[m.m15.close_time >= ch.hi_ms] = 0
    ref, _ = run_account(t, m.m15, sig, make_levels(m.m15, spec, p, "swing"), spec, p, "X2", 10_000.0,
                         start_ms=ch.lo_ms, fixed_units=10_000.0)
    assert len(ref) > 5
    assert [(r.entry_ts, r.side) for r in ref] == [(tr.t_in, tr.side) for tr in ctx.trades]
    assert [r.net for r in ref] == pytest.approx([tr.net for tr in ctx.trades], abs=1e-6)
    assert all(tr.units == 10_000 and np.isfinite(tr.sl0) for tr in ctx.trades)


@needs_ticks
def test_flowrsi_runs_on_a_synthetic_cross():
    from research.lab.feed import real_ticks
    t = real_ticks("EURGBP", date(2025, 3, 1), date(2025, 4, 15))
    ch = Chunk("EURGBP", "real", 2025, t, day_ms(date(2025, 3, 10)), day_ms(date(2025, 4, 10)), instrument("EURGBP"))
    ctx = Ctx(ch, "FLOWRSI")
    flowrsi(ctx, "C0", "X2")
    assert ctx.trades and all(tr.symbol == "EURGBP" and tr.units == 10_000 for tr in ctx.trades)
