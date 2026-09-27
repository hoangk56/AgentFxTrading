# Daily-check 2026-09-24 fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the open findings of `docs/audits/2026-09-24-daily-check.md` that the user chose to fix: #1 lost position reports, #3 minimum-lot risk overshoot, #4 stale H1 cross-lock, #8 FlowRSI close labels, #9 FlowRSI snapshot bar.

**Architecture:** Server (`app/portfolio.py`, `app/server.py`) becomes idempotent on `ctrader_id` for open / partial-close / close reports and rebuilds a closed row from a close report whose open never arrived. The three cBots retry `/portfolio/report` with backoff and retire pooled sockets before uvicorn's 5 s keep-alive closes them. FlowRsiBot and AiAgentBot refuse a minimum-lot entry that risks more than 1.5× the configured risk. FlowRsiBot replaces a cross-lock older than 24 macro bars by an H1 EMA50 trend bias, and the server stops trusting stale locks.

**Tech Stack:** Python 3 / FastAPI / SQLite (tests) + PostgreSQL (prod); C# cTrader cBots (.NET, compiled only on the VPS).

**Spec:** `docs/audits/2026-09-24-daily-check.md` (findings and "Hướng sửa"), plus the user's decisions of 2026-09-24:
- #3: refuse when risk at the minimum lot > 1.5× target (per-bot parameter, default 1.5, 0 = off).
- #4: lock older than 24 macro bars → H1 EMA50 bias (price vs EMA and EMA slope); in the bot filter and in the server gate.
- #5: no currency exposure limit (not done).
- #6: VPS load handled separately after measuring (no code).

## Global Constraints

- Never commit or push; leave changes in the working tree (AGENTS.md, memory `no-auto-commit`).
- No `dotnet` on the Mac: cBot tests are source-text tests (`tests/test_flowrsi_min_lot_risk_cap.py` style). The C# must be compile-checked on the VPS before deploy (memory `cbot-compile-check`); that needs the user's permission.
- C#: stay with features already used in the bots (classic `using (...) { }` blocks, no `using var`).
- Keep the log substrings the daily-audit collector greps: `Failed to report`, `Close position ignored`.
- Tests: `.venv/bin/python -m pytest -q -p no:cacheprovider` (baseline 675 passed).

## File map

| File | Change |
|---|---|
| `app/portfolio.py` | `register_position` idempotent; `record_partial_close` idempotent; `close_position` duplicate-safe + recovery insert |
| `app/server.py` | `/portfolio/report` close passes entry fields; `TmsSignals.bias_source`; `get_tms_cross_lock` / registry ignore stale locks |
| `cBot/FlowRsiBot.cs` | report retry + socket idle timeout; close payload `sl_pips`; min-lot multiple guard; lock age + EMA fallback; close labels; snapshot on closed bar |
| `cBot/AiAgentBot.cs` | report retry + socket idle timeout; close payload entry fields; min-lot multiple guard |
| `cBot/AsianRangeJudasSweepBot.cs` | report retry + socket idle timeout; close payload entry fields |
| `tests/test_report_idempotency_and_recovery.py` | new, server behaviour |
| `tests/test_cbot_report_retry.py` | new, cBot source |
| `tests/test_min_lot_risk_multiple.py` | new, cBot source |
| `tests/test_macro_lock_age.py` | new, server behaviour + FlowRsiBot source |
| `tests/test_flowrsi_close_labels.py` | new, FlowRsiBot source |
| `tests/test_flowrsi_snapshot_closed_bar.py` | new, FlowRsiBot source |

---

### Task 1: Server — idempotent reports and recovery of a lost open (#1)

**Files:**
- Modify: `app/portfolio.py` (`register_position`, `record_partial_close`, `close_position`)
- Modify: `app/server.py` (`/portfolio/report`, action `close`)
- Test: `tests/test_report_idempotency_and_recovery.py`

