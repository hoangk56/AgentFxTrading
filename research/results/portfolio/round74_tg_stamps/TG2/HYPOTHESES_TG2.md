# HYPOTHESES_TG2: a <= 3 s capture route for @upbit_news (A2-D5L promotion gate)

Written 2026-11-02 14:23 UTC (`date -u`), before any TG2 fetch. Engineering and latency only: no P&L, no orders, no
prices, no HOLD.

## Question
A2-D5L's LIVE promotion needs the KRW-listing notice seen <= 3 s after N on >= 80 % of live notices
(PREREG_A2_D5L.md, "Promotion to LIVE"). @upbit_news stamps 100 % of 2026 KRW listings <= 1 s after N (round 73 TG),
so the capture route itself must show a post <= ~2 s after its Telegram post time.

Forward evidence at 14:15 UTC (agentFx, read only): t.me/s poller at 1.5 s, 7 posts, seen - post median 22.5 s,
p90 50.6 s; Telethon passive push (`events.NewMessage`), 2 posts at +58.4 s and +11.0 s. Both fail by a wide margin.

## Hypotheses
- H0 (clock): the lags are not clock skew. Test: agentFx `chronyc tracking`, Mac `sntp` offset. Skew > 0.5 s would
  invalidate the lags; skew < 0.1 s is irrelevant at a 10-50 s scale.
- H1 (passive MTProto): Telegram does not push every new post of a large broadcast channel to every subscriber at
  once; a client that does not have the chat "open" gets the post late (on its next getDifference / a later
  push). An active client that calls `updates.getChannelDifference` (or `channels.getMessages` for the next id) every
  ~2 s sees the post within ~1 poll period + RTT. Prediction: active pull delay - post time <= 3 s on >= 80 % of posts;
  passive push (same posts) stays > 3 s on most.
- H2 (keyless forms): the t.me/s top page is served from a cache that refreshes every tens of seconds. Other public
  forms (per-post embed `t.me/upbit_news/<id>?embed=1`, `t.me/s/upbit_news?after=<id>`, `t.me/s/upbit_news?before=<id>`,
  `t.me/s/upbit_news/<id>`) may be built from a different cache key and show the post sooner. Prediction (weak):
  at least one form shows new posts earlier than the top page; whether any reaches <= 3 s is open.

## Decision rule (fixed now)
- Route **passes** if >= 80 % of new posts are first seen <= 3.0 s after their Telegram post time (seen - post time,
  stamps whole seconds, so the true delay is 0-1 s less; I do not subtract it). With few posts (n < 5) the result is
  reported as "indicative", not a pass.
- The gate is about KRW listings, but any channel post goes through the same delivery path; all posts count (KRW
  listings are ~1 in 10 posts, too rare to wait for).
- A route that needs an account (MTProto) is a user-run route on agentFx; keyless routes are tested from the Mac only.

## Routes and periods
- MTProto active (TG2/code/tg_pull.py, user deploys it on agentFx): GetChannelDifference with stored pts, default 2 s,
  never < 1 s; FloodWait -> sleep + double period; stop on FloodWait > 300 s or auth errors; hard end time.
- Keyless (TG2/code/tg2_poll.py, Mac): rotates 2-3 public forms, one request every >= 3 s through the shared
  round-74 t.me lock (>= 1.5 s between any two t.me requests from this Mac), plain `Python-urllib/3` UA, stop on
  403 / 429 / 418 / 503. Each form is sampled every (forms x 3) s, so its first-seen time has that resolution; the
  comparison is form vs form on the same posts and vs agentFx's capture.csv (top page at 1.5 s, Helsinki).

## Expected counts
@upbit_news posts ~4 a day, mostly 01-10 UTC. A few hours from 14:23 UTC is outside the busy window, so the Mac run
may see 0-3 posts; it runs in the background with an end time and keeps logging after this stream reports.
