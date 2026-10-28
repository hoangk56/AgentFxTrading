# PREREG (joint, rounds 32-36): one HOLD look for six VAL-strong rules, Bonferroni bar. Tier DEMO at most

Prepared 2026-10-28 02:56-03:15 UTC (`date -u`). **Not yet registered and HOLD not opened.** The registration takes
effect when the user confirms this file. Only then does the lead run the HOLD commands below, once.

No return, signal or price statistic dated on or after 2025-01-01 was computed while preparing this file, and no
2025-26 data was fetched:
- every script refuses `--end` after 2025-01-01, and refuses any `pull`, unless `HOLD_RUN=1`;
- the frozen inputs in `prereg_code/data/` stop at 2024-12-31.

The raw ProShares and CBOE files in the round 32 / 34 scratchpads contain 2025-26 rows. They were filtered by year
without being printed.

## Why this exists: a bar change approved by the user
- On 2026-10-28 the user approved one joint registration that opens HOLD 2025-01-01..2026-09-24 once for the rules of
  rounds 32-36 that are strong in VAL with their side fixed before any return, but fail IS.
- Under the research bars (research/PROMPT.md), none of them is a candidate:
  - DEMO needs IS net t >= 2.0;
  - every rule below has IS net t between 0.05 and 2.51;
  - A5 has IS t 2.51 but fails DEMO on its IS random control (0.879).
- So this is a **bar change**: IS t is replaced by a multiplicity-adjusted HOLD test. A rule that passes becomes DEMO
  at most, never LIVE directly.
- Retention: rules picked after seeing VAL have kept about 1/4 of their VAL size in HOLD (round 18,
  [round18_decay_dom_2026-10-06.md](../round18_decay_dom_2026-10-06.md)). Every rule here was picked on VAL.

## 1. Selection (criterion written before the scan)
The criterion was written at **2026-10-28T02:56:29Z**, before any STREAM output of rounds 31-36 was scanned
([prereg_code/SELECTION_CRITERION.txt](prereg_code/SELECTION_CRITERION.txt)). A cell is eligible if all of these hold:
1. its side and parameters were declared in a HYPOTHESES_*.md before its returns;
2. IS net > 0;
3. VAL net t >= 2.0;
4. it beats >= 90 % of its random / shift control in VAL. A cell with no VAL control is not eligible;
5. it is graded on the stream's registered cost model.

Eligible cells are then grouped by mechanism, and one cell is kept per mechanism: the one with the highest VAL net t.

**Scan.**
- Covered: all 14 STREAM_*.md of rounds 31-36 and every cell in the outputs they cite (scratchpad `r3x/<stream>/out/`).
- r33 K, r34 D, r34 E and r36 U were scanned from their JSON / text outputs by the lead.
- The other ten streams were scanned by a sub-agent with file:line evidence. The lead re-checked the two cells it
  added (r32 V `cells.tsv` lines 50 and 93) and the L3 cell.

### Eligible cells (10) and what was kept (6)
| stream | cell | IS net bp (t) | VAL n, net bp (t) | VAL control | mechanism | kept? |
|---|---|---|---|---|---|---|
| r34 D | **K hi>med allFri fade 1h** (BTCUSD) | +6.07 (0.80) | 89, +16.68 (**3.237**) | 1.00 | Deribit Friday 08:00 expiry reversal | **kept: D-K4** |
| r34 D | G3 K4 & GEX<0 lastFri | +33.42 (0.65) | 34, +15.26 (3.206) | 0.965 | same | no (lower VAL t) |
| r34 D | G3 K4 & GEX<0 allFri | +18.83 (1.42) | 146, +8.97 (2.399) | 0.91 | same | no |
| r34 E | **H1roll_USTEC_w30** | +10.26 (1.38) | 93, +11.49 (**2.775**) | 1.00 | equity LETF rebalancing into the close | **kept: E-USTEC** |
| r34 E | H1roll_XAUUSD_w15 | +2.34 (1.86) | 66, +3.11 (2.17) | 0.99 | gold momentum into the COMEX settlement (not LETF, see below) | **excluded**: this mechanism's HOLD is already open (round 12) |
| r32 A | **A5 HN-FEAR US500 q95 h3** | +32.87 (2.51) | 28, +100.41 (**2.700**) | 1.00 (300 seeds) / 0.998 (1,000) | attention-measured fear sell-off reverses (FEARS) | **kept: A5-HN** |
| r36 U | **U3 h3 BTCUSD** | +96.44 (1.06) | 92, +159.37 (**2.2652**) | 0.98 | household-cash surprise -> retail buying | **kept: U3-BTC** |
| r36 U | U3 h3 USTEC | +33.33 (1.90) | 90, +55.21 (2.2568) | 0.98 | same | no (lower VAL t by 0.008) |
| r32 L | **L3 k5 USDJPY** | +1.15 (0.05) | 18, +85.03 (**2.582**) | 0.995 | large Treasury + RRP liquidity flows -> USD | **kept: L3-JPY** |
| r32 V | **V1 VRP(VXN) USTEC k0.5 h1** | +6.04 (0.52) | 186, +24.26 (**2.182**) | 0.995 | option-priced fear premium -> long index | **kept: V1-VXN** |
| r32 V | V3b VVIX USTEC k1.5 h1 | +15.19 (0.60) | 64, +40.51 (2.005) | 0.99 | same | no |

