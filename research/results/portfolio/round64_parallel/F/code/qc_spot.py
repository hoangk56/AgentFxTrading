"""Stream F QC (not part of the rule): for a random sample of <= 300 guarded T3 events (de-duplicated), fetch the spot
pair's 1m klines for minutes e-1..e from data.binance.vision spot daily 1m files (api.binance.com robots.txt is
"Disallow: /", so the REST API is not used) and report the share whose spot close-to-
close return in minute e has the same sign and >= half the perp move. Run with python -I. Events are all < 2025.
Logs to research/data/binance_1m_wicks/requests.log; responses saved raw under spot_qc/ (untrusted, parsed as JSON).
"""
import io, json, os, sys, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks")
OUT = os.path.join(HERE, "..", "out")
T0 = 1577836800000; MIN = 60000; VAL0 = (1640995200000 - T0) // MIN
sys.path.insert(0, HERE)
from report import dedup  # noqa


def spot_name(perp):
    for pre, fac in (("1000000", 1e6), ("1000", 1e3), ("1M", 1e6)):
        if perp.startswith(pre) and not perp[len(pre):][0].isdigit():
            return perp[len(pre):]
    return perp


def log(url, status, nb):
    with open(os.path.join(D, "requests.log"), "a") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{status},{nb}\n")


def main():
    z = np.load(os.path.join(OUT, "cand.npz"))
    syms = list(z["syms"]); sym, t, r = z["sym"], z["t"].astype(np.int64), z["r"]
    idx = np.where(np.abs(r) >= 0.03)[0]
    idx = idx[dedup(sym[idx], t[idx])]
    rng = np.random.default_rng(7)
    samp = rng.choice(idx, size=min(300, len(idx)), replace=False)
    os.makedirs(os.path.join(D, "spot_qc"), exist_ok=True)
    res = []
    for j in samp:
        s = spot_name(syms[sym[j]])
        st = T0 + (t[j] - 1) * MIN
        assert st + 3 * MIN <= 1735689600000
        dd = dt.datetime.fromtimestamp(st / 1000, dt.timezone.utc).strftime("%Y-%m-%d")
        dd2 = dt.datetime.fromtimestamp((st + MIN) / 1000, dt.timezone.utc).strftime("%Y-%m-%d")
        if dd != dd2:
            res.append((int(j), "gap", np.nan)); continue
        url = f"https://data.binance.vision/data/spot/daily/klines/{s}/1m/{s}-1m-{dd}.zip"
        time.sleep(0.3)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60) as resp:
                b = resp.read()
            log(url, 200, len(b))
            with zipfile.ZipFile(io.BytesIO(b)) as zf:
                txt = zf.read(zf.namelist()[0]).decode("ascii", "replace")
            kk = {}
            for ln in txt.splitlines():
                p_ = ln.split(",")
                if p_ and p_[0].isdigit():
                    o_ = int(p_[0])
                    if o_ > 10 ** 14:  # microsecond stamps in newer spot files
                        o_ //= 1000
                    if o_ in (st, st + MIN):
                        kk[o_] = float(p_[4])
            k = [[st, 0, 0, 0, kk[st]], [st + MIN, 0, 0, 0, kk[st + MIN]]] if len(kk) == 2 else []
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code in (403, 418, 429):
                print("stop", e.code); break
            res.append((int(j), "nospot", np.nan)); continue
        if len(k) < 2:
            res.append((int(j), "gap", np.nan)); continue
        rs = float(k[1][4]) / float(k[0][4]) - 1
        ok = np.sign(rs) == np.sign(r[j]) and abs(rs) >= 0.5 * abs(r[j])
        res.append((int(j), "ok" if ok else "fail", rs))
    st = [x[1] for x in res]
    eras = ["IS" if t[x[0]] < VAL0 else "VAL" for x in res]
    lines = [f"sampled {len(res)}: " + ", ".join(f"{k} {st.count(k)}" for k in ("ok", "fail", "nospot", "gap"))]
    for e in ("IS", "VAL"):
        ss = [s for s, ee in zip(st, eras) if ee == e]
        lines.append(f"{e}: " + ", ".join(f"{k} {ss.count(k)}" for k in ("ok", "fail", "nospot", "gap")))
    fails = [x for x in res if x[1] == "fail"]
    for x in fails[:20]:
        lines.append(f"fail {syms[sym[x[0]]]} {dt.datetime.fromtimestamp((T0 + t[x[0]] * MIN) / 1000, dt.timezone.utc):%Y-%m-%d %H:%M} perp {r[x[0]]*1e4:+.0f} bp spot {x[2]*1e4:+.0f} bp")
    json.dump(res, open(os.path.join(OUT, "qc_spot.json"), "w"))
    open(os.path.join(OUT, "qc_spot.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
