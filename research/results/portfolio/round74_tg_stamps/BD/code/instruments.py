"""Stream BD: map each event coin to a short instrument (declared order: Binance USDT-M <C>USDT, 1000<C>USDT,
then Bybit linear <C>USDT), and the Binance spot pair for the information-only spot path (<C>USDT, <C>BTC).
Pulls per-second arrays for the notice day and the next day (24 h exit), BTC for the hedge sensitivity comes from 1m klines (analyze.py), not ticks.
Writes BD/trades_in.csv. Run: python -I instruments.py"""
import csv, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pull

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/BD"
CUT = 1735689600


def days(N):
    d = dt.datetime.fromtimestamp(N, dt.timezone.utc).date()
    return [str(d), str(d + dt.timedelta(days=1))]


def main(only_cls=("S", "F", "MT")):
    E = list(csv.DictReader(open(os.path.join(OUT, "events_binance_announcements.csv"))))
    rows = []
    for e in E:
        if e["cls"] not in only_cls or not e["coins"]:
            continue
        N = int(e["time"]); assert N < CUT
        d0, d1 = days(N)
        for c in e["coins"].split():
            inst = None
            if N >= 1567296000:  # Binance USDT-M from 2019-09
                for s in (f"{c}USDT", f"1000{c}USDT"):
                    if pull.exists("bu", s, d0):
                        inst = ("bu", s); break
            if inst is None and e["cls"] != "F" and N >= 1577836800 and pull.exists("by", f"{c}USDT", d0):
                inst = ("by", f"{c}USDT")
            spot = None
            if e["cls"] == "S":
                for s in (f"{c}USDT", f"{c}BTC"):
                    if pull.exists("bs", s, d0):
                        spot = s; break
            rows.append(dict(id=e["id"], time=N, utc=e["utc"], edited=e["edited"], cls=e["cls"], coin=c,
                             venue=inst[0] if inst else "", sym=inst[1] if inst else "", spot=spot or "", d0=d0, d1=d1))
            print(e["utc"], e["cls"], c, inst, spot, flush=True)
    with open(os.path.join(OUT, "trades_in.csv"), "w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # pull arrays (d1 only if it is <= 2024-12-31)
    jobs = set()
    for r in rows:
        dd = [d for d in (r["d0"], r["d1"]) if d <= "2024-12-31"]
        for d in dd:
            if r["venue"]:
                jobs.add((r["venue"], r["sym"], d))
            if r["spot"]:
                jobs.add(("bs", r["spot"], d))
    for k, j in enumerate(sorted(jobs, key=lambda x: (x[2], x[0], x[1]))):
        ok = pull.build(*j)
        print(f"{k+1}/{len(jobs)}", j, ok, flush=True)


if __name__ == "__main__":
    main()