### Mechanism decisions (fixed before keeping cells)
- **E: two mechanisms, equity vs gold.**
  - Round 34 P1 showed gold's settlement momentum does not rise with the measured dose (IS interaction t -4.0). Gold's
    ProShares dose is about 0.005 % of COMEX open interest per 1 % move, against 1-2 % of NQ open interest for the
    Nasdaq funds.
  - So XAU w15 is not an LETF flow. It is round 12's L4-G-d: top-decile move days, follow from 13:15 to 13:30 ET.
  - That rule was registered and opened on this same HOLD on 2026-10-06 ([PREREG_L](../round12_flows_execution/PREREG_L_gold_settlement_bigday.md):
    46 trades, +1.68 bp, t 0.37). It is already a DEMO candidate under its own terms.
  - A second HOLD look at nearly the same trades would not be blind, so XAU w15 is excluded and USTEC w30 is the
    kept cell for the LETF mechanism.
- **D: K4 (volume condition) and G3 (gamma condition) are one mechanism**, the Friday expiry reversal. Keep the
  highest VAL t: K hi>med allFri, 3.237 against G3 last Fridays 3.206.
- **U3: BTCUSD and USTEC are one mechanism**, with the same signal and the same declared channel. By the rule, BTCUSD
  is kept because its VAL t is 2.2652 against 2.2568. The difference is negligible, and the stream's verdict cell was
  USTEC (see the user decisions at the end).
- **V1 and V3b are one mechanism.** HYPOTHESES_V gives both the same channel: risk-premium side, long when fear is
  priced high. V1 is kept.
- **A5 and V1 are kept as separate mechanisms.** Both buy US equities after fear, but they declare different
  channels: a sentiment sell-off that reverses over 3 days (attention data), against a 1-day variance risk premium
  (option prices). Their HOLD outcomes are positively correlated; see the honesty section.

### Expected candidates that were excluded, and other near misses
- **r33 K, Coinbase premium -> BTC.**
  - The only declared cells with VAL t >= 2 fail the criterion:
    - CB1 BTC k1.0 h1d: VAL +37.1 bp (t 2.07), but the VAL random control is 0.77;
    - CB1 k1.0 h3d: IS -20.5.
  - The K3-CBX composites are the source of the "VAL t 2.0-2.7": k1.0 h3d VAL t 2.74, random 0.94; hourly 2.27 /
    0.95; k1.5 h3d 2.23 / 0.90. They fail criterion 1:
    - HYPOTHESES_K labels round 3 (19:26 UTC) "POST-HOC";
    - its Bitfinex leg's sign was set after reading K2-BFX's IS and VAL returns, which are the same trades with the
      sign reversed.
- **r32 A, other A5 US500 thresholds**: q80 h3 VAL t 2.74, q80 h5 2.57, q95 h5 2.23, q90 h3 2.18, q90 h5 2.15. None
  has a VAL control (the stream ran controls only for the IS-chosen cell), so they are not eligible. The kept cell is
  the stream's own IS choice.
- **Other cells with no VAL control (not eligible):**
  - r32 A A2 FEARS USDJPY q90 h1: VAL t 2.0;
  - r32 A A3 ETH q90 h3 / h5: 2.91 / 2.68;
  - r31 J M1 basket k1 h1: 2.48;
  - r36 A P3 USDCNH h5: n 6, t not graded.
