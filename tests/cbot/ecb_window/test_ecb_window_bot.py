"""cBot/EcbWindowBot.cs against the registered rules it implements (E1 and F3) and the brief's hard rules.

The rule's numbers live in the registered code: research/results/portfolio/round24_relaxed/prereg_code/hold_r24.py.txt
(F3: the selector, the window, the Christmas skip) and clib.py.txt (the quote at a minute). The cBot's defaults must
equal them, or a live result no longer says anything about the holdout. The hard rules: lots never depend on account
capital, no position is held longer than 5 days, a bot never holds more than 3 positions (this one: 1 at a time).

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build is checked on the VPS.
"""
import csv
import datetime as dt
import re

from tests._paths import CBOT_DIR, REPO_ROOT

SRC = (CBOT_DIR / "EcbWindowBot.cs").read_text(encoding="utf-8")
PREREG = REPO_ROOT / "research" / "results" / "portfolio" / "round24_relaxed" / "prereg_code"
HOLD = (PREREG / "hold_r24.py.txt").read_text(encoding="utf-8")
CLIB = (PREREG / "clib.py.txt").read_text(encoding="utf-8")
SEED = CBOT_DIR / "seeds" / "ecb_usd_top_seed.csv"
SEED_TOOL = (REPO_ROOT / "research" / "tools" / "ecb_usd_top_seed.py").read_text(encoding="utf-8")   # research venv only


