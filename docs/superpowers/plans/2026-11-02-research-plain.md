# Research Screen in Plain Words Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The `#research` detail and list read in plain Vietnamese, with a trend arrow, four period bars and a dated
journey for every algorithm.

**Architecture:** A second read-only data file `research/plain.yaml` (keyed by registry id) is cleaned by a new
loader and attached to each algorithm in `/api/research`. Trackers gain a forward-only t; a new `live_r` tracker gives
Gotobi its real-money R. All wording, trend and chart logic lives in pure functions in `static/js/research.js`.

**Tech Stack:** FastAPI, PyYAML, vanilla JS (node-tested pure functions), pytest.

**Spec:** `docs/superpowers/specs/2026-11-02-research-plain-design.md`

## Global Constraints

- Do not touch `research/registry.yaml` or `research/PROMPT.md` (another session has uncommitted edits).
- No new package; no inline JS; repo tokens in `static/css/dashboard.css` (`rs-*` classes).
- Every asset stamp moves together from `?v=20261102_d8` to `?v=20261102_d9` in `templates/dashboard.html`.
- Loaders never raise; problems become text in the payload's `warning`.
- Units: `R` (bar = mean × 100, "$ lãi trên mỗi $100 chịu rủi ro"), `bp` ("$ lãi trên mỗi $10.000 vào lệnh"),
  `pct_week` ("% lãi mỗi tuần"), `pct_year` ("% lãi mỗi năm").
- Stage words: live "Tiền thật", demo "Demo", cho-kiem "Chờ anh quyết", da-loai "Đã loại".
- Certainty: t ≥ 3 "Rất chắc", ≥ 2 "Khá chắc", ≥ 1 "Chưa chắc", > −1 "Như may rủi", else "Lỗ khá rõ"; real run under
  30 trades: "mới N lệnh, chưa đủ".
- Run `./venv/bin/python -m pytest -q` after every task.

## Review Focus

- Algorithm without a plain entry (new registry rows from the research session): falls back to registry name /
  description, empty bars, "Chưa rõ"; no JS error. → Task 4 test `fallback_without_plain`.
- Tracker in a unit other than the plain unit (e.g. bp tracker on an R algorithm): fourth bar "chưa có", trend uses
  research only. → Task 4 test `real_run_unit_mismatch`.
- All bars negative or one value zero: chart still draws a zero line inside the box, no NaN in SVG. → Task 4 test
  `chart_negative_and_zero`.
- `is.mean` ≤ 0 (ratio meaningless): trend must not say "Giữ vững"; hold ≤ 0 → "Yếu đi", else "Chưa rõ". → Task 4
  trend table row.
- Dates as YAML dates vs strings, and a bad date: both valid forms come out `YYYY-MM-DD`, a bad one is dropped with a
  warning. → Task 2 test.

---

### Task 1: Forward-only t in both trackers

**Files:**
- Modify: `app/forward_status.py` (add `forward_t`, add field in `evaluate`)
- Modify: `app/basis_b_status.py` (`evaluate` output)
- Test: `tests/app/test_forward_status.py` (existing file; add tests), `tests/app/test_basis_b_status.py` if present,
  else add to the forward test file

**Interfaces:**
- Produces: `forward_t(values: Sequence[float]) -> Optional[float]` in `app/forward_status.py`; tracker dicts gain
  key `forward_t` (rules trackers: over the bp nets; basis B: over the bp values, i.e. `v * 1e4`), rounded to 2.

- [ ] **Step 1: Failing tests**

```python
def test_forward_t_is_mean_over_standard_error():
    assert forward_t([]) is None and forward_t([3.0]) is None
    assert forward_t([1.0, 3.0]) == pytest.approx(2.0)          # mean 2, sd 1.414, se 1.0
    assert forward_t([2.0, 2.0]) is None                        # sd 0

def test_evaluate_reports_forward_t_beside_pooled_t():
    out = evaluate(CANDIDATES["ecb_f3"], [1.0, 3.0])
    assert out["forward_t"] == pytest.approx(2.0) and "pooled_t" in out
```
Basis B: `evaluate([...two closed trades with net 1e-4 and 3e-4...])["forward_t"] == pytest.approx(2.0)`.

