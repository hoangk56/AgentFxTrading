# Round 33, stream S: hypotheses (gold in segmented markets, SNB sight deposits)

Written 2026-10-27 19:14-19:16 UTC (`date -u` 19:14:22 at the start), **before any return was computed**. At this
time the stream had loaded: the SGE Shanghai Gold Benchmark (AM / PM, 2016-04-19..2024-12-31), SGE Au99.99 daily
OHLC (2016-12-19..2024-12-31), the SNB weekly sight deposits (2009-01-09..2024-12-27), IC XAUUSD / USDCNH quotes at
the premium minutes (same-timestamp legs only, to time the premium) and IC spreads at the entry minutes (cost only).
No price change after a signal has been joined to any signal. The SGE historical daily-quote archive (2002-10..2023-12,
for Au99.99 closes before 2016-12 and the Au(T+D) delivery direction) is still being crawled; it is used only by the
rules below, written now.

Disclosures (HOLD hygiene):
- SGE's `/graph/DayilyJzj` ignored the `end` date and returned the benchmark to 2026-10-26; one line printed the last
  row (2026-10-26, AM 858.32 / PM 861.01 CNY per gram). Nothing uses it: the raw file was overwritten and only rows
  before 2025-01-01 (Beijing) were kept. `/graph/Dailyhq` (Au99.99) also returns 2026; it was cut before any print
  (only the first row was printed).
- No 2025-26 value of any other series was printed.

## Sources (fetched; log in the scratchpad `web/requests.log`)
| source | URL | span kept | content | status |
|---|---|---|---|---|
| SGE Shanghai Gold Benchmark Price (SHAU) | POST https://www.sge.com.cn/graph/DayilyJzj | 2016-04-19..2024-12-31, 2,118 days | AM (早盘) and PM (午盘) price, CNY / g | used (AM) |
| SGE Au99.99 daily quote | POST https://www.sge.com.cn/graph/Dailyhq (instid=Au99.99) | 2016-12-19..2024-12-31, 1,951 days | open, close, low, high, CNY / g | used |
| SGE historical daily quotes (每日行情 articles) | https://www.sge.com.cn/sjzx/mrhqsj?p=N and /sjzx/mrhqsj/<id> | 2002-10..2023-12 (crawling) | every contract's OHLC, volume, OI, Au(T+D) delivery direction (交收方向) and volume | used for PRE and T+D |
| SGE daily quotes 2024 (new system) | https://www.sge.com.cn/sjzx/quotation_daily_new?start_date&end_date (1-month windows) | 2024 | same columns | to fetch for the 2024 T+D direction |
| SGE SHAU auction rounds (bid / ask volume per round) | /sjzx/shanghaiAuAuto | only ~2024 on | | **unusable** (no IS) |
| SNB sight deposits, weekly | https://data.snb.ch/api/cube/snbgwdchfsgw/data/csv/en | GI 2009-01-09..2024-12-27 (834 Fridays); TG / UEB from 2011-08 | CHF mn, dated Friday; the cube's PublishingDate is Monday 10:00 Zurich | used (GI) |
| SNB FX transactions | cube snbfxtr | quarterly from 2020-Q1, published ~1 quarter later | | **unusable** for 1-5 days |
| India: IBJA rates | ibjarates.com | history only via the paid API (indiagoldratesapi.com) | | **unusable** (payment) |
| India: MCX bhavcopy | mcxindia.com | 403 (Akamai) | | **unusable** |
| India / China: WGC GoldHub local premium | gold.org/goldhub/data/local-gold-price-premiumdiscount; xlsx and PDFs 403 without a login; chart API fsapi.gold.org robots.txt `Disallow: /` | | | **unusable** (login; robots) |

## Timestamp rule for the premium (fixed here, before any return)
Premium in bp: `prem = (P_SGE_CNY_per_g / (XAU_mid_USD_per_ozt x USDCNH_mid / 31.1034768) - 1) x 1e4`.
Both foreign legs are taken **as of the same instant** as the SGE price: quote as of T = close (last tick) of the M1
bar starting at T-1 min, within 10 minutes for XAU (3 for the check), 15 for CNH; no quote = no signal that day.
- **Au99.99 close: T = 07:30:00 UTC** (15:30 Beijing, the day-session close; China has no DST). Check done before
  this file (contemporaneous prices only, no returns): the sd of the day-to-day premium change is minimal at 07:30 UTC
  in each of 2017-18, 2019-21, 2022-24 (16.97 / 23.32 / 28.47 bp, rising on both sides), so the close is a 15:30 print.
