"""The pre-registered pass bar of docs/superpowers/specs/2026-09-26-strategy-refresh-design.md applied to a lab run.

  python -m research.lab.verdict RUN_DIR [ID ...]   ->   RUN_DIR/verdict.md   (default ids: catalog.REFRESH_IDS)

Per variant, pooled over its symbols: (1) holdout 2025-26 >= 100 trades, mean net R > 0, t >= 2.5; (2) net $ > 0
in 2025 and in 2026; (3) check period 2023-24 mean net R > 0; (4) holdout net above >= 95 % of the random-entry
control seeds; (5) mirrored holdout net > 0 (not for N1/N2); (6) holdout net > 0 on >= 60 % of the symbols that
traded in the holdout (not for N2)."""
import csv
import gzip
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HOLDOUT, CHECK = (2025, 2026), (2023, 2024)
MIN_TRADES, MIN_T, CONTROL_PCT, BREADTH = 100, 2.5, 95.0, 0.6
NO_MIRROR = {"N1-FIX", "N2-GOTOBI"}
NO_BREADTH = {"N2-GOTOBI"}
NAN = float("nan")


def _mean_t(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return len(r), (float(r.mean()) if len(r) else NAN), NAN
    sd = float(r.std(ddof=1))
    return len(r), float(r.mean()), float(r.mean() / (sd / math.sqrt(len(r)))) if sd > 0 else NAN


def evaluate(rows, control, sid: str) -> dict:
    """rows: trade dicts of one strategy (all variants); control: {seed: pooled holdout net}."""
    real = [r for r in rows if r["variant"] == "real"]
    hold = [r for r in real if int(r["year"]) in HOLDOUT]
    n, mean_r, t = _mean_t([float(r["r"]) for r in hold])
    _, mean_r_check, _ = _mean_t([float(r["r"]) for r in real if int(r["year"]) in CHECK])
    net = {y: sum(float(r["net"]) for r in real if int(r["year"]) == y) for y in HOLDOUT}
    hold_net = sum(net.values())
    mirror_rows = [r for r in rows if r["variant"] == "mirror" and int(r["year"]) in HOLDOUT]
    mirror = sum(float(r["net"]) for r in mirror_rows) if mirror_rows else NAN
    by_sym = defaultdict(float)
    for r in hold:
        by_sym[r["symbol"]] += float(r["net"])
    breadth = sum(v > 0 for v in by_sym.values()) / len(by_sym) if by_sym else NAN
    seeds = list(control.values())
    control_pct = 100.0 * float(np.mean(np.asarray(seeds) < hold_net)) if seeds else NAN
    checks = {
        "holdout >= 100 trades, mean R > 0, t >= 2.5": n >= MIN_TRADES and mean_r > 0 and t >= MIN_T,
        "2025 > 0 and 2026 > 0": net[2025] > 0 and net[2026] > 0,
        "2023-24 mean R > 0": mean_r_check > 0,
        "beats >= 95 % of control seeds": control_pct >= CONTROL_PCT,
        "mirror net > 0": sid in NO_MIRROR or mirror > 0,
        "breadth >= 60 %": sid in NO_BREADTH or breadth >= BREADTH,
    }
    return dict(id=sid, n=n, mean_r=mean_r, t=t, net_2025=net[2025], net_2026=net[2026], mean_r_check=mean_r_check,
                control_pct=control_pct, mirror_net=mirror, breadth=breadth, symbols=len(by_sym), checks=checks,
                passed=all(checks.values()))


def load(run_dir, ids):
    run_dir, ids = Path(run_dir), set(ids)
    rows = defaultdict(list)
    with gzip.open(run_dir / "trades.csv.gz", "rt") as fh:
        for r in csv.DictReader(fh):
            if r["strategy"] in ids:
                rows[r["strategy"]].append(r)
    control = defaultdict(lambda: defaultdict(float))
    if (run_dir / "control.csv").exists():
        with open(run_dir / "control.csv") as fh:
            for r in csv.DictReader(fh):
                if r["strategy"] in ids and int(r["year"]) in HOLDOUT:
                    control[r["strategy"]][int(r["seed"])] += float(r["net"])
    return dict(rows), {k: dict(v) for k, v in control.items()}


def _f(x, fmt):
    return "" if isinstance(x, float) and math.isnan(x) else format(x, fmt)


def render(results) -> str:
    names = list(results[0]["checks"]) if results else []
    lines = ["# Verdict — strategy refresh 2026-09-26", "",
             "Pass bar: docs/superpowers/specs/2026-09-26-strategy-refresh-design.md (pre-registered). Holdout = "
             "2025-01 .. 2026-09, check = 2023-24.", "",
             "| id | holdout n | mean R | t | 2025 $ | 2026 $ | 2023-24 mean R | ctrl % | mirror $ | breadth | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in results:
        lines.append(f"| {v['id']} | {v['n']} | {_f(v['mean_r'], '+.3f')} | {_f(v['t'], '+.2f')} | "
                     f"{v['net_2025']:+,.0f} | {v['net_2026']:+,.0f} | {_f(v['mean_r_check'], '+.3f')} | "
                     f"{_f(v['control_pct'], '.0f')} | {_f(v['mirror_net'], '+,.0f')} | "
                     f"{_f(v['breadth'], '.0%')} of {v['symbols']} | {'PASS' if v['passed'] else 'fail'} |")
    lines += ["", "## Conditions", "", "| id | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for v in results:
        lines.append(f"| {v['id']} | " + " | ".join("yes" if v["checks"][k] else "**no**" for k in names) + " |")
    passed = [v["id"] for v in results if v["passed"]]
    lines += ["", f"Passed: {', '.join(passed) if passed else 'none'}."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    run_dir = Path(argv[0])
    if len(argv) > 1:
        ids = argv[1:]
    else:
        from research.lab.catalog import REFRESH_IDS
        ids = list(REFRESH_IDS)
    rows, control = load(run_dir, ids)
    results = [evaluate(rows.get(i, []), control.get(i, {}), i) for i in ids]
    (run_dir / "verdict.md").write_text(render(results))
    print(run_dir / "verdict.md")


if __name__ == "__main__":
    main()
