"""Price every stream H event with k2rule.trade (unchanged) and the declared siblings. Writes ../h_trades.csv.
Usage: python -I run_h.py"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import k2rule
from k2rule import H, M
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

ev = [x for x in csv.DictReader(open(os.path.join(OUT, "h_events.csv"))) if not x["drop"]]
done = set()
fp = os.path.join(OUT, "h_trades.csv")
if os.path.exists(fp):
    done = {x["coin"] for x in csv.DictReader(open(fp))}
keys = ["coin", "sym", "L", "cls", "te", "price", "fund", "net", "net_x15", "net_late5", "net_late2h", "net_h24", "runup"]
f = open(fp, "a", newline=""); w = csv.DictWriter(f, keys)
if not done:
    w.writeheader()
for e in ev:
    if e["coin"] in done:
        continue
    sym, L = e["sym"], int(e["L"])
    b = k2rule.trade(sym, L)
    if b is None:
        print("NOFILL", e["coin"], e["Lutc"], flush=True)
        w.writerow(dict(coin=e["coin"], sym=sym, L=L, cls=e["cls"])); f.flush(); continue
    te, price, fund, net = b
    l5 = k2rule.trade(sym, L, off=H + 5 * M)
    l2 = k2rule.trade(sym, L, off=2 * H)
    h24 = k2rule.trade(sym, L, hold=24 * H)
    a0, a1 = k2rule.px(sym, L - 24 * H), k2rule.px(sym, te)
    b0, b1 = k2rule.px("BTCUSDT", L - 24 * H), k2rule.px("BTCUSDT", te)
    run = (a1 / a0 - 1) - (b1 / b0 - 1)
    w.writerow(dict(coin=e["coin"], sym=sym, L=L, cls=e["cls"], te=te, price=price, fund=fund, net=net,
                    net_x15=price + fund - 1.5 * k2rule.COST, net_late5=l5[3] if l5 else "", net_late2h=l2[3] if l2 else "",
                    net_h24=h24[3] if h24 else "", runup=run))
    f.flush()
    print(e["coin"], e["Lutc"], e["cls"], "done", flush=True)
