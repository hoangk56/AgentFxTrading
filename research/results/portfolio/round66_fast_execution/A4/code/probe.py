"""Stream A4: public.bybit.com/trading/<SYM>/ directory listings (file names only, no prices) for every KRW coin in
the screen without a Binance perp >= 7 d old, to check point-in-time Bybit trading (instruments launchTime is the
latest launch, so a closed-and-relaunched contract could hide an earlier life). Also BTCUSDT for the file name
pattern. Listing saved under research/data/upbit_bybit_notice/listing/ (untrusted, parsed as text with -I)."""
import os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
from events import build, DAY

OUT = os.path.join(net.D, "listing"); os.makedirs(OUT, exist_ok=True)


def days(sym):
    fn = os.path.join(OUT, sym + ".html")
    if not os.path.exists(fn):
        s, b = net.get(f"https://public.bybit.com/trading/{sym}/")
        open(fn, "wb").write(b if s == 200 else b"")
    txt = open(fn, "rb").read().decode("utf8", "replace")
    return sorted(set(re.findall(re.escape(sym) + r"(\d{4}-\d\d-\d\d)\.csv\.gz", txt)))


if __name__ == "__main__":
    rows, log = build()
    for nid, coin, n_utc, why in log:
        if why.startswith("has Binance"):
            continue
        N = dt.datetime.strptime(n_utc, "%Y-%m-%d %H:%M:%S")
        ds = days(coin + "USDT")
        pre = [d for d in ds if d <= (N - dt.timedelta(days=7)).strftime("%Y-%m-%d")]
        on = (N.strftime("%Y-%m-%d") in ds)
        print(nid, coin, n_utc, "|", why[:40], "| dump first", ds[0] if ds else None, "| files <= N-7d:", len(pre),
              "| file on N:", on, flush=True)
    print("BTCUSDT first", days("BTCUSDT")[:1])
