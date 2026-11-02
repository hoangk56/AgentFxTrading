"""Stream R2: windows that share (symbol, start) with another window but end later were saved only once by fetch.py
(file name keyed by start). Re-fetch those whose saved file ends too early, as <sym>_<t0>x<t1>.json. Same politeness
and logging as fetch.py (single thread here, >= 0.3 s)."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch  # noqa: E402

OUT = fetch.OUT; MIN = fetch.MIN


def main():
    have = set(os.listdir(fetch.NPZ))
    todo = []
    for line in open(os.path.join(OUT, "windows.csv")).readlines()[1:]:
        s, a, b = line.strip().split(","); a = int(a); b = int(b)
        if all((s + "_" + m + ".npz") in have for m in {fetch.mon(a), fetch.mon(b)}):
            continue
        fn = os.path.join(fetch.RAW, "%s_%d.json" % (s, a))
        rows = json.load(open(fn))
        if rows and int(rows[-1][0]) >= b - 2 * MIN:
            continue
        todo.append((s, a, b))
    print("todo", len(todo), flush=True)
    for s, a, b in todo:
        fn = os.path.join(fetch.RAW, "%s_%dx%d.json" % (s, a, b))
        if os.path.exists(fn):
            continue
        assert b < fetch.CUT
        url = ("https://fapi.binance.com/fapi/v1/klines?symbol=%s&interval=1m&startTime=%d&endTime=%d&limit=%d"
               % (s, a, b, min(1500, (b - a) // MIN + 1)))
        time.sleep(0.3)
        st, body = fetch.get(url)
        if st == 200:
            open(fn, "wb").write(body)
        else:
            print("status", st, s, body[:200], flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