- [ ] **Step 2: Run, expect FAIL** — `./venv/bin/python -m pytest tests/app/test_forward_status.py -q`
- [ ] **Step 3: Implement** (`statistics.stdev`; `None` under 2 values or sd 0); `evaluate` of both modules adds
  `forward_t` (NO_DATA path: `None`). `basis_b_status` imports `forward_t` from `app.forward_status`.
- [ ] **Step 4: Run, expect PASS** (full suite).
- [ ] **Step 5: Commit** `feat: report a forward-only t from the research trackers`

### Task 2: `research/plain.yaml` loader and API merge

**Files:**
- Create: `app/research_plain.py`
- Modify: `app/research_api.py` (`research_payload` attaches `plain`; warnings joined)
- Create/keep: `research/plain.yaml` (already written; 26 ids)
- Test: `tests/app/test_research_plain.py`, fixture `tests/fixtures/research/plain.yaml`

**Interfaces:**
- Produces: `PLAIN_PATH: Path`; `UNITS = ("R", "bp", "pct_week", "pct_year")`;
  `KINDS = ("find", "demo", "live", "change", "wait", "out")`;
  `load_plain(path: Path = None, known_ids: Iterable[str] = ()) -> Tuple[Dict[str, dict], List[str]]`.
  Cleaned entry: `{name, what, why, unit, periods: {is|val|hold: {years, n, mean, t}}, history: [{date, kind, text}],
  note}` (missing text → `None`, missing periods → `{}`, missing history → `[]`).
- API: each algorithm gains `plain` (entry or `None`).

- [ ] **Step 1: Failing tests**

```python
def test_missing_file_gives_nothing_and_no_warning(tmp_path):
    assert load_plain(tmp_path / "nope.yaml") == ({}, [])

def test_broken_file_warns(tmp_path):        # "a: [unclosed", "- list", "\xff\xfe"
    plain, warnings = load_plain(path_with(text)); assert plain == {} and warnings

def test_fields_are_cleaned_and_bad_ones_dropped_with_a_warning(tmp_path):
    # unknown id (known_ids given), unit "usd", mean "abc", n -3, kind "boom", date "31/10" -> each dropped + warning
    # date: 2026-10-15 (YAML date) and "2026-10-16" (string) -> "2026-10-15", "2026-10-16"; history sorted oldest first

def test_committed_plain_file_matches_the_committed_registry():
    algorithms, _, _ = load_registry()
    plain, warnings = load_plain(known_ids=[a["id"] for a in algorithms])
    assert warnings == [] and set(plain) == {a["id"] for a in algorithms}

def test_api_attaches_plain_and_null(registry, no_basis, monkeypatch):   # fixture plain has one fixture id
    rows = {a["id"]: a for a in client.get("/api/research").json()["algorithms"]}
    assert rows["<fixture id>"]["plain"]["unit"] == "bp" and rows["<other id>"]["plain"] is None
```
Note: the committed registry check runs against the worktree file (origin/main), not the main checkout.

- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement** with the same safety as `load_registry` (`yaml.safe_load`; non-dict → warning). `n` must be
  a non-negative int or null; `mean`/`t` numbers or null (bool is not a number). Warnings in Vietnamese, prefixed with
  the id. `research_payload(path=None, plain_path=None)` passes registry ids as `known_ids`.
- [ ] **Step 4: Run, expect PASS** (full suite)
- [ ] **Step 5: Commit** `feat: plain-language research file merged into /api/research`

### Task 3: `live_r` tracker for live R algorithms

**Files:**
- Create: `app/live_r.py`
- Modify: `app/research_api.py` (choose `live_r` when `plain.unit == "R"`, tier `live`, `forward` null, `bot` set)
- Test: `tests/app/test_live_r.py`

**Interfaces:**
- Consumes: `app.gotobi_calendar.leg_of(side, entry) -> Optional[Tuple[str, date]]`, `is_trading_day(d, skips)`,
  `skip_dates()`; `app.close_reasons.DECOY_PREFIX`; `get_db_connection(db_target)`.
- Produces: `expand_bots(pattern: str) -> List[str]`; `pip_size(symbol: str) -> float`;
  `trade_r(row: dict) -> Optional[float]`; `live_r_status(bot_pattern: str, since: Optional[str], db_target=None)
  -> dict` returning `{n, mean, forward_t, skipped}`. API tracker: `{"key": "live_r", "kind": "live_r",
  "available": bool, "message": None|NO_DATA, "data": {...}}`.

