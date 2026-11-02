"""TRY and USD short rates for the carry of a long USDTRY position.
TRY: the CBRT one-week repo (lending) rate step schedule parsed from the CBRT page saved at
research/data/usdtry_premium/raw_cbrt/page0.html (fetched 2026-11-01; robots.txt 404 = no rules). Steps dated
>= 2025-01-01 are dropped at parse. Known understatement: 2017-01..2018-05 the CBRT funded at the late liquidity
window (~9-12.75 %) while the repo stayed 8 %; 2020-08..09 funding drifted above the repo; offshore overnight TRY
swap rates spiked far above policy in 2018-08 and 2019-03. USD: EFFR from research/data/rates/DFF.csv."""
import csv
import datetime as dt
import html
import re

import numpy as np

PAGE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/usdtry_premium/raw_cbrt/page0.html"
DFF = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/rates/DFF.csv"
CUT = dt.date(2025, 1, 1)


def try_steps():
    t = open(PAGE, encoding="utf-8", errors="replace").read()
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, flags=re.S):
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, flags=re.S)]
        if len(c) == 3 and re.match(r"\d\d\.\d\d\.\d{4}$", c[0]):
            d = dt.datetime.strptime(c[0], "%d.%m.%Y").date()
            if d < CUT:
                out.append((d, float(c[2].replace(",", ".")) / 100))
    return out


_STEPS = try_steps()
_SD = np.array([d.toordinal() for d, _ in _STEPS])
_SV = np.array([v for _, v in _STEPS])


def r_try(d):
    k = int(np.searchsorted(_SD, d.toordinal(), side="right")) - 1
    return float(_SV[max(k, 0)])


def _dff():
    ds, vs = [], []
    with open(DFF) as f:
        rd = csv.reader(f)
        next(rd)
        for a, b in rd:
            try:
                v = float(b) / 100
            except ValueError:
                continue
            d = dt.date.fromisoformat(a)
            if d < CUT:
                ds.append(d.toordinal()); vs.append(v)
    return np.array(ds), np.array(vs)


_UD, _UV = _dff()


def r_usd(d):
    k = int(np.searchsorted(_UD, d.toordinal(), side="right")) - 1
    return float(_UV[max(k, 0)])


def carry_cost(d0, d1, markup=0.02):
    """Fraction of notional paid by a long USDTRY from date d0 to d1 (calendar nights), rates on d0."""
    nights = (d1 - d0).days
    return nights * (r_try(d0) / 365 - r_usd(d0) / 360 + markup / 365)
