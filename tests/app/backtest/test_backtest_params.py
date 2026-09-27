"""cBot parameters for the Backtest page: the cached `ctrader-cli metadata` schema, the form view
(bot values over defaults, integration groups hidden), and override validation.

The CLI takes enums and time frames by name (verified 2026-09-24: --SlMode=ATR_Multiplier and
--MacroTimeFrame=Hour4 show up as `cmd arg`), so every value is stored in that canonical text form."""
import json

import pytest

from app import backtest_params as bp
from app.backtest_command import parse_run_command
from app.cbot_presets import build_run_command
from tests._paths import FIXTURES_DIR

META_TEXT = (FIXTURES_DIR / "backtest" / "gotobi_metadata.json").read_text()
META = json.loads(META_TEXT)
ACCOUNT = {"slug": "demo-demo", "ctid_email": "trader@example.com", "account_number": "10115236",
           "label": "demo", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd"}


def source(**params):
    src = parse_run_command("cbot-demo-demo-usdjpy-fix-gotobi",
                            build_run_command(ACCOUNT, "gotobi", "USDJPY", "/w", "/r"))
    src.params.update(params)
    return src


# --- metadata output and cache ------------------------------------------------------------------

def test_parse_metadata_output_skips_the_command_echo():
    meta = bp.parse_metadata_output("dotnet metadata /algo/GotobiBot.algo\n" + META_TEXT + "\n")
    assert meta["Name"] == "GotobiBot" and len(meta["Parameters"]) == 26


@pytest.mark.parametrize("text", ["Error: Algo file is not specified", "{not json}", '{"Name": "x"}'])
def test_parse_metadata_output_rejects_garbage(text):
    with pytest.raises(bp.MetadataError):
        bp.parse_metadata_output(text)


def test_cache_runs_metadata_once_per_algo_build(tmp_path):
    algo = tmp_path / "GotobiBot.algo"
    algo.write_bytes(b"build-1")
    calls = []

    def runner(path):
        calls.append(path)
        return META_TEXT

    cache = bp.MetadataCache(tmp_path / "meta", runner)
    first = cache.get(algo)
    assert cache.get(algo) is first and len(calls) == 1
    assert first["sha256"] == bp.algo_sha256(algo)
    assert bp.MetadataCache(tmp_path / "meta", runner).get(algo)["Name"] == "GotobiBot"   # disk cache
    assert len(calls) == 1
    algo.write_bytes(b"build-2")                                                          # rebuilt .algo
    cache.get(algo)
    assert len(calls) == 2


# --- form view ----------------------------------------------------------------------------------

def test_param_view_hides_locked_and_integration_groups():
    view = bp.param_view(META, source())
    assert [g["name"] for g in view["groups"]] == ["General", "Schedule (UTC)", "Risk"]
    keys = {p["key"] for g in view["groups"] for p in g["params"]}
    assert "ShowLogs" in keys and "RiskPerTradeMoney" in keys and "FixMinuteUtc" in keys
    assert not keys & {"BotId", "AccountLabel", "ApiUrl", "TelemetryUrl", "ReportUrl", "CommandPollMs"}
    assert view["locked"]["ApiUrl"] == "http://127.0.0.1:9/disabled" and view["locked"]["BotId"] == "bt-<id>"
    assert view["timeframes"] == list(bp.TIMEFRAMES)
    assert view["algo_build_time"] == "2026-09-27T09:12:05.1234567Z"


def test_param_view_shows_bot_values_over_canonical_defaults():
    view = bp.param_view(META, source(StopAtrMultiplier="2.5"))
    params = {p["key"]: p for g in view["groups"] for p in g["params"]}
    assert (params["StopAtrMultiplier"]["default"], params["StopAtrMultiplier"]["bot_value"]) == ("3.0", "2.5")
    assert params["RiskPerTradeMoney"]["bot_value"] == "50.0"
    assert params["MaxSpreadPips"]["bot_value"] == "3.0"
    assert params["AtrPeriod"]["bot_value"] == "20"
    assert params["TradeLong"]["bot_value"] == "true"
    assert params["SkipDates"]["bot_value"] == "2026-12-25"
    assert (params["FixMinuteUtc"]["min"], params["FixMinuteUtc"]["max"]) == (0, 59)
    assert params["StopAtrMultiplier"]["label"] == "Stop (x ATR of H1)"
    assert params["TradeLong"]["enum_values"] is None


# --- overrides ----------------------------------------------------------------------------------

def test_overrides_are_canonical_and_no_ops_are_dropped():
    changes = bp.validate_overrides(META, source(), {
        "StopAtrMultiplier": 2, "AtrPeriod": "20", "TradeShort": False, "RiskPerTradeMoney": 50,
    })
    assert changes == {
        "StopAtrMultiplier": {"from": "3.0", "to": "2.0"},
        "TradeShort": {"from": "true", "to": "false"},
    }


@pytest.mark.parametrize("key, value, message", [
    ("ApiUrl", "http://evil", "locked"),
    ("TelemetryUrl", "http://evil", "locked"),
    ("CommandPollMs", 2000, "locked"),
    ("BotId", "x", "locked"),
    ("NoSuchParam", 1, "not a parameter"),
    ("AtrPeriod", 1, "minimum"),
    ("AtrPeriod", 7.5, "whole number"),
    ("AtrPeriod", True, "number"),
    ("StopAtrMultiplier", 11, "maximum"),
    ("RiskPerTradeMoney", "abc", "number"),
    ("RiskPerTradeMoney", "inf", "number"),
    ("TradeLong", "yes", "true or false"),
    ("TradeLong", 1, "true or false"),
    ("SkipDates", "2026-12-25\n2026-12-31", "one line"),
])
def test_invalid_overrides_are_rejected(key, value, message):
    with pytest.raises(bp.OverrideError, match=message) as err:
        bp.validate_overrides(META, source(), {key: value})
    assert str(err.value).startswith(key)


def test_enum_and_timeframe_parameters_take_names():
    """Neither current bot declares one, but cTrader metadata can: the CLI takes them by name."""
    enum = {"PropertyName": "SlMode", "Type": "Enum", "EnumValues": {"Swing": 0, "Atr": 1}}
    assert bp.canonical(enum, "Atr") == "Atr" and bp.canonical(enum, 0) == "Swing"
    with pytest.raises(bp.OverrideError, match="one of"):
        bp.canonical(enum, "Nope")
    tf = {"PropertyName": "MacroTimeFrame", "Type": "TimeFrame"}
    assert bp.canonical(tf, {"Type": 0, "Size": 60}) == "Hour" and bp.canonical(tf, "Hour4") == "Hour4"
    with pytest.raises(bp.OverrideError, match="one of"):
        bp.canonical(tf, "h1")


def test_job_params_drop_locked_keys_and_apply_overrides():
    params = bp.job_params(source(), {"StopAtrMultiplier": {"from": "3.0", "to": "2.0"}})
    assert params["StopAtrMultiplier"] == "2.0" and params["RiskPerTradeMoney"] == "50.0"
    for key in ("ApiUrl", "BotId", "AccountLabel", "CommandPollMs"):
        assert key not in params, key