- **AM benchmark: T = 02:15:00 UTC** (10:15 Beijing, the auction start). The same check is flat-bottomed at
  02:05-02:20 UTC in every group (13.9-14.2 / 19.1-19.5 / 24.5-24.6 bp).
- **PM benchmark: not used.** The check puts its best minute at 06:15-06:20 UTC in 2016-18 but 06:45-06:50 in 2019-21
  and ~07:00 in 2022-24, i.e. the clock of the published PM price is uncertain; a mistimed leg is an artefact source.
- USDCNH (offshore) converts the onshore price: the CNH-CNY basis becomes part of the premium (it is itself a
  segmentation price). IC USDCNH ticks 2016-24; Dukascopy USDCNH bid 2012-15 + half IC's 2016-17 median spread at
  that minute. XAU: IC M1 2016-24, Dukascopy 2004-15 (bid + IC 2016-17 spread profile, as round 31 G's `px.py`).
- Typical level (no returns): median premium ~+46 bp (AM) / ~+52 bp (close); the sd of its daily change 14-28 bp.

## Costs (IC, measured at the entry minutes, median full spread, bp)
- XAUUSD 07:45 UTC: ~0.73 IS / ~0.38 VAL (07:35 measured; 07:45 to be measured in the test from the actual bars);
  02:30 UTC measured in the test. Commission 0.6 bp round trip. Swap per night from `research/swing/rates.py`
  (`swap_frac_at`); round 31 G: long -0.5..-1.8 bp, short +0.1..+1.35 bp.
- XAGUSD 07:35 UTC: 3.5 IS / 3.8 VAL (+0.6).
- USDCHF 09:30 UTC: 0.31 IS / 0.24 VAL; EURUSD 09:30 UTC: ~0.0 (median zero-spread bars) + 0.6 commission per pair;
  FX swap from `swap_frac_at`.
- Executable: buy at the ask, sell at the bid of the fill minute (signal minute + 1), actual bars; variants +1 more
  minute and spread x1.5. PRE: IC 2016-17 spread by minute of day + 0.6 bp (convention of rounds 13-31).

## Power arithmetic (before any test)
HOLD = 1.73 years. LIVE needs per-trade net Sharpe x sqrt(n_HOLD) >= 3 (overlapping holds: use n / hold); DEMO needs IS
day-clustered t >= 2. Daily sd assumed from typical vol (not measured): gold ~90 bp, silver ~170, USDCHF ~55,
EURCHF proxy ~45.

| cell type | trades / yr | n HOLD | LIVE net edge needed | DEMO net edge (IS) | cost | implied mid for DEMO |
|---|---|---|---|---|---|---|
| gold 1 day, every SGE day | ~240 | ~415 | Sharpe 0.147 = **13 bp** | 2 / sqrt(1440) = 0.053 = 4.7 bp | ~1.4 + ~1 swap | ~7 bp = 0.08 sd |
| gold 3 days, daily entries (overlapping) | ~240 | ~140 eff. | 0.25 x 156 = **40 bp** | 2 / sqrt(480) = 0.09 x 156 = 14 bp | ~1.4 + ~3 | ~18 bp |
| gold 5 days, top tercile, <= 3 open | ~45 | ~80 | 0.34 x 200 = **67 bp** | 2 / sqrt(270) = 0.12 x 200 = 24 bp | ~1.4 + ~5 | ~30 bp |
| silver 3 days, daily entries | ~240 | ~140 eff. | 0.25 x 295 = **74 bp** | 0.09 x 295 = 27 bp | ~4.1 + ~3 | ~34 bp |
| SNB weekly, 1 day, top half | ~26 | ~45 | 0.45 x 55 = **25 bp** | 2 / sqrt(156) = 0.16 x 55 = 9 bp | ~0.9 | ~10 bp |
| SNB weekly, 4 days, top half | ~26 | ~45 | 0.45 x 110 = **49 bp** | 0.16 x 110 = 18 bp | ~1 + swap | ~19 bp |

Reading: a LIVE gold cell needs ~0.15 sd of next-day predictability from a public premium; the SNB cells cannot reach
LIVE at any plausible size (45 HOLD trades), DEMO at most. Literature: Qian (2020, *J. Economics and Finance*,
doi 10.1007/s12197-020-09517-5) finds SGE an isolated market with COMEX / LBMA the net spillover senders (the premium
should follow London, not lead it); Kügler (2020, Basel WP, doi 10.5451/unibas-ep76180) finds on weekly 2015-18 data
that a 1 % rise in sight deposits goes with a 0.41 % CHF **appreciation** in the same week (the SNB leans against the
wind: the contemporaneous sign is the reaction function, not the flow's impact). Priors: gold DEMO ~5 %, LIVE ~1 %;
SNB DEMO ~3-5 %, LIVE ~0 (power).

## Family S: onshore gold premium (SGE) -> XAUUSD / XAGUSD
Mechanism: China imports gold under PBoC quotas through Hong Kong / Switzerland; a premium above its recent level
means onshore demand exceeds what the licensed importers are currently bringing in. The arbitrage is capped by
quotas, so it is met over days by importers buying in London / Zurich (and the PBoC widening quotas), i.e. buying
pressure in the international market after the premium rises. Side fixed by this mechanism: **premium above its
recent level -> long gold; below -> short**. (Opposite story, not a cell: Chinese buyers buy dips, so the premium rises
after London falls; if gold then mean-reverts, the cell would show reversal, not the flow. Checked by the control below.)

Signal: `d_t = prem_t - mean(prem over the previous 20 SGE trading days)` (needs >= 15 of them). Side = sign(d_t).
Entry on SGE day t (IC weekdays only) at the stated clock, fill one minute later; exit at the same clock k IC trading
days later. Days without an SGE quote (Chinese holidays) have no signal.

| cell | signal | entry (UTC) | exit | positions | symbol |
|---|---|---|---|---|---|
| S1 | Au99.99 close premium d_t, every day | 07:45 (fill 07:46) | +1 IC trading day 07:45 | 1 | XAUUSD |
| S2 | same | 07:45 | +3 trading days 07:45 | <= 3 (daily entries) | XAUUSD |
| S3 | same, only days with |d_t| >= IS (2016-21) 2/3 quantile of |d| (signal distribution only) | 07:45 | +5 trading days 07:45 | <= 3: a signal is skipped when 3 are open | XAUUSD |
| S4 | AM benchmark premium d_t (benchmark from 2016-04-19) | 02:30 (fill 02:31) | +1 trading day 02:30 | 1 | XAUUSD |
| S5 | Au99.99 close premium d_t | 07:45 | +3 trading days 07:45 | <= 3 | XAGUSD |

Eras: S1-S3, S5 PRE 2012-2015 (Au99.99 closes from the SGE archive, Dukascopy XAU / XAG and USDCNH; silver PRE uses
Dukascopy XAG, reliable from 2008), IS 2016-21, VAL 2022-24. S4: IS 2016-05..2021, VAL 2022-24, no PRE.

## Family T: Au(T+D) delivery direction (交收方向) -> XAUUSD
Mechanism: on SGE's deferred contract the deferral fee is paid by the side whose delivery requests fall short: when
longs asking to take metal exceed shorts offering it (onshore physical shortage), shorts pay longs (空支付给多).
A published, daily fact of onshore physical tightness; with import quotas the shortage is met abroad, as for S.
Side fixed: **空支付给多 (short pays long) -> long gold; 多支付给空 (long pays short) -> short; anything else (超期,
blank, equal) -> no trade.** Published with the day's quotes after the 15:30 Beijing close.

| cell | signal | entry | exit | eras |
|---|---|---|---|---|
| T1 | direction on SGE day t | 07:45 UTC t (fill 07:46) | +1 trading day 07:45 | PRE 2004-15 (no FX leg needed; Dukascopy XAU, bid only before 2010 with the PRE cost convention), IS, VAL (2024 from the new daily-quote page) |
| T2 | same | 07:45 | +3 trading days 07:45 (<= 3 open) | same |

If the archive's labels differ from the two strings above, the mapping keeps the economic meaning (short pays long =
long gold) and the change is noted in STREAM_S.md before any return.

## Family N: SNB weekly sight deposits (GI, domestic banks) -> USDCHF, EURCHF proxy
Mechanism: SNB FX purchases are paid in sight deposits; the SNB intervened in long, persistent campaigns (2009-10,
2011-15 floor, 2015-17, 2020) and sold FX in 2022-23. A weekly rise in GI is the public footprint of last week's
buying; persistence means more buying of EUR / USD against CHF in the coming days. Side fixed: **GI up -> CHF weaker:
long USDCHF, long EURCHF proxy; GI down -> short both.** (Kügler 2020's contemporaneous opposite sign is the
reaction function; a predictive test after publication is not in that paper.) Caveats: GI also moves with SNB bills
(2008-11, 2022-), repo absorption since 2022-09 and the 2019-11 / 2022 tiering changes, so VAL is a noisier proxy.

Publication: the cube's PublishingDate is Monday 10:00 Zurich (= 09:00 UTC winter, 08:00 UTC summer); assumed for every
year (assumption; robustness entry on Tuesday). Entry: the Monday after the Friday value at **09:30 UTC** (fill
09:31); if that Monday is a Swiss national holiday (Easter Monday, Whit Monday; `holidays` CH) or has no quote, the
next weekday. Δ_w = GI_w - GI_{w-1} (CHF mn). Threshold: |Δ_w| >= IS (2016-21) median |Δ| (signal distribution only).
EURCHF proxy = EURUSD leg + USDCHF leg, same side, equal notional (return = sum of the two leg returns, costs of both).

| cell | signal | symbol | exit |
|---|---|---|---|
| N1 | sign Δ_w, top half | USDCHF | +1 trading day 09:30 UTC |
| N2 | same | USDCHF | +4 trading days 09:30 UTC (Friday) |
| N3 | same | EURCHF proxy | +1 day |
| N4 | same | EURCHF proxy | +4 days |
| N5 | sign of the 4-week sum Σ Δ_{w-3..w}, |sum| >= IS median | USDCHF | +4 days |
| N6 | same | EURCHF proxy | +4 days |

Eras: PRE 2009-2015 (Dukascopy USDCHF / EURUSD M1, PRE cost convention), IS 2016-21, VAL 2022-24. Trades whose hold
spans 2015-01-15 (floor removal; quotes gapped and unexecutable) are excluded from the primary PRE number and
reported separately.

## Checks per cell (not extra cells)
- Mid and net by era and year; day-clustered t (1-day cells), Newey-West t with lag = hold for overlapping cells.
- Dose response: OLS of the signed trade return on d_t / its IS sd (S) or Δ_w / its IS sd (N).
- Momentum / reversal control (S, T): joint OLS of the trade return on sign(d_t) and the sign of the gold return over
  the 24 h ending at the premium minute; the cell counts as the premium mechanism only if the premium coefficient
  keeps >= 2/3 of its size and its sign. For N: the USDCHF return over the week ending Friday.
- Random-entry control: >= 200 circular shifts of the signal series against the trade dates (shift >= 20 SGE days /
  >= 8 weeks), side recomputed from the shifted signal, same clock and hold; percentile of the actual net mean.
- Spread x1.5 and +1 minute on both fills; for N also the Tuesday entry.
- C3 daily-P&L correlation for any survivor.

## Multiple testing
13 declared cells (S1-S5, T1-T2, N1-N6), sides fixed. Chance benchmark: best one-sided t of 13 independent nulls has
median ~1.65 and 95th percentile ~2.65 (cells within a family are correlated, so this is conservative for the max).

## Not declared (and why)
- PM benchmark: uncertain clock (see above).
- SHAU auction bid / ask imbalance: only from ~2024.
- Indian premium: no free source reachable (table above): a user decision (free WGC GoldHub login; or the paid IBJA API).
- BoJ current-account / operations: the balance moves with JGB purchases and Treasury flows; Japan's FX intervention
  is financed and recorded by the MoF (round 31 J has the MoF intervention record), so no new mechanical flow.
- SNB quarterly FX transactions (2020-): published a quarter later; nothing to trade at 1-5 days.
- Silver onshore premium: China levies VAT on imported silver, so the Ag(T+D) "premium" is mostly tax; not declared.

## Addendum 2026-10-27 20:05 UTC (before any T return; S, N and S4 results already computed)
- The SGE archive prints the T+D direction as 空支付多 / 多支付空 (no 给), sometimes with a trailing `&nbsp;`; mapped by
  meaning as declared (空支付多 = short pays long = long gold).
- The archive has the direction column only from **2014-09** (no column 2012-01..2014-08; the 2002-2011 articles are
  not needed). T's PRE is therefore 2014-09..2015-12 only (~1.3 years), not 2004-15 as declared.
- 2024 direction from `/sjzx/quotation_daily_new` (one-month windows), cut at 2024-12-31.
