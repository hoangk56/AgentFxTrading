"""
Regression guards for C-12 and C-14 (audit 2026-09-22): the XML news fallback.

C-12 (FlowRsiBot) -- ForexFactory's XML feed writes Eastern Time with NO offset.
``DateTime.TryParse(..., DateTimeStyles.AdjustToUniversal)`` on an offset-less
string treats it as machine time, and the containers run TZ=UTC, so every event
was shifted 4-5 hours EARLY. NFP at 08:30 ET (12:30 UTC) was filed as 08:30 UTC;
the 30-minute block expired at 09:00 UTC and the bot traded straight through the
real release. The JSON path is correct because its `date` carries an offset.

C-14 (AsianRangeJudasSweepBot) -- ``TryFetchXmlFallback`` read the body into a
local and never parsed it, yet still set ``_lastNewsFetchTime`` and printed
"fetched successfully". ``CheckNewsEvents`` only refetches after 6 hours, so one
JSON failure disabled the news filter completely for 6 hours with a log line
claiming success.

Both need the same thing: convert ET to UTC explicitly, and never report success
for a fetch that produced no usable events.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _src(cs_name: str) -> str:
    return (ROOT / "cBot" / cs_name).read_text(encoding="utf-8")


def _method_body(cs_name: str, signature: str) -> str:
    src = _src(cs_name)
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
    raise AssertionError(f"Unbalanced braces in {cs_name} {signature!r}")


# ── C-12: FlowRsiBot must convert Eastern Time explicitly ──

def test_xml_times_are_not_parsed_as_machine_local_time():
    body = _method_body("FlowRsiBot.cs", "private void ParseNewsEventsFromXml(string xml)")
    assert "DateTimeStyles.AdjustToUniversal" not in body, (
        "AdjustToUniversal on an offset-less Eastern timestamp treats it as machine "
        "time (TZ=UTC in the containers), shifting every event 4-5 hours early."
    )


def test_xml_times_are_converted_from_eastern_to_utc():
    body = _method_body("FlowRsiBot.cs", "private void ParseNewsEventsFromXml(string xml)")
    src = _src("FlowRsiBot.cs")
    assert "ConvertTimeToUtc" in body, (
        "ForexFactory XML times are US Eastern and must be converted to UTC explicitly."
    )
    assert "America/New_York" in src or "Eastern Standard Time" in src, (
        "No US Eastern time zone is resolved anywhere - the conversion has no source zone."
    )


def test_unresolvable_timezone_skips_rather_than_recording_wrong_times():
    body = _method_body("FlowRsiBot.cs", "private void ParseNewsEventsFromXml(string xml)")
    assert "return;" in body, (
        "If the Eastern zone cannot be resolved the parser must bail out. Recording "
        "events at an unknown offset is worse than having none."
    )


# ── C-14: Judas must actually parse, and must not fake success ──

def test_judas_xml_fallback_parses_what_it_downloads():
    body = _method_body("AsianRangeJudasSweepBot.cs", "private void TryFetchXmlFallback()")
    assert "ParseNewsXml" in body, (
        "TryFetchXmlFallback reads the response into a local and discards it - "
        "_newsEvents stays empty and IsNewsPauseActive always returns false."
    )


def test_judas_does_not_suppress_retries_after_a_fruitless_fetch():
    body = _method_body("AsianRangeJudasSweepBot.cs", "private void TryFetchXmlFallback()")
    stamp_idx = body.index("_lastNewsFetchTime = DateTime.UtcNow")
    preceding = body[:stamp_idx]
    assert "_newsEvents.Count" in preceding, (
        "_lastNewsFetchTime is set unconditionally, so CheckNewsEvents will not refetch "
        "for 6 hours - the news filter stays off with no sign of trouble."
    )


def test_judas_does_not_claim_success_without_events():
    body = _method_body("AsianRangeJudasSweepBot.cs", "private void TryFetchXmlFallback()")
    assert "XML Fallback news fetched successfully." not in body, (
        'The unconditional "fetched successfully" line is what made this invisible '
        "in the logs."
    )


def test_judas_xml_uses_the_same_eastern_conversion():
    src = _src("AsianRangeJudasSweepBot.cs")
    assert "ConvertTimeToUtc" in src, (
        "The Judas XML parser must convert Eastern Time to UTC like FlowRsiBot's, "
        "or it reintroduces C-12 in a second bot."
    )
    assert "using System.Xml.Linq;" in src, (
        "XDocument is used without importing System.Xml.Linq - this will not compile."
    )


@pytest.mark.parametrize("cs_name", ["FlowRsiBot.cs", "AsianRangeJudasSweepBot.cs"])
def test_unqualified_bcl_types_in_the_xml_parsers_are_imported(cs_name):
    """CultureInfo/DateTimeStyles live in System.Globalization; unqualified use needs the using."""
    src = _src(cs_name)
    uses_unqualified = any(
        tok in src.replace("System.Globalization.", "")
        for tok in ("CultureInfo.InvariantCulture", "DateTimeStyles.")
    )
    if uses_unqualified:
        assert "using System.Globalization;" in src, (
            f"{cs_name} uses CultureInfo/DateTimeStyles unqualified without importing "
            f"System.Globalization - this will not compile."
        )
