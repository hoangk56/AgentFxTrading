# Round 74: Telegram channel history as second-precise announcement times (TG2, BL, BD, CL, WA), 2026-11-02

Brief: [round74_tg_stamps/BRIEF.md](round74_tg_stamps/BRIEF.md) (14:19 UTC). The user asked on 2026-11-02 to keep
researching until a LIVE algorithm exists. Idea of the round: public Telegram channels keep full history with
second stamps in the keyless preview `t.me/s/<channel>?before=<id>`, so they can time announcements that rounds 63 D,
66 B2 and 71 could not (Binance `/bapi/` is robots-banned, Bithumb keeps ~20 notices).

## Answer first
- **No LIVE or DEMO candidate.** One HOLD was opened, the user-approved new-era test of BD S-24h, and it failed.
- **Main finding:** the relay channels post minutes **after** the price moves, unlike @upbit_news, which posts before
  the jump.
  - @binance_announcements posts listings a median 246 s after the perp's half-move in VAL (84 s in 2021).
  - Delistings come ~2-7 min after Binance itself from 2023 on.
  - @coin_listing posts Coinbase / Bithumb listings 30-200 s after the move starts.
  - So these channels can time slow drifts, not seconds edges.
- **One strong VAL-only effect, BD S-24h:** short the coin's perp after a Binance spot-delisting notice and hold 24 h.
  - VAL: +1,418 bp a trade, t 3.60, n 14 on 7 days.
  - Beats 100 % of random sets; costs x1.5 +1,413; +10 s late +1,399; power at VAL size 3.6.
  - The edge is the 24 h drift: entered at N + 60 min it still makes +738 bp.
  - It cannot be graded on the standard bars. IS 2020-21 has 0 trades, because no delisted coin had a perp then.
    Grading it needs a new-era split, which is a **user decision**.
