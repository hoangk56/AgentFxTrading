"""N1a-c at the Dukascopy-measured ECN cost: 0.4 bp commission + half the 2010-15 Dukascopy median spread at the
entry fill's New York minute label + half at the 18:00 label (out/n1_duka_spreads.json)."""
import json
import numpy as np
import eng
import run

D = json.load(open(run.OUT / "n1_duka_spreads.json"))
for v in ("N1a", "N1b", "N1c"):
    z = np.load(run.OUT / f"{v}_trades.npz", allow_pickle=True)
    sym = z["sym"]; ms = z["ms_in"]; g = z["gross"]
    lab = eng.ny_minute(ms)
    c = np.empty(len(ms))
    for i, (s, l) in enumerate(zip(sym, lab)):
        key = f"{l // 60:02d}:{l % 60:02d}"
        tab = D[str(s)]
        sp_in = tab[key][0] if key in tab else tab["17:10"][0]
        c[i] = 0.4 + 0.5 * (sp_in + tab["18:00"][0])
    day = eng.day_of(ms)
    for e, m in run.era_masks(ms).items():
        mu, t = eng.cl_t(g[m] - c[m], day[m])
        print(f"{v} {e}: n {m.sum()} mid {np.mean(g[m]):+.2f} duka cost {c[m].mean():.2f} net {mu:+.2f} (t {t:+.2f}) "
              f"break-even cost {np.mean(g[m]):.2f}; by pair net " +
              " ".join(f"{s} {np.mean((g - c)[m & (sym == s)]):+.2f}" for s in np.unique(sym)))
