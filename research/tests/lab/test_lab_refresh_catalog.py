import math
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.lab.catalog import CATALOG, REFRESH_IDS, by_id  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk, real_ticks  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402


def test_refresh_entries_are_the_fourteen_pre_registered_candidates():
    assert REFRESH_IDS == ("T1-ORB", "T2-TMSORB", "T3-TMSORB-X", "T4-TMS-H4", "T5-TMS-H1", "J1-ICT", "J2-ICT-MO",
                           "J3-ICT-2R", "J4-ICT-2KZ", "J5-SWEEP", "N1-FIX", "N2-GOTOBI", "N3-IMOM", "N4-LBO")
    cat = by_id()
    assert all(cat[i].status == "rejected" and cat[i].runnable for i in REFRESH_IDS)      # verdict v2: none passed
    assert all(cat[i].findings[0].startswith("Lab run v2 (2026-09-26") for i in REFRESH_IDS)
    assert not ({"BTCUSD", "ETHUSD"} & set(cat["J1-ICT"].symbols))
    assert cat["N2-GOTOBI"].symbols == ("USDJPY",) and "mirror" not in cat["N1-FIX"].variants
    assert {"PREFOMC", "WKGAP", "CARRY"} <= {s.id for s in CATALOG if s.status == "rejected" and not s.runnable}


@needs_ticks
@pytest.mark.parametrize("sid,sym", [("T2-TMSORB", "EURUSD"), ("T3-TMSORB-X", "USDJPY"), ("T5-TMS-H1", "EURUSD"),
                                     ("J1-ICT", "EURUSD"), ("J5-SWEEP", "GBPUSD"), ("N3-IMOM", "US30"),
                                     ("N4-LBO", "EURUSD")])
def test_no_lookahead_cutting_the_ticks_keeps_every_earlier_entry(sid, sym):
    t = real_ticks(sym, date(2025, 1, 6), date(2025, 3, 28))
    cut = day_ms(date(2025, 3, 7))
    lo, hi = day_ms(date(2025, 2, 3)), day_ms(date(2025, 3, 28))
    keep = t.ts < cut
    full = Chunk(sym, "real", 2025, t, lo, hi, instrument(sym))
    part = Chunk(sym, "real", 2025, Ticks(t.ts[keep], t.bid[keep], t.ask[keep]), lo, hi, instrument(sym))
    runs = []
    for ch in (full, part):
        ctx = Ctx(ch, sid)
        by_id()[sid].run(ctx)
        runs.append([(tr.t_in, tr.side, round(tr.sl0, 6), None if math.isnan(tr.tp0) else round(tr.tp0, 6))
                     for tr in ctx.trades if tr.t_in < cut])
    assert runs[0] == runs[1] and len(runs[0]) > 0
