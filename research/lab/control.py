"""Random-entry control for one (strategy, symbol, chunk): the real trades' shapes (stop distance, target
distance, holding time as a time cap) replayed in order at random M15 bar closes with random sides, one
position at a time. Its P&L is what the costs and the exit shape earn without the entry signal."""
from typing import List

import numpy as np

from research.lab.engine import Ctx, Intent, Trade, run_intents
from research.lab.feed import Chunk


def random_control(ch: Chunk, real: List[Trade], seed: int) -> List[Trade]:
    if not real:
        return []
    ctx = Ctx(ch, f"control:{seed}")
    closes = getattr(ch, "_control_closes", None)       # built once per chunk, reused by every strategy and seed
    if closes is None:
        closes = ctx.bars(15).close_time
        closes = ch._control_closes = closes[(closes >= ch.lo_ms) & (closes < ch.hi_ms)]
    if len(closes) == 0:
        return []
    rng = np.random.default_rng(seed)
    times = np.sort(rng.choice(closes, size=min(len(closes), 3 * len(real)), replace=False))
    shapes = [(abs(tr.entry - tr.sl0), abs(tr.tp0 - tr.entry), max(tr.t_out - tr.t_in, 60_000)) for tr in real]
    k = 0
    for at in times:
        if k == len(shapes):
            break
        sl_d, tp_d, hold = shapes[k]
        side = 1 if rng.random() < 0.5 else -1
        before = len(ctx.trades)
        run_intents(ctx, [Intent(int(at), side, sl_d, tp_d, int(at) + int(hold))])
        k += len(ctx.trades) > before
    return ctx.trades
