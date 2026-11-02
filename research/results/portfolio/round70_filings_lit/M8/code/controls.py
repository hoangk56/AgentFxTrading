"""Post-hoc control (added after the first results, labelled post-hoc): the same UTC clock time 7 and 14 days before
each FRESH event (same weekday), skipping days that hold any event. Writes research/data/btc_treasury_8k/controls.csv."""
import csv, os
import numpy as np
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
ev = list(csv.DictReader(open(os.path.join(D, "events.csv"))))
evdays = {str(np.datetime64(int(e["T_ms"]), "ms"))[:10] for e in ev}
rows = []
for e in ev:
    if e["cls"] != "FRESH":
        continue
    for k in (7, 14):
        Tc = int(e["T_ms"]) - k * 86400000
        day = str(np.datetime64(Tc, "ms"))[:10]
        if day in evdays:
            continue
        rows.append(dict(acc=e["acc"], tk=e["tk"], lag_days=k, T_ms=Tc, day=day))
with open(os.path.join(D, "controls.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), len({r["day"] for r in rows}))
