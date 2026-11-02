"""Stream O2: stated listing start S per event (no prices; declared in HYPOTHESES_O2.md).
OKX: from the article body, every 'H:MM [am|pm] ... <Month> <day>[, <year>]' time in a sentence that mentions UTC and
     trading / listed / live / open / enabled, and not deposit / withdraw / settlement / funding / delist; the sentence
     naming the coin is preferred. S = the earliest such time in (N, N + 24 h].
Bybit: a time in the title ('on Nov 19, 2024, 7:00AM UTC'); bodies are not reachable.
No S in (N, N + 24 h] -> exit at N + 60 min. Each time is judged by its own clause (see okx_start). Output O2/events_s.csv (events.csv + S, exit X, xsrc)."""
import csv, html, os, re, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bodies

OUTD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
H, DAY = 3600000, 86400000
MON = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
TIME = re.compile(r"(\d{1,2})\s*:\s*(\d\d)\s*(a\s?\.?\s?m\.?|p\s?\.?\s?m\.?)?", re.I)
DATE = re.compile(r"(?:on\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\.?\s*(\d{1,2})(?:st|nd|rd|th)?(?:\s*,?\s*(20\d\d))?", re.I)
DATE_DMY = re.compile(r"(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?(?:\s*,?\s*(20\d\d))?", re.I)
GOOD = re.compile(r"trading|listed|live|open|enabled|launch|start|available", re.I)
BAD = re.compile(r"deposit|withdraw|settlement|funding|delist|interest|end\b|ends\b|close", re.I)


def text(url):
    s = open(bodies.path(url), encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>", " ", s, flags=re.S); t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(re.sub(r"\s+", " ", t)).replace("\xa0", " ")
    i = t.find("min read")
    j = t.find("Disclaimer", i)
    return t[i: j if j > i else i + 6000][:6000]


def times(seg, N):
    out = []
    for m in TIME.finditer(seg):
        h, mi, ap = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower().replace(" ", "").replace(".", "")
        if ap == "pm" and h < 12:
            h += 12
        if ap == "am" and h == 12:
            h = 0
        if h > 23:
            continue
        near = seg[m.end(): m.end() + 45]
        d = DATE.search(near) or None
        if d:
            mo, day, yr = MON[d.group(1).lower()[:3]], int(d.group(2)), d.group(3)
        else:
            d = DATE_DMY.search(near) or DATE.search(seg[max(0, m.start() - 40): m.start()])
            if not d:
                continue
            if d.re is DATE_DMY:
                day, mo, yr = int(d.group(1)), MON[d.group(2).lower()[:3]], d.group(3)
            else:
                mo, day, yr = MON[d.group(1).lower()[:3]], int(d.group(2)), d.group(3)
        y0 = int(yr) if yr else dt.datetime.fromtimestamp(N / 1000, dt.timezone.utc).year
        for y in ([y0] if yr else [y0, y0 + 1]):
            try:
                t = int(dt.datetime(y, mo, day, h, mi, tzinfo=dt.timezone.utc).timestamp() * 1000)
            except ValueError:
                continue
            if t > N - DAY:
                out.append(t); break
    return out


def okx_start(e):
    """Each time in the body is judged by its own clause: the text since the previous time (<= 160 chars) must say
    trading / listed / live / open / enabled and not deposit / withdraw / ...; 'UTC' within 60 chars after the time."""
    N = int(e["N"]); t = text(e["url"])
    ms = list(TIME.finditer(t))
    cand, cand_coin = [], []
    for k, m in enumerate(ms):
        a = max(ms[k - 1].end() if k else 0, m.start() - 160)
        ctx = t[a: m.start()]
        if "UTC" not in t[m.end(): m.end() + 60] or not GOOD.search(ctx) or BAD.search(ctx):
            continue
        ts = [x for x in times(t[m.start(): m.end() + 60], N) if N < x <= N + DAY]
        if not ts:
            continue
        cand.append(ts[0])
        if re.search(r"\b" + re.escape(e["coin"]) + r"\b", ctx):
            cand_coin.append(ts[0])
    c = cand_coin or cand
    return (min(c), "body") if c else (None, "none")


def bybit_start(e):
    N = int(e["N"])
    m = re.search(r"on\s+([A-Z][a-z]{2})[a-z]*\.?\s+(\d{1,2}),\s*(20\d\d),?\s*(\d{1,2}):(\d\d)\s*(AM|PM)\s*UTC", e["title"])
    if not m:
        return None, "none"
    h = int(m.group(4)) % 12 + (12 if m.group(6) == "PM" else 0)
    t = int(dt.datetime(int(m.group(3)), MON[m.group(1).lower()], int(m.group(2)), h, int(m.group(5)), tzinfo=dt.timezone.utc).timestamp() * 1000)
    return (t, "title") if N < t <= N + DAY else (None, "none")


if __name__ == "__main__":
    ev = list(csv.DictReader(open(os.path.join(OUTD, "events.csv"))))
    for e in ev:
        S, src = okx_start(e) if e["venue"] == "OKX" else bybit_start(e)
        e["S"] = S or ""; e["X"] = S if S else int(e["N"]) + H; e["xsrc"] = src if S else "N+60m"
        e["S_utc"] = dt.datetime.fromtimestamp(S / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M") if S else ""
    cols = list(ev[0].keys())
    with open(os.path.join(OUTD, "events_s.csv"), "w") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); [w.writerow(e) for e in ev]
    for e in ev:
        print(e["venue"][:3], e["coin"], e["N_utc"], "S", e["S_utc"] or "--", e["xsrc"], f"{(int(e['X']) - int(e['N'])) / 60000:.0f}m")
