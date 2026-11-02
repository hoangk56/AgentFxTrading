# Research screen ("Nghiên cứu")

Dashboard view `#research`, the "Ứng viên" tab of Nghiên cứu, written for a reader who is not a professional investor
(2026-11-02, spec `docs/superpowers/specs/2026-11-02-research-plain-design.md`). A status line counts the stages, the
rules getting weaker and any forward tracker that hit its stop or promotion rule. Each list row shows the plain name, a
trend word (Mạnh lên / Giữ vững / Yếu dần / Yếu đi / Chưa rõ / Đã loại) and four tiny period bars. The detail has three
short blocks, **Làm gì**, **Mạnh hay yếu** (verdict sentence, bar chart of the periods, certainty in words) and
**Hành trình** (dated events), then the folded **Số kỹ thuật** with everything the screen showed before (tier reason,
IS / VAL / HOLD text, tracker, files). Below the list sits the folded "Đã thử, không đạt" table. Layout follows the research
page of the sibling project 106.dnse-stock. The separate "Chờ kiểm" cards were dropped on 2026-11-02: they repeated the
list group and its detail.

| Part | File |
|---|---|
| API `GET /api/research` | `app/research_api.py` |
| Plain-language layer | `app/research_plain.py`, data `research/plain.yaml` |
| Real-money R of live R rules (Gotobi) | `app/live_r.py` |
| Rules trackers (F3, E1, gold) | `app/forward_status.py` |
| Basis B tracker | `app/basis_b_status.py` |
| Page script / CSS | `static/js/research.js`, `static/css/dashboard.css` (`rs-*` classes) |
| Markup | `templates/dashboard.html`, `#view-research` |
| Tests | `tests/app/test_research_api.py`, `tests/app/test_research_plain.py`, `tests/app/test_live_r.py`, `tests/app/test_research_ui.py` (fixtures `tests/fixtures/research/`) |

Filter, search and the selected algorithm live in the hash: `#research?tier=demo&q=ecb&id=F3`.

## Data source: `research/registry.yaml`

Written by the research sessions; the server only reads it (`yaml.safe_load`, PyYAML in `requirements.txt`). A missing,
unreadable or malformed file never breaks the page: the API returns empty lists and a `warning` the page shows. A row
without `id`, a duplicate `id` or an unknown tier adds a warning too (an unknown tier is listed under Chờ kiểm).

```yaml
algorithms:
  - id: F3                       # unique, short
    name: ...                    # list and detail title
    description: ...             # one or two plain sentences
    market: EURUSD
    round: 24
    tier: live                   # live | demo | cho-kiem | da-loai
    tier_reason: ...             # why it sits in that tier
    research: {is: "...", val: "...", hold: "..."}   # free text, any key may be missing
    forward: ecb_f3              # ecb_f3 | ecb_e1 | gold_levels | basis_b | null
    bot: cbot-...                # or null
    prereg: research/results/.../PREREG_....md      # or null
    report: research/results/.../REPORT.md
tried:
  - {round: 31, name: ..., reason: ..., report: research/results/...}
```

No figure on the screen comes from anywhere else: research numbers are the registry's text, forward numbers are the
trackers' output.

## Plain layer: `research/plain.yaml`

A second read-only file, keyed by the registry `id`, kept apart so the registry keeps its shape. An algorithm without
an entry shows the registry name and description, no bars and "Chưa rõ". Missing file: no plain data, no warning;
broken file or bad field: skipped with a warning in the payload's `warning`.

```yaml
ecb-f3:
  name: "ECB F3: bán euro buổi trưa ngày đô mạnh"   # plain title
  what: "..."                                       # one sentence: what it trades and when
  why: "..."                                        # one sentence: why it may make money ("Giả thuyết: ..." if unproven)
  unit: bp                                          # R | bp | pct_week | pct_year
  periods:                                          # copied from the registry's research lines; any may be missing
    is:   {years: "2016–2021", n: 381, mean: 2.39, t: 3.29}
    val:  {years: "2022–2024", n: 207, mean: 3.01, t: 2.60}
    hold: {years: "2025–2026", n: 117, mean: 2.00, t: 2.16}
  history:                                          # dated events; kind: find | demo | live | change | wait | out
    - {date: 2026-10-15, kind: find, text: "Tìm ra ở vòng R24, luật được đăng ký trước khi kiểm"}
    - {date: 2026-10-16, kind: live, text: "Chạy tiền thật 0,01 lot, chỉ để đo giá khớp lệnh"}
  note: "..."                                       # optional, appended to the verdict sentence
```

