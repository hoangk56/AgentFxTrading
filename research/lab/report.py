"""Tables from a lab run.   python -m research.lab.report RUN_DIR   ->   cells.csv, matrix.csv, report.md

A cell is (strategy, symbol) on real data. Per cell: trades, net $, gross, commission, swap, PF, win rate,
mean R and its t, max drawdown, worst month, share of positive months, the date a $10k account would have
reached zero ("blown"), net and trades per year, and the stress tests: mirror net, and the percentile of the real
net among the random-control seeds and among the week-shuffle seeds. Flags: E = positive in every year that had
trades (at least two such years), C = above >= 95 % of the control seeds, S = above >= 95 % of the shuffle seeds
(shuffled cells only), M = mirror net > 0 (mirrored cells only)."""
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from research.lab.feed import YEARS

START = 10_000.0
NAN = float("nan")
CELL_FIELDS = (["strategy", "symbol", "n", "net", "gross", "comm", "swap", "pf", "win", "mean_r", "t_r", "max_dd",
                "worst_month", "months_pos", "blown"] + [f"net_{y}" for y in YEARS] + [f"n_{y}" for y in YEARS]
               + ["mirror_net", "control_pct", "shuffle_pct", "shuffles", "pos_every_year", "beats_control",
                  "shuffle_ok", "mirror_ok", "all_flags"])
FLAGS = (("E", "pos_every_year"), ("C", "beats_control"), ("S", "shuffle_ok"), ("M", "mirror_ok"))


def _month(ms) -> int:
    d = datetime.fromtimestamp(int(ms) / 1000, timezone.utc)
    return d.year * 100 + d.month


def stats(rows) -> dict:
    if not rows:
        return dict(n=0, net=0.0, gross=0.0, comm=0.0, swap=0.0, pf=NAN, win=NAN, mean_r=NAN, t_r=NAN, max_dd=0.0,
                    worst_month=0.0, months_pos=NAN, blown="")
    rows = sorted(rows, key=lambda r: int(r["t_out"]))
    net = np.array([float(r["net"]) for r in rows])
    rr = np.array([float(r["r"]) for r in rows])
    rr = rr[np.isfinite(rr)]
    cum = np.cumsum(net)
    dd = float(np.max(np.maximum.accumulate(np.r_[0.0, cum]) - np.r_[0.0, cum]))
    months = defaultdict(float)
    for r, v in zip(rows, net):
        months[_month(r["t_out"])] += v
    mv = np.array(list(months.values()))
    below = np.flatnonzero(START + cum <= 0)
    wins, losses = float(net[net > 0].sum()), float(-net[net < 0].sum())
    sd = float(rr.std(ddof=1)) if len(rr) > 1 else 0.0
    return dict(n=len(net), net=float(net.sum()), gross=sum(float(r["gross"]) for r in rows),
                comm=sum(float(r["comm"]) for r in rows), swap=sum(float(r["swap"]) for r in rows),
                pf=wins / losses if losses > 0 else math.inf, win=float((net > 0).mean()),
                mean_r=float(rr.mean()) if len(rr) else NAN,
                t_r=float(rr.mean() / (sd / math.sqrt(len(rr)))) if sd > 0 else NAN, max_dd=dd,
                worst_month=float(mv.min()), months_pos=float((mv > 0).mean()),
                blown=(datetime.fromtimestamp(int(rows[below[0]]["t_out"]) / 1000, timezone.utc).date().isoformat()
                       if below.size else ""))


def _pct_below(x: float, sample) -> float:
    return 100.0 * float(np.mean(np.asarray(sample) < x)) if len(sample) else NAN


def build(run) -> list:
    run = Path(run)
    trades = defaultdict(list)
    with gzip.open(run / "trades.csv.gz", "rt") as fh:
        for row in csv.DictReader(fh):
            trades[(row["strategy"], row["symbol"], row["variant"])].append(row)
    control = defaultdict(lambda: defaultdict(float))
    if (run / "control.csv").exists():
        with open(run / "control.csv") as fh:
            for row in csv.DictReader(fh):
                control[(row["strategy"], row["symbol"])][int(row["seed"])] += float(row["net"])
    shuffles, mirrors = defaultdict(list), {}
    for (s, sym, v), rows in trades.items():
        if v.startswith("shuffle:"):
            shuffles[(s, sym)].append(sum(float(r["net"]) for r in rows))
        elif v == "mirror":
            mirrors[(s, sym)] = sum(float(r["net"]) for r in rows)
    cells = []
    for s, sym in sorted({(s, sym) for (s, sym, v) in trades if v == "real"} | set(control)):
        real = trades.get((s, sym, "real"), [])
        full = stats(real)
        years = {y: stats([r for r in real if int(r["year"]) == y]) for y in YEARS}
        ctrl, shuf = list(control[(s, sym)].values()), shuffles.get((s, sym), [])
        cell = dict(strategy=s, symbol=sym, **full, **{f"net_{y}": years[y]["net"] for y in YEARS},
                    **{f"n_{y}": years[y]["n"] for y in YEARS}, mirror_net=mirrors.get((s, sym), NAN),
                    control_pct=_pct_below(full["net"], ctrl), shuffle_pct=_pct_below(full["net"], shuf),
                    shuffles=len(shuf))
        with_trades = [y for y in YEARS if years[y]["n"] > 0]
        cell["pos_every_year"] = len(with_trades) >= 2 and all(years[y]["net"] > 0 for y in with_trades)
        cell["beats_control"] = bool(ctrl) and cell["control_pct"] >= 95.0
        cell["shuffle_ok"] = bool(shuf) and cell["shuffle_pct"] >= 95.0
        cell["mirror_ok"] = math.isfinite(cell["mirror_net"]) and cell["mirror_net"] > 0
        cell["all_flags"] = all(cell[k] for _, k in FLAGS)
        cells.append(cell)
    return cells