- **IS net <= 0 (not eligible):**
  - r32 L3 k1 US2000 / XAUUSD / BASKET: VAL t 2.95 / 2.56 / 2.74;
  - r32 V3b VVIX US30: 2.10;
  - r32 A2 FEARS US500 q95 h3 / h5;
  - r34 E H3rev XAU;
  - r33 K CB1 BTC h3d and ETH cells.
- **Control below 0.90 (not eligible):** r34 D K top3 allFri (VAL t 2.27, control 0.795) and K hi>med lastFri (2.17,
  0.69).
- **Just below the VAL bar:** r36 U3 h3 US500, VAL t 1.96.

## 2. The six rules
Common to all rules:
- **HOLD** = 2025-01-01 .. 2026-09-24. The IC M1 cache ends 2026-09-24, so every script runs with
  `--end 2026-09-25`.
- **Clipped trades:** a trade entered before 2025 whose exit falls in 2025 belongs to no era. A HOLD trade whose exit
  falls on or after `--end` is dropped.
- **Prices:** IC M1 bid / ask from `research/data/m1`.
- **Fills:** each rule uses its stream's own fill, which is the next bar's close, or +1 minute where the stream
  defines it so.
- **Costs:** half the actual spread at each fill.
- **Data sources:** every external input listed is public and needs no account. Pull code is in each script and was
  never run.
- **Swaps:** for index and FX legs, `research.swing.rates.swap_frac_at` (FRED rates cached in
  `research/data/rates`). For BTC, -5 bp per weekday rollover with Friday counting 3 (round 31 C).
- **t:** each rule uses its stream's t (below).

### D-K4: BTC Friday expiry fade on high expiring volume (round 34 D, HYPOTHESES_D family K, 20:33-20:50 UTC)
- **Signal:**
  - On Fridays with a Deribit BTC option expiry at 08:00 UTC, m = ln(IC mid 08:00 / IC mid 07:00). Prices are taken
    at the minute, from the close of the bar labelled one minute earlier.
  - EXV = the BTC amount traded in options expiring that Friday with strike within +-5 % of the index at the trade,
    over [Friday-7 d 07:00, Friday 07:00) UTC.
  - Trade only if EXV is above the median of the previous 26 expiry Fridays' EXV (at least 13 required).
- **Trade:** side -sign(m); entry at 08:01 (close of the bar labelled 08:00), exit 09:00. At most one position; no
  swap.
- **t:** clustered by day (one trade a day).
- **HOLD data:** `history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time` (BTC, kind option),
  2024-12-01 .. 2026-09-24.
  - This is about 10 M trades, roughly 1,000 requests at 1.1 s each.
  - The December 2024 trades only complete the EXV of the 2025-01-03 expiry; the EXV of every pre-2025 expiry comes
    from the frozen `data/d_exv_btc_to2024.csv`.

### E-USTEC: follow the day's move from 15:30 to 16:00 ET on top-decile LETF-dose days (round 34 E, H1roll w30, 20:36-20:40 UTC)
- **Days:** NYSE days from `holidays` 0.106, early-close days dropped.
- **Dose:** Γ = Σ AUM × L(L-1) over TQQQ 3, SQQQ -3, QLD 2, QID -2, PSQ -1, using the latest ProShares row dated
  before d.
- **Move:** r = ln(mid at 15:29 ET / mid at 16:00 ET on the previous day).
- **Dollar open interest:** DOI = CFTC legacy NQ OI (209742 × 20 + 209741 × 100), latest report with as-of + 3 days
  < d, × the previous 16:00 mid.
- **Signal:** S = Γ r / DOI. Trade when |S| > the 90th percentile of |S| over the previous 250 days (at least 120
  valid).
- **Trade:** side sign(r); entry at the 15:30 bar, exit at the 16:00 bar. No swap; one trade a day. The t is plain.
- **HOLD data:**
  - `accounts.profunds.com/etfdata/ByFund/<T>-historical_nav.csv` for the 5 funds; rows from 2025 on are used,
    pre-2025 rows are frozen in `data/`;
  - `www.cftc.gov/files/dea/history/deacot2025.zip` and `deacot2026.zip`.

