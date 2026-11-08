"""Stream WA: probe pages of t.me/s/whale_alert_io to find the post-id boundaries of eras (2019, 2020, 2022, 2025).
Uses the shared round-74 fetcher (one lock, >= 1.5 s gap). Pages saved as raw/whale_alert_io/b<before>.html.
Prints only id ranges and whether the page is before / after each boundary (no post text, no 2025+ content).
Usage: python -I probe.py top | python -I probe.py <before_id> [<before_id> ...]"""
import os, sys, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import tg, parse

CH = "whale_alert_io"
D = os.path.join(tg.RAW, CH)
os.makedirs(D, exist_ok=True)
H25 = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()


def page(bef):
    fn = os.path.join(D, f"b{bef}.html")
    if os.path.exists(fn):
        return open(fn, "rb").read()
    url = f"https://t.me/s/{CH}" + ("" if bef == "top" else f"?before={bef}")
    b, c, _ = tg.get(url)
    if c != 200 or not b:
        raise SystemExit(f"status {c}")
    open(fn, "wb").write(b)
    return b


def show(bef):
    ps, _ = parse.parse(page(bef))
    ps = [p for p in ps if p["time"]]
    if not ps:
        print(bef, "empty"); return
    lo, hi = min(ps, key=lambda p: p["id"]), max(ps, key=lambda p: p["id"])
    if hi["time"] >= H25:  # HOLD: report only the id range and that it is >= 2025
        print(bef, "ids", lo["id"], hi["id"], "n", len(ps), ">=2025" if lo["time"] >= H25 else "straddles 2025")
    else:
        f = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
        print(bef, "ids", lo["id"], hi["id"], "n", len(ps), f(lo["time"]), "..", f(hi["time"]))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(a)
