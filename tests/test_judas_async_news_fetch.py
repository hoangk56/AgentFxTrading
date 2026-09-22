"""
Regression guard for C-15 (audit 2026-09-22): news fetch blocked the trading thread.

``OnBarClosed`` -> ``CheckNewsEvents`` -> ``FetchForexFactoryNews`` used SYNCHRONOUS
``HttpWebRequest`` calls: dashboard 5s + ForexFactory JSON 10s + XML fallback 10s,
so up to ~25 seconds on the cBot thread. While it blocks, no ticks are processed --
break-even, trailing stops, ``CheckStructuralInvalidation`` and
``ProcessStagedOrderExecution`` all freeze, during the most volatile seconds of the bar.

``FlowRsiBot`` runs its fetch on a background task from OnStart with a 15-minute
loop. Moving the fetch off the trading thread means ``_newsEvents`` is now written
by one thread and read by another, so it needs a lock -- FlowRsiBot locks it, the
Judas bot never did.
"""

from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AsianRangeJudasSweepBot.cs"


def _src() -> str:
    return CS_PATH.read_text(encoding="utf-8")


def _method_body(signature: str) -> str:
    src = _src()
    start = src.index(signature)
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError(f"Unbalanced braces in {signature!r}")


def test_bar_close_does_not_fetch_news_synchronously():
    body = _method_body("private void CheckNewsEvents()")
    assert "FetchForexFactoryNews();" not in body, (
        "CheckNewsEvents runs on the cBot thread from OnBarClosed and still calls the "
        "synchronous fetch directly - up to ~25s with no tick processing."
    )


def test_startup_does_not_fetch_news_synchronously():
    body = _method_body("private void InitializeNewsFilter()")
    assert "FetchForexFactoryNews();" not in body, (
        "InitializeNewsFilter blocks OnStart on the same synchronous fetch."
    )


def test_news_fetch_runs_on_a_background_task():
    src = _src()
    assert "private void StartNewsFetch()" in src, (
        "There is no background entry point for the news fetch."
    )
    body = _method_body("private void StartNewsFetch()")
    assert "Task.Run" in body, "StartNewsFetch must dispatch to a background task."


def test_overlapping_news_fetches_are_prevented():
    body = _method_body("private void StartNewsFetch()")
    assert "Interlocked.CompareExchange" in body, (
        "Nothing stops a second fetch starting while one is in flight, so two "
        "background threads could rewrite _newsEvents at once."
    )


def test_news_events_are_locked_for_reading():
    body = _method_body("private void CheckNewsEvents()")
    assert "lock (_newsEvents)" in body, (
        "CheckNewsEvents iterates _newsEvents on the trading thread while a background "
        "fetch may be rewriting it - that throws 'Collection was modified'."
    )


def test_news_events_are_locked_for_writing():
    for signature in (
        "private void ParseNewsJson(string json)",
        "private void ParseNewsXml(string xml)",
    ):
        body = _method_body(signature)
        assert "lock (_newsEvents)" in body, (
            f"{signature} rewrites _newsEvents from the background fetch without a lock."
        )