### A5-HN: long US500 for 3 days after a Hacker News "recession" spike (round 32 A, HYPOTHESES_A A5, 18:57 UTC)
- **Signal:**
  - c7 = 7-day count of HN stories matching "recession" (Algolia `search_by_date`, tags story, no typo tolerance).
  - a = ln(1 + c7) - ln(1 + median of c7 at -7, -14, -21, -28 days), clipped to [-2, 2].
  - Z = a / sd(a over the previous 365 days, at least 120 values).
- **Trigger:** weekday E triggers if Z(E-1) >= **1.8207467842895426**, the IS q95. The script recomputes it from the
  frozen IS data and asserts it.
- **Trade:**
  - long at E 07:00 UTC, exit 3 weekdays later at 07:00; a weekend landing exits Friday 20:00 UTC;
  - every trigger day opens a position, so at most 3 are open;
  - swap: US500, Friday triple.
- **t:** clustered in 2-week blocks.
- **HOLD data:** `hn.algolia.com/api/v1/search_by_date`, 2025-01 .. 2026-09-24, only `created_at_i` retrieved.
  - HN moderation removes some stories later, so counts pulled in 2026 may differ slightly from what was live. This
    was also true of the pre-2025 data.

### U3-BTC: long BTC for 3 marks after a US household-cash surprise (round 36 U, HYPOTHESES_U U3, 01:50 / 01:52 UTC)
- **Signal:**
  - T5 = refunds + SS + SSI + EIP + CTC + unemployment + VA over the last 5 DTS days;
  - x = ln(T5 / T5 one year earlier), where the earlier value is taken at the first DTS day on or after D-365;
  - the signal fires if x > the 80th percentile of x over the previous 250 DTS days.
- **Trade:**
  - long at the 19:30 UTC mark of the first weekday mark on or after DTS day D+2, exit 3 marks later;
  - one trade at a time;
  - ex-EIP windows as declared (no EIP is expected in HOLD).
- **Costs:** long at the ask, exit at the bid; -5 bp a rollover. The t is plain.
- **HOLD data:** fiscaldata.treasury.gov `dts/deposits_withdrawals_operating_cash`, withdrawals, 2025-01-01 ..
  2026-09-24.
- **Precondition (counts only, before any return):** every household group except EIP / CTC must have matched rows in
  each HOLD year. Otherwise the run stops and asks the user, because DTS may have renamed a line.

### L3-JPY: USDJPY 5 marks after a large Treasury + RRP liquidity flow (round 32 L, HYPOTHESES_L L3, 18:50-19:05 UTC)
- **Signal:**
  - y1 = -(ΔTGA + ΔRRP) per DTS business day; y5 = 5-day sum; z5 = y5 / sd of the previous 250 values of y5.
  - At the 15:00 UTC mark of business day m, v = z5 of business day m-2.
  - Marks are every 5th business day, counted from the first 2016 mark.
- **Trade:** when |v| > 1.5: v > 0 (liquidity added) -> **short** USDJPY; v < 0 (drain) -> long.
  - Exit at the 15:00 mark 5 marks later.
  - Cost: + 0.6 bp commission; swap with a Wednesday triple.
  - The t is plain.
- **HOLD data:** fiscaldata `dts/operating_cash_balance` for 2025-26 (TGA), and `markets.newyorkfed.org`
  `api/rp/reverserepo/propositions/search.json` for 2025 and 2026.
- **Precondition:** the DTS account types are printed, and if no TGA row parses, the run stops.

### V1-VXN: long USTEC 1 day when the Nasdaq variance risk premium is high (round 32 V, HYPOTHESES_V V1, 18:51 UTC)
- **Dates:** CBOE VIX trading dates.
- **Mark:** IC USTEC bar starting at 16:30 ET (else the last bar in [16:00, 16:30]).
- **Signal:**
  - VRP = VXN close² - RV21², where RV21 is computed from 21 daily mark log returns ending at i-1 (at least 15).
  - z = (VRP - mean) / sd over the previous 252 dates (at least 200).
- **Trade:** long when z > 0.5; exit at the next date's 16:30 mark; non-overlapping. The t is plain.
- **HOLD data:** `cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv` and `VXN_History.csv`.

