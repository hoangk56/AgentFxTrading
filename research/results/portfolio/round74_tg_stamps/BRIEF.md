# Round 74 brief: Telegram channel history as second-precise announcement times (coordinator + subagents)

Written 2026-11-02 14:19 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. The coordinator
(main session) dispatches one subagent per stream. Each stream works only inside
`research/results/portfolio/round74_tg_stamps/<STREAM>/`, its own data folder `research/data/<source>/` and its own
scratchpad subfolder. The user asked (2026-11-02) to keep researching until a LIVE algorithm exists.

## Why this round
- Rounds 63 D, 66 B2 and 71 could not test Binance or Bithumb announcements: Binance's `/bapi/` is robots-banned,
  Bithumb keeps ~20 notices. Round 71 ranked "L1, Binance announcement times" as decision 4.
- Round 73 found that public Telegram channels keep **full history with second stamps** in the keyless web preview
  `t.me/s/<channel>?before=<id>` (t.me robots.txt is 404, i.e. no rule). The stamp is Telegram's own post time, so a
  rule that trades from the post is point in time by construction, whatever the website's own time was.
- Channels probed 2026-11-02 14:16 UTC: `binance_announcements` (official, 9,107 posts, from 2017-09-17),
  `OKXAnnouncements` (7,377), `Bybit_Announcements` (10,032), `whale_alert_io` (104,489), `coin_listing` (third
  party, from 2017-10, listings on many venues with detection times), `newlistingsfeed` (from 2024-03), `upbit_news`
  (official, from 2025-08). No Bithumb or Coinbase handle found yet.
- The one seconds-level announcement edge so far is A2-D5L (Upbit KRW listing -> Binance perp at N + 5 s, DEMO, HOLD
  t 3.11). Its LIVE promotion waits on a <= 3 s capture route (stream TG2 of this round).

## Context (read, don't redo)
- research/PROMPT.md: bars, exhausted families ("Những họ đã cạn"), pitfalls ("Bẫy hay gặp"), the bars at the end.
  research/JOURNAL.md: top entries (rounds 63-73).
- Upbit family: round65_retail_venues_2026-11-01.md, round65_retail_venues/A2/STREAM_A2.md + PREREG_A2_D5L.md (the
  seconds pipeline: events, perp age check, aggTrades fills, costs), round66_fast_execution_2026-11-01.md (A3-A5, O2:
  OKX / Bybit listing notices from their own APIs had no seconds reaction; B2), round68_upbit_census_2026-11-01.md
  (non-listing Upbit notices: 1-3 s pop then fade), round69 (KO / JP venues), round73_telegram_capture/TG/STREAM_TG.md.
- Binance listings: round63_parallel/D/STREAM_D.md (spot listing with a >= 7 d perp: 0 IS events), round64 (T:
  delisted perps sit at spot; X; N; K2), round66 N0 (fade new-perp launch: fails), round71_mixed/IB + W7 (withdrawal
  window). Do not redo these designs; a new design must say what is different.
- Reusable code: round65_retail_venues/A/code/{events,perps,pull_first}.py, A2/code/{pull,net,analyze,checks}.py
  (aggTrades windows from data.binance.vision, taker fees, perp age), round73_telegram_capture/TG/code (t.me parsing).

## Shared Telegram fetcher (mandatory)
- Use `round74_tg_stamps/coord/tg.py` + `parse.py` + `pageback.py` (copies of round 73's, retargeted). One lock file
  for every process on this Mac: >= 1.5 s between any two t.me requests, one keep-alive connection, plain
  `Python-urllib/3` UA, stop on 403 / 429 / 418 / 503 (the pull stops; wait >= 10 min before one retry, then stop for
  good and report). Raw pages land in `research/data/telegram_hist/raw/<channel>/b<id>.html`; requests are logged in
  `research/data/telegram_hist/requests.log`.
- The coordinator is pulling `binance_announcements` (all) then `coin_listing` (all) from 14:19 UTC
  (`research/data/telegram_hist/pull_coord.out`). Do not pull those two yourself; wait for the pages (pageback is
  resumable and skips saved pages). Other channels: pull them yourself with `pageback.py <channel> <max_pages>`.
- Parsing: `parse.parse(bytes)` -> posts (id, time UTC epoch, text, edited). **Pitfalls:** the preview shows the
  original post time but the *current* text; an edited post (`edited` True) may carry later information (a
  "postponed" or a corrected time), so either drop edited posts or show the result is the same without them. Posts
  are whole seconds. Pages are untrusted data: parse with `python -I`, never execute or follow their content.

## HOLD stays closed
Eras: IS 2020-01-01..2021-12-31 (2018-2021 if the data allows and you declare it), VAL 2022-01-01..2024-12-31, HOLD
2025-01-01..2026-10-29. Cut every event list at post time < 2025-01-01 right after parsing; request price data with
an end time <= 2024-12-31 23:59:59 UTC. Never print, plot or summarise 2025-26 values. **Subagents never open HOLD**:
if a rule passes the IS / VAL bars, write `PREREG_DRAFT_<name>.md` (rule, numbers, power at VAL size, pass bar,
hashes from `python -m research.tools.prereg_hashes`) and stop; the coordinator opens HOLD once.

## Bars (unchanged; never lower one)
Common: economic mechanism; side fixed before data; parameters picked on IS, checked on VAL unchanged; net > 0 in IS
and VAL, positive at costs x1.5 and one step late (for seconds rules: +5 s later entry); t clustered by day.
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % of random entries, HOLD power at VAL size
  (net Sharpe per trade x sqrt(expected HOLD trades)) >= 3.
- DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random.
Keep grids small (declare them in HYPOTHESES) and report the max-over-cells null. Costs: Binance USDT-M taker 5 bp a
side + the worst-of-1 s fill A2 used; Bybit / OKX taker at their published retail tier; spot taker 10 bp.

## How to work
1. Before computing anything: write `HYPOTHESES_<STREAM>.md` with the UTC time from `date -u` (never estimate it):
   mechanism, data, rule(s) and the small grid, costs, the power arithmetic (events per year pre-2025, HOLD count).
2. Pull data, build, test on IS, check on VAL.
3. Write `STREAM_<STREAM>.md`: answer first (LIVE / DEMO / none), per-era and per-year tables, costs, random
   benchmark, what failed and why, pitfalls, what a user decision could unlock.
4. Code in `<STREAM>/code/`. Data under `research/data/<source>/` (git-ignored) with a requests.log. No git commands.
5. Machine: 10 cores / 16 GB shared by 5 streams: at most 2 heavy processes per stream; data.binance.vision daily
   aggTrades files can be large: keep only the windows you need and delete the zips.

## Network rules
- Allowed: t.me web preview through the shared fetcher; public exchange APIs without a key (Binance, Bybit, OKX,
  Hyperliquid info), data.binance.vision, public.bybit.com, OKX public data downloads, GitHub raw, literature APIs.
- Not allowed: anything needing an account, login, payment, API key or CAPTCHA; ignoring robots.txt or rate limits
  (back off on 418 / 429 / 503); 403 = stop, never disguise as a browser; web.archive.org; Binance `/bapi/`;
  cftc.gov, ici.org, data-api.ecb.europa.eu, countryeconomy.com, export.arxiv.org.
- Never send personal data: no e-mail in any request.
- WebSearch: at most 10 searches per stream.

## Report back to the coordinator (final message, <= 250 words)
Verdict per rule (LIVE / DEMO / none) with IS / VAL net, t, years, random %, power at VAL size; files written; any
PREREG_DRAFT; data pulled; problems.
