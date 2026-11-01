"""Stream O: print the tables of ../out/cells.json (markdown rows) to ../out/report.txt."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
J = json.load(open(os.path.join(OUT, "cells.json")))


def f(x, nd=1):
    return "-" if x is None else f"{x:+.{nd}f}"


lines = []
lines.append("| cell | DISC n | DISC net bp | DISC t | DISC gross | cost | rand % | VAL n | VAL net bp | VAL t | VAL gross |"
             " rand % | 2022 / 2023 / 2024 net | x1.5 t D / V | late t D / V | power trade / clust |")
lines.append("|" + "---|" * 16)
for name, c in J["cells"].items():
    d, v = c["DISC"], c["VAL"]
    yrs = " / ".join(f"{c['years'][y][0]:+.0f}" if y in c["years"] else "-" for y in ("2022", "2023", "2024"))
    lines.append(
        f"| {name} | {d.get('n', 0)} | {f(d.get('net'))} | {f(d.get('t'), 2)} | {f(d.get('gross'))} | {d.get('cost', 0):.1f} |"
        f" {d.get('rand_pct', float('nan')):.0f} | {v.get('n', 0)} | {f(v.get('net'))} | {f(v.get('t'), 2)} | {f(v.get('gross'))} |"
        f" {v.get('rand_pct', float('nan')):.0f} | {yrs} | {f(c['x1.5']['DISC'].get('t'), 2)} / {f(c['x1.5']['VAL'].get('t'), 2)} |"
        f" {f(c['late']['DISC'].get('t'), 2)} / {f(c['late']['VAL'].get('t'), 2)} |"
        f" {f(v.get('power_trade'), 2)} / {f(v.get('power_clust'), 2)} |")
lines.append("")
lines.append("null: " + json.dumps(J["null"]))
lines.append("")
lines.append("| information | DISC n | DISC net | DISC t | DISC gross | VAL n | VAL net | VAL t | VAL gross |")
lines.append("|" + "---|" * 9)
for name, c in J["info"].items():
    d, v = c["DISC"], c["VAL"]
    lines.append(f"| {name} | {d.get('n', 0)} | {f(d.get('net'))} | {f(d.get('t'), 2)} | {f(d.get('gross'))} | {v.get('n', 0)} |"
                 f" {f(v.get('net'))} | {f(v.get('t'), 2)} | {f(v.get('gross'))} |")
open(os.path.join(OUT, "report.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
