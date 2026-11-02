"""Bảng kết quả stream S (chỉ IS / VAL). Chạy: research/.venv/bin/python -I run.py"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import peg  # noqa: E402

HOLD_YEARS = 1.83
VAL_YEARS = 3.0


def fmt(x, nd=1):
    return "nan" if x != x else f"{x:+.{nd}f}"


def line(name, s):
    if s["n"] == 0:
        return f"{name}: n 0"
    return (f"{name}: n {s['n']}, episodes {s['G']} (pos {s['ep_pos']}), mean {s['mean'] * 1e4:+.1f} bp, "
            f"t_ep {fmt(s['t'], 2)}, Sh/ep {fmt(s['sh_ep'], 2)}, Sh/tr {fmt(s['sh_tr'], 2)}")


def main():
    data, cells = peg.main()
    out = []
    P = out.append
    P("# coverage (1m bars, < 2025-01-01)")
    for p, d in data.items():
        t = d["t"]
        isn = int((t < peg.VAL0).sum())
        P(f"{p}: {peg.ymd(int(t[0]))} .. {peg.ymd(int(t[-1]))}, bars {len(t)}, IS {isn}, VAL {len(t) - isn}, "
          f"median quote vol/min {np.median(d['qv']):.0f} USDT, zero-trade bars {np.mean(d['n'] == 0) * 100:.1f} %")
        disc = 1 - d["c"]
        for era, m in (("IS", t < peg.VAL0), ("VAL", t >= peg.VAL0)):
            if m.sum() == 0:
                continue
            P(f"   {era}: minutes with d>=10bp {np.mean(disc[m] >= 1e-3) * 100:.2f} %, >=30 {np.mean(disc[m] >= 3e-3) * 100:.3f} %, "
              f">=100 {np.mean(disc[m] >= 1e-2) * 100:.4f} %, rich<=-30 {np.mean(disc[m] <= -3e-3) * 100:.3f} %, "
              f"min close {d['c'][m].min():.4f}, max {d['c'][m].max():.4f}")
    rng = np.random.default_rng(64)
    best = {}
    rnd_store = {}
    rows = []
    for k in peg.KS:
        for H in peg.HS:
            trs = cells[(k, H, 0)]
            late = cells[(k, H, 1)]
            P(f"\n# cell k={k} bp, H={H} d  (net = after standard 10 bp taker + half-spread, minus DFF cash)")
            for era in ("IS", "VAL"):
                e_tr = [x for x in trs if peg.era_of(x) == era]
                e_late = [x for x in late if peg.era_of(x) == era]
                s = peg.stats(e_tr)
                P(line(f"  {era} excess", s))
                if s["n"] == 0:
                    continue
                g = peg.stats(e_tr, mult=0.0, excess=False)
                nc = peg.stats(e_tr, excess=False)
                x15 = peg.stats(e_tr, mult=1.5)
                lt = peg.stats(e_late)
                zf = peg.stats(e_tr, zero_fee=True)
                P(f"     gross {g['mean'] * 1e4:+.1f} bp (t {fmt(g['t'], 2)}); net before cash {nc['mean'] * 1e4:+.1f}; "
                  f"x1.5 {x15['mean'] * 1e4:+.1f} (t {fmt(x15['t'], 2)}); late {lt['mean'] * 1e4:+.1f} "
                  f"(t {fmt(lt['t'], 2)}, n {lt['n']}); zero-fee from 2023-07 {zf['mean'] * 1e4:+.1f} (t {fmt(zf['t'], 2)})")
                tk = peg.stats(e_tr, fill="taker")
                tk15 = peg.stats(e_tr, fill="taker", mult=1.5)
                tkl = peg.stats(e_late, fill="taker")
                tkz = peg.stats(e_tr, fill="taker", zero_fee=True)
                wf = peg.stats(e_tr, fill="worst")
                P(f"     TAKER-VWAP fill (excess): {tk['mean'] * 1e4:+.1f} bp (t {fmt(tk['t'], 2)}, ep pos {tk['ep_pos']}/{tk['G']}, "
                  f"Sh/ep {fmt(tk['sh_ep'], 2)}); x1.5 {tk15['mean'] * 1e4:+.1f} (t {fmt(tk15['t'], 2)}); late "
                  f"{tkl['mean'] * 1e4:+.1f} (t {fmt(tkl['t'], 2)}); zero-fee {tkz['mean'] * 1e4:+.1f} (t {fmt(tkz['t'], 2)}); "
                  f"worst-fill {wf['mean'] * 1e4:+.1f} (t {fmt(wf['t'], 2)})")
                tyrs = {}
                for x in e_tr:
                    tyrs.setdefault(peg.year_of(x), []).append(peg.net(x, fill="taker"))
                P("     taker-fill years: " + ", ".join(f"{y} {np.mean(v) * 1e4:+.1f}" for y, v in sorted(tyrs.items())))
                hows = {}
                for x in e_tr:
                    hows[x["how"]] = hows.get(x["how"], 0) + 1
                hold = np.array([x["hold"] for x in e_tr])
                P(f"     exits {hows}; median hold {np.median(hold) * 24:.1f} h; pairs "
                  f"{sorted(set(x['sym'] for x in e_tr))}")
                yrs = {}
                for x in e_tr:
                    yrs.setdefault(peg.year_of(x), []).append(peg.net(x))
                P("     years: " + ", ".join(f"{y} {np.mean(v) * 1e4:+.1f} (n {len(v)})" for y, v in sorted(yrs.items())))
                byp = {}
                for x in e_tr:
                    byp.setdefault(x["sym"], []).append(peg.net(x))
                P("     pairs: " + ", ".join(f"{p} {np.mean(v) * 1e4:+.1f} (n {len(v)})" for p, v in sorted(byp.items())))
                ru = peg.random_bench(data, e_tr, rng=rng)
                rd = peg.random_bench(data, e_tr, mode="disc", k=k, rng=rng)
                P(f"     random uniform: rule beats {np.mean(ru < s['mean']) * 100:.1f} % (rand mean {ru.mean() * 1e4:+.1f}); "
                  f"same-discount: beats {np.mean(rd < s['mean']) * 100:.1f} % (rand mean {rd.mean() * 1e4:+.1f})")
                rnd_store[(k, H, era)] = (s["mean"], ru)
                if era == "VAL":
                    E = s["G"]
                    pw_ep = s["sh_ep"] * np.sqrt(E / VAL_YEARS * HOLD_YEARS) if E > 1 else float("nan")
                    pw_tr = s["sh_tr"] * np.sqrt(s["n"] / VAL_YEARS * HOLD_YEARS)
                    pw_tk = tk["sh_ep"] * np.sqrt(E / VAL_YEARS * HOLD_YEARS) if E > 1 else float("nan")
                    P(f"     power at VAL size: by episode {fmt(pw_ep, 2)} (HOLD ~{E / VAL_YEARS * HOLD_YEARS:.1f} episodes), "
                      f"by trade {fmt(pw_tr, 2)}; taker fill by episode {fmt(pw_tk, 2)}")
                best[(k, H, era)] = s
                for x in e_tr:
                    rows.append([k, H, era, x["sym"], peg.ymd(x["te"]), peg.ymd(x["tx"]), f"{x['pe']:.5f}",
                                 f"{x['px']:.5f}", f"{x['d_sig'] * 1e4:.1f}", f"{x['hold']:.3f}", x["how"],
                                 f"{peg.net(x, excess=False) * 1e4:.2f}", f"{peg.net(x) * 1e4:.2f}",
                                 f"{peg.net(x, fill='taker') * 1e4:.2f}"])
            # đợt lớn nhất
            if trs:
                lab = peg.episodes(trs)
                r = np.array([peg.net(x) for x in trs])
                ep = np.bincount(lab, weights=r)
                order = np.argsort(-np.abs(ep))[:8]
                P("     largest episodes (|sum|): " + "; ".join(
                    f"{peg.ymd(min(trs[i]['te'] for i in np.flatnonzero(lab == g)))[:10]} "
                    f"{'/'.join(sorted(set(trs[i]['sym'][:-4] for i in np.flatnonzero(lab == g))))} "
                    f"n{(lab == g).sum()} {ep[g] * 1e4:+.0f}bp" for g in order))
    # max-over-cells null theo kỷ
    for era in ("IS", "VAL"):
        keys = [kk for kk in rnd_store if kk[2] == era]
        if not keys:
            continue
        dev = np.max([rnd_store[kk][1] - rnd_store[kk][1].mean() for kk in keys], axis=0)
        bestk = max(keys, key=lambda kk: rnd_store[kk][0] - rnd_store[kk][1].mean())
        bd = rnd_store[bestk][0] - rnd_store[bestk][1].mean()
        P(f"\n# max-over-cells null {era}: best cell {bestk[:2]} excess over its random mean {bd * 1e4:+.1f} bp; "
          f"beats {np.mean(dev < bd) * 100:.1f} % of max-over-{len(keys)}-cells random draws")
    text = "\n".join(out)
    print(text)
    os.makedirs(peg.OUT, exist_ok=True)
    with open(os.path.join(peg.OUT, "summary.txt"), "w") as f:
        f.write(text + "\n")
    head = ["k_bp", "H_d", "era", "pair", "entry_utc", "exit_utc", "p_entry", "p_exit", "d_sig_bp", "hold_d", "exit",
            "net_bp", "excess_bp", "excess_taker_fill_bp"]
    # đủ mọi ô: để ở thư mục data (lớn, git-ignore); ô k=100 (nhỏ) để cạnh báo cáo
    for path, rr in ((os.path.join(peg.ROOT, "data/binance_stables/trades_all_cells.csv"), rows),
                     (os.path.join(peg.OUT, "trades_k100.csv"), [r for r in rows if r[0] == 100])):
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rr)


if __name__ == "__main__":
    main()
