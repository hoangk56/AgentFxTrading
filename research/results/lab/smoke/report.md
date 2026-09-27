# Strategy lab run smoke

$10k account, fixed lots, no loss limits, one position per strategy x symbol, ticks 2023-2026. Cells: 23; strategy errors: 0; catalog 03033d128929, lab code b83140c99245.

Flags: E = positive in every year with trades (>= 2 years), C = above >= 95 % of 20 random-entry seeds, S = above >= 95 % of the week-shuffle seeds, M = mirror net > 0. Long-only rules (TOM, OD1) cannot pass M by construction.

## Strategies (real data, summed over symbols)

| strategy | 2023 | 2024 | 2025 | 2026 | total $ | cells + | E | C | all |
|---|---|---|---|---|---|---|---|---|---|
| BTC-S1 | +0 | +0 | +1,332 | +0 | +1,332 | 3/4 | 0 | 3 | 0 |
| TOM | +0 | +0 | +687 | +0 | +687 | 1/1 | 0 | 1 | 0 |
| K1 | +0 | +0 | +330 | +0 | +330 | 1/2 | 0 | 1 | 0 |
| TMSORB | +0 | +0 | -700 | +0 | -700 | 1/4 | 0 | 1 | 0 |
| JUDAS | +0 | +0 | -970 | +0 | -970 | 1/4 | 0 | 1 | 0 |
| FLOWRSI | +0 | +0 | -8,125 | +0 | -8,125 | 0/4 | 0 | 2 | 0 |
| WF1 | +0 | +0 | -11,796 | +0 | -11,796 | 1/4 | 0 | 1 | 0 |

## Top 30 cells by net $

| strategy | symbol | n | net $ | 2023 | 2024 | 2025 | 2026 | PF | mean R | max DD $ | worst month $ | blown | mirror $ | ctrl pct | shuf pct | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-S1 | BTCUSD | 209 | +2,154 | +0 | +0 | +2,154 | +0 | 1.42 | +0.126 | 455 | -289 | - | +28 | 100 | nan | CM |
| WF1 | BTCUSD | 2071 | +1,058 | +0 | +0 | +1,058 | +0 | 1.03 | -0.003 | 2,456 | -2,076 | - | -89 | 100 | nan | C |
| K1 | EURUSD | 20 | +781 | +0 | +0 | +781 | +0 | 2.43 | +0.174 | 353 | -252 | - | +608 | 100 | nan | CM |
| TOM | US30 | 47 | +687 | +0 | +0 | +687 | +0 | 1.83 | +0.056 | 231 | -197 | - | -415 | 100 | nan | C |
| BTC-S1 | US30 | 312 | +267 | +0 | +0 | +267 | +0 | 1.10 | +0.027 | 348 | -91 | - | +111 | 100 | nan | CM |
| TMSORB | US30 | 275 | +155 | +0 | +0 | +155 | +0 | 1.05 | +0.008 | 525 | -168 | - | +6 | 100 | nan | CM |
| BTC-S1 | EURUSD | 150 | +87 | +0 | +0 | +87 | +0 | 1.08 | +0.014 | 193 | -122 | - | +10 | 100 | nan | CM |
| JUDAS | EURGBP | 4 | +21 | +0 | +0 | +21 | +0 | 1.81 | +0.264 | 16 | +1 | - | +nan | 100 | nan | C |
| JUDAS | EURUSD | 28 | -29 | +0 | +0 | -29 | +0 | 0.88 | -0.069 | 90 | -43 | - | -28 | 0 | nan | - |
| TMSORB | EURUSD | 320 | -197 | +0 | +0 | -197 | +0 | 0.90 | -0.030 | 368 | -192 | - | -26 | 50 | nan | - |
| JUDAS | US30 | 39 | -219 | +0 | +0 | -219 | +0 | 0.39 | -0.373 | 236 | -47 | - | -65 | 0 | nan | - |
| TMSORB | EURGBP | 111 | -315 | +0 | +0 | -315 | +0 | 0.57 | -0.161 | 331 | -53 | - | +nan | 0 | nan | - |
| TMSORB | BTCUSD | 344 | -343 | +0 | +0 | -343 | +0 | 0.96 | -0.019 | 1,794 | -504 | - | +nan | 50 | nan | - |
| K1 | EURGBP | 17 | -451 | +0 | +0 | -451 | +0 | 0.41 | -0.179 | 459 | -277 | - | +nan | 50 | nan | - |
| FLOWRSI | US30 | 670 | -614 | +0 | +0 | -614 | +0 | 0.94 | -0.054 | 946 | -341 | - | -514 | 50 | nan | - |
| WF1 | US30 | 1270 | -628 | +0 | +0 | -628 | +0 | 0.92 | -0.016 | 1,184 | -518 | - | -577 | 0 | nan | - |
| FLOWRSI | EURUSD | 544 | -699 | +0 | +0 | -699 | +0 | 0.89 | -0.072 | 1,016 | -274 | - | -666 | 100 | nan | C |
| JUDAS | BTCUSD | 99 | -743 | +0 | +0 | -743 | +0 | 0.60 | -0.231 | 773 | -181 | - | -5 | 50 | nan | - |
| BTC-S1 | EURGBP | 164 | -1,175 | +0 | +0 | -1,175 | +0 | 0.28 | -0.698 | 1,181 | -187 | - | +nan | 0 | nan | - |
| WF1 | EURUSD | 1029 | -1,463 | +0 | +0 | -1,463 | +0 | 0.70 | -0.145 | 1,500 | -335 | - | -832 | 0 | nan | - |
| FLOWRSI | EURGBP | 295 | -2,207 | +0 | +0 | -2,207 | +0 | 0.51 | -0.281 | 2,326 | -376 | - | +nan | 0 | nan | - |
| FLOWRSI | BTCUSD | 926 | -4,604 | +0 | +0 | -4,604 | +0 | 0.88 | -0.050 | 5,680 | -1,455 | - | -689 | 100 | nan | C |
| WF1 | EURGBP | 1515 | -10,763 | +0 | +0 | -10,763 | +0 | 0.20 | -0.788 | 10,769 | -1,434 | 2025-12-14 | +nan | 0 | nan | - |

## Cells with all four flags: 0

- none

Full tables: cells.csv (every cell), matrix.csv (strategy x symbol net $).