Rules: every number comes from the registry line (and so from a result file); an event with no source for its date is
left out, never guessed. After each research round, or when a bot changes stage or settings, add or extend the entry;
`test_committed_plain_file_matches_the_committed_registry` fails when an entry has no registry row (a registry row
without an entry just falls back). Once the other
session's edits to `research/PROMPT.md` are committed, add one line there asking each round to fill this file.

### Units, certainty, trend

| unit | bar value | caption |
|---|---|---|
| `R` | mean × 100 | $ lãi trên mỗi $100 chịu rủi ro |
| `bp` | mean | $ lãi trên mỗi $10.000 vào lệnh |
| `pct_week` | mean | % lãi mỗi tuần |
| `pct_year` | mean | % lãi mỗi năm (gross; carry rules say in `note` what is left after cash interest) |

The fourth bar is the forward run: "Chạy thật" for a live rule, "Chạy demo" otherwise, from the rules tracker's
`mean` (bp), basis B's `mean_net_bp` (bp) or `live_r` (R). A tracker in another unit than `unit` is not drawn.

Certainty from t: ≥ 3 Rất chắc, ≥ 2 Khá chắc, ≥ 1 Chưa chắc, > −1 Như may rủi, else Lỗ khá rõ. A forward run uses its
own `forward_t` (forward trades alone, never `pooled_t`) and says "mới N lệnh, chưa đủ" under 30 trades.

Trend (`rsTrend` in `static/js/research.js`): `da-loai` → Đã loại. With 30+ forward trades (`rsRealVerdict`, needs a
positive IS mean and a forward t): mean ≥ IS mean and t ≥ 2 → Mạnh lên; mean ≥ ½ IS → Giữ vững; otherwise Yếu đi
(mean ≤ 0) or Yếu dần, but only when the run sits at least one standard error (|mean / t|) under the IS mean. A
shortfall inside one standard error is noise: the research rule below decides and the sentence adds "chưa đủ chắc để
đổi kết luận" (Gotobi's 42 live legs on 2026-11-02: −0,02 R, t −0,25, 0,8 se under IS). Otherwise from research: HOLD ≤ 0 → Yếu đi;
HOLD ≥ 1,25 × IS and HOLD t ≥ 2 → Mạnh lên; ≥ 0,75 × IS → Giữ vững; ≥ 0,4 × IS → Yếu dần; else Yếu đi; IS or HOLD
missing (or IS ≤ 0 with HOLD > 0) → Chưa rõ.

## Tiers

| Tier | Label | On the page |
|---|---|---|
| `live` | Tiền thật | list group |
| `demo` | Demo | list group |
| `cho-kiem` | Chờ anh quyết | list group |
| `da-loai` | Đã loại | list group, collapsed when the page opens |

`tried` rows are hypotheses that never became an algorithm; they fill the collapsed "Đã thử, không đạt" table.

## Adding a research round's rows

1. Append the round's surviving rule(s) to `algorithms` with their tier, `tier_reason`, IS / VAL / HOLD lines copied
   from the round's report, and the PREREG / report paths.
2. Append every rejected hypothesis of the round to `tried` (round, name, one-line reason, report path).
3. Move an existing entry by changing its `tier` and `tier_reason`; never delete it (dropped rules go to `da-loai`).
4. Set `forward` only when a tracker exists for it. A new tracker key needs code in `app/research_api.py`; until then
   the entry shows "Không có bộ theo dõi tên ...".
5. Check the file loads: `.venv/bin/python -c "from app.research_api import load_registry; print(load_registry()[2])"`
   prints the warnings (an empty list when clean). No restart is needed: the file is read on every request.

## Trackers

