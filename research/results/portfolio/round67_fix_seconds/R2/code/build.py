"""Stream R2: notices, point-in-time baskets, real + random windows (../HYPOTHESES_R2.md). No prices are read here.
Output: research/data/upbit_rotation/plan.npz (+ plan.json summary). Everything is cut at ts < 2025-01-01."""
import csv, json, os, sys
import numpy as np

RES = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research"
sys.path.insert(0, os.path.join(RES, "results/portfolio/round65_retail_venues/R/code"))
import rdata  # noqa: E402  (read-only use of stream R's panel cache)

EV = os.path.join(RES, "results/portfolio/round65_retail_venues/A/notice_events_L.csv")
OUT = os.path.join(RES, "data", "upbit_rotation")
MIN = 60000; HOUR = 3600000; DAY = 86400000
CUT = rdata.CUT; H0 = rdata.H0
VAL0 = 1640995200000; IS0 = 1577836800000
NDRAW = int(os.environ.get("R2_NDRAW", "20"))
SEED = 67002


def notices():
    rows = list(csv.DictReader(open(EV)))
    by = {}
    for r in rows:
        by.setdefault(r["nid"], []).append(r)
    out = []
    for nid, rs in by.items():
        Ls = []
        for r in rs:
            if r["L1m"]:
                Ls.append(int(r["L1m"]))
            elif r["coin"] in ("STG", "BONK") and r["stated"]:
                Ls.append(int(r["stated"]) + 5 * MIN)
        if nid == "2217":  # MATIC / SOL: SOL's L
            Ls = [int(r["L1m"]) for r in rs if r["coin"] == "SOL"]
        if not Ls:
            continue  # SRM
        N = int(rs[0]["N"])
        if N >= CUT:
            continue
        out.append(dict(nid=nid, N=N, L=min(Ls), perps=[r["perp"] for r in rs], coins=[r["coin"] for r in rs]))
    out.sort(key=lambda e: e["N"])
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    D = rdata.load()
    S = rdata.shares(D)
    syms = D["syms"]; U = D["U"]; rk = D["rk"]
    ev = notices()
    nday = np.array([(e["N"] - H0) // DAY for e in ev])
    rng = np.random.default_rng(SEED)
    plan = []
    for e, d in zip(ev, nday):
        A = np.where(U[:, d] & np.isfinite(S[:, d]))[0]
        A = np.array([i for i in A if syms[i] not in e["perps"] and syms[i] != "BTCUSDT"])
        k = len(A) // 3
        o = A[np.argsort(-S[A, d], kind="stable")]
        hi, lo = o[:k], o[::-1][:k]
        te = -(-(e["N"] + MIN) // MIN)            # first bar opening at or after N + 60 s (minute index since epoch)
        t_in = (te + 1) * MIN                     # entry instant = close of bar te
        exits = [e["L"], e["L"] + HOUR, e["L"] + 6 * HOUR]
        era = "IS" if e["N"] < VAL0 else "VAL"
        lo_era, hi_era = (IS0, VAL0) if era == "IS" else (VAL0, CUT)
        # random day shifts
        cand = []
        for s in range(-60, 61):
            if abs(s) < 2:
                continue
            dd = d + s
            if np.min(np.abs(nday - dd)) < 2:
                continue
            t0 = t_in + s * DAY - 3 * MIN; t1 = exits[2] + s * DAY + 7 * MIN
            if t0 < lo_era or t1 >= hi_era:
                continue
            kst = np.datetime64(int(t_in + s * DAY + 9 * HOUR), "ms").astype("datetime64[D]")
            wd = (kst.astype(int) + 3) % 7       # 0 = Monday
            if wd >= 5:
                continue
            cand.append(s)
        draws = rng.choice(cand, size=min(NDRAW, len(cand)), replace=False) if cand else np.zeros(0, int)
        plan.append(dict(nid=e["nid"], coins=e["coins"], N=e["N"], L=e["L"], d=int(d), era=era, t_in=int(t_in),
                         exits=[int(x) for x in exits], hi=[syms[i] for i in hi], lo=[syms[i] for i in lo],
                         hi_rank=[int(rk[i, d]) for i in hi], lo_rank=[int(rk[i, d]) for i in lo],
                         hi_share=[float(S[i, d]) for i in hi], nA=int(len(A)), shifts=[int(x) for x in sorted(draws)],
                         ncand=len(cand)))
    json.dump(plan, open(os.path.join(OUT, "plan.json"), "w"), indent=1)
    # windows: (sym, start_ms, end_ms) for real (shift 0) and random shifts
    win = set()
    for p in plan:
        for s in [0] + p["shifts"]:
            t0 = p["t_in"] + s * DAY - 4 * MIN; t1 = p["exits"][2] + s * DAY + 8 * MIN
            assert t1 < CUT
            for sym in p["hi"] + p["lo"] + ["BTCUSDT"]:
                win.add((sym, t0, t1))
    win = sorted(win)
    with open(os.path.join(OUT, "windows.csv"), "w") as f:
        f.write("sym,t0,t1\n")
        for w in win:
            f.write("%s,%d,%d\n" % w)
    n_is = sum(p["era"] == "IS" for p in plan); n_val = len(plan) - n_is
    print("notices IS", n_is, "VAL", n_val, "windows", len(win))
    for p in plan:
        print(p["nid"], p["era"], np.datetime64(p["N"], "ms"), "lagmin", (p["L"] - p["N"]) // MIN, "nA", p["nA"],
              "hi", ",".join(x.replace("USDT", "") for x in p["hi"]), "| lo", ",".join(x.replace("USDT", "") for x in p["lo"]),
              "| ncand", p["ncand"])


if __name__ == "__main__":
    main()
