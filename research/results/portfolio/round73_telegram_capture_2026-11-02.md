# Round 73: Upbit's official Telegram channel as A2-D5L's notice capture route (TG), 2026-11-02

Shared brief: [round73_telegram_capture/BRIEF.md](round73_telegram_capture/BRIEF.md) (02:51 UTC). Asked by the user
after keyless polling of Upbit's own notice API failed A2's capture gate (">= 80 % of live KRW-listing notices seen
<= 3 s after the stamp N"; [CAPTURE_A2.md](round65_retail_venues/A2/coord/forward/CAPTURE_A2.md)).

## Answer first
- **Not settled yet, but the route looks feasible.** Upbit's official channel **@upbit_news** is keyless through the
  web preview `t.me/s/upbit_news`.
  - It reposted 124 / 124 KRW-listing notices since it opened on 2025-08-20.
  - 95 % were posted <= 2 s after N. In 2026, all 80 were posted <= 1 s after N. The first weeks of 2025-08/09 lagged
    ~60 s.
  - No post came before N.
- Modelled end to end (channel lag + poll phase + response time), the share seen <= 3 s is:

  | poll period | from the Mac | from a host near Telegram (agentFx, 0.18 s) |
  |---|---|---|
  | 1-1.5 s | 82-96 % | 90-99 % |
  | 2 s | 71-78 % | 84-90 % |

- Two conditions are still unmeasured:
  - whether the preview shows a new post at once (no post arrived during the probes);
  - whether Telegram tolerates ~1 request / 1.5 s from one IP for days. So far: 2 x 60 polls at 2 s and 833 requests
    at 0.9 / s over 15 min, with no 429.
- Third-party repost channels (newlistingsfeed, coin_listing, CLWfeed, BWEnews) are 0.3-1 s slower and model at most
  79 % even at 1 s.
- A push route needs an account (**user decision**): a Telegram user account with an MTProto client subscribed to
  @upbit_news. It has no poll term and passes on history. The Bot API cannot read a channel it does not administer.

Detail: [TG/STREAM_TG.md](round73_telegram_capture/TG/STREAM_TG.md), per-channel lags in `TG/lag_*.csv`,
model in `TG/e2e.txt`.

## Forward logger (running)
- `TG/coord/tg_capture.py` polls t.me/s/upbit_news every 1.5 s on one keep-alive connection from agentFx (one IP,
  `research-script` UA). It logs each new post's Telegram time and first-seen time.
  - 429: backs off. 403 or no posts parsed: stops.
- A first 6 h run started 2026-11-02 ~03:35 UTC, attached to the coordinator's session. The user then allowed a cron
  line, so that run was stopped at ~04:47 and the logger runs from forge's crontab since 04:53 UTC (`# tg-capture-a2`,
  every minute under `flock`, so it restarts if it dies). It stops itself at 2026-11-09T00:00Z (`run 1.5 <until>`).
  - Remove: `crontab -l | grep -v tg-capture-a2 | crontab -`. Read: `python3 -I tg_capture.py report` in
    `/home/forge/tg_capture_a2`.
  - Gap 04:47-04:53 UTC: a post in that window would be logged with an inflated delay; ignore it.
- First run: 0 errors and no 429 in ~1,950 polls (~400 per 10 min), median response 0.12-0.13 s.
- **First sample, a warning:** post 2050 (a GAS airdrop notice, not a KRW listing), Telegram time 04:45:16, was first
  seen at 04:45:33.7, i.e. **17.7 s** late although the poll ran every 1.5 s. If the preview often lags like this, the
  t.me/s route fails the gate and only the MTProto (account) route is left. One sample decides nothing; the week of
  data (~25-30 posts) will.
- @upbit_news posts ~4 notices a day, so a 6 h run gives ~1-2 samples of the preview delay. A2's registered gate
  stays on live KRW-listing notices (~4 a month).

## Standing after round 73
- C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L. Forward-registered: F0.
- A2's promotion path is now: the t.me/s poller (if the forward logger confirms the preview delay and allowance) or
  an MTProto client (account), then real fills.
