"""Markdown tables from out/*.json (and out_r24read/*.json)."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["F2", "F4", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F23", "F24", "M2", "M4", "M7",
         "M11", "M12", "I1", "I3", "I4", "I5", "I6", "I8", "I10", "I13", "E1x", "E2x", "C1", "N1a", "N1b", "N1c"]
VENUE = {"F": "ECN", "M": "GC", "I1": "NQ", "I3": "YM", "I4": "ES", "I5": "Z", "I6": "SPI", "I8": "HSI", "I10": "FDAX",
         "I13": "ES", "E1x": "CL", "E2x": "CL", "C1": "CME BTC", "N": "ECN"}


def venue(i):
    return VENUE.get(i, VENUE.get(i[0]))


def main(d="out"):
    print("| id | sym | sel | venue | cost rt bp IS / VAL: venue lo-up (IC) | IS n | IS mid | IS net up (t) | IS net lo (t) "
          "| VAL n/yr | VAL mid | VAL net up (t) | VAL net lo (t) | x1.5 IS/VAL | +1m IS/VAL | random IS/VAL % | yrs+ "
          "| power VAL (at 0.65) | LIVE cost rt | tier up / lo | fails (up) |")
    print("|" + "---|" * 21)
    rows = []
    for i in ORDER:
        p = ROOT / d / f"{i}.json"
        if not p.exists():
            continue
        r = json.load(open(p)); a, b = r["IS"], r["VAL"]
        flag = " (c)" if r["contaminated"] else ""
        rows.append(r)
        print(f"| {i}{flag} | {r['sym']} | {r['sel']} | {venue(i)} | {a['cost_lo']:.2f}-{a['cost_up']:.2f} ({a['cost_ic']:.2f}) / "
              f"{b['cost_lo']:.2f}-{b['cost_up']:.2f} ({b['cost_ic']:.2f}) | {a['n']} | {a['mid']:+.2f} | {a['net_up']:+.2f} ({a['t_up']:+.2f}) "
              f"| {a['net_lo']:+.2f} ({a['t_lo']:+.2f}) | {b['n']}/{b['per_year']:.0f} | {b['mid']:+.2f} | {b['net_up']:+.2f} ({b['t_up']:+.2f}) "
              f"| {b['net_lo']:+.2f} ({b['t_lo']:+.2f}) | {a['x15']:+.2f}/{b['x15']:+.2f} | {a['lat1']:+.2f}/{b['lat1']:+.2f} "
              f"| {r['random']['IS']:.0f}/{r['random']['VAL']:.0f} | {r['years_pos']} | {r['power']:+.2f} ({r['power065']:+.2f}) "
              f"| {r['live_cost']:+.2f} | {r['tier']} / {r['tier_lo']} | {', '.join(r['fails'])} |")
    ts = [abs(r["IS"]["t_up"]) for r in rows if r["id"] in ORDER]
    print(f"\nK = {len(rows)}; best IS t at the upper bound {max(r['IS']['t_up'] for r in rows):+.2f} "
          f"({max(rows, key=lambda r: r['IS']['t_up'])['id']}); max |t| of K normals: median "
          f"{np.median(np.abs(np.random.default_rng(1).standard_normal((20000, len(rows)))).max(1)):.2f}, p95 "
          f"{np.percentile(np.abs(np.random.default_rng(1).standard_normal((20000, len(rows)))).max(1), 95):.2f}")
    print("\nby year (net at the upper bound):")
    for r in rows:
        print(f"- {r['id']}: " + ", ".join(f"{y} {v:+.2f}" for y, v in {**r['IS']['by_year'], **r['VAL']['by_year']}.items()))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
