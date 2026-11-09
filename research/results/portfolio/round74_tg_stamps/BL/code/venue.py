"""L1: pick the pre-open venue for each spot-listing coin (HYPOTHESES section 2): Binance USDT-M perp, else Bybit USDT
perp, else OKX USDT swap, each needing history >= 24 h before N (checked as: a daily file exists for UTC day(N) - 2,
which implies >= 24 h). No prices are read: local perp_1d first-row dates, the Bybit directory listing, OKX HEADs.
Writes research/data/binance_tg_listing/l1_venue.json."""
import json, os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
D = net.D
PERP1D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance/perp_1d"
CUT = 1735689600


def day(t, k=0):
    return (dt.datetime.fromtimestamp(t, dt.timezone.utc) + dt.timedelta(days=k)).strftime("%Y-%m-%d")


def cands(coin):
    return [coin + "USDT", "1000" + coin + "USDT", "1000000" + coin + "USDT", "10000" + coin + "USDT",
            "1M" + coin + "USDT"]


def binance_perp_first():
    out = {}
    for f in os.listdir(PERP1D):
        if f.endswith(".csv"):
            with open(os.path.join(PERP1D, f)) as fh:
                fh.readline(); rows = [l for l in fh if l.strip()]
            if rows:  # (first day, set of days with a 1d row): the perp must trade on day(N) (ticker reuse, e.g. LUNA)
                out[f[:-4]] = (int(rows[0].split(",")[0]) // 1000, {day(int(r.split(",")[0]) // 1000) for r in rows})
    return out


_bydir = {}


def bybit_days(sym):
    if sym not in _bydir:
        fn = os.path.join(D, "bybit_dirs", sym + ".json")
        if os.path.exists(fn):
            _bydir[sym] = json.load(open(fn))
        else:
            b, s = net.get_small(f"https://public.bybit.com/trading/{sym}/")
            ds = sorted(set(re.findall(rf"{sym}(\d{{4}}-\d{{2}}-\d{{2}})\.csv\.gz", (b or b"").decode("utf-8", "replace"))))
            ds = [x for x in ds if x < "2025-01-01"]
            os.makedirs(os.path.dirname(fn), exist_ok=True); json.dump(ds, open(fn, "w")); _bydir[sym] = ds
    return _bydir[sym]


def okx_has(coin, d):
    sym = f"{coin}-USDT-SWAP"
    u = f"https://static.okx.com/cdn/okex/traderecords/trades/daily/{d.replace('-', '')}/{sym}-trades-{d}.zip"
    r, s = net.opener(u, method="HEAD"); net.log(u, s, 0, "HEAD")
    return s == 200, sym


def main():
    ev = json.load(open(os.path.join(D, "l1_titles.json")))
    bp = binance_perp_first()
    bys = set(json.load(open(os.path.join(D, "bybit_trading_syms.json"))))
    out = []
    for e in ev:
        assert e["t"] < CUT
        d2 = day(e["t"], -2); v = None
        for s in cands(e["coin"]):
            if s in bp and day(bp[s][0]) <= d2 and day(e["t"]) in bp[s][1]:
                v = dict(src="bum", sym=s, first=day(bp[s][0])); break
        if v is None:
            for s in cands(e["coin"]):
                if s in bys:
                    ds = bybit_days(s)
                    if ds and ds[0] <= d2 and day(e["t"]) in ds:
                        v = dict(src="bybit", sym=s, first=ds[0]); break
        if v is None and day(e["t"]) >= "2021-09-01":
            ok, s = okx_has(e["coin"], d2)
            if ok:
                v = dict(src="okx", sym=s, first="<= " + d2)
        out.append(dict(e, venue=v))
        print(day(e["t"]), e["coin"], v, flush=True)
    json.dump(out, open(os.path.join(D, "l1_venue.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
