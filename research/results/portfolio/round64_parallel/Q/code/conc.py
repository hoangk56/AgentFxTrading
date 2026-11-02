"""Information: concentration of a cell on 1h opens (coins, days, side, gap at signal)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import q, run
pairs = q.load()
cn = sys.argv[1]
c = [c for c in run.CELLS if run.name(c) == cn][0]
rows = [r for r in run.price_1m(pairs, c, run.trades_for(pairs, c), None) if not np.isnan(r["net1h"])]
for era in q.ERAS:
    K = run.era_rows(rows, era)
    tot = sum(r["net1h"] for r in K)
    by = {}
    for r in K:
        by.setdefault(r["coin"], []).append(r["net1h"])
    days = {}
    for r in K:
        days.setdefault(run.day_of(r["te"]), []).append(r["net1h"])
    print(era, "n", len(K), "sum bp", round(tot * 1e4), "cm cheap share", np.mean([r["side"] > 0 for r in K]).round(2),
          "median |d| bp", round(np.median([abs(r["d"]) for r in K]) * 1e4))
    print(" coins", sorted([(k, len(v), round(np.mean(v) * 1e4)) for k, v in by.items()], key=lambda x: -x[1] * x[2])[:10])
    top = sorted(days.items(), key=lambda x: -sum(x[1]))[:6]
    print(" top days", [(d, len(v), round(sum(v) / tot * 100)) for d, v in top])
    ex = [r["net1h"] for r in K if not any(a <= run.day_of(r["te"]) <= b for a, b in
          (("2020-03-01", "2020-03-31"), ("2021-05-17", "2021-05-24"), ("2022-05-07", "2022-05-20"), ("2022-11-06", "2022-11-20")))]
    print(" ex crash windows n", len(ex), "net", round(np.mean(ex) * 1e4, 1) if ex else None)
