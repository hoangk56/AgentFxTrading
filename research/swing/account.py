"""Account-level simulation with capital-based sizing (round 5, results/portfolio/sizing_round5_2026-09-27.md).

Each trade risks a fixed fraction of the account equity at its entry: risk = f x equity x lot multiplier, P&L = R x
risk, realized at the exit. Positions overlap as in the trade list (the bot's cap is already applied there), so a
trade opened while others are running is sized off the equity realized so far. This changes nothing about a
strategy's edge (mean R); it shows what compounding at a given risk does to growth and drawdown.

    python -m research.swing.account research/results/portfolio/trades_C3_gotobi_jpy_basket.csv --risk 0.01 0.02
    python -m research.swing.account research/results/portfolio/gotobi_cbot_trades.csv --ctrader-risk-usd 50 --risk 0.02
"""
import argparse
import csv
import datetime
import heapq
from typing import Dict, List, Sequence, Tuple

import numpy as np

Trade = Tuple[int, int, float, float]          # (t_in ms, t_out ms, R, lot multiplier)
YEAR_MS = 365.25 * 86_400_000


def _ms(text: str, fmt: str) -> int:
    return int(datetime.datetime.strptime(text, fmt).replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)


def load_research_trades(path: str) -> List[Trade]:
    """A trade list written by the swing engine (columns t_in_utc, t_out_utc, r, lot_x_default)."""
    with open(path) as fh:
        return sorted((_ms(r["t_in_utc"], "%Y-%m-%d %H:%M"), _ms(r["t_out_utc"], "%Y-%m-%d %H:%M"), float(r["r"]),
                       float(r["lot_x_default"])) for r in csv.DictReader(fh))


def load_ctrader_trades(path: str, risk_usd: float) -> List[Trade]:
    """A cTrader backtest trade list (entry_utc, close_utc, net); R = net / the run's $ risk per trade."""
    with open(path) as fh:
        return sorted((_ms(r["entry_utc"], "%Y-%m-%d %H:%M:%S"), _ms(r["close_utc"], "%Y-%m-%d %H:%M:%S"),
                       float(r["net"]) / risk_usd, 1.0) for r in csv.DictReader(fh))


def compound(trades: Sequence[Trade], risk_frac: float, start: float = 1.0) -> List[Tuple[int, float]]:
    """Equity after each exit, as (t_out, equity)."""
    eq, running, curve = start, [], []
    for t_in, t_out, r, lot in sorted(trades):
        while running and running[0][0] <= t_in:
            t, pnl = heapq.heappop(running)
            eq += pnl
            curve.append((t, eq))
        heapq.heappush(running, (t_out, r * risk_frac * eq * lot))
    while running:
        t, pnl = heapq.heappop(running)
        eq += pnl
        curve.append((t, eq))
    return curve


def stats(curve: Sequence[Tuple[int, float]], start: float = 1.0) -> Dict[str, object]:
    t = np.array([c[0] for c in curve])
    e = np.array([c[1] for c in curve])
    peak = np.maximum.accumulate(np.r_[start, e])
    dd = 1.0 - np.r_[start, e] / peak
    years = max((t[-1] - t[0]) / YEAR_MS, 1e-9)
    by_year, prev = {}, start
    for ti, ei in zip(t, e):
        by_year[datetime.datetime.fromtimestamp(ti / 1000, datetime.timezone.utc).year] = ei
    growth = {}
    for y in sorted(by_year):
        growth[y] = by_year[y] / prev - 1.0
        prev = by_year[y]
    return dict(cagr=(e[-1] / start) ** (1 / years) - 1.0, max_dd=float(dd.max()), final=float(e[-1] / start),
                by_year=growth)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trades")
    ap.add_argument("--risk", type=float, nargs="+", default=[0.005, 0.01, 0.02, 0.03, 0.04])
    ap.add_argument("--ctrader-risk-usd", type=float, help="read a cTrader trade list whose runs risked this $ per trade")
    args = ap.parse_args(argv)
    trades = (load_ctrader_trades(args.trades, args.ctrader_risk_usd) if args.ctrader_risk_usd
              else load_research_trades(args.trades))
    print(f"{len(trades)} trades, mean R {np.mean([t[2] for t in trades]):+.3f}")
    for f in args.risk:
        s = stats(compound(trades, f))
        years = " ".join(f"{y}:{g:+.0%}" for y, g in s["by_year"].items())
        print(f"risk {f:.1%}/trade: CAGR {s['cagr']:+.1%}  max DD {s['max_dd']:.1%}  x{s['final']:,.1f}  | {years}")


if __name__ == "__main__":
    main()
