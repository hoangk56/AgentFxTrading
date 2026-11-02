"""Stream UC: build pull_list.csv in the declared priority order (HYPOTHESES_UC.md). Uses events_kept.csv (titles,
categories, perp; no prices). Category labels are taken from the current events_kept.csv (re-run after the body
re-labelling: the set of rows pulled does not change, because every title-rule DWSUSP row is pulled in step 1).
Columns: order, nid, coin, perp, cat, side, N, N_utc, testable."""
import csv, os, random
UC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round68_upbit_census/UC"
END = 1735689600000
IS_END = 1640995200000
TITLE_DWS = os.path.join(UC, "title_dwsusp_keys.txt")

rows = [r for r in csv.DictReader(open(os.path.join(UC, "events_kept.csv"))) if int(r["N"]) + 3665000 < END]
key = lambda r: f"{r['nid']}|{r['perp']}"
if not os.path.exists(TITLE_DWS):  # frozen on the first run (title rules only)
    open(TITLE_DWS, "w").write("\n".join(key(r) for r in rows if r["cat"] == "DWSUSP"))
tds = set(open(TITLE_DWS).read().split())
rng = random.Random(68)
step1 = [r for r in rows if key(r) in tds]; rng.shuffle(step1)
rest = [r for r in rows if key(r) not in tds]
step2 = [r for r in rest if r["cat"] in ("WARN", "AIRDROP")]
net = [r for r in rest if r["cat"] == "NETUP"]
ni = [r for r in net if int(r["N"]) < IS_END]; nv = [r for r in net if int(r["N"]) >= IS_END]
rng2 = random.Random(68)
step3 = rng2.sample(ni, min(25, len(ni))) + rng2.sample(nv, min(25, len(nv)))
step4 = [r for r in rest if r["cat"] in ("RESUME", "SWAP", "SUPPLY", "OTHER", "EVENT")]
# rows exposed by the re-labelling (dedup changes) in pulled categories: appended (step 5)
step5 = [r for r in rest if r["cat"] in ("DWSUSP", "DWWALLET")]
# testable = side + >= 20 IS and >= 20 VAL kept events in the final labels
cnt = {}
for r in rows:
    cnt.setdefault(r["cat"], [0, 0])[int(r["N"]) >= IS_END] += 1
testable = {c for c, (a, b) in cnt.items() if a >= 20 and b >= 20 and any(r["side"] for r in rows if r["cat"] == c)}
order = step1 + step2 + step3 + step4 + step5
with open(os.path.join(UC, "pull_list.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["order", "step", "nid", "coin", "perp", "cat", "side", "N", "N_utc", "testable"])
    for i, r in enumerate(order):
        st = 1 if r in step1 else 2 if r in step2 else 3 if r in step3 else 4 if r in step4 else 5
        w.writerow([i, st, r["nid"], r["coin"], r["perp"], r["cat"], r["side"], r["N"], r["N_utc"], int(r["cat"] in testable)])
print("rows", len(order), "step sizes", len(step1), len(step2), len(step3), len(step4), len(step5), "testable", sorted(testable), cnt)
