# Round 66: effects that live inside the first minute (F0, G0, A3, B2, O2, N0, A4, A5), 2026-11-01

Shared brief: [round66_fast_execution/BRIEF.md](round66_fast_execution/BRIEF.md) (12:21 UTC; streams added as slots
freed). Question: are the effects that rounds 64-65 found inside the first minute capturable by a bot that reacts at
the bar close or within seconds? F-family rules are forward-only (F's HOLD is known).

## Answer first
- **No new LIVE candidate on a registered holdout.** F0 passes every LIVE bar on IS / VAL and is registered for a
  FORWARD test from 2026-10-30 ([PREREG_F0](round66_fast_execution/F0/PREREG_F0_bar_close_fade.md); ~333 events,
  ~3.5 months; F kept ~15 % of its VAL size in HOLD, so the forward test may lack power).
- The Upbit KRW-listing notice is the one public announcement that moves prices within seconds (round 65 A2-D5L passed
  HOLD as DEMO, t 3.11). OKX / Bybit listing announcements do not (O2); Bithumb has no allowed notice history (B2);
  the Binance-spot (A3) and Bybit-perp (A4) versions have no IS events, though A4's 7 VAL events are +5,029 bp each.
- Altcoin catch-up after BTC shocks at seconds (G0) and the new-perp launch fade (N0) fail.

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| F0 | F's wick fade entered at the first trade after the event bar's close (and +1 / +3 s) | **LIVE bars on IS / VAL** (E0 H60: IS +319.5 bp t 4.90, VAL +339.2 t 4.56; +1 s, +3 s, $10k fills all pass); registered FORWARD only | [STREAM_F0.md](round66_fast_execution/F0/STREAM_F0.md), [PREREG_F0](round66_fast_execution/F0/PREREG_F0_bar_close_fade.md) |
| G0 | Laggard altcoins after real-time BTC shocks, entered 1-3 s after detection | none: best IS +2.4 bp/shock t 0.48; +17 / +12 bp recovery in 60 s vs 10 bp taker fees | [STREAM_G0.md](round66_fast_execution/G0/STREAM_G0.md) |
| A3 | Upbit notice -> Binance SPOT for coins without a Binance perp | none: 5 IS / 0 VAL events (from 2022 Binance always had a perp, or no / too young a spot pair) | [STREAM_A3.md](round66_fast_execution/A3/STREAM_A3.md) |
| B2 | Bithumb listing notices at seconds | not testable: feed.bithumb.com robots 403, the keyless API keeps only the latest ~20 notices | [STREAM_B2.md](round66_fast_execution/B2/STREAM_B2.md) |
| O2 | OKX / Bybit listing announcements -> Binance perp at seconds | none: median +2 bp at +5 s; holding to the venue's own opening gives IS +107 (t 1.88) / VAL +166 (t 1.94), speed irrelevant | [STREAM_O2.md](round66_fast_execution/O2/STREAM_O2.md) |
| N0 | Fade the first-minutes move of a new Binance perp | none: 7 of 8 cells lose in IS; big early moves continue | [STREAM_N0.md](round66_fast_execution/N0/STREAM_N0.md) |
| A4 | Upbit notice -> Bybit perp for coins without a Binance perp | not gradable: IS 0 events; VAL 7 events +5,029 bp, t 3.08, 7 / 7 positive; on Bybit the move keeps going after 5 s | [STREAM_A4.md](round66_fast_execution/A4/STREAM_A4.md) |
| A5 | Upbit notice -> Binance perp listed 1-7 days before | none: 0 events; Upbit lists first and Binance opens the perp a median ~0.4 day later (13 cases); A's day-precision perp check let ARB (6.42 d) into A2's VAL set | [STREAM_A5.md](round66_fast_execution/A5/STREAM_A5.md) |

## What a user decision could unlock
- An Upbit-notice bot: A2-D5L (registered DEMO, HOLD t 3.11) needs notice detection within ~3 s; the same bot could
  log A4-type events (Bybit perp when Binance has none) as a forward-only, new-era observation (IS has no events, so
  it can never pass the standard bars on history).
- A bar-close bot on Binance 1m klines for F0's forward test (the research forward test runs on public data anyway).

## Pitfalls found this round
- Binance 1m kline opens equal the previous close in ~21.5 % of F's events: use the first aggTrade after the close.
- OKX announcements before 2023-03 carry the migration date in `pTime`; the post time is `businessPTime`. Bybit's
  `dateTimestamp` is author-filled (half at :00); `publishTime` exists only from 2024-03.
- `pgrep -f <script>` inside a wait loop matches the loop's own command line: use a distinctive path pattern.
- Bybit public trade dumps (public.bybit.com/trading, robots 404) are ~80 MB a day for BTC; keep only the windows.

## Standing after round 66
C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L. Forward-registered LIVE candidate: F0.
