"""FlowRSI in the lab: the calibrated replica (research/flowrsi/signals.py + research/flowrsi/sim.py; Macro TMS off, which the
replica does not model) with the lab's fixed units instead of the risk sizing, and the P&L rebuilt from the
replica's fills with the lab's costs. name = C0 (live presets), C1 (SL floor 25/30) or an entry-screening
candidate E1a..E5b; exit_mode X2 = FlowRSI's break-even/partial/trailing, X1 = fixed ATR stop and 1.5R target."""
from research.lab.engine import Ctx, Pos
from research.lab.universe import PRESET_TEMPLATE
from research.flowrsi.screen import params_for
from research.flowrsi.signals import Market, build
from research.flowrsi.sim import make_levels, run_account


def flowrsi(ctx: Ctx, name: str = "C0", exit_mode: str = "X2") -> None:
    spec = ctx.inst.spec()
    p = params_for(PRESET_TEMPLATE.get(ctx.ch.symbol, ctx.ch.symbol), name, exit_mode)
    m = Market(ctx.bars(15), ctx.bars(60), ctx.bars(240))
    sig = build(name, m, spec, p).copy()
    sig[m.m15.close_time >= ctx.ch.hi_ms] = 0
    levels = make_levels(m.m15, spec, p, "atr" if exit_mode == "X1" else "swing")
    trades, _ = run_account(ctx.t, m.m15, sig, levels, spec, p, exit_mode, 10_000.0,
                            start_ms=max(ctx.ch.lo_ms, ctx.busy_ms + 1), fixed_units=ctx.units)
    for tr in trades:
        pos = Pos(tr.side, tr.entry_tick, tr.entry, 0.0, tr.sl0, tr.tp0, tr.sl0, tr.tp0)
        pos.deals = [(j, px, u, "exit") for j, px, u in tr.fills]
        ctx.finish(pos)
