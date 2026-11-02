"""Tables for STREAM_N.md from out/results_*.json (writes out/report.txt)."""
import json, glob, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
C, top = {}, None
for f in sorted(glob.glob(os.path.join(OUT, "results_*.json"))):
    if f.endswith("results_P.json"):
        continue
    r = json.load(open(f)); C.update(r["configs"]); conc = r["concurrency"]; top = r["istop"]; sett = r["settled"]
L = []
pr = L.append
pr("concurrency " + json.dumps(conc))
pr("IS top coins by IS signal count: " + ", ".join(f"{c}({n},{b:.0f}bp sum)" for c, n, b in top[:20]))
pr("settled-perp guard: " + str(sett))
hdr = "| config | era | capital Q (held) | price | funding | build+reset+unwind | liq | inv net | cash | inv excess | B route | B trades cov / P&L cov | comb excess (%/yr cap) | t_nw | DD comb Q (% cap) | cost per B trade bp | resets / liqs |"
pr(hdr); pr("|" + "---|" * 17)
for nm, r in C.items():
    for e, s in r["eras"].items():
        ev = s["events"]
        pr(f"| {nm} | {e} | {s['cap_mean']:.1f} ({s['held_mean']:.1f}) | {s['price']:+.2f} | {s['fund']:+.2f} | {s['build']+s['reset']+s['unwind']:.2f} | {s['liq']:.2f} | "
           f"{s['inv']:+.2f} | {s['cash']:.2f} | {s['excess_inv']:+.2f} | {s['B_route_Qyr']:+.2f} | {s['B_share_trades']:.2f} / {s['B_share_pnl']:.2f} | "
           f"{s['excess_comb']:+.2f} ({s['excess_comb_pct']:+.1f} %) | {s['t_nw_excess_comb']:+.2f} | {s['dd_comb_Q']:.1f} ({s['dd_comb_pct']:.1f} %) | "
           f"{s['route_cost_per_Btrade_bp']:+.0f} | {ev['resets']} / {ev['liqs']} |")
pr("")
pr("| P year | capital Q | held | price | funding | funding %/yr of notional | costs | inv net | cash | inv excess | B route (n cov) | comb excess | comb excess %/yr | DD comb Q | worst day Q |")
pr("|" + "---|" * 15)
for y, s in C["P"]["years"].items():
    notional = s["held_mean"] * 1.25
    pr(f"| {y} | {s['cap_mean']:.1f} | {s['held_mean']:.1f} | {s['price']:+.2f} | {s['fund']:+.2f} | {s['fund'] / notional * 100:+.1f} | {s['cost']:.2f} | {s['inv']:+.2f} | "
       f"{s['cash']:.2f} | {s['excess_inv']:+.2f} | {s['B_route_Qyr']:+.2f} ({s['B_n_cov']}) | {s['excess_comb']:+.2f} | {s['excess_comb_pct']:+.1f} | {s['dd_comb_Q']:.1f} | {s['worst_day_comb_Q']:+.2f} |")
pr("")
pc = C["P"]["per_coin"]
for e in ("IS", "VAL"):
    Ls = sorted(pc, key=lambda x: x[1][e][0])
    pr(f"P {e} worst inventory coins (net Q, funding Q, price Q over the era): " + ", ".join(f"{c} {t[e][0]:+.2f} ({t[e][1]:+.2f}, {t[e][2]:+.2f})" for c, t in Ls[:8]))
    pr(f"P {e} best: " + ", ".join(f"{c} {t[e][0]:+.2f} ({t[e][1]:+.2f}, {t[e][2]:+.2f})" for c, t in Ls[-5:]))
# portfolio-margin proxy from m1.0 (few liquidations): capital N* x 1.1 instead of N* x 2
for nm in ("m1.0", "info_m1.0_rehedge"):
    for e, s in C[nm]["eras"].items():
        cash_pm = s["cash"] * 1.1 / 2.0
        inv_noliq = s["inv"] + s["liq"]
        pr(f"PM proxy from {nm} {e}: capital {s['cap_mean'] * 1.1 / 2:.1f} Q, inv without liq {inv_noliq:+.2f}, cash {cash_pm:.2f}, excess {inv_noliq - cash_pm:+.2f} Q/yr, "
           f"+B {inv_noliq - cash_pm + s['B_route_Qyr']:+.2f} Q/yr, per B trade {-(inv_noliq - cash_pm) / (s['B_n_cov'] / (2.0 if e == 'IS' else 3.0)) * 1e4:+.0f} bp")
open(os.path.join(OUT, "report.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
