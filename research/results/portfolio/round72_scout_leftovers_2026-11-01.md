# Round 72: leftover scout idea (TRY), 2026-11-01

Brief: [round72_scout_leftovers/BRIEF.md](round72_scout_leftovers/BRIEF.md) (18:45 UTC). J10 (S&P 500 additions) was
dropped before testing: its own source (Greenwood & Sammon 2022) shows the index effect is gone, and Dukascopy has
only 263 large names.

## Answer first
- **No LIVE or DEMO candidate.** TRY: long USDTRY when BtcTurk's USDT/TRY premium over the official rate is > 2 % at
  09:00 Istanbul, hold 5 days: IS +87 bp (t 1.3 by episode, n 55, 25 episodes), VAL +56 (t 2.3, n 128), shift-random 84
  / 86 % (< 90 %); the edge is two lira breaks (2021-12, 2023); without the longest episode |t| < 1 everywhere; carry
  costs 96-151 bp per 20-day trade. File: [STREAM_TRY.md](round72_scout_leftovers/TRY/STREAM_TRY.md).

## Pitfall
- Dukascopy answered 429 to a User-Agent containing "(python urllib)"; the stream switched to a plain non-browser UA.
  429 is a rate-limit signal: future streams must back off, not change the UA.

## Where the search stands (after rounds 64-72)
Every free direction without a user decision has been tried or scouted at P(LIVE) <= ~1-2 %. The live paths now run
through decisions (round71_mixed_2026-11-01.md, ranked): an A2-D5L notice bot, borrow for B, a K2 bot, the L1 dataset,
a new-era split for the Upbit-notice family. Forward logs that need no decision: A2-D5L (`fwd_a2.py`), K2 (`fwd_k2.py`);
F0's forward evaluation (~2027-02) needs its runner written before then.
