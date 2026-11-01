"""Build the market universe table from raw gamma pages (python -I; data only).
Output: research/data/polymarket/markets.json (list of dicts). Prints counts only (no outcomes)."""
import json, glob, os, sys, datetime as dt, collections
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/raw_gamma"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/markets.json"
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)

SPORTS = {"sports", "nba", "nfl", "mlb", "nhl", "soccer", "football", "basketball", "tennis", "ufc", "mma", "boxing",
          "golf", "f1", "formula 1", "cricket", "epl", "premier league", "champions league", "ncaa", "olympics",
          "esports", "baseball", "hockey", "chess", "nascar", "cfb", "cbb", "la liga", "serie a", "bundesliga",
          "euro 2024", "copa america", "wnba", "super bowl"}
CRYPTO = {"crypto", "bitcoin", "ethereum", "solana", "crypto prices", "btc", "eth", "airdrops", "nft", "defi",
          "memecoins", "stablecoins"}
POLITICS = {"politics", "elections", "us election", "2024 election", "geopolitics", "world elections",
            "global elections", "trump", "biden", "congress", "us politics", "uk politics", "middle east", "ukraine",
            "israel", "courts", "supreme court", "world", "global politics", "presidential election", "senate",
            "house", "primaries"}

def ts(s):
    if not s:
        return None
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"):
        s += ":00"
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t

def category(tags, slug, question):
    labs = {(t.get("label") or "").strip().lower() for t in (tags or [])}
    if labs & SPORTS:
        return "sports"
    if labs & CRYPTO:
        return "crypto"
    if labs & POLITICS:
        return "politics"
    if labs - {"all", ""}:
        return "other"
    return "untagged"

def main():
    seen = {}
    for fn in sorted(glob.glob(RAW + "/m_*.json")):
        for m in json.load(open(fn)):
            seen[m["id"]] = m
    rows = []
    for m in seen.values():
        try:
            outs = json.loads(m.get("outcomes") or "[]")
            final = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            toks = json.loads(m.get("clobTokenIds") or "[]")
        except Exception:
            continue
        end, closed = ts(m.get("endDate")), ts(m.get("closedTime"))
        if end is None or closed is None or closed >= CUT or end >= CUT:
            continue
        ev = (m.get("events") or [{}])[0]
        rows.append(dict(id=m["id"], cond=m.get("conditionId"), event=str(ev.get("id") or m["id"]),
                         event_title=ev.get("title"), question=m.get("question"), slug=m.get("slug"),
                         end=end.timestamp(), closed=closed.timestamp(), created=(ts(m.get("createdAt")) or end).timestamp(),
                         vol=float(m.get("volumeNum") or 0), vol_clob=float(m.get("volumeClob") or 0),
                         ob=bool(m.get("enableOrderBook")), neg_risk=bool(m.get("negRisk") or ev.get("enableNegRisk")),
                         outcomes=outs, final=final, tokens=toks, fees_enabled=bool(m.get("feesEnabled")),
                         uma=m.get("umaResolutionStatus"), cat=category(m.get("tags"), m.get("slug"), m.get("question"))))
    json.dump(rows, open(OUT, "w"))
    c = collections.Counter()
    for r in rows:
        yr = dt.datetime.fromtimestamp(r["closed"], dt.timezone.utc).year
        ok = r["ob"] and len(r["tokens"]) == 2 and r["vol"] >= 10000
        c[(yr, "all")] += 1
        if ok:
            c[(yr, "ob2_vol10k")] += 1
            c[(yr, r["cat"])] += 1
    ev = collections.defaultdict(set)
    for r in rows:
        if r["ob"] and len(r["tokens"]) == 2 and r["vol"] >= 10000:
            ev[dt.datetime.fromtimestamp(r["closed"], dt.timezone.utc).year].add(r["event"])
    for k in sorted(c):
        print(k, c[k])
    print({y: len(s) for y, s in ev.items()}, "events (filtered)")
    print("feesEnabled count", sum(r["fees_enabled"] for r in rows))

if __name__ == "__main__":
    main()
