# Research screen in plain words: design

Date: 2026-11-02. Screen: dashboard view `#research` ("Nghiên cứu", tab "Ứng viên"). Mockup the owner picked
(direction B): https://claude.ai/artifact/RPf7CZ23Us6sfsdq94nGu3

## Why

The owner is not a professional investor. Today the detail pane copies the research registry verbatim ("stop 3 x ATR20
H1", "+2,00 bp/lệnh, t 2,16", IS / VAL / HOLD, RELAXED, CONTINUE…): it is long and full of jargon, so it does not get
read. The owner wants to see two things for every algorithm:

1. its journey: when it was found, went to demo, went to real money, had its settings changed, or was dropped;
2. whether it is getting stronger or weaker over time.

## Goals

- Every list row answers "where is it, and is it holding up?" at a glance: plain name, stage, trend arrow + word,
  four tiny bars (one per period).
- The detail pane has three short blocks in plain Vietnamese: **Làm gì**, **Mạnh hay yếu**, **Hành trình**.
- Money is shown in units a layman reads: "$ lãi trên mỗi $10.000 vào lệnh", "$ trên mỗi $100 chịu rủi ro",
  "% mỗi tuần". Certainty is words, not `t`.
- Nothing the screen shows today is lost: the technical numbers move into a folded "Số kỹ thuật" section.

## Non-goals

- No layout change: list left, detail right, chips, search, hash state (`#research?tier=&q=&id=`) and the folded
  "Đã thử, không đạt" table stay as they are.
- No change to the Dự đoán AI and Backtest tabs, to the trackers' rules or to how tiers are decided.
- No editing from the screen; the data files are written by people and research sessions.

## Anti-goals

- A trend word that contradicts the numbers beside it, or that sounds sure on 3 trades.
- Invented dates or numbers: a missing value shows as missing, never as an estimate.
- Breaking the page when the new file is missing or malformed.

## Constraints

- Stack as today: FastAPI (`app/research_api.py`), vanilla JS (`static/js/research.js`, pure functions tested in node
  by `tests/app/test_research_ui.py`), CSS in `static/css/dashboard.css` (`rs-*`), repo theme tokens, no new package,
  no inline JS. Bump every asset stamp together (`?v=`; `test_every_local_asset_carries_the_same_release_stamp`).
- Repo rule: no performance figure without a result file under `research/results/`. Every number in the new file is
  copied from the registry line or report it came from.
- `research/registry.yaml` and `research/PROMPT.md` have uncommitted edits by another session in the main checkout.
  This change must not touch them (see Data).

## Data: `research/plain.yaml` (new)

A second read-only file, keyed by the registry's algorithm `id`, so the registry stays untouched and an algorithm
without an entry simply falls back to today's text.

```yaml
c3-gotobi:
  name: "Gotobi: mua yên Nhật ngày gotobi"     # plain title for list and detail
  what: "…"                                     # one sentence: what it trades and when
  why: "…"                                      # one sentence: why it may make money
  unit: R                                       # R | bp | pct_week | pct_year (unit of every mean below)
  periods:                                      # research periods; any may be missing
    is:   {years: "2016–2021", n: null, mean: 0.043, t: 5.4}
    val:  {years: "2022–2024", n: null, mean: 0.041, t: 3.7}
    hold: {years: "2025-01..2026-09", n: 738, mean: 0.042, t: 2.9}
  history:                                      # dated events, oldest first
    - {date: 2026-09-27, kind: find, text: "Tìm ra (vòng Swing v2)"}
    - {date: 2026-10-23, kind: change, text: "Đổi thông số: …"}
  note: "…"                                     # optional, appended to the verdict sentence
```

- `kind` ∈ `find | demo | live | change | wait | out`; it colours the dot.
- Carry rules quoted in %/year (A2, A3, B2) use `pct_year` with the gross figures the registry gives for every
  period, so the bars compare like with like; why they were dropped (no better than cash) goes in `note`.
- `date` is a real date (YAML date or `YYYY-MM-DD` string). An event whose date is unknown is left out.
- Loader: same safety as the registry. Missing file → no plain data, no warning. Unreadable / malformed file, unknown
  id, bad `unit`, non-numeric `mean`/`t`/`n`, bad `kind` or date → skip that field or row and add a warning to the
  payload's existing `warning` string. Never raises.
- API: `research_payload()` attaches `plain` to each algorithm (`null` when absent). Shape after cleaning:
  `{name, what, why, unit, periods: {is|val|hold: {years, n, mean, t}}, history: [{date: "YYYY-MM-DD", kind, text}],
  note}`.
- Initial content: written for every algorithm in the committed registry (26). Numbers copied from each registry
  `research` line; dates from report file names, `tier_reason` text, `research/JOURNAL.md` and git history. Where no
  source gives a date, the event is omitted.

## Real-money results for R algorithms (new tracker)

Gotobi C3 is live but has no tracker, so its "Chạy thật" bar would be empty. Add tracker kind `live_r`, chosen
automatically for an algorithm whose plain `unit` is `R`, whose tier is `live`, and whose `forward` is null:

- Bots: the registry `bot` field, with shell braces expanded (`cbot-live-live-{usdjpy,eurjpy,gbpjpy}-fix-gotobi` →
  three ids).
- Trades: closed positions of those bots on live accounts, exited on or after the first `live` event date in
  `history` (all closed trades of those bots when there is none). Only real legs count: for Gotobi bots a leg is real
  when `app/gotobi_calendar.leg_of()` places it on a day `is_trading_day()` accepts, as the Calendar screen does, and
  its close reason does not start with `DECOY_PREFIX`; decoys and out-of-window trades are left out (not counted as
  skipped).
- Per trade R = signed price move / stop distance = `(exit − entry) × (+1 buy / −1 sell) / (sl_pips × pip size)`,
  pip size 0.01 for JPY quotes and 0.0001 otherwise (a small helper in the new module). Trades with `sl_pips` ≤ 0 or
  a missing price are skipped and counted. Fills are real, so spread is included; commission is not, said in the caption.
- Output `{n, mean, t, skipped}`; `t = mean / (sd / √n)` for n ≥ 2. A DB failure empties this tracker only.

## Screen

### List row

`plain.name` (fallback `name`) · stage chip · trend arrow + word · four tiny bars (is, val, hold, real run; an empty
slot is a flat dash). Stage chips and the filter chips use the new words: live → **Tiền thật**, demo → **Demo**,
cho-kiem → **Chờ anh quyết**, da-loai → **Đã loại** (tier keys unchanged). Search also matches the plain name, what
and why. A tracker that hit STOP or PROMOTE_CHECK still shows its badge on the row.

### Detail

1. Head: plain name, stage chip; under it, dim, the registry name and id.
2. **Làm gì**: `what`, then **Vì sao có lãi**: `why`. Without plain data: the registry `description`.
3. **Mạnh hay yếu**:
   - Verdict box: arrow + word + a generated sentence + `note`. If the tracker says STOP or PROMOTE_CHECK, the box says
     so first (that outranks the trend).
   - Caption with the unit in words, then a bar chart of the four periods: "Lúc tìm ra / Kiểm lần 1 / Kiểm cuối /
     Chạy thật", each with its years and trade count, value printed on the bar, green above zero, red below, real run
     drawn solid, missing period shown as "chưa có".
   - Certainty line per period: four squares + word.
4. **Hành trình**: vertical dated list with coloured dots; empty → "Sổ chưa ghi mốc thời gian."
5. **Số kỹ thuật** (`<details>`, closed): everything the detail shows today: tier reason, IS / VAL / HOLD lines with
   the R / t legend, the tracker block (rules, basis B tables, gold calendar) and the files.

### Units

| unit | bar value | caption |
|---|---|---|
| `R` | mean × 100 | $ lãi trên mỗi $100 chịu rủi ro |
| `bp` | mean | $ lãi trên mỗi $10.000 vào lệnh |
| `pct_week` | mean | % lãi mỗi tuần |
| `pct_year` | mean | % lãi mỗi năm |

Real-run value: rules trackers' `mean` (bp), basis B `mean_net_bp` (bp), `live_r` `mean` (R).

Real-run certainty uses a **forward-only t** (the forward trades alone), never the trackers' `pooled_t`, which
mixes in the registered HOLD run and would read "Rất chắc" after a handful of trades. `app/forward_status.py` and
`app/basis_b_status.py` gain a `forward_t` field (mean / (sd / √n) over the forward values, `None` under 2 values);
`pooled_t` keeps its place in "Số kỹ thuật".

The fourth bar is labelled by tier: **Chạy thật** for `live`, **Chạy demo** for `demo` (and the sentence says
"Chạy demo: N lệnh"). Both feed the trend rule's real-run branch. A tracker in another
unit than the plain `unit` is not drawn (the bar reads "chưa có").

### Certainty words (from t)

t ≥ 3 Rất chắc · t ≥ 2 Khá chắc · t ≥ 1 Chưa chắc · t > −1 Như may rủi · otherwise Lỗ khá rõ. A real run under 30
trades shows "mới N lệnh, chưa đủ" instead of a word.

### Trend rule (pure JS function, tested)

Inputs: `is.mean`, `hold.mean`, `hold.t`, real run `{n, mean, forward_t}`.

- Tier `da-loai` → × **Đã loại**.
- Real run n ≥ 30: mean ≤ 0 → ↘ **Yếu đi**; mean ≥ is.mean and t ≥ 2 → ↗ **Mạnh lên**; mean ≥ 0.5 × is.mean →
  → **Giữ vững**; else ↘ **Yếu dần**.
- Otherwise, from research: missing `is` or `hold` → ? **Chưa rõ**; hold.mean ≤ 0 → ↘ **Yếu đi**;
  hold ≥ 1.25 × is and hold.t ≥ 2 → ↗ **Mạnh lên**; hold ≥ 0.75 × is → → **Giữ vững**; hold ≥ 0.4 × is → ↘ **Yếu dần**;
  else ↘ **Yếu đi**.
- Sentence: "Kiểm cuối lãi bằng X% lúc tìm ra." plus, when a real run exists, "Chạy thật: N lệnh" and, under 30,
  ", chưa đủ để kết luận" (with the tracker's target when it has one: "N/100 lệnh").

### Status line

"N tiền thật · N demo · N chờ anh quyết · N đang yếu đi" plus today's STOP / PROMOTE flags.

## Tests

- API: plain file merged by id; missing file; malformed file; bad fields each skipped with a warning; the committed
  `research/plain.yaml` loads with no warning and every id exists in the committed registry.
- `live_r`: brace expansion; R sign for buy/sell; JPY vs non-JPY pip; skipped rows; decoy and off-day legs left out;
  live-date cut-off; DB failure.
- `forward_t` in both tracker modules (forward values only; `None` under 2 values).
- UI (node): trend rule table, certainty words, unit conversion, chart SVG for negative / missing values, list row and
  detail with hostile strings escaped, fallback without plain data, STOP outranks trend.
- Existing research tests keep passing (wording updates where labels changed).

## Docs

`docs/research-screen.md`: the new file, its fields, the trend rule and how a research session adds an entry. Once the
other session has committed `research/PROMPT.md`, add one line there asking each round to fill `plain.yaml` (not in
this change).

## Decided after the builder check

- Real-run t is forward-only (new `forward_t`), not `pooled_t`.
- `live_r` counts real Gotobi legs only, using the Calendar's rule.
- `pct_year` unit for the %/year carry rules, gross figures, reason in `note`.
- Fourth bar "Chạy thật" for live, "Chạy demo" for demo.

## Decided after the final review

- A real run of 30+ trades turns the trend down only when it sits at least one standard error under the "lúc tìm ra"
  mean; inside that it is noise, the research rule decides and the sentence says so.
- "chưa có lệnh nào" only when the tracker reports 0 trades; an unreadable tracker says "chưa đọc được số"; a tracker
  in another unit says nothing in the sentence.
- `plain.yaml` ids must be a subset of the registry (a new registry row falls back), so a research commit cannot turn
  the suite red.
- The live_r caption says commission is not deducted. Gotobi's 2026-10-23 broker stop-outs stay in the R bar: their
  price-based R (−0,63 / −0,75) is close to the loss over risk (about −0,5).

## Left to the builder

CSS details within the repo tokens, exact copy of generated sentences, the chart's pixel geometry, phone layout
(the list already stacks above the detail under 960 px).