- **A2-D5L capture (TG2):** the user-account route passes only with active polling. `tg_pull.py` is now deployed
  (user-approved); its first post was received in 2.1 s.
  - The passive MTProto push is late by documented design: Telegram "may stop sending updates" for large channels,
    and a client must poll getChannelDifference itself.
  - Every keyless t.me form lags 4-63 s.
  - `tg_pull.py` (active getChannelDifference every 2 s) is written and tested, but has never talked to Telegram.
  - Deploying it on agentFx is a **user step**: [TG2/USER_STEPS_TG2.md](round74_tg_stamps/TG2/USER_STEPS_TG2.md).

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| TG2 | A <= 3 s capture route for @upbit_news (A2-D5L's promotion gate) | not passed yet. Clocks fine (agentFx chrony 11 µs). Passive push late by design. Keyless forms 4-63 s. Active MTProto pull `tg_pull.py` ready, 10 tests pass (`research/tests/test_tg_pull.py`), not deployed | [STREAM_TG2.md](round74_tg_stamps/TG2/STREAM_TG2.md) |
| BL | Binance spot listing -> long the coin's existing perp at post + 5 s (L1). Binance perp launch -> long Binance spot (L2) | **none, not gradable**. L1: 4 IS events < gate 20; VAL spot-open exit +542 bp t 1.94 but random 59 %, 2022 negative, power 1.3-2.4; the post comes a median 246 s after the half-move. L2: 73 posts 2019-21, 1 in 2022, 0 after; IS +43 bp t 2.43 at 5 min, no VAL events | [STREAM_BL.md](round74_tg_stamps/BL/STREAM_BL.md) |
| BD | Binance delisting / monitoring-tag notices -> short the perp at post + 5 s | **none at the standard bars** (IS 0 trades). VAL S-24h +1,418 bp t 3.60 n 14 (7 days, 13 of them in 2024); MT-24h (monitoring tag) +377 bp t 3.59 n 15 (5 days); perp delisting 4 emergency events | [STREAM_BD.md](round74_tg_stamps/BD/STREAM_BD.md) |
| CL | Other-venue listings via @coin_listing / @newlistingsfeed (Bithumb KRW, Coinbase, Robinhood) -> Binance perp at post + 5 s | **none**: best IS t 1.32 (Bithumb 60 m) < random p95 1.46; VAL +24 / +5 bp. The coin was already +2 % before post + 5 s in 100 % of Coinbase and 77-79 % of Bithumb events. Bithumb coverage only 2020-21-08 and 2024-07..12 | [STREAM_CL.md](round74_tg_stamps/CL/STREAM_CL.md) |
| WA | Whale Alert transfers / mints -> BTC / ETH perp 5-60 min | **none**: 42 cells, IS best t 0.66 (p95 null 2.20), 38 / 42 IS cells negative. VAL is ~+1-2 bp gross against a 12 bp round trip. Mints and burns follow price (as in round 53) | [STREAM_WA.md](round74_tg_stamps/WA/STREAM_WA.md) |

## BD S-24h new-era test (user-approved 2026-11-02, HOLD opened once 16:08 UTC)
Registration: [PREREG_BD_S24h.md](round74_tg_stamps/BD/PREREG_BD_S24h.md) (16:07:59 UTC). The rule was frozen from the
VAL run; a dry run on VAL reproduced every number. Result: [hold_results.txt](round74_tg_stamps/BD/hold_results.txt).

**FAIL.** The pass bar was net > 0, t >= 2.5, x1.5 > 0 and +10 s > 0.

| HOLD 2025-01..2026-10 | value |
|---|---|
| n (days) | 57 (18) |
| net / median per trade | +547 / +1,190 bp |
| day-clustered t | **0.98** |
| win rate | 74 % |
| costs x1.5 / +10 s / BTC-hedged | +542 / +538 / +481 |
| years | 2025 +1,026 (24), 2026 +199 (33) |
| leave-one-day-out t | 0.59-2.30 |
| random | beats 100 % of random sets, but event t beats only 64 % of random t |

- Most delisted coins keep falling for 24 h, but squeezes make the tail: ALPACA -14,897 bp, VIC -12,294, CHESS -3,269.
  This is the same shape round 60 found for shorting new listings.
- HOLD has 4x VAL's trades, yet its Sharpe per trade is 0.17 against VAL's 0.96.
- Dropped for good: no re-registration, and no stop chosen after seeing HOLD.

## What a user decision could unlock (ranked)
1. **Deploy `tg_pull.py` on agentFx** (A2-D5L, DEMO with HOLD t 3.11).
   - Steps: copy the script and a copy of the session, run it with an end time; [USER_STEPS_TG2.md](round74_tg_stamps/TG2/USER_STEPS_TG2.md).
   - Pass: >= 80 % of new posts received <= 3 s over >= 5 posts (~1-2 days).
   - Risk: it shares the login key with tg_push. Telegram revokes a key it sees from two IPs at once; both copies run
     on one IP, so this is not expected.
   - If it passes, A2's promotion needs real fills (Binance USDT-M key with trading rights: user decision).
2. Done: the new-era test of BD S-24h was approved and **failed HOLD** (section above). MT-24h (the monitoring tag)
   has the same squeeze risk; it is not recommended.

## Pitfalls found this round
- Telegram relay stamps are post time, not the venue's time. Measure the burst against the stamp before any rule:
  only @upbit_news leads its price jump. Binance's own channel lags its site by minutes from 2023.
- The t.me/s preview is stale for 4-60 s even with `cache-control: no-store` and fresh URLs. A keyless poller cannot
  pass a 3 s gate.
- The preview shows the original post time but the current text. Drop edited posts or show the result without them
  (BD S-24h with edited posts kept: +1,180, t 2.91).
- fapi aggTrades REST serves only the last 2 days: use data.binance.vision daily files. OKX daily files are UTC+8 days.
- @coin_listing has almost no non-Upbit / non-Binance posts from 2023-05 to 2024-12. @binance_futures is not official.
- Network: one shared t.me lock (round74_tg_stamps/coord/tg.py, 1.5 s gap) carried ~5,000 requests across 5 streams
  with no 403 / 429. The Mac had occasional read timeouts, so `coord/pull_loop.sh` retries.

## Standing after round 74
- C3 is the only LIVE algorithm.
- DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L. Forward-registered: F0 (16 events so far, evaluation 2027-01-31).
- Forward logs 2026-11-02: A2 0 events, K2 1 event (+2,238 bp).
- `tg_pull.py` runs on agentFx since 15:57 UTC; it ends 2026-11-09T00:00Z.
  - The user approved the deploy and let Claude install it.
  - First post (2057): pull +2.1 s, passive push +22.0 s, t.me/s +33.8 s.
  - The A2 capture gate is graded after >= 5 posts.
  - Read: `ssh agentFx 'cd /home/forge/tg_capture_a2 && venv-push/bin/python -I tg_pull.py report'`.
  - Stop: `touch STOP_PULL` in that folder.