def _default(prop: str) -> str:
    m = re.search(r'DefaultValue = ("[^"]*"|[\w.]+)[^\]]*\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no [Parameter] default for {prop}"
    return m.group(1).strip('"')


def _body(signature: str) -> str:
    start = SRC.index(signature)
    open_idx = SRC.index("{", start)
    depth = 0
    for i in range(open_idx, len(SRC)):
        depth += {"{": 1, "}": -1}.get(SRC[i], 0)
        if depth == 0:
            return SRC[open_idx:i + 1]
    raise AssertionError(f"unbalanced braces in {signature}")


def _expr(signature: str) -> str:
    """An expression-bodied member (`... => expr;`): its text up to the semicolon."""
    start = SRC.index(signature)
    return SRC[start:SRC.index(";", start)]


def test_window_is_the_registered_one():
    m = re.search(r'loc_ms\(d, (\d+), (\d+), "LON"\) for d in dates\]\); B = arr\(\[loc_ms\(d, (\d+), (\d+), "LON"\)', HOLD)
    assert (int(_default("EntryHourLondon")), int(_default("EntryMinuteLondon"))) == (int(m.group(1)), int(m.group(2)))
    assert (int(_default("ExitHourLondon")), int(_default("ExitMinuteLondon"))) == (int(m.group(3)), int(m.group(4)))
    assert 'side=-1' in HOLD[HOLD.index("def build_F3"):] and "TradeType.Sell" in _body("private void TryOpen(DateTime day)")


def test_selector_is_the_registered_one():
    call = re.search(r'sel = top_select\(\["(\w+)", "(\w+)"\], WKD, lambda d: loc_ms\(prev_wkd\(d\), (\d+), 0, "NY"\), '
                     r'lambda d: loc_ms\(d, (\d+), 0, "LON"\), (\d+)\)', HOLD)
    assert call, "hold_r24.py.txt's F3 selector call changed shape"
    assert _default("SelectorSymbols") == f"{call.group(1)},{call.group(2)}"
    assert _default("SelectorFromHourNewYork") == call.group(3)
    assert _default("SelectorToHourLondon") == call.group(4)
    assert float(_default("SelectorPercentile")) == float(call.group(5))
    hist, mn = re.search(r"def top_select\(sym_list, d_list, t0_fn, t1_fn, q, hist=(\d+), mn=(\d+)\)", HOLD).groups()
    assert _default("SelectorHistoryWeekdays") == hist and _default("SelectorMinHistory") == mn
    # the history is the previous `hist` weekdays (unknown scores dropped), the threshold numpy's linear percentile
    assert "U[max(0, i - hist):i]" in HOLD and "np.percentile(h, q)" in HOLD and "U[i] >= np.percentile" in HOLD
    decide = _body("private Decision Decide(DateTime day)")
    assert "for (int i = 0; i < SelectorHistoryWeekdays; i++)" in decide and "h = PreviousWeekday(h);" in decide
    assert "history.Count >= SelectorMinHistory" in decide and "d.Score.Value >= d.Threshold.Value" in decide
    pct = _body("public static double Percentile(List<double> values, double q)")
    assert "(s.Count - 1) * q / 100.0" in pct and "(pos - lo)" in pct
    # the score: mean log change over the selector symbols, unknown when any quote is missing
    score = _body("private double? Score(DateTime day, ref string sources)")
    assert "Math.Log(pb.Value / pa.Value)" in score and "return sum / _selectorSymbols.Length;" in score


def test_quote_age_is_the_registered_one():
    back = re.search(r"def quote_k\(sym, ms, back=(\d+)\)", CLIB).group(1)
    assert "k = k_of(ms) - 1" in CLIB and "(k - j <= back)" in CLIB      # bar ending at X, up to `back` bars before
    assert _default("QuoteMaxAgeMinutes") == back == re.search(r"^MAX_AGE_BARS = (\d+)", SEED_TOOL, re.M).group(1)
    assert "x.AddMinutes(-(QuoteMaxAgeMinutes + 1))" in _expr("private DateTime QuoteWindowStart(DateTime x)")


def test_christmas_window_is_the_registered_one():
    assert "return (d.month == 12 and d.day >= 24) or (d.month == 1 and d.day <= 1)" in HOLD
    assert "(d.Month == 12 && d.Day >= 24) || (d.Month == 1 && d.Day == 1)" in SRC
    assert "!IsChristmasWindow(londonDate)" in _expr("private bool IsTradingDay(DateTime londonDate)")


def test_lot_is_fixed_and_never_reads_the_account():
    body = _body("private void TryOpen(DateTime day)")
    assert "Account." not in body
    assert "Lots * Symbol.LotSize" in body


def test_one_position_held_hours_not_days():
    assert int(_default("MaxHoldMinutes")) <= 24 * 60
    assert re.search(r'Max Hold \(minutes\)", Group = "Risk", DefaultValue = \d+, MinValue = \d+, MaxValue = (\d+)\)', SRC)
    assert int(re.search(r'Max Hold \(minutes\)".*MaxValue = (\d+)\)', SRC).group(1)) <= 5 * 24 * 60
    body = _body("private void TryOpen(DateTime day)")
    order = body.index("ExecuteMarketOrderAsync(")
    assert body.index("if (GetBotPositions().Count > 0) return;") < order
    assert body.index("if (_orderPending)") < order and body.index("WindowAlreadyTraded(day)") < order
    assert "ExecuteMarketOrder(" not in SRC and SRC.count("ExecuteMarketOrderAsync(") == 1
    closes = _body("private void CloseDueWindows(DateTime now)")
    assert "now >= exit" in closes and "TimeSpan.FromMinutes(MaxHoldMinutes)" in closes


def test_f3_trades_only_usd_top_days_and_e1_every_trading_day():
    body = _body("private void TryOpen(DateTime day)")
    assert "if (UsdTopOnly && !decision.UsdTop)" in body
    assert body.index("var decision = Decide(day);") < body.index("ExecuteMarketOrderAsync(")


def test_a_late_entry_is_skipped_not_chased():
    # one minute late took E1's whole HOLD net (PREREG_M), so the day is dropped after the grace
    assert int(_default("EntryGraceSeconds")) <= 60
    evaluate = _body("private void Evaluate()")
    assert "if (now > entry.AddSeconds(EntryGraceSeconds))" in evaluate


def test_seed_is_where_the_bot_reads_it_and_covers_a_full_history():
    assert _default("SeedFile") == "/workspace/cBot/seeds/ecb_usd_top_seed.csv"
    rows = list(csv.DictReader(SEED.open()))
    assert rows and set(rows[0]) == {"time_utc", "symbol", "bid", "ask"}
    assert {r["symbol"] for r in rows} == set(_default("SelectorSymbols").split(","))
    days = sorted({dt.datetime.strptime(r["time_utc"], "%Y-%m-%dT%H:%M").date() for r in rows})
    weekdays = [d for d in days if d.weekday() < 5]
    assert len(weekdays) >= 300, "the seed must cover the selector's 250-weekday history and then some"
    for r in rows:
        assert (r["bid"] == r["ask"] == "") or (0 < float(r["bid"]) <= float(r["ask"])), r
