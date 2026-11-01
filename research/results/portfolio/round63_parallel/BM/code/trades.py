"""Stream BM step 2: list every trade of B's registered rule k100_H24_cheap in IS / VAL / HOLD.
Uses B's HOLD harness unchanged (B/code/hold_run.py imports the frozen basis.py / universe.py and only overrides
universe.END, basis.CUT, basis.ERAS['HOLD']), then simulate(coins, 100, 24, -1) unchanged.
Writes BM/out/trades_b.csv (one row per trade)."""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BCODE = os.path.normpath(os.path.join(HERE, "..", "..", "B", "code"))
sys.path.insert(0, BCODE)
import hold_run  # noqa: E402  (runtime overrides of the HOLD harness)
import basis  # noqa: E402

H = basis.H
OUT = os.path.join(HERE, "..", "out", "trades_b.csv")


def era_of(t):
    for nm, (a, b) in basis.ERAS.items():
        if a <= t < b:
            return nm
    return None


def main():
    coins = basis.load()
    T = basis.simulate(coins, 100, 24, -1)
    rows = []
    for i in range(len(T["e"])):
        c = coins[T["ci"][i]]
        e, x, h = int(T["e"][i]), int(T["x"][i]), int(T["h"][i])
        era = era_of(T["t"][i])
        if era is None:
            continue
        rows.append(dict(
            id=i, era=era, perp=c["perp"], spot=c["spot"], fac=c["fac"], rank=int(c["rank"][h]),
            T=int(c["hours"][e]), X=int(c["hours"][x]), hold_h=x - e,
            b_h=c["b"][h], m_h=c["m"][h], d_h=c["b"][h] - c["m"][h],
            Fc_h=c["Fc"][h], Sc_h=c["Sc"][h], Fo_e=c["Fo"][e], So_e=c["So"][e], Fo_x=c["Fo"][x], So_x=c["So"][x],
            price=T["price"][i], fund=T["fund"][i], cost=T["cost"][i], carry=T["carry"][i], net=T["net"][i],
            forced=int(T["forced"][i])))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for era in ("IS", "VAL", "HOLD"):
        s = basis.summarize(T, era)
        print(f"{era}: n {s['n']} net {s['net_bp']:.1f} bp t {s['t']:.2f}")
    print("rows", len(rows), "->", OUT)


if __name__ == "__main__":
    main()
