# Round 36 brief: Asian central-bank liquidity operations, US household cash payments (daily Treasury outlays)

Written 2026-10-28 01:42 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as
rounds 25-35 (the user's LIVE and DEMO bars in research/PROMPT.md; no RELAXED tier).

**Why this round exists.** The user asked on 2026-10-27 to keep researching until a LIVE algorithm is found, using other
sources. Rounds 31-35 loaded 17 public non-price sources (positioning, flows, holdings, premiums, option flows, attention)
and found no candidate; see the reports round31_..._2026-10-27.md to round34_..._2026-10-28.md and
round35_options_volume_asia_positioning/STREAM_*.md. Round 32 L tested US Fed / Treasury liquidity against US assets
(nothing). Two dated, mechanical cash flows with a published daily dose remain unloaded:
- Asian central banks' daily liquidity operations, in markets where they bind harder than in the US (a currency board,
  a managed currency, a quantity-targeting central bank);
- cash paid by the US Treasury straight to households (tax refunds, Social Security, economic impact payments), which
  the retail-flow literature links to buying of risky assets within days.

Reachable from this Mac (probed 2026-10-28 01:41 UTC): api.hkma.gov.hk (HTTP 200, open API); api.fiscaldata.treasury.gov
(round 32 L used it; DTS table `deposits_withdrawals_operating_cash` has daily withdrawals by category, e.g. "IRS Tax
Refunds Individual", "Social Security Benefits", economic impact payments); www.pbc.gov.cn answers 302 (check whether a
plain browser-like request reaches the open-market-operation announcements without a JS challenge; if not, use other
free official mirrors such as chinamoney.com.cn, and say so); BoJ statistics pages exist under www.boj.or.jp (find the
current-account / money-market-operation series URLs).

**Everything not changed here follows research/results/portfolio/round31_new_sources/BRIEF.md**: read it first,
including its "Read first" list, Data section (HOLD 2025-01-01..2026-09-24 closed, new series cut at 2024-12-31 at
load), network rules (no accounts / logins / payment / CAPTCHA, robots.txt, >= 1 s between requests to one host and the
site's own limits, one download job per host at a time, no e-mail in any request, downloads under `web/` parsed with
`python -I`, every fetch logged), test rules, PREREG_DRAFT rule and what to return. Read the "Rules added" of rounds
32-35 and round 32's STREAM_L.md (how DTS was parsed, its row-name changes, its publication lag) before building.

## Streams
| stream | direction | why it might escape the limits | already done (don't redo) |
|---|---|---|---|
| A | **Asian central-bank liquidity operations.** (1) HKMA: daily aggregate balance, convertibility-undertaking interventions (weak-side HKD purchases drain the aggregate balance; strong-side add), HIBOR fixings; target HK50 (and US500 / USTEC as controls), 1-5 days; the weak-side triggers are dated and the drain size is published. (2) PBoC: daily open-market operations (reverse-repo injections / maturities, net), MLF / TMLF monthly, RRR cuts; targets USDCNH, HK50, AUDUSD, 1-5 days. (3) BoJ: daily current-account balances / money-market operations only if a series is a mechanical, dated flow not already covered (round 31 J did MoF flows and interventions). Sides from the mechanism (liquidity drained -> local assets weaker; a published injection after a squeeze -> relief) and from the literature, fixed before any return. Publication times: HKMA posts intraday / end of day (verify), PBoC announces OMOs at ~09:20 Beijing for the same day (no look-ahead: an entry after the announcement only). | In a currency board the drain is mechanical and its size is public; in China the central bank sets daily liquidity by quantity, and its net injection is a policy signal published before the Asian day. Neither was ever loaded here; round 32 L found nothing for the US, where reserves are abundant. | round 32 L (US liquidity); round 7 PBoC fix surprise (priced in 6 min) and round 7 countercyclical reversal; round 30 CFETS close; round 31 J (Japan MoF / JPX); round 33 S (SNB) |
| U | **US household cash payments from the Daily Treasury Statement.** Daily withdrawals for individual tax refunds (with the February-April refund season), Social Security / SSI benefits (paid on known calendar days: the 3rd, and the 2nd / 3rd / 4th Wednesdays), economic impact payments (2020-21) and other transfers; build the dose (dollars paid to households over the last 1-5 days, and the scheduled dose known in advance from the calendar). Hypotheses from the retail-flow literature (e.g. stimulus-check and tax-refund retail trading studies, Robinhood flow papers; the side "household cash in -> retail buying of high-attention risky assets" fixed before any return): targets BTCUSD, ETHUSD, US2000, USTEC, US500, 1-5 days; report 2020-21 separately (stimulus checks would dominate IS) and a version without the EIP days. DTS for day D is published ~16:00 ET on D+1: use only what was public before the entry, or the calendar-scheduled part known in advance. | A scheduled, sized cash transfer to the exact investor group that buys crypto and small caps, like gotobi's scheduled importer payments; the calendar part is known in advance, so the entry need not wait for the publication. Never loaded here (round 32 L used DTS only for the TGA balance and withheld taxes). | round 32 L (TGA, withheld taxes, RRP, H.4.1); round 13 tax / settlement-day dummies; round 18 day-of-month scan (calendar days without dose); round 2-11 turn-of-month |

## Rules added for this round
- Round 35 stream O may still be running: use **at most 1 heavy Python process** per stream while
  `ps aux | grep -c "[r]esearch/.venv/bin/python"` is above 4, each under ~3 GB RAM. One download job per host.
- Wait on your own background jobs via an output file or a PID, never `pgrep -f <pattern>`.
- Publication time is part of the rule (write it into HYPOTHESES before the first return). Do the power arithmetic
  first (round 16 STREAM_X frontier, round 10 minimum-edge table).
- Write ONLY `HYPOTHESES_<stream>.md`, `STREAM_<stream>.md` and `PREREG_DRAFT_*` in
  research/results/portfolio/round36_asia_liquidity_household_cash/. Scripts, data and outputs under
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r36/<stream>/`.
- A series that starts after 2016 shortens IS: say which bar it can still meet (no rescaling).
- Keep going inside your stream: an unusable or null first source is not the end; move to related free sources.
