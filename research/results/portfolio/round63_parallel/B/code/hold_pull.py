"""HOLD look data pull (PREREG_B_cheap_basis.md). Runs the frozen pull.py source unchanged except its CAP constant
(2024-12-31 -> 2026-10-29 23:59:59.999 UTC), into a staging root research/data/binance_basis/hold_stage/ whose
requests.log is a symlink to the main requests.log, then appends the new rows to the existing files.
Usage (python -I):
  hold_pull.py stage          build hold_stage/{perp,spot,funding}_rows.csv from ../universe60_hold.csv
  hold_pull.py pull perp|spot|funding
  hold_pull.py merge          append staged rows (t > last existing t) into binance_basis/<kind>/
"""
import csv, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
BB = os.path.join(RES, "data", "binance_basis")
BF = os.path.join(RES, "data", "binance", "funding")
ST = os.path.join(BB, "hold_stage")
UFILE = os.path.join(HERE, "..", "universe60_hold.csv")
PULL = os.path.join(HERE, "pull.py")
OLD_CAP, NEW_CAP = "CAP = 1735689599999", "CAP = 1793318399999"
H, DAY = 3600000, 86400000
DIRS = {"perp": "perp_1h", "spot": "spot_1h", "funding": "funding"}
EXCL = {"BTCUSDT", "ETHUSDT"}


def last_t(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        r = csv.reader(f); next(r)
        t = None
        for row in r:
            if row:
                t = int(row[0])
    return t


def stage():
    os.makedirs(ST, exist_ok=True)
    log = os.path.join(ST, "requests.log")
    if not os.path.lexists(log):
        os.symlink(os.path.join(BB, "requests.log"), log)
    rows = [r for r in csv.reader(open(UFILE)) if r[0] not in EXCL]
    for kind in ("perp", "spot", "funding"):
        out, nfull, nappend, nskip = [], 0, 0, 0
        for perp, spot, fac, a, b in rows:
            a, b = int(a), int(b)
            sym = spot if kind == "spot" else perp
            if kind == "funding" and os.path.exists(os.path.join(BF, perp + ".csv")):
                nskip += 1
                continue
            start = a - 8 * DAY
            lt = last_t(os.path.join(BB, DIRS[kind], sym + ".csv"))
            if lt is not None:
                start = max(start, lt + (1 if kind == "funding" else H))
                nappend += 1
            else:
                nfull += 1
            if start >= min(b + 2 * DAY, 1793318400000):
                continue
            # pull.py starts at a - 8 days: pass start + 8 days
            out.append([perp, spot, fac, start + 8 * DAY, b])
        with open(os.path.join(ST, kind + "_rows.csv"), "w") as f:
            csv.writer(f).writerows(out)
        print(kind, "rows", len(out), "new symbols", nfull, "appends", nappend, "skipped (data/binance/funding)", nskip)


def pull(kind):
    src = open(PULL).read()
    assert src.count(OLD_CAP) == 1
    src = src.replace(OLD_CAP, NEW_CAP)
    sys.argv = [PULL, kind, os.path.join(ST, kind + "_rows.csv"), ST]
    exec(compile(src, PULL, "exec"), {"__file__": PULL, "__name__": "__main__"})


def merge():
    for kind, d in DIRS.items():
        sd = os.path.join(ST, d)
        if not os.path.isdir(sd):
            continue
        nnew, napp, nrows = 0, 0, 0
        for fn in sorted(os.listdir(sd)):
            if not fn.endswith(".csv"):
                continue
            with open(os.path.join(sd, fn)) as f:
                r = csv.reader(f); head = next(r); new = [x for x in r if x]
            dst = os.path.join(BB, d, fn)
            lt = last_t(dst)
            if lt is None:
                shutil.copyfile(os.path.join(sd, fn), dst); nnew += 1; nrows += len(new)
                continue
            add = [x for x in new if int(x[0]) > lt]
            if add:
                with open(dst, "a", newline="") as f:
                    csv.writer(f).writerows(add)
                napp += 1; nrows += len(add)
        print(kind, "new files", nnew, "appended files", napp, "rows added", nrows)


if __name__ == "__main__":
    {"stage": lambda: stage(), "pull": lambda: pull(sys.argv[2]), "merge": lambda: merge()}[sys.argv[1]]()
