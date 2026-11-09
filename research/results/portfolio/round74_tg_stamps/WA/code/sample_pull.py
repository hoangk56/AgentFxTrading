"""Stream WA: pull the declared page sample of t.me/s/whale_alert_io (HYPOTHESES_WA.md, sampling plan).
IS: before = 56860 - 80 j (> 6960); VAL: before = 85500 - 40 j (> 56870). Resumable (skips saved pages).
Shared fetcher: one lock, >= 1.5 s gap; stops on 403/429/418/503 (tg.Stop). Prints progress only (no content).
Usage: python -I sample_pull.py"""
import os, sys, time
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import tg

CH = "whale_alert_io"
D = os.path.join(tg.RAW, CH)
os.makedirs(D, exist_ok=True)


def plan():
    v = list(range(85500, 56870, -40))
    i = list(range(56860, 6960, -80))
    # interleave so a stopped pull still has both eras
    out = []
    for k in range(max(len(v), len(i))):
        if k < len(v): out.append(v[k])
        if k < len(i): out.append(i[k])
    return out


def main():
    p = plan(); n = 0; t0 = time.time()
    print("planned", len(p), flush=True)
    for k, b in enumerate(p):
        fn = os.path.join(D, f"b{b}.html")
        if os.path.exists(fn):
            continue
        body, c, _ = tg.get(f"https://t.me/s/{CH}?before={b}")
        if c != 200 or not body:
            print("status", c, "at", b, "skip", flush=True); continue
        open(fn, "wb").write(body); n += 1
        if n % 50 == 0:
            print(k + 1, "/", len(p), "new", n, f"{time.time()-t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    print("done new", n, flush=True)


if __name__ == "__main__":
    try:
        main()
    except tg.Stop as e:
        print("STOP", e, flush=True)
