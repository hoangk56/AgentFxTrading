"""Stream A3: existence probes only (HEAD, no prices). robots.txt of data.binance.vision, then for each screened coin
the spot daily aggTrades file on N - 7 d and on N (Binance spot <COIN>USDT trading >= 7 d before N), and the BTCUSDT
futures/um file on N. Prints status and Content-Length. Usage: python -I probe.py COIN:YYYY-MM-DD ..."""
import sys, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/code")
import net

B = "https://data.binance.vision/data"


def head(url):
    r, s = net.opener(url, method="HEAD")
    n = r.headers.get("Content-Length", "0") if r else 0
    if r:
        net.log(url, s, n, "HEAD"); r.close()
    return s, n


if __name__ == "__main__":
    if sys.argv[1] == "robots":
        r, s = net.opener("https://data.binance.vision/robots.txt")
        body = r.read() if r else b""
        if r:
            net.log(r.url, s, len(body), "GET"); r.close()
        print("robots", s, body[:300]); sys.exit()
    for a in sys.argv[1:]:
        coin, day = a.split(":")
        d = dt.date.fromisoformat(day)
        for dd in (d - dt.timedelta(days=7), d):
            assert dd < dt.date(2025, 1, 1)
            sym = coin + "USDT"
            print(coin, dd, "spot", *head(f"{B}/spot/daily/aggTrades/{sym}/{sym}-aggTrades-{dd}.zip"), flush=True)
