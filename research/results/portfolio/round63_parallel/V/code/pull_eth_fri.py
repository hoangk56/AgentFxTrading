"""Pull Deribit ETH option trades in Friday windows 07:30-10:00 UTC, 2021-03-05..2024-12-27 (history.deribit.com,
public, no key). Same fields as round 34's BTC pull. One npz per year in research/data/deribit/ETH_fri/.
Run: python -I pull_eth_fri.py (fetch.py is imported by path)."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, fetch

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit/ETH_fri"
CUT = 1735689600000
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}


def exp_ms(s):
    d = int(s[:-5]); m = MON[s[-5:-2]]; y = 2000 + int(s[-2:])
    return int(dt.datetime(y, m, d, 8, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)


def parse(trades, seen):
    rows = []
    for t in trades:
        tid = t["trade_id"]
        if tid in seen:
            continue
        seen.add(tid)
        p = t["instrument_name"].split("-")
        if len(p) != 4:
            continue
        try:
            e = exp_ms(p[1]); k = float(p[2].replace("d", "."))
        except Exception:
            continue
        rows.append((t["timestamp"], e, k, 1 if p[3] == "C" else -1, t["price"], t["amount"],
                     1 if t["direction"] == "buy" else -1, t.get("iv") if t.get("iv") is not None else np.nan,
                     t["index_price"], t.get("mark_price") if t.get("mark_price") is not None else np.nan,
                     1 if "block_trade_id" in t else 0, 1 if "combo_id" in t or "combo_trade_id" in t else 0,
                     1 if "liquidation" in t else 0))
    return rows


def windows(year):
    d = dt.datetime(2021, 3, 5, tzinfo=dt.timezone.utc)
    while d.year <= 2024:
        if d.year == year:
            a = int((d + dt.timedelta(hours=7, minutes=30)).timestamp() * 1000)
            b = int((d + dt.timedelta(hours=10)).timestamp() * 1000)
            yield a, min(b, CUT)
        d += dt.timedelta(days=7)


def main():
    os.makedirs(OUT, exist_ok=True)
    for y in (2021, 2022, 2023, 2024):
        out = f"{OUT}/{y}.npz"
        if os.path.exists(out):
            continue
        rows = []
        for a, b in windows(y):
            seen, s = set(), a
            while True:
                u = (f"https://history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time?currency=ETH"
                     f"&kind=option&start_timestamp={s}&end_timestamp={b - 1}&count=10000&sorting=asc")
                r = json.loads(fetch.get(u, gap=1.1))["result"]
                tr = r["trades"]
                rows += parse(tr, seen)
                if not r["has_more"] or not tr:
                    break
                ns = tr[-1]["timestamp"]
                if ns <= s and len(tr) >= 10000:
                    sys.exit("STUCK")
                s = ns
                seen = {t["trade_id"] for t in tr if t["timestamp"] == ns}
        A = np.array(rows, dtype=float)
        A = A[np.argsort(A[:, 0], kind="stable")]
        np.savez_compressed(out, ts=A[:, 0].astype(np.int64), exp=A[:, 1].astype(np.int64), k=A[:, 2],
                            cp=A[:, 3].astype(np.int8), px=A[:, 4], amt=A[:, 5], dirn=A[:, 6].astype(np.int8),
                            iv=A[:, 7], idx=A[:, 8], mark=A[:, 9], blk=A[:, 10].astype(np.int8),
                            combo=A[:, 11].astype(np.int8), liq=A[:, 12].astype(np.int8))
        print(y, len(A), dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
