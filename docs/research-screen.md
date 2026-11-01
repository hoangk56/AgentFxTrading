# Research screen ("Nghiên cứu")

Dashboard view `#research` (old links `#forward` still open it), the "Ứng viên" tab of Nghiên cứu. A status line counts
the tiers and names any forward tracker that hit its stop or promotion rule; below it the list by tier, the selected
algorithm's research numbers and forward tracker, and the folded "Đã thử, không đạt" table. Layout follows the research
page of the sibling project 106.dnse-stock. The separate "Chờ kiểm" cards were dropped on 2026-11-02: they repeated the
list group and its detail.

| Part | File |
|---|---|
| API `GET /api/research` | `app/research_api.py` |
| Rules trackers (F3, E1, gold) | `app/forward_status.py` (also served alone at `GET /api/forward/status`) |
| Basis B tracker | `app/basis_b_status.py` |
| Page script / CSS | `static/js/research.js`, `static/css/dashboard.css` (`rs-*` classes) |
| Markup | `templates/dashboard.html`, `#view-research` |
| Tests | `tests/app/test_research_api.py`, `tests/app/test_research_ui.py` (fixture `tests/fixtures/research/registry.yaml`) |

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

## Tiers

| Tier | Label | On the page |
|---|---|---|
| `live` | Đang live | list group |
| `demo` | Demo | list group |
| `cho-kiem` | Chờ kiểm | list group |
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
| `cum_net_bp`, `mean_net_bp`, `pooled_t` | float (mean / t may be null) | NaN is sent as null |
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
                  "tracker": {"key": "ecb_e1", "kind": "rules", "available": true, "message": null,
                              "data": {"verdict": "CONTINUE", "n": 12, "mean": 0.4, "...": "..."},
                              "rules": {"stop_t_after": 100, "...": "..."}}}],
  "tried": [{"round": "31", "name": "...", "reason": "...", "report": "..."}],
  "gold_calendar": {"valid_through": "2026-12-11", "days_left": 40}
}
```

`tracker` is null when `forward` is null; otherwise `kind` is `rules`, `basis_b` or `unknown`, and `available: false`
comes with a `message`. The login middleware (`app/auth.py`) covers the endpoint like every other dashboard route.
