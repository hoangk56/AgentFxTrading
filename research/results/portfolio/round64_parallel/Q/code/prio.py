"""Order the 1m need list by priority (Q1 k100 / k60 cells and Q2b_k30 first); split into two files."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import q, run
OUT = run.OUT
pairs = q.load()
sel = {}
for r in csv.DictReader(open(os.path.join(OUT, "selection.csv"))):
    sel.setdefault(r["cell"], set()).add((int(r["pi"]), int(r["e"])))
order = ["Q1_k100_H72", "Q1_k100_H24", "Q1_k60_H72", "Q1_k60_H24", "Q2b_k30", "Q2b_k20", "Q2b_k10", "Q2_k100_H72"]
order += [run.name(c) for c in run.CELLS if run.name(c) not in order]
seen, prio = set(), []
for cn in order:
    c = [c for c in run.CELLS if run.name(c) == cn][0]
    lines = []
    for t in run.trades_for(pairs, c):
        if (t["pi"], t["e"]) not in sel.get(cn, ()):
            continue
        p = pairs[t["pi"]]
        te, tx = run.ms(t["e"]), run.ms(t["x"])
        tts = (te - q.M, te + q.M, te + 5 * q.M, tx + q.M) + ((tx - 30 * q.M,) if c[0] == "Q2b" else ())
        for mk, sym in ((p["Amarket"], p["A"]), ("um", p["U"])):
            for tt in tts:
                k = (mk, sym, run.day_of(tt))
                if k not in seen:
                    seen.add(k); lines.append(k)
    prio.append((cn, lines))
    print(cn, len(lines), flush=True)
allk = [k for _, L in prio for k in L]
for i in range(2):
    with open(os.path.join(OUT, f"need_m1_{i}.txt"), "w") as f:
        for k in allk[i::2]:
            f.write(" ".join(k) + "\n")
