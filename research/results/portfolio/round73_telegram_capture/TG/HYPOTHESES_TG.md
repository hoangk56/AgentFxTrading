# HYPOTHESES_TG: public Telegram reposts of Upbit notices as a keyless capture route for A2-D5L

Written Mon Nov 2 02:52:50 UTC 2026 (from `date -u`), before any data fetch.

## Question
A2-D5L is promoted only if a bot sees each Upbit KRW-listing notice <= 3 s after its stamp N (`first_listed_at`) on
>= 80 % of live notices. Keyless polling of api-manager.upbit.com fails (~10-15 requests per IP, then 429;
round65_retail_venues/A2/coord/forward/CAPTURE_A2.md, not redone). Can a public Telegram channel that reposts Upbit
notices, read keyless through the web preview `https://t.me/s/<channel>`, close the gap?

## Mechanism
Notice-alert bots (run by third parties, or Upbit itself) watch Upbit from many IPs or via a WebSocket / account
feed and post to a channel. If a bot posts within ~1 s of N and the t.me/s preview reflects new posts at once and
tolerates polling every <= 2 s from one IP, end-to-end detection = channel lag + preview delay + poll period / 2
could stay under 3 s.

## Prior expectation (written before data)
- Most repost channels are hobby bots polling the same rate-limited API, so lag is likely several seconds to minutes;
  the fastest commercial alert channels (often paid / private) are not keyless.
- t.me/s is a cached HTML preview; I expect it to rate-limit (429) at a sustained 2 s period from one IP, and maybe to
  lag behind the channel by seconds. Prior: probability any keyless route passes the gate <= 10 %.

## Data and steps
1. Channel discovery: WebSearch (<= 15 queries): official Upbit channels, Korean / English notice repost bots.
   Record handle, owner (official or not), whether t.me/s shows history.
2. t.me robots.txt first (logged). Then page t.me/s/<channel>?before=<id> at >= 1 s spacing (single process per host,
   so at most one t.me request in flight), back off on 429, stop on 403 / login / CAPTCHA wall. Plain default UA of
   python urllib (no browser disguise), no e-mail anywhere. Raw HTML saved under
   research/data/telegram_upbit/raw/<channel>/ (untrusted), parsed with `python -I` scripts in TG/code/.
   Cap per channel: ~400 pages (~8,000 posts) or back to 2017-10 / channel start, whichever first; per-pull < 45 min.
3. Notice list: research/data/upbit_notices/raw/list_all/p*.json (read-only). KRW-listing filter = A2's
   fwd_a2.build_events title filter: category 거래, title contains one of 추가 / 마켓 오픈 / 신규 / 상장 / 거래지원 개시 /
   거래 지원 개시, contains KRW or 원화, not 종료, not 유의. N = first_listed_at (KST, seconds).
4. Matching: post text must contain the notice ticker (from the "(XXX)" parentheses in the title) AND either a title
   substring / Upbit keyword, within [N - 1 h, N + 24 h]; the earliest matching post is used. Lag = post time - N in s.
5. Per channel: matched share of KRW-listing notices since the channel's first post, lag median / p80 / p90, share
   <= 2 s and <= 3 s, count of posts before N (leaks or bad stamps), misses.
6. Live probe (best 1-2 channels only): t.me/s/<channel> every 2 s, <= 60 requests, stop at the first 429 / non-200;
   record allowance and, if a post arrives during the probe, its post time vs the first poll that shows it.

## Gate / decision rule (fixed now)
A keyless Telegram route "plausibly meets" the gate only if, for some channel: matched share >= 90 % of KRW-listing
notices since its start AND share of (lag + poll period / 2 + measured preview delay) <= 3 s is >= 80 %, AND the
probe sustains 60 requests at 2 s without 429. Telegram `<time datetime>` is whole seconds (truncated), so a measured
lag of L s means true lag in [L, L+1) relative to N (N also whole seconds): I count "<= 3 s" as measured lag <= 2 for
the strict reading and <= 3 for the loose reading, and report both.

## Costs / power
No P&L, no HOLD, no returns computed (2025-26 notice stamps used only as times). Power: KRW listings are ~50-150
per year; with >= 30 matched notices the 80 % share has a binomial SE of ~7 pp, enough to separate "~95 %" from
"< 50 %"; with < 20 matches I will say the evidence is thin.