**Interfaces:**
- Produces: `PortfolioManager.close_position(..., side=None, volume=None, entry_price=None, entry_time=None, sl_pips=None) -> bool`. Returns True after inserting a recovered closed row; False (info log, no change) for a replayed close of an already-closed `ctrader_id`.
- Produces: `register_position` returns False (info log, no insert) when `(account_id, ctrader_id)` already exists.
- Produces: `record_partial_close` returns False (info log, P&L unchanged) when the open row already has `volume == remaining_volume`.
- Replays return False like any unmatched report (kept from `tests/test_position_identity_and_gold_buffer.py`), so no second TRADE_* event is broadcast; the bot only checks the HTTP status (200).

- [ ] **Step 1: Write the failing tests**

```python
from app.portfolio import PortfolioManager

ACCT = "acct-1"


def _pm(tmp_path):
    return PortfolioManager(db_path=str(tmp_path / "reports.db"))


def _rows(pm, ctrader_id):
    conn = pm._get_conn()
    try:
        cur = conn.execute(
            "SELECT status, volume, pnl, side, entry_price, entry_time, close_reason, sl_pips, initial_volume "
            "FROM positions WHERE ctrader_id = ?", (ctrader_id,))
        return [dict(zip(["status", "volume", "pnl", "side", "entry_price", "entry_time",
                          "close_reason", "sl_pips", "initial_volume"], r)) for r in cur.fetchall()]
    finally:
        conn.close()


def _open(pm, cid=111, volume=0.1):
    return pm.register_position(bot_id="bot-a", symbol="US30", side="Buy", volume=volume,
                                entry_price=51404.8, sl_pips=1151.6, tp_pips=1659.5,
                                account_id=ACCT, ctrader_id=cid)


def test_replayed_open_report_does_not_create_a_second_row(tmp_path):
    pm = _pm(tmp_path)
    assert _open(pm)
    assert _open(pm)
    assert len(_rows(pm, 111)) == 1


def test_replayed_partial_close_is_banked_once(tmp_path):
    pm = _pm(tmp_path)
    _open(pm, volume=0.2)
    for _ in range(2):
        assert pm.record_partial_close(bot_id="bot-a", symbol="US30", remaining_volume=0.1,
                                       realized_pnl=5.0, account_id=ACCT, ctrader_id=111)
    row = _rows(pm, 111)[0]
    assert row["volume"] == 0.1
    assert row["pnl"] == 5.0


def test_replayed_close_report_is_accepted_and_changes_nothing(tmp_path):
    pm = _pm(tmp_path)
    _open(pm)
    assert pm.close_position(bot_id="bot-a", symbol="US30", exit_price=51288.6, pnl=-11.62,
                             account_id=ACCT, ctrader_id=111, close_reason="StopLoss")
    assert pm.close_position(bot_id="bot-a", symbol="US30", exit_price=51288.6, pnl=-11.62,
                             account_id=ACCT, ctrader_id=111, close_reason="StopLoss")
    rows = _rows(pm, 111)
    assert len(rows) == 1 and rows[0]["pnl"] == -11.62


def test_close_of_an_unknown_position_rebuilds_the_row(tmp_path):
    pm = _pm(tmp_path)
    assert pm.close_position(bot_id="bot-a", symbol="US30", exit_price=51288.6, pnl=-11.62,
                             account_id=ACCT, ctrader_id=675558107, close_reason="StopLoss (Initial Structural Reversal)",
                             side="Buy", volume=0.1, entry_price=51404.8,
                             entry_time="2026-09-24T07:15:14.1234567Z", sl_pips=1151.6)
    row = _rows(pm, 675558107)[0]
    assert row["status"] == "closed"
    assert row["pnl"] == -11.62
    assert row["side"] == "Buy" and row["entry_price"] == 51404.8
    assert row["volume"] == 0.1 and row["initial_volume"] == 0.1
    assert str(row["entry_time"]).startswith("2026-09-24 07:15:14")
    assert row["sl_pips"] == 1151.6
    assert row["close_reason"] == "StopLoss (Initial Structural Reversal) (recovered: open report lost)"
    # The late open report of the same trade must not reopen it.
    assert _open(pm, cid=675558107)
    assert len(_rows(pm, 675558107)) == 1


def test_close_without_entry_fields_is_still_ignored(tmp_path):
    pm = _pm(tmp_path)
    assert not pm.close_position(bot_id="bot-a", symbol="US30", exit_price=1.0, pnl=-1.0,
                                 account_id=ACCT, ctrader_id=999)
    assert _rows(pm, 999) == []


def test_report_endpoint_forwards_entry_fields_on_close(tmp_path, monkeypatch):
    import app.server as server_mod
    from fastapi.testclient import TestClient
    pm = _pm(tmp_path)
    monkeypatch.setattr(server_mod, "portfolio_manager", pm)
    resp = TestClient(server_mod.app).post("/portfolio/report", json={
        "action": "close", "bot_id": "bot-a", "symbol": "EURJPY", "ctrader_id": 675569508,
        "side": "Sell", "volume": 0.01, "entry_price": 180.191, "entry_time": "2026-09-24T07:45:37Z",
        "exit_price": 180.494, "pnl": -1.91, "close_reason": "StopLoss",
        "account_number": "10115236", "account_type": "demo",
    })
    assert resp.json()["status"] == "success"
    row = _rows(pm, 675569508)[0]
    assert row["status"] == "closed" and row["side"] == "Sell"
```

