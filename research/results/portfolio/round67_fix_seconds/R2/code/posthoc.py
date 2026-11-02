"""Stream R2 post hoc (information only, not part of the declared test): random-mean spread, splits by lead time and
by VAL half, path of the VAL BTC cell to L in fractions of the lead, C3 daily-P&L correlation. Run with python -I."""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402

C3 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv"


def main():
    plan = json.load(open(os.path.join(R.DATA, "plan.json")))
    z = np.load(R.PANEL, allow_pickle=False)
    psyms = list(z["syms"]); FR = z["FR"]
    FRc = np.concatenate([np.zeros((FR.shape[0], 1)), np.cumsum(FR, axis=1)], axis=1)
    sidx = {s: i for i, s in enumerate(psyms)}
    PX = R.load_prices(plan)
    out = []
    pr = lambda *a: out.append(" ".join(str(x) for x in a))
    era = np.array([p["era"] for p in plan]); day = np.array([p["d"] for p in plan])
    lead = np.array([(p["L"] - p["t_in"]) / R.MIN for p in plan])
    net = lambda r: r["gross"] + r["fund"] - r["cost"]
    for cell in ("BTC-L", "BTC-L1H", "LOW-L"):
        h, x = cell.split("-"); j = R.EXITS.index(x)
        real = np.array([net(R.price_trade(PX, FRc, sidx, p, 0, j, h)) for p in plan])
        rg = np.array([[R.price_trade(PX, FRc, sidx, p, s, j, h)["gross"] for s in p["shifts"]] for p in plan])
        gr = np.array([R.price_trade(PX, FRc, sidx, p, 0, j, h)["gross"] for p in plan])
        for e in ("IS", "VAL"):
            k = era == e
            rng = np.random.default_rng(5)
            pick = rng.integers(0, rg.shape[1], size=(20000, k.sum()))
            rm = rg[k][np.arange(k.sum())[None, :], pick].mean(1)
            pr(f"{cell} {e}: real gross {1e4*gr[k].mean():+.1f}; random means (20000 books) mean {1e4*rm.mean():+.1f} "
               f"sd {1e4*rm.std():.1f} p99 {1e4*np.percentile(rm, 99):+.1f} max {1e4*rm.max():+.1f}; z {(gr[k].mean()-rm.mean())/rm.std():.1f}")
        for name, m in (("IS lead >= 30 min", (era == "IS") & (lead >= 30)), ("IS lead < 30 min", (era == "IS") & (lead < 30)),
                        ("VAL lead < 120 min", (era == "VAL") & (lead < 120)), ("VAL lead >= 120 min", (era == "VAL") & (lead >= 120)),
                        ("VAL 2022-23", (era == "VAL") & (np.array([p["N"] for p in plan]) < 1704067200000)),
                        ("VAL 2024", (np.array([p["N"] for p in plan]) >= 1704067200000))):
            v = real[m]
            pr(f"   {cell} {name}: n {m.sum()} net {1e4*v.mean():+.1f} t {R.cl_t(v, day[m]):+.2f}")
    # BTC-L path: fraction of lead elapsed (VAL)
    pr("\nBTC hedge VAL gross path at fractions of the lead entry -> L (mean bp):")
    fr = [0.25, 0.5, 0.75, 1.0]
    rows = []
    for p in plan:
        if p["era"] != "VAL":
            continue
        rr = []
        for f in fr:
            X = int(p["t_in"] + f * (p["L"] - p["t_in"])) // R.MIN * R.MIN
            q = {**p, "exits": [X] * 3}
            rr.append(R.price_trade(PX, FRc, sidx, q, 0, 0, "BTC")["gross"])
        rows.append(rr)
    pr(" | ".join(f"{f:.2f}: {1e4*v:+.0f}" for f, v in zip(fr, np.mean(rows, 0))))
    # C3 daily correlation (P&L booked on exit day)
    c3 = {}
    for r in csv.DictReader(open(C3)):
        d = int(np.datetime64(r["t_out_utc"][:10], "D").astype(np.int64))
        if d * R.DAY < R.CUT:
            c3[d] = c3.get(d, 0.0) + float(r["usd_at_100_risk"])
    for cell in ("BTC-L", "BTC-L1H"):
        h, x = cell.split("-"); j = R.EXITS.index(x)
        k = {}
        for p in plan:
            dd = p["exits"][j] // R.DAY
            k[dd] = k.get(dd, 0.0) + net(R.price_trade(PX, FRc, sidx, p, 0, j, h))
        for e, (lo, hi) in (("IS", (1577836800000, 1640995200000)), ("VAL", (1640995200000, R.CUT))):
            days = np.arange(lo // R.DAY, hi // R.DAY)
            a = np.array([c3.get(int(d), 0.0) for d in days]); b = np.array([k.get(int(d), 0.0) for d in days])
            both = ((a != 0) & (b != 0)).sum()
            pr(f"C3 corr {cell} {e}: days {len(days)} active {(b != 0).sum()} overlap {both} corr {np.corrcoef(a, b)[0, 1]:+.3f}")
    txt = "\n".join(out)
    open(os.path.join(R.OUTD, "r2_posthoc.txt"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