`forward` picks the block shown in the detail pane, under "Kiểm chứng".

- `ecb_f3`, `ecb_e1`, `gold_levels`: `forward_status()` on the bots' closed trades, plus the candidate's registered
  numbers (`rules`: `stop_t_after`, `stop_t`, `stop_cum_after`, `floor_after`, `promote_after`, `promote_t`, `hold`)
  taken from `CANDIDATES` in `app/forward_status.py` and put in words by the page. Gold also shows the calendar guard.
  Only the keys the registry uses are computed. A DB failure empties those trackers, not the page.
- Both rules trackers and basis B also report `forward_t`, the t of the forward values alone, which the plain layer
  grades the run on.
- `live_r` (no registry key; chosen when the plain `unit` is `R`, the tier `live`, `forward` null and `bot` set):
  `app/live_r.py` reads the bots' closed trades on live accounts since the first `live` event in `history` (the `bot`
  field's `{a,b}` braces expand). Per trade R = signed price move / (stop pips × pip size), from real fills (spread in,
  commission out). Only real Gotobi legs count, by the Calendar's rule (`leg_of` on a trading gotobi day, close reason
  not a decoy's); a trade without a stop is skipped and counted. Output `{n, mean, forward_t, skipped, since}`; a DB
  failure empties this tracker only.
- `basis_b`: `app/basis_b_status.py`, imported lazily. If the module is missing or `status()` raises, the tracker shows
  "chưa có dữ liệu".

### `basis_b` contract

`from app.basis_b_status import status`; `status() -> dict` with:

| Key | Type | Meaning |
|---|---|---|
| `available` | bool | false until the bot has run once |
| `last_run` | ISO str or null | last run |
| `last_error` | str or null | optional, shown in red when set |
| `has_secret` | bool | signed Binance calls possible; false shows "Chưa có API secret: chưa đo được lượng coin vay được và lãi vay" |
| `signals`, `fillable`, `not_fillable`, `unknown_borrow` | int | signal counts |
| `open` | list of `{coin, entry_time, d_bp, hours_open}` | open signals |
| `closed` | list, newest first, of `{coin, entry_time, exit_time, hold_h, net_bp_registered, net_bp_book, fund_bp, fillable (bool or null), borrow_rate_y (fraction per year or null), inventory_usd (float or null)}` | the page shows the latest 10 |
| `cum_net_bp`, `mean_net_bp`, `pooled_t`, `forward_t` | float (mean / t may be null) | NaN is sent as null |
| `verdict` | `NO_DATA`, `CONTINUE`, `STOP`, `PROMOTE_CHECK` | same colours as the rules trackers |
| `verdict_reason` | str (Vietnamese) | shown next to the verdict |
| `rules` | `{stop_after, stop_not_fillable_share, promote_t, hold: {n, mean_bp, t}}` | the registered numbers, put in words |

## API shape

```json
{
  "generated_at": "2026-11-01T08:00:00+00:00",
  "registry": "research/registry.yaml",
  "warning": null,
  "algorithms": [{"id": "...", "name": "...", "tier": "demo", "research": {"hold": "..."}, "forward": "ecb_e1",
                  "plain": {"name": "...", "what": "...", "why": "...", "unit": "bp", "periods": {"...": "..."},
                            "history": [{"date": "2026-10-16", "kind": "demo", "text": "..."}], "note": null},
                  "tracker": {"key": "ecb_e1", "kind": "rules", "available": true, "message": null,
                              "data": {"verdict": "CONTINUE", "n": 12, "mean": 0.4, "...": "..."},
                              "rules": {"stop_t_after": 100, "...": "..."}}}],
  "tried": [{"round": "31", "name": "...", "reason": "...", "report": "..."}],
  "gold_calendar": {"valid_through": "2026-12-11", "days_left": 40}
}
```

`plain` is null without an entry in `research/plain.yaml`. `tracker` is null when `forward` is null (except the
`live_r` case above); otherwise `kind` is `rules`, `basis_b`, `live_r` or `unknown`, and `available: false` comes with
a `message`. The login middleware (`app/auth.py`) covers the endpoint like every other dashboard route.
