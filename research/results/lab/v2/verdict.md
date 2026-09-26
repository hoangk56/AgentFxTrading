# Verdict — strategy refresh 2026-09-26

Pass bar: docs/superpowers/specs/2026-09-26-strategy-refresh-design.md (pre-registered). Holdout = 2025-01 .. 2026-09, check = 2023-24.

| id | holdout n | mean R | t | 2025 $ | 2026 $ | 2023-24 mean R | ctrl % | mirror $ | breadth | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| T1-ORB | 9816 | -0.078 | -3.84 | +4,447 | -4,914 | -0.078 | 100 | -704 | 32% of 22 | fail |
| T2-TMSORB | 5685 | -0.071 | -2.65 | +3,693 | -1,975 | -0.081 | 100 | -411 | 41% of 22 | fail |
| T3-TMSORB-X | 5685 | -0.087 | -3.57 | +2,289 | -1,663 | -0.078 | 100 | -1,018 | 32% of 22 | fail |
| T4-TMS-H4 | 10194 | -0.059 | -5.21 | -32,031 | +3,177 | -0.034 | 95 | -11,273 | 18% of 22 | fail |
| T5-TMS-H1 | 40606 | -0.125 | -20.76 | -70,038 | -57,351 | -0.115 | 0 | -42,830 | 9% of 22 | fail |
| J1-ICT | 2355 | -0.131 | -2.69 | -2,074 | -875 | -0.191 | 90 | -1,147 | 25% of 20 | fail |
| J2-ICT-MO | 2117 | -0.128 | -2.42 | -1,833 | -637 | -0.195 | 100 | -936 | 20% of 20 | fail |
| J3-ICT-2R | 2625 | -0.114 | -3.82 | -1,790 | -323 | -0.170 | 100 | -1,167 | 25% of 20 | fail |
| J4-ICT-2KZ | 4494 | -0.156 | -4.25 | -2,733 | -1,801 | -0.213 | 100 | -1,830 | 10% of 20 | fail |
| J5-SWEEP | 5502 | -0.210 | -6.00 | -3,325 | -1,823 | -0.197 | 100 | -2,041 | 20% of 20 | fail |
| N1-FIX | 4490 | -0.048 | -7.18 | -5,258 | -2,397 | -0.013 | 5 |  | 0% of 5 | fail |
| N2-GOTOBI | 248 | +0.035 | +1.20 | +161 | +107 | +0.041 | 95 |  | 100% of 1 | fail |
| N3-IMOM | 1735 | -0.017 | -1.96 | -505 | -757 | -0.018 | 60 | -783 | 25% of 4 | fail |
| N4-LBO | 5872 | -0.070 | -3.00 | -4,253 | +71 | -0.096 | 100 | -1,203 | 19% of 16 | fail |

## Conditions

| id | holdout >= 100 trades, mean R > 0, t >= 2.5 | 2025 > 0 and 2026 > 0 | 2023-24 mean R > 0 | beats >= 95 % of control seeds | mirror net > 0 | breadth >= 60 % |
|---|---|---|---|---|---|---|
| T1-ORB | **no** | **no** | **no** | yes | **no** | **no** |
| T2-TMSORB | **no** | **no** | **no** | yes | **no** | **no** |
| T3-TMSORB-X | **no** | **no** | **no** | yes | **no** | **no** |
| T4-TMS-H4 | **no** | **no** | **no** | yes | **no** | **no** |
| T5-TMS-H1 | **no** | **no** | **no** | **no** | **no** | **no** |
| J1-ICT | **no** | **no** | **no** | **no** | **no** | **no** |
| J2-ICT-MO | **no** | **no** | **no** | yes | **no** | **no** |
| J3-ICT-2R | **no** | **no** | **no** | yes | **no** | **no** |
| J4-ICT-2KZ | **no** | **no** | **no** | yes | **no** | **no** |
| J5-SWEEP | **no** | **no** | **no** | yes | **no** | **no** |
| N1-FIX | **no** | **no** | **no** | **no** | yes | **no** |
| N2-GOTOBI | **no** | yes | yes | yes | yes | yes |
| N3-IMOM | **no** | **no** | **no** | **no** | **no** | **no** |
| N4-LBO | **no** | **no** | **no** | yes | **no** | **no** |

Passed: none.