### Reproduction check (mandatory; frozen copies, IS + VAL only)
Output: [prereg_code/repro_check_output.txt](prereg_code/repro_check_output.txt).
- How it was run: the `.py.txt` files were copied to a fresh folder, renamed to `.py`, and run with `HOLD_RUN` unset.
- Result: every n, net bp and t equals the stream to the printed precision.

| rule | stream IS n / net / t | frozen IS | stream VAL n / net / t | frozen VAL | VAL control (stream / frozen) |
|---|---|---|---|---|---|
| D-K4 | 144 / +6.07 / 0.80 | 144 / +6.07 / 0.803 | 89 / +16.68 / 3.237 | 89 / +16.68 / 3.237 | 1.00 / 1.000 |
| E-USTEC | 150 / +10.26 / 1.38 | 150 / +10.26 / 1.382 | 93 / +11.49 / 2.78 | 93 / +11.49 / 2.775 | 1.00 / 1.000 |
| A5-HN | 79 / +32.87 / 2.51 | 79 / +32.87 / 2.511 | 28 / +100.41 / 2.70 | 28 / +100.41 / 2.700 | 1.00 / 1.000 |
| U3-BTC | 108 / +96.4 / 1.06 | 108 / +96.44 / 1.056 | 92 / +159.37 / 2.265 | 92 / +159.37 / 2.265 | 0.98 / 0.990 |
| L3-JPY | 33 / +1.2 / 0.05 | 33 / +1.15 / 0.053 | 18 / +85.0 / 2.58 | 18 / +85.03 / 2.582 | 0.99 / 0.995 |
| V1-VXN | 255 / +6.04 / 0.52 | 255 / +6.04 / 0.523 | 186 / +24.26 / 2.182 | 186 / +24.26 / 2.182 | 0.995 / 0.995 |

How the random-control percentiles compare:
- D and A5 use the stream's seeds and match exactly.
- E, U3, L3 and V1 drew their seeds from a stream-wide random stream that a single cell cannot replay. Their controls
  were rerun with fixed seeds and differ by at most 0.01.

### Expected HOLD n and t
- HOLD is 1.73 years. Expected n = the VAL rate × 1.73.
- Expected t at the VAL size = VAL t × sqrt(1.73 / 3). This keeps each rule's clustering.
- Power = P(HOLD t >= 2.394), using the normal approximation.

| rule | VAL trades / yr | expected HOLD n | expected t: VAL size | power | expected t: 1/4 size | power at 1/4 size | null pass rate |
|---|---|---|---|---|---|---|---|
| D-K4 | 30 | ~51 | 2.46 | 0.53 | 0.61 | 0.038 | 0.0083 |
| E-USTEC | 31 | ~54 | 2.11 | 0.39 | 0.53 | 0.031 | 0.0083 |
| A5-HN | 9 (3 episodes) | ~16 (~5 episodes) | 2.05 | 0.37 | 0.51 | 0.030 | 0.0083 |
| U3-BTC | 31 | ~53 | 1.72 | 0.25 | 0.43 | 0.025 | 0.0083 |
| L3-JPY | 6 | ~10 | 1.96 | 0.33 | 0.49 | 0.029 | 0.0083 |
| V1-VXN | 62 | ~107 | 1.66 | 0.23 | 0.41 | 0.024 | 0.0083 |

The power figures for A5 and L3 are optimistic:
- A5's t uses ~5-8 two-week clusters;
- L3 has ~10 trades;
- with that little data the t distribution has fat tails.

## 3. Bar and rules after HOLD (fixed now)
- **m = 6.** Each rule is tested at one-sided Bonferroni α = 0.05 / 6 = 0.00833, so the bar is z = **2.394**.
  - For comparison: m = 4 gives 2.241, m = 5 gives 2.326.
  - If the user drops or adds rules before HOLD, m and z change. They must be fixed again here before the run.
- **A rule passes HOLD only if all of these hold:**
  1. HOLD n >= 3;
  2. HOLD net t >= 2.394, where t is the rule's registered statistic (D clustered by day, A5 in 2-week blocks, the
     others plain);
  3. HOLD net > 0 with the half spreads × 1.5;
  4. HOLD net > 0 with the +1 minute fills.
- The random control, the per-year figures and the mid are reported but do not gate.
- **The run, in this order:**
  1. all six pulls;
  2. the preconditions (counts only);
  3. the six evals, each once.
  - If a precondition stops the run (a DTS line renamed, a CFTC code missing, a feed changed), the lead asks the user
    before any return is computed.
  - Nothing is rerun after a return is printed.
