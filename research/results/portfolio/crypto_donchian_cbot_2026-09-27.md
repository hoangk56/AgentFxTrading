# CryptoDonchianBot — cTrader build and backtest (2026-09-27)

`cBot/CryptoDonchianBot.cs` implements research candidate C1 (`swing_lab_v2_2026-09-27.md`, registered in
`prereg_swing_v2.md`): crypto Donchian breakout on H4, BTCUSD and ETHUSD, one bot per symbol. **C1 failed its
pre-registered holdout (mean R -0.025), so this bot is a forward test, not an adopted strategy.** The cTrader backtest
reproduces the research engine trade for trade, holdout failure included.

## The rule (registered, unchanged)

- UTC H4 bars (00:00, 04:00, ... UTC). Buy on a close above the prior 55-bar high, sell on a close below the prior
  55-bar low; every qualifying bar is an entry, so a persistent breakout stacks up to 3 positions (the bot's cap).
- Exit on the first of: an H4 close below the prior 20-bar low (shorts: above the 20-bar high), the stop at
  3 x ATR20(H4) from the fill, 5 days after entry.
- Lot: default $ risk x clip(breakout distance in ATR / median of this symbol's earlier breakout distances, 0.5, 2);
  1x until there are 10 earlier breakouts. The account balance is never read.

## What the cBot had to add

- **UTC H4 bars built from H1.** IC's own H4 bars open at 21:00/22:00 UTC (the broker's server day). The first
  build used them; the research engine on those phases gives IS/VAL R +0.19..+0.30 (the rule holds) but HOLD moves
  from -0.025 (0 h, the registered phase) to +0.117 (1 h), +0.077 (2 h), +0.094 (3 h). The phase is part of the
  registered rule and was not picked on HOLD, so the bot aggregates H1 bars into UTC buckets; its chart is `h1`.
  (Seeing that HOLD depends this much on the bar phase is itself a sign that C1's HOLD number is noisy.)
- **Stub bars not merged.** The research merged buckets with < 30 % of the usual minutes (IC's Saturday 20:00-21:00
  hour before a 3-hour break, 1.4 % of bars) into the next bar; the bot does not. Research engine without the merge:
  IS +0.264 / VAL +0.227 / HOLD -0.021 R (vs +0.276 / +0.227 / -0.025).
- **Breakout median from the loaded history.** The research used an expanding median since 2018; the bot loads
  20,000 H1 bars (~5,000 H4, ~2.3 years) at start and keeps adding. Research engine: expanding, trailing
  100/200/400-breakout and a fixed 0.48 median all give the same R per era and within 5 % of the $.
- **Spread cap = 10 % of the stop distance** (crypto pip sizes differ by broker). Spread at entry was 0.4-2.6 % of
  the stop in 2024-2026 (99th pct < 6 %), but ETHUSD quoted 15-35 % of the stop in 2018-2020; the cap skips those.
- **Entry window 30 min** after the bar close (retries every 30 s on a wide spread or a failed order); one attempt
  per signal bar, History-checked across restarts. Exits scan every bar closed since the entry, so a restart catches
  an exit it slept through.
- **5-day limit across market breaks.** IC's crypto closed every weekend until April 2024 and still pauses ~1 h on Friday
  and ~3 h on Saturday nights. A position whose 5 days end inside a break could only close at the reopen (up to
  168 h in the first backtest). The bot now closes it in the last 5 minutes before such a break, as the research
  closed at the last minute before the deadline. It reads the symbol's trading sessions, so it works live; a
  backtest applies today's sessions to every year and still shows the 2018-2024 weekend overruns.
- **Kill switch, off by default** (`KillSwitchTrades`, `KillSwitchMinR`): stops new entries when the mean R of the
  last N closed trades is below the threshold. The research suggested N = 100, R < 0. On 2018-2026 (research engine,
  after the fact) that would have stopped ETHUSD in January 2020 and skipped 513 trades worth +$12,032 (R +0.127),
  and BTCUSD in April 2025 (skipped 139 trades, +$1,602, R -0.087); N = 50 or 150 are no better, and a
  pause-and-resume variant on paper trades lowers HOLD $ as well. It is a guard, not an edge, so it is available and
  documented but not on.

## How it was run

- Build: `ctrader-console create cbot CryptoDonchianBot` + `build` in an isolated home on the VPS
  (`~/donchian-build/home`), not the live `~/ctrader` nor the repo's `cBot/`. 0 errors; only the usual CS1701
  warnings. The 2018-2026 runs used the first UTC-bar build (before the pre-break close); the 2024-2026 rerun used
  sha256 `90ab3c78…`; the committed source (`53689d36…`, also built with 0 errors) differs from it only in comments
  and the `RiskPerTradeMoney` default (50 -> 100, which every run passed explicitly).
- Backtest: same container spec as the Backtest page (bridge network, 1 GB / 2 CPU, tick cache), `backtest
  --data-mode=ticks --balance=10000 --commission-auto --period=h1`, `--RiskPerTradeMoney=100.0` (the preset and the
  research's $ risk), every server URL locked to `http://127.0.0.1:9/disabled`, `--CommandPollMs=0`, demo account
  10115236. One continuous run per symbol 2018-01-01 .. 2026-09-26; ETHUSD also with `--MaxSpreadStopFraction=1.0`
  (no cap) to compare with the research. Scripts and raw reports: `~/donchian-build` on the VPS; every trade:
  `crypto_donchian_cbot_trades.csv` (git-ignored).
- The research's side: `trades_C1_crypto_donchian_h4.csv` (the registered run). "Same signal bar" = both took the
  trade of that H4 bar and side; "same sign" = both won or both lost it.

## Results ($100 default risk, 2018-01 .. 2026-09)

### BTCUSD

| year | cTrader n | net $ | R | research n | research $ | research R | same signal bar | same sign |
|---|---|---|---|---|---|---|---|---|
| 2018 | 72 | +3,415 | +0.378 | 71 | +3,838 | +0.365 | 69 | 65 |
| 2019 | 58 | +5,564 | +0.715 | 56 | +5,037 | +0.603 | 55 | 51 |
| 2020 | 70 | +7,705 | +0.731 | 68 | +7,416 | +0.783 | 67 | 64 |
| 2021 | 73 | -685 | -0.002 | 70 | -22 | +0.098 | 69 | 66 |
| 2022 | 60 | +1,527 | +0.149 | 60 | +1,555 | +0.151 | 59 | 56 |
| 2023 | 57 | +5,608 | +0.851 | 57 | +4,617 | +0.648 | 55 | 55 |
| 2024 | 85 | +1,656 | +0.136 | 85 | +1,627 | +0.145 | 85 | 85 |
| 2025 | 92 | -87 | -0.170 | 92 | -380 | -0.176 | 92 | 92 |
| 2026 (to Sep) | 71 | +808 | -0.126 | 71 | +760 | -0.118 | 71 | 71 |
| **all** | **638** | **+25,511** | **+0.257** | 630 | +24,448 | +0.244 | | |

IS 2018-21 R +0.439 (t 3.9) · VAL 2022-24 R +0.342 (t 2.7) · **HOLD 2025-26 R -0.151 (t -1.6), net +$721** —
the research's HOLD was R -0.151, +$380. Max drawdown $2,361; 44 % winners; exits: 373 at 5 days, 219 stops,
46 channel exits.

### ETHUSD

| year | cTrader n (cap 10 %) | net $ | R | cTrader n (no cap) | net $ | R | research n | research $ | research R |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 37 | +2,352 | +0.388 | 78 | +4,561 | +0.414 | 72 | +4,494 | +0.391 |
| 2019 | 1 | -51 | -1.007 | 55 | -286 | -0.159 | 53 | -664 | -0.145 |
| 2020 | 9 | +425 | +0.554 | 77 | +792 | +0.149 | 77 | +1,334 | +0.090 |
| 2021 | 87 | +1,406 | +0.035 | 87 | +1,408 | +0.035 | 86 | +1,835 | +0.061 |
| 2022 | 67 | +2,495 | +0.200 | 67 | +2,495 | +0.200 | 67 | +2,053 | +0.165 |
| 2023 | 57 | +2,106 | +0.134 | 57 | +2,106 | +0.134 | 56 | +1,434 | +0.062 |
| 2024 | 88 | +2,992 | +0.266 | 88 | +2,992 | +0.266 | 88 | +2,898 | +0.239 |
| 2025 | 84 | +1,590 | +0.189 | 84 | +1,590 | +0.189 | 84 | +1,646 | +0.193 |
| 2026 (to Sep) | 55 | +801 | +0.011 | 55 | +801 | +0.011 | 55 | +833 | +0.017 |
| **all** | **485** | **+14,116** | **+0.170** | **648** | **+16,459** | **+0.153** | 638 | +15,863 | +0.134 |

No cap: IS R +0.128 · VAL +0.209 · HOLD +0.119 (research +0.113 / +0.168 / +0.123). The 10 % cap changes nothing
after 2020. Max drawdown $2,715.

### Both bots, HOLD 2025-01 .. 2026-09

302 trades, net +$3,112, mean R -0.027 — the research's -0.025. C1's holdout verdict does not change in cTrader.

### Why cTrader and the research differ a little in 2018-2024

- Positions whose 5 days ended on a weekend (crypto closed Friday night to Sunday night at IC until April 2024) were
  closed by the research on Friday and by the backtest at the Sunday reopen (see "5-day limit" above; the backtest
  cannot know those old sessions). 126 BTCUSD and 123 ETHUSD (no cap) trades ran past 120 h, all but one (August 2025)
  before April 2024. They account for most of the yearly gaps: BTCUSD 2019 +$690 of +$526, 2021 -$719 of -$664, 2023 +$843
  of +$991; ETHUSD 2023 +$831 of +$672. Over 2018-2026 they net +$1,641 on BTCUSD and -$66 on ETHUSD.
- Stub bars (above) and cTrader's own fills.

## Fix check (after the break rule, 2024-01 .. 2026-09)

Rebuilt with the pre-break close and rerun on 2024-01-01 .. 2026-09-26 (source sha256 `90ab3c78…`):

| | n | net $ | R | research n | research $ | research R |
|---|---|---|---|---|---|---|
| BTCUSD 2024 | 85 | +1,590 | +0.136 | 85 | +1,627 | +0.145 |
| BTCUSD HOLD 2025-26 | 163 | +754 | -0.150 | 163 | +380 | -0.151 |
| ETHUSD 2024 | 88 | +2,940 | +0.266 | 88 | +2,898 | +0.239 |
| ETHUSD HOLD 2025-26 | 139 | +2,498 | +0.118 | 139 | +2,479 | +0.123 |

Every signal bar the research traded in 2025-26 was traded by the bot (163/163, 139/139), with the same win/loss
on 301 of 302. The break rule closed 6 positions at 21:54 UTC on a Saturday (4 BTCUSD, 2 ETHUSD). 14 positions
still ran past 120 h: 13 in January-March 2024, when IC still closed crypto for the weekend (the last closure was
the weekend of 2024-04-06; the backtest only knows today's sessions), and one BTCUSD long in August 2025 whose
deadline fell in an unscheduled 15-hour gap in IC's prices (2025-08-15 22:15 -> 2025-08-16 13:35 UTC), which no
schedule predicts. IC's prices also stopped for 6-10 hours on 2024-05-04, 2024-06-08, 2025-07-05 and 2025-11-21/22;
a position due in such a gap closes at the first price after it. Longest hold since April 2024: 133.6 h, that one trade.

## Before it trades

1. Merge the branch and pull on the VPS; build the `.algo` (`scripts/install.sh` or the README's step 5), restart
   `agentfx.service` so the dashboard knows the `donchian` cells and the Backtest page supports them.
2. Create BTCUSD and ETHUSD from Setup Instances (column "Crypto Donchian") on the **demo** account. $100 default
   risk: BTCUSD's minimum 0.01 BTC already risks ~$30-40 at today's stop, so a much smaller default would skip the
   weak breakouts (the lot rounds down). Worst case per bot: 3 positions x 2x = $600 at risk.
3. Watch the fills at the UTC H4 closes and the Friday/Saturday pre-break closes; compare with this backtest.
4. Decide the kill switch before any live money: with the research's N = 100 it would have stopped ETHUSD in 2020.
