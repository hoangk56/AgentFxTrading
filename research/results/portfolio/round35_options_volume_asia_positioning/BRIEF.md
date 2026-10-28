# Round 35 brief: listed-option volume by underlying (OCC), Asian equity-derivative positioning (TAIFEX, KRX, CFFEX)

Written 2026-10-28 01:24 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as
rounds 25-34 (the user's LIVE and DEMO bars in research/PROMPT.md; no RELAXED tier).

**Why this round exists.** The user asked on 2026-10-27 to keep researching until a LIVE algorithm is found, using other
sources. Rounds 31-34 loaded 15 public non-price sources and found no candidate (reports
round31_new_sources_2026-10-27.md, round32_..., round33_..., and round34_china_etf_options/STREAM_*.md). Two kinds of
public positioning data remain unloaded and reachable from this Mac (probed 2026-10-27 20:30 UTC, HTTP 200):
marketdata.theocc.com (OCC volume query: daily option volume by underlying, calls / puts, customer / firm / market-maker
where published), www.taifex.com.tw (daily OI and trading of the "three institutional investors", foreign institutions
first, in TAIEX futures and options; no robots.txt, answers 404), data.krx.co.kr (Korean derivatives by investor type;
no robots.txt, answers 404). www.cmegroup.com times out from this Mac (no CME margin or volume history).

**Everything not changed here follows research/results/portfolio/round31_new_sources/BRIEF.md**: read it first,
including its "Read first" list, Data section (HOLD 2025-01-01..2026-09-24 closed, new series cut at 2024-12-31 at
load), network rules (no accounts / logins / payment / CAPTCHA, robots.txt, >= 1 s between requests to one host and the
site's own limits, one download job per host at a time, no e-mail in any request, downloads under `web/` parsed with
`python -I`, every fetch logged), test rules, PREREG_DRAFT rule and what to return. Read the "Rules added" of rounds
32-34 (publication lags, power arithmetic first, same-timestamp rule) and the STREAM files of rounds 31-34.

## Streams
| stream | direction | why it might escape the limits | already done (don't redo) |
|---|---|---|---|
| O | **Listed-option volume by underlying from the OCC.** Daily call and put volume (and by account type if the query gives it) for SPY, QQQ, IWM, DIA, the index options SPX / NDX / RUT, GLD, SLV, USO, UNG, FXE, FXY, plus total equity. Check how far back the query goes (the CBOE put/call files end 2019-10, round 4: this is the replacement if OCC goes to 2024). Hypotheses with sides from the literature before any return: put/call contrarian at extremes (retail fear), customer vs firm split (Pan & Poteshman's informed flow only with open-buy data: say what the free split can and cannot show), option volume relative to the underlying's (Johnson & So 2012, O/S ratio: high O/S -> negative), GLD / SLV / USO call-buying bursts -> metals and oil. Targets US500, USTEC, US2000, US30, XAUUSD, XAGUSD, XTIUSD, EURUSD, USDJPY; horizons 1-5 days; OCC publishes after the US close (state the time you verify). | The free CBOE put/call ended in 2019 so no round could test it on VAL; per-underlying volume for the commodity ETFs and the O/S ratio were never built. | round 4 GEX / DIX and CBOE put/call (history ended 2019); round 9 VRP; round 32 V (CBOE implied vols, SKEW, VVIX); round 34 D (Deribit flows: nothing) and E (LETF dose) |
| T | **Asian equity-derivative positioning by investor type.** TAIFEX daily: foreign institutions' net OI in TX / MTX futures and in TXO calls / puts (from ~2007), dealers and investment trusts; KRX daily: foreigners' net KOSPI200 futures (and USD/KRW futures if free); CFFEX daily top-20 member long / short OI in IF / IH / IC (from 2010). Hypotheses (sides from the mechanism / practitioner and academic sources, e.g. the literature on foreign futures positioning in Taiwan and Korea, Chinese member-ranking studies): foreign institutions as informed (follow) or as hedgers (no direction), sizable changes in foreign net short as global risk-off signals. Targets HK50, JP225, US500, USTEC, AUDUSD, USDJPY (and USDCNH if useful); horizons 1-5 days; entries after publication (TAIFEX ~15:00 Taipei, KRX after its close, CFFEX after 15:15 Beijing: verify). Exclude C3's gotobi window on JPY pairs or report it separately. | Positioning of segmented, widely followed venues (Taiwan's foreign futures OI is a classic practitioner indicator) with the investor split that round 31 J's TFX data lacked; published before the European and US sessions, so a 1-5 day lead into other markets is mechanically possible. Never loaded here. | round 31 J (Japan TFX, MoF, JPX); round 34 H (SHFE / INE commodity member rankings: read STREAM_H.md if it exists, don't duplicate CFFEX if H already did it); round 29 O (Asian opens, price only) |

## Rules added for this round
- Round 34 stream H may still be running: use **at most 1 heavy Python process** per stream while
  `ps aux | grep -c "[r]esearch/.venv/bin/python"` is above 4, each under ~3 GB RAM. One download job per host.
- Background waiters: don't use `pgrep -f <pattern>` to wait on your own job (round 34 D's waiter matched its own
  command line and never fired); wait on an output file or a PID.
- Publication time is part of the rule (write it into HYPOTHESES before the first return).
- Do the power arithmetic first (round 16 STREAM_X frontier, round 10 minimum-edge table).
- Write ONLY `HYPOTHESES_<stream>.md`, `STREAM_<stream>.md` and `PREREG_DRAFT_*` in
  research/results/portfolio/round35_options_volume_asia_positioning/. Scripts, data and outputs under
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r35/<stream>/`.
- A series that starts after 2016 shortens IS: say which bar it can still meet (no rescaling).
- Keep going inside your stream: an unusable or null first source is not the end; move to related free sources.
