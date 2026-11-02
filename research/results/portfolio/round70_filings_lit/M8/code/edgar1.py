"""Robots + company tickers + submissions JSON (recent + older pages) for candidate CIKs."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
R = os.path.join(net.D, "raw"); os.makedirs(R, exist_ok=True)
step = sys.argv[1]
if step == "robots":
    for u in ["https://www.sec.gov/robots.txt", "https://data.sec.gov/robots.txt", "https://data.binance.vision/robots.txt"]:
        b = net.get(u, os.path.join(R, "robots_" + u.split("/")[2] + ".txt"))
        print(u, None if b is None else len(b))
    net.get("https://www.sec.gov/files/company_tickers.json", os.path.join(R, "company_tickers.json"))
elif step == "subs":
    for cik in sys.argv[2:]:
        c = f"{int(cik):010d}"
        p = os.path.join(R, "subs", f"CIK{c}.json")
        if not os.path.exists(p):
            net.get(f"https://data.sec.gov/submissions/CIK{c}.json", p)
elif step == "older":
    for name in sys.argv[2:]:
        p = os.path.join(R, "subs", name)
        if not os.path.exists(p):
            net.get(f"https://data.sec.gov/submissions/{name}", p)