- [ ] **Step 2: Run to verify they fail** — `.venv/bin/python -m pytest -q tests/test_report_idempotency_and_recovery.py` → duplicate row / double P&L / `TypeError: unexpected keyword 'side'`.

- [ ] **Step 3: Implement**

`register_position`, before the INSERT:

```python
            if ctrader_id is not None:
                # A bot retries a report whose answer it never got, and a close report may
                # already have rebuilt the row: the same position must not be booked twice.
                cur = conn.execute(
                    "SELECT id FROM positions WHERE account_id = ? AND ctrader_id = ? LIMIT 1",
                    (account_id, ctrader_id),
                )
                if cur.fetchone():
                    logger.info(f"Duplicate open report ignored: ctrader_id={ctrader_id} by {bot_id} on account {account_id}")
                    return True
```

`record_partial_close`, primary UPDATE gets `AND ABS(volume - ?) > 0.0001` (param `remaining_volume`), then before the NULL-ctrader_id fallback:

```python
                if not matched:
                    # Replayed report: the row already shows this slice closed.
                    cur = conn.execute(
                        "SELECT id FROM positions WHERE bot_id = ? AND symbol = ? AND status = 'open' "
                        "AND account_id = ? AND ctrader_id = ? AND ABS(volume - ?) <= 0.0001 LIMIT 1",
                        (bot_id, symbol, account_id, ctrader_id, remaining_volume),
                    )
                    if cur.fetchone():
                        logger.info(f"Duplicate partial close report ignored: ctrader_id={ctrader_id} by {bot_id}")
                        return True
```

`close_position`: new keyword params; after the two ctrader_id UPDATEs miss:

```python
                if not matched:
                    matched = self._recover_or_skip_close(conn, ...)
```

