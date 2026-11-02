"""Stream A2 events: stream A's notice_events_L.csv (read-only). L fallbacks as stream A: MATIC = SOL's L (same notice),
STG / BONK = stated start + 5 min; SRM dropped (L unknown). Every N < 2025-01-01."""
import csv
A = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A/notice_events_L.csv"
END = 1735689600000


def load_events():
    R = list(csv.DictReader(open(A)))
    byn = {}
    for r in R:
        if r["L1m"]:
            byn.setdefault(r["nid"], []).append(int(r["L1m"]))
    out = []
    for r in R:
        if r["coin"] == "SRM":
            continue
        if r["L1m"]:
            L, how = int(r["L1m"]), "candle"
        elif r["coin"] == "MATIC":
            L, how = byn[r["nid"]][0], "SOL's L"
        else:
            L, how = int(r["stated"]) + 300000, "stated+5m"
        N = int(r["N"])
        assert N < END
        out.append(dict(nid=r["nid"], coin=r["coin"], perp=r["perp"], N=N, L=L, Lhow=how,
                        era="IS" if N < 1640995200000 else "VAL", year=r["N_utc"][:4], day=r["N_utc"][:10]))
    return out
