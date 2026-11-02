"""Parse SAFE RMBQuery.do HTML pages (untrusted data) into data/cny_fix/usdcny_fix.csv (date, fix CNY per USD).

Run with python -I. Rows on or after 2025-01-01 are dropped (HOLD guard), though none were requested.
"""
import re
from pathlib import Path

DATA = Path("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/cny_fix")
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)


def clean(c: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).replace("&nbsp;", "").strip()


def parse(path: Path) -> dict[str, float]:
    t = path.read_bytes().decode("utf-8", "replace")
    out, usd_col = {}, None
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        cells = [clean(c) for c in CELL.findall(r)]
        if not cells:
            continue
        if usd_col is None and any(c.endswith("美元") for c in cells):
            usd_col = [i for i, c in enumerate(cells) if c.endswith("美元")][0]
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[0]) and usd_col is not None:
            v = float(cells[usd_col]) / 100.0  # quoted per 100 USD
            out[cells[0]] = v
    if usd_col is None:
        raise SystemExit(f"no USD header in {path.name}")
    return out


def main() -> None:
    allv: dict[str, float] = {}
    for p in sorted((DATA / "raw").glob("safe_20*.html")):
        d = parse(p)
        print(p.name, len(d), "header col ok")
        allv.update(d)
    rows = sorted((k, v) for k, v in allv.items() if k < "2025-01-01")
    with (DATA / "usdcny_fix.csv").open("w") as f:
        f.write("date,fix\n")
        for k, v in rows:
            f.write(f"{k},{v:.4f}\n")
    print("rows", len(rows), rows[0][0], rows[-1][0])


if __name__ == "__main__":
    main()
