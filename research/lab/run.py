"""Run the strategy catalog over the lab universe (docs/superpowers/specs/2026-09-25-strategy-lab-design.md).

  python -m research.lab.run [--strategies ID ...] [--symbols SYM ...] [--variants real mirror]
                             [--years 2023 2024 2025 2026] [--seeds 20] [--workers 3] [--run-dir DIR]
  python -m research.lab.run --shuffle 20 --into RUN_DIR      # week-shuffle the cells whose real net > 0

One job = one (symbol, variant). Inside a job the years run in order, so a position can carry across a year end,
and every strategy trades the same loaded chunk. Real-data jobs also run the random-entry control (--seeds).
Each job writes RUN_DIR/parts/<SYMBOL>_<variant>.*.csv; merge() joins them into trades.csv.gz, control.csv,
errors.csv and coverage.csv. meta.json records the arguments, the git HEAD, the lab code hash and the catalog hash."""
import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import time
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from research.lab.catalog import by_id, catalog_hash, runnable_ids
from research.lab.feed import YEARS
from research.lab.universe import ALL, REAL, instrument
from research.ticks import DATA_DIR

RESULTS = Path(__file__).resolve().parents[1] / "results" / "lab"
TRADE_FIELDS = ["strategy", "symbol", "variant", "year", "side", "t_in", "t_out", "entry", "exit", "units", "sl0",
                "tp0", "gross", "comm", "swap", "net", "risk_usd", "r", "why"]
CONTROL_FIELDS = ["strategy", "symbol", "year", "seed", "n", "net", "sum_r", "n_r"]
ERROR_FIELDS = ["strategy", "symbol", "variant", "year", "traceback"]
COVERAGE_FIELDS = ["symbol", "variant", "year", "status", "ticks"]


def trade_row(tr, year: int) -> list:
    return [tr.strategy, tr.symbol, tr.variant, year, tr.side, tr.t_in, tr.t_out, f"{tr.entry:.6f}", f"{tr.exit:.6f}",
            f"{tr.units:g}", f"{tr.sl0:.6f}", f"{tr.tp0:.6f}", f"{tr.gross:.4f}", f"{tr.comm:.4f}", f"{tr.swap:.4f}",
            f"{tr.net:.4f}", f"{tr.risk_usd:.4f}", f"{tr.r:.5f}", tr.why]


def _job_strategies(symbol: str, variant: str, ids) -> List[str]:
    base = variant.split(":")[0]
    cat = by_id()
    return [i for i in ids if symbol in cat[i].symbols and base in cat[i].variants and (base == "real" or symbol in REAL)]


def run_job(symbol: str, variant: str, ids: List[str], years: List[int], seeds: int, run_dir: str) -> dict:
    from research.lab.control import random_control
    from research.lab.engine import Ctx
    from research.lab.feed import load_chunk
    cat = by_id()
    parts = Path(run_dir) / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    tag = f"{symbol}_{variant.replace(':', '-')}"
    busy = {i: 0 for i in ids}
    n_trades = n_errors = 0
    t0 = time.time()
    files = {k: open(parts / f"{tag}.{k}.csv", "w", newline="") for k in ("trades", "control", "errors", "coverage")}
    try:
        w = {k: csv.writer(f) for k, f in files.items()}
        for y in years:
            ch = load_chunk(symbol, variant, y)
            if ch is None:
                w["coverage"].writerow([symbol, variant, y, "no data", 0])
                continue
            w["coverage"].writerow([symbol, variant, y, "ok", len(ch.t)])
            for i in ids:
                try:
                    ctx = Ctx(ch, i, busy[i])
                    cat[i].run(ctx)
                    busy[i] = ctx.busy_ms
                    w["trades"].writerows(trade_row(tr, y) for tr in ctx.trades)
                    n_trades += len(ctx.trades)
                    for s in range(seeds if variant == "real" else 0):
                        c = random_control(ch, ctx.trades, s)
                        rs = [x.r for x in c if math.isfinite(x.r)]
                        w["control"].writerow([i, symbol, y, s, len(c), f"{sum(x.net for x in c):.4f}", f"{sum(rs):.5f}",
                                               len(rs)])
                except Exception:
                    n_errors += 1
                    w["errors"].writerow([i, symbol, variant, y, traceback.format_exc()])
            del ch
    finally:
        for f in files.values():
            f.close()
    return dict(symbol=symbol, variant=variant, strategies=len(ids), trades=n_trades, errors=n_errors,
                seconds=round(time.time() - t0))


