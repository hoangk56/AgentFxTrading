"""Round 75: check every cached month of a symbol; prints the bad months (one per line) after a summary line.

    research/.venv/bin/python -I .../check_fp.py SOLUSDT
A month is good when its decoded footprint minutes equal its 1m bar minutes, every footprint bucket lies inside that
minute's [low, high] (+-1 bp), aggressive buy / sell qty per minute equal the 1m bar's, and trade counts are > 0.
"""
import importlib.util
import os
import sys

import numpy as np

spec = importlib.util.spec_from_file_location("fp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fp.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)


def check(sym, path):
    z = np.load(path)
    mi, b = fp.split_key(z["fp_key"], sym)
    if not np.array_equal(np.unique(mi), z["m_min"]) or (z["m_n"] <= 0).any():
        return False
    idx = np.searchsorted(z["m_min"], mi)
    if not np.all((b >= fp.bucket(z["m_l"])[idx] - 1) & (b <= fp.bucket(z["m_h"])[idx] + 1)):
        return False
    n = len(z["m_min"])
    for w, v in (("fp_ask", "m_vb"), ("fp_bid", "m_vs")):
        if not np.allclose(np.bincount(idx, weights=z[w], minlength=n), z[v], rtol=1e-3, atol=1e-2):
            return False
    return True


def main():
    sym = sys.argv[1]
    bad = [os.path.basename(p)[:7] for p in fp._months(sym) if not check(sym, p)]
    print(f"{sym} months {len(fp._months(sym))} bad {len(bad)}", flush=True)
    for m in bad:
        print(m)


if __name__ == "__main__":
    main()
