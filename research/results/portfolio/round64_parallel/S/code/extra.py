"""Kiểm thêm cho ô k=100, H=7 (chọn trên IS) + chiều ngược (chỉ thông tin). Chạy: python -I extra.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import peg  # noqa: E402

Y2020 = 1577836800000
CRASH = (1583020800000, 1588291200000)  # 2020-03-01 .. 2020-05-01
SVB = (1678406400000, 1679011200000)  # 2023-03-10 .. 2023-03-17


def show(name, trs):
    for fill in ("close", "taker"):
        s = peg.stats(trs, fill=fill)
        if s["n"] == 0:
            print(f"  {name} [{fill}]: n 0")
            continue
        print(f"  {name} [{fill}]: n {s['n']}, episodes {s['G']} (pos {s['ep_pos']}), excess {s['mean'] * 1e4:+.1f} bp, "
              f"t_ep {s['t']:+.2f}, Sh/ep {s['sh_ep']:+.2f}")


def main():
    data = peg.load_pairs()
    k, H = 100, 7
    trs = []
    for p, d in data.items():
        for tr in peg.simulate(p, d, k, H):
            tr["qv_e"] = float(d["qv"][tr["e"]])
            trs.append(tr)
    IS = [x for x in trs if peg.era_of(x) == "IS"]
    VAL = [x for x in trs if peg.era_of(x) == "VAL"]
    print("== k=100 H=7 subsets")
    show("IS all", IS)
    show("IS 2020-21 only (standard crypto IS)", [x for x in IS if x["te"] >= Y2020])
    show("IS 2018-19 only", [x for x in IS if x["te"] < Y2020])
    show("IS without USDS / USDSB", [x for x in IS if not x["sym"].startswith("USDS")])
    show("IS USDC + BUSD only (deep pairs)", [x for x in IS if x["sym"] in ("USDCUSDT", "BUSDUSDT")])
    show("IS without 2020-03..04", [x for x in IS if not (CRASH[0] <= x["te"] < CRASH[1])])
    show("VAL all", VAL)
    show("VAL without SVB week", [x for x in VAL if not (SVB[0] <= x["te"] < SVB[1])])
    show("VAL TUSD only", [x for x in VAL if x["sym"] == "TUSDUSDT"])
    for era, tt in (("IS", IS), ("VAL", VAL)):
        q = np.array([x["qv_e"] for x in tt])
        print(f"  {era} entry-bar quote volume (USDT): median {np.median(q):.0f}, p25 {np.percentile(q, 25):.0f}, "
              f"p75 {np.percentile(q, 75):.0f}")
        # P&L theo năm cho 1 đơn vị vốn mỗi cặp (tổng bp lệnh / số năm)
        yrs = 4.07 if era == "IS" else 3.0
        r = np.array([peg.net(x, fill="taker") for x in tt])
        print(f"  {era} taker-fill excess per year per unit of notional: {r.sum() / yrs * 1e4:+.0f} bp/yr "
              f"(days in a trade {sum(x['hold'] for x in tt):.0f} over {yrs * 365:.0f})")
        # đồng thời: số lệnh mở cùng lúc tối đa
        ev = sorted([(x["te"], 1) for x in tt] + [(x["tx"], -1) for x in tt])
        cur = mx = 0
        for _, dlt in ev:
            cur += dlt
            mx = max(mx, cur)
        print(f"  {era} max concurrent positions {mx}")
    print("\n== VAL trades k=100 H=7 (taker-fill excess bp)")
    for x in VAL:
        print(f"  {x['sym']} {peg.ymd(x['te'])} -> {peg.ymd(x['tx'])} d_sig {x['d_sig'] * 1e4:.0f} "
              f"{peg.net(x, fill='taker') * 1e4:+.1f} {x['how']}")
    print("\n== IS episode list (taker-fill excess bp per episode)")
    lab = peg.episodes(IS)
    r = np.array([peg.net(x, fill="taker") for x in IS])
    for g in range(lab.max() + 1):
        idx = np.flatnonzero(lab == g)
        print(f"  {peg.ymd(min(IS[i]['te'] for i in idx))[:10]} "
              f"{'/'.join(sorted(set(IS[i]['sym'][:-4] for i in idx)))} n {len(idx)} {r[idx].sum() * 1e4:+.0f}")

    print("\n== mirror (information only): long USDT vs X when X rich by k (price of USDT in X = 1 / close)")
    for kk in peg.KS:
        for HH in peg.HS:
            out = []
            for p, d in data.items():
                inv = dict(d)
                inv["c"] = 1.0 / d["c"]
                inv["h"] = 1.0 / d["l"]
                inv["l"] = 1.0 / d["h"]
                inv["tbb"] = np.zeros_like(d["tbb"])  # không dùng taker fill
                out.extend(peg.simulate(p, inv, kk, HH))
            for era in ("IS", "VAL"):
                tt = [x for x in out if peg.era_of(x) == era]
                # nến lỗi (BUSDUSDT 2019-09 có giá 0.0005 / 306): bỏ lệnh |gross| > 20 %
                bad = [x for x in tt if abs(x["px"] / x["pe"] - 1) > 0.2]
                tt = [x for x in tt if abs(x["px"] / x["pe"] - 1) <= 0.2]
                s = peg.stats(tt)
                if s["n"]:
                    print(f"  k {kk} H {HH} {era}: n {s['n']} (bad prints dropped {len(bad)}), episodes {s['G']} "
                          f"(pos {s['ep_pos']}), excess {s['mean'] * 1e4:+.1f} bp, t_ep {s['t']:+.2f}")


if __name__ == "__main__":
    main()


def mirror_detail():
    """Chiều ngược k=100, H=7 với giá taker: bán X (giá taker bán của X) rồi mua lại X (giá taker mua)."""
    data = peg.load_pairs()
    print("\n== mirror k=100 H=7 detail (information only, needs X inventory)")
    out = []
    for p, d in data.items():
        inv = dict(d)
        inv["c"] = 1.0 / d["c"]
        inv["h"] = 1.0 / d["l"]
        inv["l"] = 1.0 / d["h"]
        for tr in peg.simulate(p, inv, 100, 7):
            if abs(tr["px"] / tr["pe"] - 1) > 0.2:
                continue
            sell = peg.taker_px(d, tr["e"], "sell")
            buy = peg.taker_px(d, tr["x"], "buy")
            tr["pe_tk"], tr["px_tk"] = 1.0 / sell, 1.0 / buy
            out.append(tr)
    for era in ("IS", "VAL"):
        tt = [x for x in out if peg.era_of(x) == era]
        for fill in ("close", "taker"):
            s = peg.stats(tt, fill=fill)
            x15 = peg.stats(tt, fill=fill, mult=1.5)
            print(f"  {era} [{fill}]: n {s['n']}, episodes {s['G']} (pos {s['ep_pos']}), excess {s['mean'] * 1e4:+.1f} bp, "
                  f"t_ep {s['t']:+.2f}, Sh/ep {s['sh_ep']:+.2f}, x1.5 {x15['mean'] * 1e4:+.1f}")
        yrs = {}
        for x in tt:
            yrs.setdefault(peg.year_of(x), []).append(peg.net(x, fill="taker"))
        print("     taker years: " + ", ".join(f"{y} {np.mean(v) * 1e4:+.1f} (n {len(v)})" for y, v in sorted(yrs.items())))
        byp = {}
        for x in tt:
            byp.setdefault(x["sym"], []).append(peg.net(x, fill="taker"))
        print("     taker pairs: " + ", ".join(f"{p} {np.mean(v) * 1e4:+.1f} (n {len(v)})" for p, v in sorted(byp.items())))
        if era == "VAL":
            s = peg.stats(tt, fill="taker")
            print(f"     power at VAL size by episode: {s['sh_ep'] * np.sqrt(s['G'] / 3 * 1.83):+.2f}")


if __name__ == "__main__":
    mirror_detail()
