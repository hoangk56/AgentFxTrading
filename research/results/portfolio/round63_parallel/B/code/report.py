"""Print markdown tables from ../out/cells.json (IS / VAL only)."""
import json, os, math
J = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "cells.json")))
f = lambda v, d=1: "-" if v is None or (isinstance(v, float) and math.isnan(v)) else (f"{v:.{d}f}" if isinstance(v, float) else str(v))
print("| cell | era | n | days | gross | fund | cost | carry | net bp | t | x1.5 | late | maker | rand % | rand mean | ex-crash net (t) | SR/trade | SR/day |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for name, r in J["cells"].items():
    for era in ("IS", "VAL"):
        s = r[era]
        if not s.get("n"):
            print(f"| {name} | {era} | 0 |"); continue
        nc = s["nocrash"]
        print(f"| {name} | {era} | {s['n']} | {s['days']} | {f(s['gross_bp'])} | {f(s['fund_bp'])} | {f(s['cost_bp'])} | "
              f"{f(s['carry_bp'],2)} | {f(s['net_bp'])} | {f(s['t'],2)} | {f(s['net_x1.5_bp'])} | {f(s['late_net_bp'])} | "
              f"{f(s['maker_net_bp'])} | {f(100*s['beats_random'] if s.get('beats_random') is not None else None,0)} | "
              f"{f(s['random_mean_bp'])} | {f(nc['net_bp'])} ({f(nc['t'],2)}) | {f(s['sr'],3)} | {f(s['sr_day'],3)} |")
print()
print("| cell | " + " | ".join(str(y) for y in range(2020, 2025)) + " |")
print("|---|" + "---|" * 5)
for name, r in J["cells"].items():
    print(f"| {name} | " + " | ".join(f"{r['years'].get(str(y), [0, float('nan')])[1]:.1f} (n {r['years'].get(str(y), [0])[0]})" for y in range(2020, 2025)) + " |")
print()
print("max-over-cells null:", J["nulls"])
print()
print("| cell | VAL trades/yr | VAL event-days/yr | power per trade | power per day |")
print("|---|---|---|---|---|")
for name, r in J["cells"].items():
    s = r["VAL"]
    if not s.get("n"):
        continue
    ny, nd = s["n"] / 3, s["days"] / 3
    pt = s["sr"] * math.sqrt(1.8 * ny) if s["sr"] == s["sr"] else float("nan")
    pdy = s["sr_day"] * math.sqrt(1.8 * nd) if s["sr_day"] == s["sr_day"] else float("nan")
    print(f"| {name} | {ny:.0f} | {nd:.0f} | {pt:.2f} | {pdy:.2f} |")
