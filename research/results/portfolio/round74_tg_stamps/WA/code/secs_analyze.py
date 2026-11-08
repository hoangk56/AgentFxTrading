"""Stream WA: summarise the seconds check (secs.csv). Side-signed gross bp, day-clustered t, by era and group.
missed = from the first aggTrade >= post + 5 s to the 1-minute design's entry bar open (what the 1-minute entry gives
up); s60 / s5m / s15m / s60m = seconds-entry (post + 5 s) to post + 65 / 305 / 905 / 3605 s; late = entry at post + 10 s
to the same exits (5-min); k5m = the 1-minute design's 5-min gross on the same events (klines)."""
import csv, os, sys, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ct, px, SIDE, SYM

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/whale_alert"
rows = list(csv.DictReader(open(os.path.join(D, "secs.csv"))))
G = {"F all": lambda r: r["kind"] in ("BI", "BO", "EI", "EO"),
     "F >=100M": lambda r: r["kind"] in ("BI", "BO", "EI", "EO") and float(r["usd"]) >= 1e8,
     "inflow (short)": lambda r: r["kind"] in ("BI", "EI"), "outflow (long)": lambda r: r["kind"] in ("BO", "EO"),
     "M (long)": lambda r: r["kind"] == "M", "B (short)": lambda r: r["kind"] == "B"}
print("| era | group | n | days | missed | s60 | s5m | late s5m | k5m (1-min design) | s15m | s60m |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for era in ("IS", "VAL"):
    for g, fn in G.items():
        rs = [r for r in rows if r["era"] == era and fn(r)]
        if len(rs) < 5:
            continue
        sd = np.array([SIDE[r["kind"]] for r in rs]); day = np.array([int(r["day"]) for r in rs])
        P = lambda k: np.array([float(r[k]) if r[k] else np.nan for r in rs])
        p5, p10, pb = P("p5"), P("p10"), P("p_bar")
        k5 = np.full(len(rs), np.nan)
        for sym in ("BTCUSDT", "ETHUSDT"):
            ix = [i for i, r in enumerate(rs) if r["sym"] == sym]
            if ix:
                a, b, ok, _ = px(sym, np.array([float(rs[i]["ts"]) + 5 for i in ix]), 0, 5)
                k5[ix] = np.where(ok, b / a - 1, np.nan)
        cols = [sd * (pb / p5 - 1), sd * (P("p65") / p5 - 1), sd * (P("p305") / p5 - 1), sd * (P("p305") / p10 - 1),
                sd * k5, sd * (P("p905") / p5 - 1), sd * (P("p3605") / p5 - 1)]
        out = []
        for c in cols:
            c = c * 1e4; ok = np.isfinite(c); m, t = ct(c[ok], day[ok])
            out.append(f"{m:+.2f} ({t:+.1f})")
        print(f"| {era} | {g} | {len(rs)} | {len(set(day))} | " + " | ".join(out) + " |")