- **A rule that fails is dropped for good.** It is not re-registered, re-tuned or given a forward log under this
  mechanism, except by a new user decision recorded in the JOURNAL.

### Demo terms for a passing rule (DEMO only; the cBot and the deployment are the user's decisions)
Definitions:
- R = net bp / the VAL per-trade sd (D 48.3, E 39.9, A5 154.6, U3 674.8, L3 139.7, V1 151.6 bp).
- s = the VAL per-trade Sharpe (D 0.345, E 0.288, A5 0.649, U3 0.236, L3 0.608, V1 0.160).

Stop rules (any one stops the demo):
- **S1:** after N1 demo trades, cumulative R < 0.
- **S2:** after N2 = 2 × N1 trades, cumulative R < N2 × s / 4 - 1.5 × sqrt(N2). That is 1.5 sd below the 1/4-size
  expectation.
- **S3:** after 20 trades, the median entry slippage against the model fill is worse than the VAL median half
  spread. This is reported as an execution failure.

Promotion to a LIVE candidate (the user decides), when all of these hold:
- HOLD + demo pooled net t >= 2.5, with the registered statistic, as in
  [PREREG_G](../round27_levels_opens/PREREG_G_gold_round50_cascade.md);
- at least N2 demo trades;
- pooled net > 0 at spread × 1.5.

| rule | demo trades / yr | N1 | N2 | S2 threshold at N2 (R) | pooled trades for t 2.5 at VAL size (years of demo after HOLD) | at 1/4 size |
|---|---|---|---|---|---|---|
| D-K4 | ~30 | 30 | 60 | -6.4 | ~53 (~0, N2 binds: 2 y) | ~840 (~27 y) |
| E-USTEC | ~31 | 30 | 60 | -7.3 | ~75 (~2 y) | ~1,200 (~37 y) |
| A5-HN | ~9 | 10 | 20 | -3.5 | ~15 trades, but ~10+ episodes (~3 y) | ~240 (~25 y) |
| U3-BTC | ~31 | 30 | 60 | -8.1 | ~112 (~2 y) | ~1,800 (~56 y) |
| L3-JPY | ~6 | 10 | 20 | -3.7 | ~17 (N2 binds: ~3 y) | ~270 (~44 y) |
| V1-VXN | ~62 | 60 | 120 | -11.6 | ~244 (~2.2 y) | ~3,900 (~61 y) |

## 4. Honesty
- **This is a bar change**, approved by the user on 2026-10-28. Every rule here failed the IS bar or, for A5, the IS
  control.
  - Selection inside each stream and inside this file used VAL: the kept cell is the highest VAL t.
  - Round 18 says such picks keep about 1/4 of their VAL size.
- **HOLD is not clean.** It has been opened before for other rules, including:
  - C3;
  - round 12 I / J / L (gold settlement momentum);
  - round 13 E1;
  - round 24 F3 / FOMC A4 and its forward slices;
  - round 27 G;
  - swing v2 and the month-end USD rule.
  Round 31-36 streams also disclosed small slips: TQQQ rows of 2026-10, HKMA 2025 rows, an ECB 2026 row and a SHFE
  snippet. None of these touched the six rules' returns.
- **The broad path of markets in 2025-26 is public knowledge**, to the user and to the model that wrote this. For
  example, the April 2025 tariff sell-off and rebound would almost certainly trigger the HN "recession" rule (A5).
  The "buy fear" rules (A5, V1) and the long-equity / long-BTC rules (E, U3) therefore face a HOLD whose large
  episodes are known in outline. Their outcomes are also correlated with each other.
  - Bonferroni stays valid under this positive dependence (it is conservative).
  - It cannot remove the hindsight in choosing to look now.
- **Expected outcome:**
  - at the 1/4 retention, the expected number of passes is **0.18** (P(at least one) ~0.16);
  - at the full VAL size it would be 2.1;
  - if no rule has an edge, the chance that any passes is <= 5 %.
- **A pass makes a rule DEMO, not LIVE.**
  - The fastest promotion at the VAL size takes about 2 more years of demo.
  - At the 1/4 size, promotion is out of reach for decades.
  - LIVE remains C3 alone.

