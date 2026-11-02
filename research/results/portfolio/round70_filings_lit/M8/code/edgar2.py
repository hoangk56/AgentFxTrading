"""Build the 8-K candidate list (<= 2024-12-31 only) and fetch each primary document (text only, untrusted)."""
import sys, os, json, glob, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
R = os.path.join(net.D, "raw")
SEL = {  # cik: (name, first, last filingDate considered)
    "0001050446": ("MSTR", "2020-01-01", "2024-12-31"),
    "0001554859": ("SMLR", "2024-01-01", "2024-12-31"),
    "0001507605": ("MARA", "2024-01-01", "2024-12-31"),
    "0001662684": ("KULR", "2024-11-01", "2024-12-31"),
    "0001167419": ("RIOT", "2024-11-01", "2024-12-31"),
    "0001512673": ("SQ", "2020-09-01", "2021-03-31"),
    "0001318605": ("TSLA", "2021-01-01", "2021-03-31"),
}


def rows(p):
    d = json.load(open(p))
    r = d.get("filings", {}).get("recent", d)
    return [dict(zip(r.keys(), v)) for v in zip(*r.values())]


def cands():
    out = []
    for cik, (tk, a, b) in SEL.items():
        seen = set()
        for p in glob.glob(os.path.join(R, "subs", f"CIK{cik}*.json")):
            for x in rows(p):
                if x["form"] not in ("8-K", "8-K/A", "10-K") or not (a <= x["filingDate"] <= b):
                    continue
                if x["form"] == "10-K" and tk != "TSLA":
                    continue
                if x["accessionNumber"] in seen:
                    continue
                seen.add(x["accessionNumber"])
                assert x["filingDate"] <= "2024-12-31" and x["acceptanceDateTime"][:4] <= "2024"
                out.append(dict(tk=tk, cik=int(cik), acc=x["accessionNumber"], form=x["form"], fdate=x["filingDate"],
                                acc_dt=x["acceptanceDateTime"], items=x.get("items", ""), doc=x["primaryDocument"]))
    out.sort(key=lambda z: z["acc_dt"])
    return out


if __name__ == "__main__":
    C = cands()
    with open(os.path.join(net.D, "candidates.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(C[0].keys()))
        w.writeheader(); w.writerows(C)
    print(len(C))
    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        for c in C:
            a = c["acc"].replace("-", "")
            p = os.path.join(R, "docs", f"{c['tk']}_{a}_{c['doc']}")
            if not os.path.exists(p):
                net.get(f"https://www.sec.gov/Archives/edgar/data/{c['cik']}/{a}/{c['doc']}", p)
