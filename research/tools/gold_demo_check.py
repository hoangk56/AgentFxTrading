"""Scores cBot/GoldLevelBot.cs's demo trade log against the registered DEMO terms of the gold rule
(research/results/portfolio/round27_levels_opens/PREREG_G_gold_round50_cascade.md, "DEMO terms if it passes").

Stop rule, any one of:
- after 60 demo trades, the cumulative demo net is < 0;
- after 120 demo trades, it is below the expected sum minus 1.5 sd, with VAL's per-trade mean and sd
  (prereg_code/summary_VAL_reg.txt: mean, and sd = mean / per-trade Sharpe);
- at any time after 30 trades, the median entry slippage against the 250 ms tick model is worse than 1 x s60.
Promotion to LIVE, all of: HOLD + demo pooled, day-clustered net t >= 2.5; at least 100 demo trades; pooled net > 0 at
spread x1.5.

A demo trade is a logged trigger that filled. Its net is the real fills' (fill_net_bp: entry and exit as filled, minus
the research's 0.6 bp commission); the model net of the same trigger (model_net_bp) is shown next to it. Missed
triggers are counted, never scored. Spread x1.5 adds half of each side's half spread at the model quotes.

    scp agentFx:/home/forge/ctrader/ctrader_data/<BotId>_trades.csv /tmp/gold.csv
    research/.venv/bin/python -m research.tools.gold_demo_check /tmp/gold.csv

The pooled numbers read the holdout's trades, prereg_code/trades_HOLD.csv: a local research output that .gitignore
keeps out of git (research/results/**/*trades*.csv), so run this from the research checkout that has it.
"""
import argparse
import csv
import math
import re
from pathlib import Path

PREREG = Path("research/results/portfolio/round27_levels_opens/prereg_code")


def val_mean_sd(path=PREREG / "summary_VAL_reg.txt"):
    txt = Path(path).read_text()
    mean = float(re.search(r"\[VAL\] net 250 ms: n \d+ mean ([+-][\d.]+)", txt).group(1))
    sharpe = float(re.search(r"per-trade net Sharpe ([+-][\d.]+)", txt).group(1))
    return mean, mean / sharpe


def hold_trades(path=PREREG / "trades_HOLD.csv"):
    """[(utc_day, net_250, net_250_x1.5)] of the registered HOLD run."""
    with open(path, newline="") as f:
        return [(r["trigger_utc"][:10], float(r["net_250"]), float(r["net_250_x1.5"])) for r in csv.DictReader(f)]


def _num(s):
    return float(s) if s not in ("", None) else None


def demo_trades(path):
    """(filled, missed): filled = [dict] with day, net, net15, model_net, slip_s60; missed = [note]."""
    filled, missed = [], []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["missed"] == "1" or not r["fill_price"] or not r["close_price"]:
                missed.append(r["note"])
                continue
            net = _num(r["fill_net_bp"])
            mid_in, mid_out = _num(r["model_entry_mid"]), _num(r["model_exit_mid"])
            px_in, px_out = _num(r["model_entry"]), _num(r["model_exit"])
            extra = 0.0
            if None not in (mid_in, mid_out, px_in, px_out):
                extra = 0.5 * (abs(px_in - mid_in) + abs(px_out - mid_out)) / mid_in * 1e4
            filled.append({"day": r["trigger_utc"][:10], "net": net, "net15": net - extra,
                           "model_net": _num(r["model_net_bp"]), "slip_s60": _num(r["entry_slip_s60"])})
    return filled, missed


def clustered_t(x, groups):
    """t of the mean with standard errors clustered by group (gcommon.clustered_t)."""
    n = len(x)
    if n < 3:
        return float("nan")
    m = sum(x) / n
    sums = {}
    for v, g in zip(x, groups):
        sums[g] = sums.get(g, 0.0) + (v - m)
    G = len(sums)
    if G < 2:
        return float("nan")
    se = math.sqrt(sum(s * s for s in sums.values()) * G / (G - 1)) / n
    return m / se if se > 0 else float("nan")


def median(x):
    s = sorted(x)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def check(filled, missed, hold, val_mean, val_sd):
    n = len(filled)
    cum = sum(t["net"] for t in filled)
    slips = [t["slip_s60"] for t in filled if t["slip_s60"] is not None]
    out = {"n": n, "missed": len(missed), "cum": cum, "mean": cum / n if n else float("nan"),
           "t": clustered_t([t["net"] for t in filled], [t["day"] for t in filled])}
    out["stop_60"] = n >= 60 and cum < 0
    out["floor_120"] = n * val_mean - 1.5 * val_sd * math.sqrt(n)
    out["stop_120"] = n >= 120 and cum < out["floor_120"]
    out["median_slip_s60"] = median(slips) if slips else float("nan")
    out["stop_slip"] = len(slips) >= 30 and out["median_slip_s60"] > 1.0
    out["stop"] = out["stop_60"] or out["stop_120"] or out["stop_slip"]
    pooled = [h[1] for h in hold] + [t["net"] for t in filled]
    days = [h[0] for h in hold] + [t["day"] for t in filled]
    out["pooled_t"] = clustered_t(pooled, days)
    out["pooled15"] = (sum(h[2] for h in hold) + sum(t["net15"] for t in filled)) / len(pooled)
    out["promote"] = out["pooled_t"] >= 2.5 and n >= 100 and out["pooled15"] > 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", help="the bot's trade log (<BotId>_trades.csv)")
    a = ap.parse_args()
    filled, missed = demo_trades(a.trades)
    vm, vsd = val_mean_sd()
    r = check(filled, missed, hold_trades(), vm, vsd)
    model = [t["model_net"] for t in filled if t["model_net"] is not None]
    print(f"demo trades {r['n']} (missed triggers {r['missed']}): net {r['mean']:+.2f} bp per trade (t {r['t']:+.2f}), "
          f"sum {r['cum']:+.1f} bp; the model on the same triggers {sum(model) / len(model) if model else float('nan'):+.2f}")
    print(f"stop rule: 60 trades & sum < 0: {r['stop_60']}; 120 trades & sum < {r['floor_120']:+.1f} "
          f"(VAL mean {vm:+.2f}, sd {vsd:.1f}): {r['stop_120']}; median entry slippage {r['median_slip_s60']:+.2f} x s60 "
          f"> 1 after 30: {r['stop_slip']}  =>  {'STOP' if r['stop'] else 'continue'}")
    print(f"promotion: HOLD + demo pooled t {r['pooled_t']:+.2f} (needs 2.5), demo trades {r['n']} (needs 100), "
          f"pooled net at spread x1.5 {r['pooled15']:+.2f} (needs > 0)  =>  {'PROMOTE' if r['promote'] else 'not yet'}")
    for note in sorted(set(missed)):
        print(f"  missed ({missed.count(note)}): {note}")


if __name__ == "__main__":
    main()
