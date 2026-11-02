"""Event list for stream M8 (from EDGAR text review, before any price was read).
FRESH: an 8-K whose text discloses a completed BTC purchase announced on the filing date (no earlier-date announcement).
STALE: the 8-K reports a purchase already announced on an earlier date (descriptive only, not in the cells).
Times: submissions JSON acceptanceDateTime, true UTC (checked against 5 -index.htm 'Accepted' fields, which are ET)."""
import csv, os
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
FRESH_OTHER = {  # non-MSTR purchase 8-Ks (purchase in the 8-K or its Exhibit 99.1 press release)
    "0001554859-24-000020": "SMLR first 581 BTC, PR ex99.1",
    "0001104659-24-092635": "SMLR 83 BTC, PR ex99.1",
    "0001104659-24-119975": "SMLR 215 BTC, PR ex99.1",
    "0001104659-24-122367": "SMLR 297 BTC, PR ex99.1",
    "0001104659-24-125775": "SMLR 303 BTC, PR ex99.1",
    "0001104659-24-128691": "SMLR 211 BTC, PR ex99.1",
    "0001493152-24-048222": "MARA 6,484 BTC Oct-Nov, 7.01",
    "0001558370-24-016217": "RIOT 5,117 BTC, 8.01",
    "0001558370-24-016266": "RIOT 667 BTC, 7.01/8.01",
    "0001104659-24-131548": "KULR first 217 BTC, PR ex99.1",
}
STALE = {
    "0001193125-20-245835": "MSTR 16,796 BTC completed 2020-09-14, 8-K next morning",
    "0001193125-24-255184": "MSTR 27,200 BTC announced 2024-11-11 (EDGAR holiday), 8-K 11-12",
    "0001104659-24-069125": "SMLR 247 BTC 'as of June 6 we announced', 8-K 16:54 ET",
}
MSTR_NOT = set()  # MSTR 'Y' parses that are not purchases: none after review


def build():
    P = list(csv.DictReader(open(os.path.join(D, "filings_parsed.csv"))))
    ev = []
    for c in P:
        cls = None
        if c["acc"] in STALE:
            cls, note = "STALE", STALE[c["acc"]]
        elif c["tk"] == "MSTR" and c["buy"] == "Y" and c["acc"] not in MSTR_NOT and "2.02" not in c["items"]:
            cls, note = "FRESH", f"MSTR {c['btc_qty']} BTC"
        elif c["acc"] in FRESH_OTHER:
            cls, note = "FRESH", FRESH_OTHER[c["acc"]]
        if c["tk"] == "TSLA" and c["form"] == "10-K":
            cls, note = "TSLA10K", "Tesla 10-K disclosing $1.5 bn BTC purchase"
        if cls is None:
            continue
        import datetime as dt
        t = dt.datetime.strptime(c["acc_dt"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
        assert t.year <= 2024
        ev.append(dict(tk=c["tk"], acc=c["acc"], cls=cls, acc_utc=c["acc_dt"][:19], T_ms=int(t.timestamp() * 1000),
                       items=c["items"], note=note))
    ev.sort(key=lambda e: e["T_ms"])
    return ev


if __name__ == "__main__":
    ev = build()
    with open(os.path.join(D, "events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ev[0].keys())); w.writeheader(); w.writerows(ev)
    import collections
    print(collections.Counter((e["acc_utc"][:4], e["cls"]) for e in ev))
    for e in ev:
        print(e["acc_utc"], e["tk"], e["cls"], e["note"])
