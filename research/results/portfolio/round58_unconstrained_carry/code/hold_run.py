"""Round 58 registered HOLD look (PREREG_A_funding_carry.md). Run once: python -I hold_run.py <symbols-file>.

Prints, for each registered rule, the HOLD stats and every pass-bar item. Nothing here may change after registration.
"""
import sys

sys.path.insert(0, ".")
import numpy as np  # noqa: E402

import carry as C  # noqa: E402

RULES = {
    "A3": dict(L=14, th_in=0.10, th_out=0.0, K=2, only={"BTCUSDT", "ETHUSDT"}),
}
A2_CELL = dict(L=7, th_in=0.10, th_out=0.0, K=10)  # a2_grid.py IS pick, see PREREG


def main():
    syms = [s.strip() for s in open(sys.argv[1]) if s.strip()]
    rules = dict(RULES)
    if A2_CELL is not None:
        rules["A2"] = A2_CELL
    P = C.load_panel(syms, hold=True)
    U, rank = C.universe(P, N=30)
    d0, d1 = C.era_slice(P, "HOLD")
    yrs = C.years(P["days"][d0:d1])
    for name, cfg in rules.items():
        b, eps = C.simulate(P, U, rank, d0=d0, d1=d1, **cfg)
        st = C.stats(b)
        b15, _ = C.simulate(P, U, rank, d0=d0, d1=d1, cost_mult=1.5, **cfg)
        bl, _ = C.simulate(P, U, rank, d0=d0, d1=d1, lag=1, **cfg)
        rs = [C.stats(C.random_book(P, U, rank, eps, d0, d1, K=cfg["K"], rng=np.random.default_rng(s)))["sharpe_a"]
              for s in range(500)]
        beat = float(np.mean(np.array(rs) < st["sharpe_a"]))
        per_year = {int(y): float(b[yrs == y].sum()) for y in np.unique(yrs)}
        print(f"== {name} {cfg}")
        print("  HOLD days %d  ann %.2f%%  vol %.2f%%  SRa %.2f  t_nw %.2f  maxdd %.2f%%  episodes %d" % (
            st["n"], 100 * st["ann"], 100 * st["vol"], st["sharpe_a"], st["t_nw"], 100 * st["maxdd"], len(eps)))
        print("  per year (sum of daily net):", {k: round(100 * v, 2) for k, v in per_year.items()})
        print("  costs x1.5 ann %.2f%%   one day late ann %.2f%%" % (100 * b15.mean() * 365, 100 * bl.mean() * 365))
        print("  random draws beaten %.1f%% (median SRa %.2f)" % (100 * beat, np.median(rs)))
        print("  worst 5 days %%:", np.round(100 * np.sort(b)[:5], 3))
        bars = {
            "1 net > 0 and t_nw >= 2.25": st["ann"] > 0 and st["t_nw"] >= 2.25,
            "2 costs x1.5 > 0 and late > 0": b15.mean() > 0 and bl.mean() > 0,
            "3 every HOLD year > 0": all(v > 0 for v in per_year.values()),
            "4 beats >= 80 % random": beat >= 0.80,
        }
        for k, v in bars.items():
            print("   ", "PASS" if v else "FAIL", k)
        print("  VERDICT:", "PASS (LIVE)" if all(bars.values()) else "FAIL")
        for (i, e, x, c) in eps:
            print("    ep", P["syms"][i], str(np.datetime64(int(P["days"][e]), "ms"))[:10],
                  str(np.datetime64(int(P["days"][x]), "ms"))[:10], "%.2f%%" % (100 * (C.episode_pnl(P, i, e, x).sum() - c)))


if __name__ == "__main__":
    main()
