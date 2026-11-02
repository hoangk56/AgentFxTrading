"""Page back through t.me/s/<channel> with ?before=<min id>, saving each page (untrusted) under raw/<channel>/.
Stops at channel start, at max_pages, or on 403/429 (tg.Stop). Resumable: skips pages already saved.
Usage: python -I pageback.py <channel> <max_pages> [<channel> <max_pages> ...]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tg, parse


def run(ch, maxp):
    d = os.path.join(tg.RAW, ch); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, "btop.html")
    b = open(fn, "rb").read() if os.path.exists(fn) else tg.get(f"https://t.me/s/{ch}")[0]
    if not os.path.exists(fn):
        open(fn, "wb").write(b)
    n = 0; last = None
    while n < maxp:
        ps, _ = parse.parse(b)
        if not ps:
            print(ch, "empty page, stop"); break
        mn = min(p["id"] for p in ps)
        if mn <= 1 or mn == last:
            print(ch, "reached start", mn); break
        last = mn
        fn = os.path.join(d, f"b{mn}.html")
        if os.path.exists(fn):
            b = open(fn, "rb").read()
        else:
            b, c, _ = tg.get(f"https://t.me/s/{ch}?before={mn}")
            if c != 200 or not b:
                print(ch, "status", c, "stop"); break
            open(fn, "wb").write(b)
        n += 1
        if n % 50 == 0:
            print(ch, n, mn, time.strftime("%H:%M:%S"), flush=True)
    print(ch, "done pages", n, "last before", last, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        for i in range(0, len(a), 2):
            run(a[i], int(a[i + 1]))
    except tg.Stop as e:
        print("STOP", e, flush=True)
