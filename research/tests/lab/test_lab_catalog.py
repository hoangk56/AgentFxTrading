import inspect
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_m1, needs_ticks  # noqa: E402
from research.lab.catalog import ALL_VARIANTS, CATALOG, STATUSES, render_markdown  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk, real_ticks  # noqa: E402
from research.lab.universe import ALL, instrument  # noqa: E402
from research.ticks import day_ms  # noqa: E402


def test_catalog_entries_are_complete():
    ids = [s.id for s in CATALOG]
    assert len(ids) == len(set(ids))
    for s in CATALOG:
        assert s.status in STATUSES and s.rules and s.origin and s.findings, s.id
        assert set(s.symbols) <= set(ALL) and set(s.variants) <= set(ALL_VARIANTS), s.id
        if s.runnable:
            inspect.signature(s.fn).bind(None, **s.params)
    assert {"FLOWRSI", "JUDAS", "TMSORB"} <= {s.id for s in CATALOG if s.status == "live"}
    assert sum(s.id.startswith("BANK-") for s in CATALOG) == 24
    assert sum(s.id.startswith("FLOWRSI-E") for s in CATALOG) == 20
    assert {"BTC-S1", "XAU-T1", "TOM", "K1", "K1b", "K2", "VB1", "LC1", "GF1", "OD1", "MEF", "FXM1", "X1", "WF1",
            "PAIRS"} <= set(ids)


def test_render_markdown_lists_every_strategy_and_the_lab_result(tmp_path):
    (tmp_path / "cells.csv").write_text("strategy,symbol,net,pos_every_year,all_flags\n"
                                        "BTC-S1,BTCUSD,1234.5,True,False\nBTC-S1,ETHUSD,-34.5,False,False\n")
    md = render_markdown(tmp_path)
    for s in CATALOG:
        assert f"## {s.id} — " in md
    assert "net $+1,200 over 2 symbols, 1 positive" in md


def test_render_markdown_later_run_replaces_a_strategy_and_keeps_the_rest(tmp_path):
    main, new = tmp_path / "main", tmp_path / "new"
    main.mkdir()
    new.mkdir()
    (main / "cells.csv").write_text("strategy,symbol,net,pos_every_year,all_flags\n"
                                    "BTC-S1,BTCUSD,100,False,False\nTOM,US30,50,False,False\n")
    (new / "cells.csv").write_text("strategy,symbol,net,pos_every_year,all_flags\nBTC-S1,BTCUSD,-7,False,False\n")
    md = render_markdown([main, new])
    assert "lab runs `main`, `new`" in md
    assert "Latest lab run `new`: net $-7 over 1 symbols" in md
    assert "Latest lab run `main`: net $+50 over 1 symbols" in md
    assert "net $+100" not in md


@needs_m1
@needs_ticks
def test_every_runnable_strategy_runs_on_a_short_slice():
    chunks = {}

    def chunk(sym):
        if sym not in chunks:
            t = real_ticks(sym, date(2025, 2, 3), date(2025, 3, 21))
            chunks[sym] = Chunk(sym, "real", 2025, t, day_ms(date(2025, 3, 3)), day_ms(date(2025, 3, 15)),
                                instrument(sym))
        return chunks[sym]

    for s in CATALOG:
        if s.runnable:
            ch = chunk("EURUSD" if "EURUSD" in s.symbols else s.symbols[0])
            ctx = Ctx(ch, s.id)
            s.run(ctx)
            assert all(ch.lo_ms <= tr.t_in < ch.hi_ms for tr in ctx.trades), s.id
