"""Build Friday entry quotes (tenor 7 / 30, normal and late) per currency; save to research/data/deribit/quotes_<cur>.npy."""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vrp

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit"

if __name__ == "__main__":
    cur = sys.argv[1]
    m = vrp.Mkt(cur)
    res = {}
    for tenor in (7, 30):
        for late in (False, True):
            qs = []
            for f0 in vrp.fridays("2021-03-26", "2024-12-31"):
                q = vrp.entry_quote(m, f0, tenor, late)
                if q is not None and np.isfinite(q["dvol"]):
                    qs.append(q)
            res[(tenor, late)] = qs
            rt = [tuple(q["route"]) for q in qs]
            print(cur, tenor, "late" if late else "on-time", "n", len(qs),
                  "both legs mark", sum(r == ("mark", "mark") for r in rt), "any iv", sum("iv" in r for r in rt),
                  "hs med %.4f" % np.nanmedian([q["hs"] for q in qs]),
                  "sig/dvol med %.3f" % np.median([q["sig"] / q["dvol"] for q in qs]),
                  "|K/S-1| med %.4f" % np.median([abs(q["K"] / q["S0"] - 1) for q in qs]))
    pickle.dump(res, open(f"{OUT}/quotes_{cur}.pkl", "wb"))
