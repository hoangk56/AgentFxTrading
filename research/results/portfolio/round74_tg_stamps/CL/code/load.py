"""Stream CL: load saved t.me/s/<channel> pages (untrusted data; run with python -I) into posts.
posts(channel) -> list of dicts (id, time UTC epoch s, text, edited), deduplicated by id, cut at time < 2025-01-01
right after parsing. hold_titles(channel) returns the 2025-01-01..2026-10-29 posts' texts for COUNTING ONLY
(no times beyond the era label are kept, nothing is printed)."""
import glob, os, sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import parse

RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist/raw"
# round 73 cache of the same t.me pages (read-only); round 74 pages override it per post id
RAW73 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_upbit/raw"
CUT = 1735689600       # 2025-01-01 00:00:00 UTC (seconds)
HOLD_END = 1761782400  # 2026-10-30 00:00:00 UTC
_cache = {}


def _all(ch):
    if ch not in _cache:
        by = {}
        fs = sorted(glob.glob(os.path.join(RAW73, ch, "b*.html"))) + sorted(glob.glob(os.path.join(RAW, ch, "b*.html")))
        for f in fs:
            ps, _ = parse.parse(open(f, "rb").read())
            for p in ps:
                if p["time"] is not None:
                    by[p["id"]] = p
        _cache[ch] = [by[k] for k in sorted(by)]
    return _cache[ch]


def posts(ch):
    return [p for p in _all(ch) if p["time"] < CUT]


def hold_titles(ch):
    return [(p["text"], p["edited"]) for p in _all(ch) if CUT <= p["time"] < HOLD_END]


if __name__ == "__main__":
    ch = sys.argv[1]
    P = posts(ch)
    print(ch, "pre-2025 posts", len(P), "ids", P[0]["id"] if P else None, P[-1]["id"] if P else None)