- [ ] **Step 1: Failing tests**

```python
def test_expand_bots():
    assert expand_bots("cbot-live-live-{usdjpy,eurjpy}-fix-gotobi") == [
        "cbot-live-live-usdjpy-fix-gotobi", "cbot-live-live-eurjpy-fix-gotobi"]
    assert expand_bots("cbot-x") == ["cbot-x"]

def test_trade_r_sign_and_pip():
    assert trade_r({"symbol": "USDJPY", "side": "buy", "entry_price": 150.00, "exit_price": 150.30, "sl_pips": 30}) == pytest.approx(1.0)
    assert trade_r({"symbol": "EURUSD", "side": "sell", "entry_price": 1.1000, "exit_price": 1.1010, "sl_pips": 20}) == pytest.approx(-0.5)
    assert trade_r({"symbol": "USDJPY", "side": "buy", "entry_price": 150, "exit_price": 151, "sl_pips": 0}) is None

def test_status_keeps_real_live_legs_since_the_live_date(tmp_db):
    # rows: real gotobi leg (counted), decoy on a non-gotobi day (left out), DECOY_PREFIX reason (left out),
    # demo account (left out), exit before `since` (left out), sl_pips 0 (skipped=1)
    assert out["n"] == 1 and out["skipped"] == 1

def test_db_failure_gives_an_unavailable_tracker(monkeypatch):   # via research_payload: kind live_r, available False
```
- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement.** Query closed positions of the expanded bot ids joined to live configured accounts
  (same filter as `app/leaderboard.py`: `account_id IN (SELECT account_id FROM accounts WHERE account_type = 'live'
  AND is_configured = 1)`), `exit_time >= since` when given. For bot ids containing `gotobi`, keep a row only when
  `leg_of(side, entry_time)` gives a day `is_trading_day` accepts. Drop `close_reason` starting with `DECOY_PREFIX`.
  `since` = first `history` event with kind `live`. Wrap in try/except in the API (failure → unavailable).
- [ ] **Step 4: Run, expect PASS** (full suite)
- [ ] **Step 5: Commit** `feat: real-money R tracker for live R-sized research algorithms`

### Task 4: Plain list row and detail in `research.js`

**Files:**
- Modify: `static/js/research.js`, `static/css/dashboard.css` (`rs-*`), `templates/dashboard.html` (stamps → d9,
  research help text if it names old tier words)
- Test: `tests/app/test_research_ui.py` (extend `PURE`; update label expectations)