def _fmt(v):
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.4f}"
    return v


def _markdown(run: Path, cells: list) -> str:
    meta = json.loads((run / "meta.json").read_text()) if (run / "meta.json").exists() else {"runs": [{}]}
    errors = sum(1 for _ in csv.reader(open(run / "errors.csv"))) - 1 if (run / "errors.csv").exists() else 0
    ys = " | ".join(str(y) for y in YEARS)
    L = [f"# Strategy lab run {run.name}", "",
         f"$10k account, fixed lots, no loss limits, one position per strategy x symbol, ticks {YEARS[0]}-{YEARS[-1]}. "
         f"Cells: {len(cells)}; strategy errors: {errors}; catalog {meta['runs'][-1].get('catalog', '?')}, "
         f"lab code {meta['runs'][-1].get('lab_sha', '?')}.", "",
         "Flags: E = positive in every year with trades (>= 2 years), C = above >= 95 % of 20 random-entry seeds, "
         "S = above >= 95 % of the week-shuffle seeds, M = mirror net > 0. Long-only rules (TOM, OD1) cannot pass M "
         "by construction.", "",
         "## Strategies (real data, summed over symbols)", "",
         f"| strategy | {ys} | total $ | cells + | E | C | all |", "|---|" + "---|" * (len(YEARS) + 5)]
    by = defaultdict(list)
    for c in cells:
        by[c["strategy"]].append(c)
    for s, cs in sorted(by.items(), key=lambda kv: -sum(c["net"] for c in kv[1])):
        L.append(f"| {s} | " + " | ".join(f"{sum(c[f'net_{y}'] for c in cs):+,.0f}" for y in YEARS)
                 + f" | {sum(c['net'] for c in cs):+,.0f} | {sum(c['net'] > 0 for c in cs)}/{len(cs)} | "
                 f"{sum(c['pos_every_year'] for c in cs)} | {sum(c['beats_control'] for c in cs)} | "
                 f"{sum(c['all_flags'] for c in cs)} |")
    L += ["", "## Top 30 cells by net $", "",
          f"| strategy | symbol | n | net $ | {ys} | PF | mean R | max DD $ | worst month $ | blown | mirror $ | "
          "ctrl pct | shuf pct | flags |", "|---|---|---|---|" + "---|" * (len(YEARS) + 9)]
    for c in sorted(cells, key=lambda c: -c["net"])[:30]:
        flags = "".join(f for f, k in FLAGS if c[k]) or "-"
        L.append(f"| {c['strategy']} | {c['symbol']} | {c['n']} | {c['net']:+,.0f} | "
                 + " | ".join(f"{c[f'net_{y}']:+,.0f}" for y in YEARS)
                 + f" | {c['pf']:.2f} | {c['mean_r']:+.3f} | {c['max_dd']:,.0f} | {c['worst_month']:+,.0f} | "
                 f"{c['blown'] or '-'} | {c['mirror_net']:+,.0f} | {c['control_pct']:.0f} | {c['shuffle_pct']:.0f} | "
                 f"{flags} |")
    passing = [c for c in cells if c["all_flags"]]
    L += ["", f"## Cells with all four flags: {len(passing)}", ""]
    L += [f"- {c['strategy']} on {c['symbol']}: net {c['net']:+,.0f} $, PF {c['pf']:.2f}, max DD {c['max_dd']:,.0f} $"
          for c in passing] or ["- none"]
    L += ["", "Full tables: cells.csv (every cell), matrix.csv (strategy x symbol net $)."]
    return "\n".join(L)


def write(run, cells: list) -> None:
    run = Path(run)
    with open(run / "cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, CELL_FIELDS)
        w.writeheader()
        w.writerows({k: _fmt(c[k]) for k in CELL_FIELDS} for c in cells)
    symbols = sorted({c["symbol"] for c in cells})
    net = {(c["strategy"], c["symbol"]): c["net"] for c in cells}
    with open(run / "matrix.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["strategy"] + symbols + ["total"])
        for s in sorted({c["strategy"] for c in cells}):
            row = [net.get((s, y), NAN) for y in symbols]
            w.writerow([s] + [_fmt(v) for v in row] + [_fmt(float(np.nansum(row)))])
    (run / "report.md").write_text(_markdown(run, cells))


def main(argv=None) -> None:
    run = Path((sys.argv[1:] if argv is None else argv)[0])
    write(run, build(run))
    print(run / "report.md")


if __name__ == "__main__":
    main()