implemented inline as: a row with this `(account_id, ctrader_id)` and `status='closed'` → info log, return True (replay). No row at all and `side`, `volume`, `entry_price` present → INSERT a closed row (`initial_volume = volume`, `entry_time` = UTC text parsed from the bot's ISO time or now, `exit_time = datetime('now')`, `close_reason = f"{close_reason or 'Closed'} (recovered: open report lost)"`, `sl_pips` if > 0), warning log `Recovered position from close report …`, matched = 1. Otherwise unchanged (`Close position ignored` warning, False).

Helper at module level:

```python
_ISO_UTC = re.compile(r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})")


def _utc_text(value) -> Optional[str]:
    """'2026-09-24T07:15:14.1234567Z' -> '2026-09-24 07:15:14' (the bots send UTC)."""
    m = _ISO_UTC.match(str(value or ""))
    return f"{m.group(1)} {m.group(2)}" if m else None
```

`app/server.py` close branch passes `side=request.get("side")`, `volume=_float_or_none(request.get("volume"))`, `entry_price=_float_or_none(request.get("entry_price"))`, `entry_time=request.get("entry_time")`, `sl_pips=_float_or_none(request.get("sl_pips"))` (small local helper returning None for missing/invalid/≤0).

- [ ] **Step 4: Run the new tests and the portfolio/partial-close suites** — PASS.

---

### Task 2: cBots — retry `/portfolio/report`, short socket idle, entry fields on close (#1)

**Files:** `cBot/FlowRsiBot.cs`, `cBot/AiAgentBot.cs`, `cBot/AsianRangeJudasSweepBot.cs`; Test: `tests/test_cbot_report_retry.py`

**Interfaces:** Produces in each bot `private async Task<string> PostReportAsync(string url, string json)` → `null` when delivered, else the last error text.

- [ ] **Step 1: Failing source tests** — for each bot: `PostReportAsync` exists, loops over a retry delay table, checks `IsSuccessStatusCode`, logs `InnerException`; every `ReportPosition*` / `ReportPartialClose` body calls `PostReportAsync` and no longer calls `_httpClient.PostAsync(reportUrl`; each `HttpClient` used for reports is built with `SocketsHttpHandler` and `PooledConnectionIdleTimeout` < 5 s; the close payload of AiAgentBot and Judas carries `side`, `volume`, `entry_price`, `entry_time`; FlowRsiBot and AiAgentBot close payloads carry `sl_pips`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** — helper (same in the 3 bots):

```csharp
        // /portfolio/report is the server's only record of a trade: on 2026-09-24 two open reports
        // died on a reset keep-alive socket and both trades ran off the books. Retry transport
        // errors and non-2xx answers. The server ignores a replayed open, partial close or close
        // (matched on ctrader_id), so retrying after a lost answer cannot book a trade twice.
        private static readonly int[] ReportRetryDelaysSeconds = { 2, 4, 8, 16 };

        private async Task<string> PostReportAsync(string url, string json)
        {
            string lastError = null;
            for (int attempt = 0; attempt <= ReportRetryDelaysSeconds.Length; attempt++)
            {
                if (attempt > 0)
                    await Task.Delay(TimeSpan.FromSeconds(ReportRetryDelaysSeconds[attempt - 1]));
                try
                {
                    using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
                    using (var response = await _httpClient.PostAsync(url, content))
                    {
                        if (response.IsSuccessStatusCode) return null;
                        lastError = $"HTTP {(int)response.StatusCode}";
                    }
                }
                catch (Exception ex)
                {
                    lastError = ex.InnerException != null ? $"{ex.Message} ({ex.InnerException.Message})" : ex.Message;
                }
            }
            return $"{lastError} (after {ReportRetryDelaysSeconds.Length + 1} attempts)";
        }
```

HttpClient construction: `new HttpClient(new SocketsHttpHandler { PooledConnectionIdleTimeout = TimeSpan.FromSeconds(4) })` (FlowRsiBot keeps `Timeout = 60 s`), with a comment on uvicorn's 5 s keep-alive. Report methods await `PostReportAsync` and always print a failure (keeping the `Failed to report …` text), success only with `ShowLogs`. Close payload: AiAgentBot/Judas add `side`, `volume`, `entry_price`, `entry_time = position.EntryTime.ToUniversalTime().ToString("o")`; FlowRsiBot adds `sl_pips` from `_initialSlDistances`, AiAgentBot from `_positionInitialRiskPips`, both read before the entry is removed.
- [ ] **Step 4: Run** → PASS.

---

### Task 3: Refuse a minimum-lot entry above 1.5× target risk (#3)

**Files:** `cBot/AiAgentBot.cs` (param in "Guardrails"; check after the "Final sanity check" in the entry method), `cBot/FlowRsiBot.cs` (param next to `RiskPercentage`; check at the end of `CalculateDynamicVolumeInUnits`); Test: `tests/test_min_lot_risk_multiple.py`

- [ ] **Step 1: Failing source tests** — both bots declare `MaxMinLotRiskMultiple` with `DefaultValue = 1.5` and `MinValue = 0`; AiAgentBot's entry method compares `volume * slPips * Symbol.PipValue` with `riskAmount * MaxMinLotRiskMultiple`, calls `ReportGuardrailBlockedAsync("MinLotExceedsRiskPct"` and `return`s before `ExecuteMarketOrder`; FlowRsiBot's `CalculateDynamicVolumeInUnits` compares `finalRisk` with `effectiveRiskAmount * MaxMinLotRiskMultiple` and `return 0`s.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

AiAgentBot:
```csharp
        // The broker minimum lot ignores RiskPerTradePercent: USTEC 0.1 lot at a 1190p stop risked
        // 0.72% of balance against 0.2% (2026-09-24). 0 turns the check off.
        [Parameter("Max Min-Lot Risk (x target, 0=off)", Group = "Guardrails", DefaultValue = 1.5, MinValue = 0, Step = 0.1)]
        public double MaxMinLotRiskMultiple { get; set; }
...
            double riskAtVolume = volume * slPips * Symbol.PipValue;
            if (MaxMinLotRiskMultiple > 0 && riskAmount > 0 && riskAtVolume > riskAmount * MaxMinLotRiskMultiple)
            {
                string detail = $"{volume / Symbol.LotSize:F2} lots at {slPips:F1}p risks ${riskAtVolume:F2} = {riskAtVolume / riskAmount:F1}x the {RiskPerTradePercent:F2}% target ${riskAmount:F2} (max {MaxMinLotRiskMultiple:F1}x)";
                if (ShowLogs) Print($"[Guardrail] Blocked: {detail}");
                _ = ReportGuardrailBlockedAsync("MinLotExceedsRiskPct", detail);
                return;
            }
```
FlowRsiBot:
```csharp
            if (MaxMinLotRiskMultiple > 0 && effectiveRiskAmount > 0 && finalRisk > effectiveRiskAmount * MaxMinLotRiskMultiple)
            {
                Print($"[Guardrail] Entry REFUSED: {normalizedUnits / Symbol.LotSize:F2} lots at {slPips:F1}p risks ${finalRisk:F2}, {finalRisk / effectiveRiskAmount:F1}x the ${effectiveRiskAmount:F2} target (max {MaxMinLotRiskMultiple:F1}x).");
                return 0;
            }
```
- [ ] **Step 4: Run** → PASS.

---

### Task 4: Stale H1 cross-lock → H1 EMA50 bias (#4)

**Files:** `cBot/FlowRsiBot.cs` (params, `_macroEma`, `TmsSignals.bias_source`, `CalculateMacroTmsSignals`, `[TMS Filter]` logs), `app/server.py` (`TmsSignals.bias_source`, `MACRO_LOCK_MAX_AGE_BARS = 24`, `update_tms_cross_lock` call site, `get_tms_cross_lock`); Test: `tests/test_macro_lock_age.py`

**Interfaces:** bot sends `tms.bias` = effective bias, `tms.bias_source` = `"cross_lock"` or `"ema"`, `tms.bars_since_cross` = age of the held lock. Server `get_tms_cross_lock(snapshot) -> (bias, age, source)`.

- [ ] **Step 1: Failing tests**
  - server: snapshot own lock `BULLISH` age 30 without `bias_source` → `NEUTRAL`; age 10 → `BULLISH`; `bias_source="ema"` with age 40 → `BEARISH` kept, source contains `EMA`; registry lock age 30 → not borrowed; `trade_decision` with an `ema` snapshot does not store it in `_TMS_CROSS_LOCK_REGISTRY`.
  - FlowRsiBot source: params `MaxMacroLockAgeBars` (default 24) and `MacroEmaPeriod` (default 50); `Indicators.ExponentialMovingAverage(_macroBars.ClosePrices, MacroEmaPeriod)`; `CalculateMacroTmsSignals` sets `bias_source = "ema"` when the lock is older than `MaxMacroLockAgeBars`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** — bot:

```csharp
            // A cross-lock is held until the opposite cross is confirmed, however long that takes:
            // on 2026-09-23 GBPUSD, EURUSD, AUDUSD and XAUUSD stayed BULLISH for 31-48 H1 bars while
            // price fell. Past MaxMacroLockAgeBars (or before the first lock) the H1 EMA decides.
            string biasSource = "cross_lock";
            if (bias == "NEUTRAL" || (MaxMacroLockAgeBars > 0 && macroBarsSinceCross > MaxMacroLockAgeBars))
            {
                bias = MacroEmaBias(count - 2);
                biasSource = "ema";
            }
...
        private const int MacroEmaSlopeBars = 3;

        // Trend of the last closed macro bar: close beyond the EMA and the EMA sloping the same way.
        private string MacroEmaBias(int idx)
        {
            if (_macroEma == null || idx - MacroEmaSlopeBars < 0) return "NEUTRAL";
            double ema = _macroEma.Result[idx];
            double emaBefore = _macroEma.Result[idx - MacroEmaSlopeBars];
            double close = _macroBars.ClosePrices[idx];
            if (double.IsNaN(ema) || double.IsNaN(emaBefore)) return "NEUTRAL";
            if (close > ema && ema > emaBefore) return "BULLISH";
            if (close < ema && ema < emaBefore) return "BEARISH";
            return "NEUTRAL";
        }
```
  server:
```python
# A cross-lock older than this many macro bars no longer describes the trend (2026-09-23: 31-48
# H1 bars of BULLISH while EURUSD, GBPUSD, AUDUSD and XAUUSD fell). FlowRsiBot replaces such a
# lock by its H1 EMA bias (bias_source "ema"); a stale lock from anywhere else leaves the gate open.
MACRO_LOCK_MAX_AGE_BARS = 24
```
  `get_tms_cross_lock`: own `ema` bias → returned with source `"{bot} (Macro EMA)"`; own cross-lock → returned only if age ≤ 24; registry → only if age ≤ 24; else NEUTRAL. `trade_decision` records to the registry only when `bias_source != "ema"`.
- [ ] **Step 4: Run** new tests + `tests/test_flowrsi_tms_cross_lock_gate.py` → PASS.

---

### Task 5: FlowRSI close labels (#8)

**Files:** `cBot/FlowRsiBot.cs` (AI `CLOSE_ALL`, circuit breaker, default label in `OnPositionClosed`); Test: `tests/test_flowrsi_close_labels.py`

- [ ] **Step 1: Failing source tests** — `CLOSE_ALL` loop uses `CloseWithReason(pos, $"AI Close: {decision.reason}")`; circuit breaker uses `CloseWithReason(pos, "Circuit Breaker")`; no bare `ClosePosition(pos);` left except inside `CloseWithReason` and the partial close; the fallback label is `"Closed outside the bot (cTrader)"` and `"Take Profit Early"` is gone.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS.

---

### Task 6: FlowRSI snapshot on the closed bar (#9)

**Files:** `cBot/FlowRsiBot.cs` (`SendStateToAgentAsync`); Test: `tests/test_flowrsi_snapshot_closed_bar.py`

- [ ] **Step 1: Failing source test** — the method body uses `ClosedBarIndex()`, has no `Bars.ClosePrices.Count - 1` and no `Bars.Count - i`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```csharp
                // The bar that closed: inside OnBarClosed the last bar is sometimes already the next
                // one, a single tick old (ClosedBarIndex). Describe the bar the signal was taken on.
                int index = ClosedBarIndex();
                int maxBars = Math.Min(35, index + 1);
                var barList = new List<BarInfo>();
                for (int i = 0; i < maxBars; i++)
                {
                    int idx = index - i;
                    ...
                }
```
  and drop the later `int index = Bars.ClosePrices.Count - 1;`.
- [ ] **Step 4: Run** → PASS.

---

### Task 7: Verification and hand-off

- [ ] Full suite `.venv/bin/python -m pytest -q -p no:cacheprovider` → all pass; `git status` shows only intended files.
- [ ] Compile check the 3 bots on the VPS (memory `cbot-compile-check`) — needs the user's permission (SSH was refused as "Production Reads").
- [ ] Report to the user: changed files, test result, deploy steps (service restart for `app/`; rebuild `.algo` + restart all FlowRSI / TMS / Judas containers when flat), the SQL backfill still pending, #5 / #6 / #11 not done and why.