**Interfaces:**
- Consumes: payload fields from Tasks 1–3 (`plain`, `tracker.data.forward_t`, `tracker.kind === 'live_r'`).
- Produces (pure, all added to `PURE`):
  - `RS_TIERS` labels → stage words above.
  - `rsUnitInfo(unit) -> {scale, caption}`.
  - `rsSure(t, n) -> {level: 0..4, word}`; `n` given and < 30 → level 0, word "mới N lệnh, chưa đủ".
  - `rsRealRun(entry) -> {n, mean, t, label, target} | null`: rules → `{data.n, data.mean, data.forward_t}`,
    target `tracker.rules.promote_after`; basis B → `{closed_n, mean_net_bp, forward_t}`; live_r → `{n, mean,
    forward_t}`; null when no tracker data, n 0, or the tracker unit (bp for rules / basis, R for live_r) differs from
    `plain.unit`. `label`: "Chạy thật" for tier live, "Chạy demo" otherwise.
  - `rsTrend(entry) -> {key: 'up'|'flat'|'down'|'unk'|'out', arrow, word, sentence}` per the spec's rule (ratios
    0.5 / 1.0 with t ≥ 2 for the real run; 1.25 with t ≥ 2 / 0.75 / 0.4 for research; `is.mean` ≤ 0 → hold ≤ 0
    "Yếu đi" else "Chưa rõ"); sentence "Kiểm cuối lãi bằng X% lúc tìm ra." + real run part + `plain.note`.
  - `rsMiniBarsHtml(entry) -> svg string`, `rsPeriodChartHtml(entry) -> svg string`, `rsJourneyHtml(plain)`.
  - `rsListHtml` row: plain name, stage chip, trend, mini bars, tracker badge only for STOP / PROMOTE_CHECK.
  - `rsDetailHtml`: head (plain name, chip, dim registry name + id) → Làm gì / Vì sao có lãi (fallback description)
    → Mạnh hay yếu (verdict box; STOP / PROMOTE_CHECK sentence first) → Hành trình (empty: "Sổ chưa ghi mốc thời
    gian.") → `<details class="rs-tech">` "Số kỹ thuật" holding today's tier reason, `rsResearchHtml`,
    `rsTrackerHtml` (now also renders `live_r`: n, mean R, forward t, skipped), files.
  - `rsStatusOf`: "N tiền thật · N demo · N chờ anh quyết · N đang yếu đi" + STOP / PROMOTE flags.
  - `rsMatches` also searches `plain.name/what/why`.

- [ ] **Step 1: Failing tests** (node via `_run`):

```python
TREND_CASES = [  # (tier, is, hold, hold_t, real{n,mean,t}|None) -> key, word
  ("da-loai", 2, 2, 3, None, "out", "Đã loại"),
  ("live", 0.043, 0.042, 2.9, None, "flat", "Giữ vững"),
  ("demo", 5.99, 2.87, 1.43, None, "down", "Yếu dần"),
  ("demo", 1.0, 1.3, 2.5, None, "up", "Mạnh lên"),
  ("demo", 1.0, -0.1, -1, None, "down", "Yếu đi"),
  ("demo", 1.0, 0.3, 1, None, "down", "Yếu đi"),
  ("live", 2.0, 2.0, 2, {"n": 40, "mean": -0.5, "t": -1}, "down", "Yếu đi"),
  ("live", 2.0, 2.0, 2, {"n": 40, "mean": 2.5, "t": 2.4}, "up", "Mạnh lên"),
  ("live", 2.0, 2.0, 2, {"n": 40, "mean": 1.2, "t": 1.0}, "flat", "Giữ vững"),
  ("live", 2.0, 2.0, 2, {"n": 10, "mean": -9, "t": -3}, "flat", "Giữ vững"),   # under 30: research decides
  ("demo", -1.0, 2.0, 2, None, "unk", "Chưa rõ"),
  ("demo", None, 2.0, 2, None, "unk", "Chưa rõ"),
]
```
  plus: `rsSure` thresholds (3, 2, 1, −0.99, −1) and `(None, 3)`; `rsUnitInfo('R').scale == 100`;
  `fallback_without_plain` (entry `plain: None` renders name/description, no "undefined"/"NaN");
  `real_run_unit_mismatch` (plain unit R + rules tracker → `rsRealRun` null, chart says "chưa có");
  `chart_negative_and_zero` (values −2, 0, 3, null → no "NaN" in SVG, one `<line`);
  STOP tracker → detail verdict box starts with the stop sentence; label "Chạy demo" for a demo entry;
  hostile strings in every plain field and history text come out escaped (extend the existing escape test).
- [ ] **Step 2: Run, expect FAIL** — `./venv/bin/python -m pytest tests/app/test_research_ui.py -q`
- [ ] **Step 3: Implement** the functions, CSS (chips reuse `rs-tier--*`; trend colours from `--profit`, `--loss`,
  `--warn`, `--text-dim`; bars `fill="var(--profit)"`/`var(--loss)`), stamps → d9.
- [ ] **Step 4: Run, expect PASS** (full suite, incl. `test_every_local_asset_carries_the_same_release_stamp`)
- [ ] **Step 5: Look at it** on the local QA server (`AGENTFX_TEST_DB` scratch DB, `QA_PROD=1` proxy for
  `/api/research` through the read-only tunnel) at 1440 and 390 px: ECB F3, Gotobi, basis B, a dropped rule.
- [ ] **Step 6: Commit** `feat: research screen in plain words with trend bars and journey`

### Task 5: Docs

**Files:** Modify `docs/research-screen.md` (new file section, fields, units, trend rule, certainty words, `live_r`,
how a round adds an entry; tier words), `docs/architecture.md` only if it lists research modules.

- [ ] **Step 1:** Write the sections; mention that `research/PROMPT.md` should gain one line once the other session
  commits.
- [ ] **Step 2:** Full suite green.
- [ ] **Step 3: Commit** `docs: research screen plain-language data and trend rule`
