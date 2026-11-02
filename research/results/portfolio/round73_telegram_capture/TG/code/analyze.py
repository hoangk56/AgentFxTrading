"""Match saved t.me/s posts to Upbit KRW-listing notices and measure lag = post time - N (whole seconds).
Usage: python -I analyze.py [channel ...]   Writes TG/lag_<channel>.csv and prints per-channel stats."""
import os, sys, re, glob, csv, datetime as dt, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import parse, notices, tg
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEG = re.compile(r"delist|종료|유의|warning|caution|suspend|중단|investment alert|투자 ?유의", re.I)
UPB = re.compile(r"upbit|업비트", re.I)


def posts(ch):
    P = {}
    for f in glob.glob(os.path.join(tg.RAW, ch, "b*.html")):
        for p in parse.parse(open(f, "rb").read())[0]:
            if p["time"]:
                P[p["id"]] = p
    return sorted(P.values(), key=lambda p: p["time"])


def has_tick(text, t):
    if len(t) <= 2:
        return re.search(r"(\$%s|\(%s\)|(?<![A-Za-z0-9])%s(?= listed))(?![A-Za-z0-9])" % (t, t, t), text) is not None
    return re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(t), text) is not None


def match(ch, need_upbit):
    ps = posts(ch)
    if not ps:
        return None
    t0, t1 = ps[0]["time"], ps[-1]["time"]
    E = [e for e in notices.load() if t0 <= e["N"] <= t1 - 3600 and e["tickers"]]
    rows = []
    for e in E:
        best = None
        for p in ps:
            if p["time"] < e["N"] - 3600:
                continue
            if p["time"] > e["N"] + 86400:
                break
            tx = p["text"]
            if NEG.search(tx) or (need_upbit and not UPB.search(tx)):
                continue
            # a Korean market-add post that names only BTC / USDT markets is not a KRW listing
            if "마켓" in tx and not ("KRW" in tx or "원화" in tx):
                continue
            if any(has_tick(tx, t) for t in e["tickers"]):
                best = p; break
        rows.append(dict(nid=e["id"], N_utc=dt.datetime.utcfromtimestamp(e["N"]).isoformat(), tickers="/".join(e["tickers"]),
                         post=best["id"] if best else "", lag=int(best["time"] - e["N"]) if best else "",
                         text=(best["text"][:90].replace("\n", " ") if best else ""), title=e["title"][:70]))
    return dict(ch=ch, n_posts=len(ps), t0=t0, t1=t1, rows=rows)


def stats(r, lo=None):
    rows = [x for x in r["rows"] if lo is None or x["N_utc"] >= lo]
    n = len(rows); L = np.array([x["lag"] for x in rows if x["lag"] != ""], float)
    if n == 0:
        return dict(n=0)
    pos = L[L >= 0]
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else float("nan")
    return dict(n=n, matched=len(L), share=len(L) / n, before=int((L < 0).sum()),
                med=q(pos, 50), p80=q(pos, 80), p90=q(pos, 90),
                le2=float((L[(L >= 0)] <= 2).sum() / n), le3=float((L[(L >= 0)] <= 3).sum() / n),
                le2_m=float((pos <= 2).mean()) if len(pos) else float("nan"),
                le3_m=float((pos <= 3).mean()) if len(pos) else float("nan"),
                over60=int((L > 60).sum()))


CH = {"upbit_news": False, "coin_listing": True, "newlistingsfeed": True, "CLWfeed": True, "BWEnews": True,
      "NewListingsFeedPlus": True}

if __name__ == "__main__":
    chs = sys.argv[1:] or [c for c in CH if os.path.isdir(os.path.join(tg.RAW, c))]
    for ch in chs:
        r = match(ch, CH.get(ch, True))
        if not r:
            continue
        with open(os.path.join(OUT, f"lag_{ch}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(r["rows"][0].keys()) if r["rows"] else ["nid"])
            w.writeheader(); w.writerows(r["rows"])
        print(f"== {ch}: {r['n_posts']} posts {dt.datetime.utcfromtimestamp(r['t0']):%Y-%m-%d} .. {dt.datetime.utcfromtimestamp(r['t1']):%Y-%m-%d}")
        for lo in (None, "2025-01-01", "2026-01-01"):
            s = stats(r, lo)
            print("  since", lo or "start", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})