def merge(run_dir: Path) -> None:
    run_dir = Path(run_dir)
    parts = sorted((run_dir / "parts").glob("*.csv"))
    with gzip.open(run_dir / "trades.csv.gz", "wt", newline="") as out:
        w = csv.writer(out)
        w.writerow(TRADE_FIELDS)
        for p in parts:
            if p.name.endswith(".trades.csv"):
                with open(p, newline="") as fh:
                    w.writerows(csv.reader(fh))
    for kind, fields in (("control", CONTROL_FIELDS), ("errors", ERROR_FIELDS), ("coverage", COVERAGE_FIELDS)):
        with open(run_dir / f"{kind}.csv", "w", newline="") as out:
            w = csv.writer(out)
            w.writerow(fields)
            for p in parts:
                if p.name.endswith(f".{kind}.csv"):
                    with open(p, newline="") as fh:
                        w.writerows(csv.reader(fh))


def positive_cells(run_dir: Path, ids) -> Dict[str, List[str]]:
    """Real-data cells with net > 0 over the whole period, eligible for the week shuffle: symbol -> ids."""
    net = defaultdict(float)
    with gzip.open(Path(run_dir) / "trades.csv.gz", "rt") as fh:
        for row in csv.DictReader(fh):
            if row["variant"] == "real" and row["strategy"] in ids:
                net[(row["strategy"], row["symbol"])] += float(row["net"])
    out = defaultdict(list)
    for (s, sym), v in sorted(net.items()):
        if v > 0 and _job_strategies(sym, "shuffle:0", [s]):
            out[sym].append(s)
    return dict(out)


def _weight(symbol: str) -> int:
    inst = instrument(symbol)
    legs = inst.cross[:2] if inst.synthetic else (symbol,)
    return sum(f.stat().st_size for s in legs for f in (DATA_DIR / s / "t1").glob("*.zticks"))


def _provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()
    h = hashlib.sha256()
    for f in sorted(Path(__file__).parent.rglob("*.py")):
        h.update(f.read_bytes())
    return dict(git=head, lab_sha=h.hexdigest()[:12], catalog=catalog_hash())


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies", nargs="*")
    ap.add_argument("--symbols", nargs="*", default=list(ALL))
    ap.add_argument("--variants", nargs="*", default=["real", "mirror"])
    ap.add_argument("--years", nargs="*", type=int, default=list(YEARS))
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--run-dir")
    ap.add_argument("--shuffle", type=int, default=0)
    ap.add_argument("--into")
    args = ap.parse_args(argv)
    ids = args.strategies or runnable_ids()
    if args.shuffle:
        run_dir = Path(args.into)
        jobs = [(sym, f"shuffle:{k}", sids) for sym, sids in positive_cells(run_dir, ids).items()
                for k in range(args.shuffle)]
    else:
        run_dir = Path(args.run_dir) if args.run_dir else RESULTS / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
        jobs = [(sym, v, _job_strategies(sym, v, ids)) for sym in args.symbols for v in args.variants]
    jobs = sorted((j for j in jobs if j[2]), key=lambda j: -_weight(j[0]))
    run_dir.mkdir(parents=True, exist_ok=True)
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"runs": []}
    meta["runs"].append(dict(argv=vars(args), jobs=len(jobs), started=datetime.now(timezone.utc).isoformat(),
                             **_provenance()))
    meta_path.write_text(json.dumps(meta, indent=1))
    print(f"{run_dir}: {len(jobs)} jobs", flush=True)
    with ProcessPoolExecutor(args.workers) as ex:
        futures = [ex.submit(run_job, sym, v, sids, args.years, args.seeds, str(run_dir)) for sym, v, sids in jobs]
        for f in as_completed(futures):
            print(json.dumps(f.result()), flush=True)
    merge(run_dir)
    meta["runs"][-1]["finished"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=1))
    print(run_dir)


if __name__ == "__main__":
    main()