## 5. Code and data (sha256, first 16 hex; `python -m research.tools.prereg_hashes`; do not edit before HOLD)
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/jcommon.py.txt` e941d082d41edfdc
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_a5_hn.py.txt` 200eaf7ef8bd5dca
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_d_k4.py.txt` 5681fe4209dcad58
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_e_letf.py.txt` 02d86f4ab0c30d7e
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_l3.py.txt` f25e52907a064c75
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_u3.py.txt` 619f4e9479ca232e
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/rule_v1.py.txt` 7551b92652a0efa0
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/a5_hn_recession_to2024.json` d649114310ae5c9a
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/d_exv_btc_to2024.csv` dfd01b156ef5480f
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/e_cot_ndx_to2024.csv` 1607ade4e83f18eb
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/e_proshares_nasdaq_to2024.csv` 54262233114c88c7
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/l3_dts_tga_to2024.json` 346b143dcdf9e94a
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/l3_rrp_daily_to2024.json` 787128954503a27b
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/u3_dts_household_to2024.json` 5dde1e90400638f6
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/v1_cboe_VIX_to2024.csv` 1d2ad769bed2854d
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/data/v1_cboe_VXN_to2024.csv` 3c272f8fce0df576
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/SELECTION_CRITERION.txt` c3f704a1a2589fb8
- `research/results/portfolio/joint_prereg_2026-10/prereg_code/repro_check_output.txt` 54c5ce10bf5e81b4
- Repo helpers (clean at 4d684c4): `research/m1.py` 3970b82bffee304c, `research/specs.py` 95512c94933790c9,
  `research/swing/rates.py` d5ec1cd0fd79819d, `research/swing/swing.py` 8511bfbae1366fc4, `research/ticks.py`
  505e45e1dc02e706.
- Rates cache: `research/data/rates/` DFF 77377d10b2bf65c9, ECBDFR a50ea4895af37549, IRSTCI01JPM156N
  9108c5b20bcdb0ce, IUDSOIA 4164ffc420e7666a, IR3TIB01CHM156N 57fea956653ea325, IR3TIB01NZM156N 664fb6460febb638,
  IRSTCI01AUM156N c2d4b9d7432b2fbc, IRSTCI01CAM156N 85b1c5adb819d648.
- IC M1 caches: `research/data/m1/` BTCUSD 67ba69afefe1ef11, USTEC 875bf543260a8c19, US500 c9a252c605e80e45,
  USDJPY 462277851d499921.
- Pre-2025 inputs: they are frozen in `prereg_code/data/`, so the HOLD run does not depend on the round 32-36
  scratchpads.
- The IS / VAL trade lists of the reproduction are in `prereg_code/repro_trades/`.

### HOLD run (lead, once, after the user confirms; `R` = an empty run folder)
```
mkdir -p $R/code $R/out $R/hold_data && cp -r <prereg_code>/data $R/data
for f in <prereg_code>/*.py.txt; do cp $f $R/code/$(basename $f .txt); done
research/.venv/bin/python -m research.tools.prereg_hashes <prereg_code>/*.py.txt <prereg_code>/data/*   # must equal section 5
for r in d_k4 e_letf a5_hn u3 l3 v1; do HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $R/code/rule_$r.py pull --end 2026-09-25; done
for r in d_k4 e_letf a5_hn u3 l3 v1; do HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $R/code/rule_$r.py eval --end 2026-09-25; done | tee $R/out/hold_output.txt
```
Run every command from the repo root. The decision lines are `[HOLD]` in `hold_output.txt`. The pulls keep >= 1.1-1.5 s between
requests to one host, send a browser User-Agent and no e-mail, and log to `hold_data/requests.log`.

## 6. Decisions the user must make before HOLD opens
1. **Confirm the bar change and the set of m = 6** with z 2.394. Two kept rules were not in the lead's list: L3-JPY
   (IS t 0.05, n 18 in VAL) and V1-VXN (IS t 0.52). The criterion keeps them. Dropping either is allowed only now,
   and it changes m and z.
2. **U3: BTCUSD (mechanical pick, VAL t 2.2652) or USTEC (2.2568, the stream's own verdict cell).**
3. **K3-CBX (Coinbase premium composite) stays out** unless the user overrides the post-hoc exclusion. Adding it
   gives m = 7, z 2.45.
4. **Gold LETF / settlement (XAU w15) stays out**, because its mechanism's HOLD is already open (round 12 L).
5. **Network at HOLD time:** history.deribit.com (~1,000 requests), accounts.profunds.com, cftc.gov, hn.algolia.com,
   api.fiscaldata.treasury.gov, markets.newyorkfed.org, cdn.cboe.com. All are public, with no account.

## 7. Registration (user decisions, 2026-10-28 07:34 UTC, before any HOLD pull)
The user confirmed on 2026-10-28 ("ok, bỏ L3 và V1, U3 dùng BTC, mở holdout đi"):
1. **L3-JPY and V1-VXN are dropped** before HOLD. Their pulls and evals are not run, and their HOLD is never computed.
2. **m = 4: D-K4, E-USTEC, A5-HN, U3-BTC.** The bar is one-sided Bonferroni α = 0.05 / 4 = 0.0125, **z = 2.241**. The
   other pass conditions of section 3 are unchanged (n >= 3, net > 0 at spread × 1.5 and at +1 min).
3. **U3 trades BTCUSD** (the mechanical pick). The USTEC cell is not run on HOLD.
4. K3-CBX and XAU w15 stay out.
5. The network pulls of section 6.5 are approved, minus markets.newyorkfed.org and cdn.cboe.com (L3 / V1 only).

The HOLD run follows section 5 with `for r in d_k4 e_letf a5_hn u3`. Power at z 2.241, normal approximation: at the VAL
size D 0.59, E 0.45, A5 0.42, U3 0.30; at 1/4 size D 0.051, E 0.044, A5 0.042, U3 0.035, so the expected number of
passes is 0.17 and P(at least one pass) ~0.16 at 1/4 retention.

## HOLD result
(appended after the run, below this line; nothing above edited)

Run 2026-10-28, lead, once, as registered in section 7 (m = 4, bar z 2.241). Folder: scratchpad `hold_run/` (code
copied from `prereg_code/*.py.txt`, hashes checked equal to section 5 at 07:34 UTC; IC M1 caches and repo helpers equal
too).
- Pulls 07:35-08:40 UTC, in parallel, one job per host: 904 requests, all HTTP 200
  ([prereg_code/hold_requests.log](prereg_code/hold_requests.log)). Deribit 2024-12..2026-09 option trades, ProShares
  NAV files of the 5 funds, CFTC deacot2025 / 2026, HN Algolia (140 story timestamps), DTS withdrawals (5 pages). The
  raw HOLD data (74 MB) stays in the scratchpad.
- Preconditions (counts only): E has 52 / 42 NQ COT reports in 2025 / 2026; U3 matched every household group in both
  years (250 / 185 rows each). Neither stopped the run.
- Evals 08:40 UTC, each once, nothing rerun: [prereg_code/hold_output.txt](prereg_code/hold_output.txt). IS and VAL
  lines equal the reproduction check exactly. U3 printed a numpy "All-NaN slice" warning, also present in IS / VAL
  (the first rolling windows).

| rule | HOLD n | mid bp | net bp (t) | x1.5 | +1 min | random | years | verdict |
|---|---|---|---|---|---|---|---|---|
| D-K4 | 45 | -10.06 | -11.51 (**-1.123**) | -12.23 | -10.15 | 0.325 | 2025 -3.8, 2026 -28.6 | **fails** |
| E-USTEC | 42 | -1.65 | -2.22 (**-0.352**) | -2.50 | -1.62 | 0.353 | 2025 -5.9, 2026 +0.5 | **fails** |
| A5-HN | 15 (5 episodes) | -12.09 | -24.44 (**-0.245**) | -24.85 | -26.55 | 0.197 | 2025 +20.3, 2026 -91.6 | **fails** |
| U3-BTC | 58 | -19.90 | -43.31 (**-0.693**) | -44.16 | -43.88 | 0.363 | 2025 -51.2, 2026 -35.9 | **fails** |

**Verdict: no rule passes; all four are dropped for good** (section 3). Every HOLD net is negative, also at mid, and
every random control is below 0.4. Retention against VAL is below zero for all four (round 18 expected about 1/4); the
equal-weight z of the four HOLD t is -1.21. The trade counts came in near the registered expectation (51 / 54 / 16 /
53), so the failure is the effect, not the sample. LIVE remains C3 alone.
