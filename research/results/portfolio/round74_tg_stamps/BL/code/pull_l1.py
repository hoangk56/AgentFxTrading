"""L1: (1) spot open O = first Binance spot aggTrade of the coin on or after day(N) - 1 over its main pairs (S3 listing of
data.binance.vision daily aggTrades, then the first day's file); (2) venue trade files for day(N) (and day(N)+1 when the
N + 65 min window crosses midnight) and for O's day(s) when O <= N + 48 h. Writes l1_events.json. Run with python -I.
Nothing on or after 2025-01-01 is requested."""
import json, os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net, pull
D = net.D
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
SPOT = set(json.load(open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_announcements/spot_symbols.json")))
QUOTES = ("USDT", "BTC", "BUSD", "BNB", "ETH", "FDUSD", "USDC", "TUSD", "PAX")
H48 = 172800000


def day(ms, k=0):
    return (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc) + dt.timedelta(days=k)).strftime("%Y-%m-%d")


def first_day_on_or_after(pair, d_min):
    fn = os.path.join(D, "s3_first", f"{pair}_{d_min}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    marker = ""; found = None
    for _ in range(10):
        url = f"{S3}?delimiter=/&prefix=data/spot/daily/aggTrades/{pair}/" + (f"&marker={marker}" if marker else "")
        b, s = net.get_small(url)
        if b is None:
            break
        txt = b.decode("utf-8", "replace")
        ks = re.findall(r"<Key>([^<]+\.zip)</Key>", txt)
        ds = [re.search(r"(\d{4}-\d{2}-\d{2})\.zip$", k).group(1) for k in ks]
        ok = [x for x in ds if x >= d_min]
        if ok:
            found = min(ok); break
        if "<IsTruncated>true</IsTruncated>" not in txt or not ks:
            break
        marker = re.findall(r"<Key>([^<]+)</Key>", txt)[-1]
    os.makedirs(os.path.dirname(fn), exist_ok=True); json.dump(found, open(fn, "w"))
    return found


def spot_open(coin, N):
    d_min = day(N, -1); best = None
    for q in QUOTES:
        pair = coin + q
        if pair not in SPOT:
            continue
        fd = first_day_on_or_after(pair, d_min)
        if fd is None or fd >= "2025-01-01" or fd > day(N, 3):
            continue
        z = np.load(pull.get("bspot", pair, fd, []))
        if int(z["missing"]) or int(z["n_all"]) == 0:
            continue
        n = z["n"]; k = int(np.argmax(n > 0)); t0 = int(z["d0"]) + k * 1000
        if best is None or t0 < best[0]:
            best = (t0, pair)
    return best


def main():
    V = json.load(open(os.path.join(D, "l1_venue.json")))
    out = []
    for e in V:
        N = e["t"] * 1000
        era = "IS" if N < 1640995200000 else "VAL"
        if e["venue"] is None:
            continue
        so = spot_open(e["coin"], N)
        X = so[0] if so else None
        src, sym = e["venue"]["src"], e["venue"]["sym"]
        win = [(N - 3900000, N + 3900000)]
        days = {day(N - 3900000), day(N), day(N + 3900000)}
        if X and N + 300000 < X <= N + H48:
            win.append((X - 120000, X + 120000)); days |= {day(X - 120000), day(X + 120000)}
        if src == "okx":  # OKX file date = UTC+8 date
            days = {day(N - 3900000 + 28800000), day(N + 28800000), day(N + 3900000 + 28800000)}
            if X and N + 300000 < X <= N + H48:
                days |= {day(X - 120000 + 28800000), day(X + 120000 + 28800000)}
        days = sorted(d for d in days if d < "2025-01-01")
        for d in days:
            pull.get(src, sym, d, win)
        out.append(dict(id=e["id"], N=N, coin=e["coin"], edited=e["edited"], src=src, sym=sym, X=X,
                        spot_pair=so[1] if so else None, era=era, year=int(day(N)[:4]), day=day(N), days=days,
                        title=e["title"]))
        print(day(N), e["coin"], src, sym, "O-N min", None if X is None else round((X - N) / 60000, 1), flush=True)
    json.dump(out, open(os.path.join(D, "l1_events.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
