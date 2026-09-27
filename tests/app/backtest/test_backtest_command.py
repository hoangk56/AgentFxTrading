"""Backtest container specs: an installed bot's run_command as a backtest source, and the safety rules
of the `docker run … backtest` spec (docs/superpowers/specs/2026-09-24-backtest-page-design.md).

A cBot that reached the server while backtesting would write fake trades into production, so these tests
pin that a backtest container never shares the host network, never sees more than its three mounts, and
always runs with every server URL disabled."""
import re
from pathlib import Path

import pytest

from app import backtest_command as bc
from app.cbot_presets import build_run_command

ACCOUNT = {"slug": "demo-demo", "ctid_email": "trader@example.com", "account_number": "10115236",
           "label": "demo", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd"}


def preset(strategy="gotobi", symbol="USDJPY"):
    return build_run_command(ACCOUNT, strategy, symbol, "/home/forge/AgentFxTrading", "/home/forge/ctrader")


@pytest.fixture
def homes(tmp_path):
    project = tmp_path / "project"
    (project / "cBot").mkdir(parents=True)
    (project / "cBot" / "GotobiBot.algo").write_bytes(b"algo")
    ctrader = tmp_path / "ctrader"
    (ctrader / "ctrader_data").mkdir(parents=True)
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").write_text("s3cret-password")
    return project, ctrader


def make_job(**over):
    job = {"id": 7, "strategy": "gotobi", "algo": "GotobiBot.algo", "ctid_email": "trader@example.com",
           "account": "10115236", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd",
           "symbol": "USDJPY", "period": "m15", "start_date": "2026-07-24", "end_date": "2026-09-23",
           "data_mode": "ticks", "spread_pips": None, "balance": 10000.0,
           "params": {"MaxSpreadPips": "3.0", "StopAtrMultiplier": "2.0", "CommandPollMs": "2000",
                      "ApiUrl": "http://127.0.0.1:8000/trade", "BotId": "cbot-demo-demo-usdjpy-fix-gotobi"}}
    job.update(over)
    return job


def spec_for(homes, **over):
    project, ctrader = homes
    return bc.build_container_spec(make_job(**over), project, ctrader)


# --- parsing ------------------------------------------------------------------------------------

def test_parses_a_preset_gotobi_command():
    src = bc.parse_run_command("cbot-demo-demo-usdjpy-fix-gotobi", preset())
    assert src.algo == "GotobiBot.algo" and src.strategy == "gotobi"
    assert (src.ctid, src.account, src.symbol, src.period) == ("trader@example.com", "10115236", "USDJPY", "m15")
    assert src.pwd_file == "/root/ctrader_data/ctid_demo-demo_pwd"
    assert src.params["BotId"] == "cbot-demo-demo-usdjpy-fix-gotobi"      # quotes stripped
    assert src.params["RiskPerTradeMoney"] == "50.0"
    assert src.params["MaxSpreadPips"] == "3.0"
    assert "full-access" not in src.params and "ctid" not in src.params


def test_parses_a_multiline_hand_written_command():
    cmd = ("docker run -d --name cbot-x --network host \\\n  -v /home/forge/AgentFxTrading:/workspace \\\n"
           "  ghcr.io/spotware/ctrader-console:latest run /workspace/cBot/GotobiBot.algo \\\n"
           "  --ctid=trader@example.com --pwd-file=/root/ctrader_data/pw --account=1 \\\n"
           "  --symbol=XAUUSD --period=m15 --full-access --StopAtrMultiplier=2.5 -e")
    src = bc.parse_run_command("cbot-x", cmd)
    assert src.symbol == "XAUUSD" and src.params == {"StopAtrMultiplier": "2.5"}


@pytest.mark.parametrize("cmd, message", [
    ("docker run -d ghcr.io/spotware/ctrader-console:latest accounts", "run <file>.algo"),
    ("docker run img run /workspace/cBot/GotobiBot.algo --pwd-file=/root/ctrader_data/pw --account=1 "
     "--symbol=EURUSD --period=m15", "--ctid"),
    ("docker run img run /root/elsewhere/GotobiBot.algo --ctid=a@b.c --pwd-file=/root/ctrader_data/pw "
     "--account=1 --symbol=EURUSD --period=m15", "/workspace/cBot"),
    ('docker run img run /workspace/cBot/GotobiBot.algo --ctid="unterminated', "does not parse"),
])
def test_rejects_commands_it_cannot_use(cmd, message):
    with pytest.raises(bc.SourceError, match=re.escape(message)):
        bc.parse_run_command("x", cmd)


# --- host paths ---------------------------------------------------------------------------------

def test_password_file_maps_into_ctrader_home(homes):
    _, ctrader = homes
    host = bc.pwd_host_path("/root/ctrader_data/ctid_demo-demo_pwd", ctrader)
    assert host == (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").resolve()


@pytest.mark.parametrize("pwd_file", [
    "/root/ctrader_data/../.ssh/id_rsa", "/root/other/ctid_pwd", "/root/ctrader_data/", "ctid_pwd",
    "/root/ctrader_data/missing_pwd",
])
def test_password_file_cannot_leave_ctrader_data(homes, pwd_file):
    with pytest.raises(bc.SourceError):
        bc.pwd_host_path(pwd_file, homes[1])


def test_password_file_symlink_out_of_ctrader_data_is_refused(homes, tmp_path):
    _, ctrader = homes
    outside = tmp_path / "outside"
    outside.write_text("x")
    (ctrader / "ctrader_data" / "link_pwd").symlink_to(outside)
    with pytest.raises(bc.SourceError, match="not found"):
        bc.pwd_host_path("/root/ctrader_data/link_pwd", ctrader)


# --- describe_source ----------------------------------------------------------------------------

def test_describe_gotobi_source_is_supported(homes):
    project, ctrader = homes
    (project / "cBot" / "GotobiBot.algo").write_bytes(b"algo")
    name = "cbot-demo-demo-usdjpy-fix-gotobi"
    row = bc.describe_source(name, preset("gotobi", "USDJPY"), project, ctrader)
    assert row == {"name": name, "strategy": "gotobi", "symbol": "USDJPY", "period": "m15",
                   "account_label": "demo", "supported": True, "reason": ""}


def test_gotobi_backtest_never_reaches_the_server(homes):
    project, ctrader = homes
    (project / "cBot" / "GotobiBot.algo").write_bytes(b"algo")
    src = bc.parse_run_command("cbot-demo-demo-usdjpy-fix-gotobi", preset("gotobi", "USDJPY"))
    job = make_job(strategy="gotobi", algo="GotobiBot.algo", symbol="USDJPY", params=dict(src.params))
    command = bc.build_container_spec(job, project, ctrader)["command"]
    locked = bc.locked_params("gotobi", 7)
    assert command[-len(locked):] == [f"--{k}={v}" for k, v in locked.items()]
    for key in ("ApiUrl", "TelemetryUrl", "ReportUrl"):
        assert f"--{key}={bc.DISABLED_URL}" in command
    assert "--CommandPollMs=0" in command
    assert "--ApiUrl=http://127.0.0.1:8000/trade" not in command
    assert "--RiskPerTradeMoney=50.0" in command


def test_donchian_backtest_is_supported_and_never_reaches_the_server(homes):
    project, ctrader = homes
    (project / "cBot" / "CryptoDonchianBot.algo").write_bytes(b"algo")
    name = "cbot-demo-demo-btcusd-h4-donchian"
    row = bc.describe_source(name, preset("donchian", "BTCUSD"), project, ctrader)
    assert row == {"name": name, "strategy": "donchian", "symbol": "BTCUSD", "period": "h1",
                   "account_label": "demo", "supported": True, "reason": ""}
    src = bc.parse_run_command(name, preset("donchian", "BTCUSD"))
    job = make_job(strategy="donchian", algo="CryptoDonchianBot.algo", symbol="BTCUSD", period="h1",
                   params=dict(src.params))
    command = bc.build_container_spec(job, project, ctrader)["command"]
    locked = bc.locked_params("donchian", 7)
    assert command[-len(locked):] == [f"--{k}={v}" for k, v in locked.items()]
    for key in ("ApiUrl", "TelemetryUrl", "ReportUrl"):
        assert f"--{key}={bc.DISABLED_URL}" in command
    assert "--CommandPollMs=0" in command
    assert "--RiskPerTradeMoney=100.0" in command


def test_describe_other_bots_as_unsupported(homes):
    cmd = preset().replace("/workspace/cBot/GotobiBot.algo", "/workspace/cBot/SomeOtherBot.algo")
    row = bc.describe_source("x", cmd, *homes)
    assert row["supported"] is False and row["reason"] == bc.UNSUPPORTED_REASON
    assert row["strategy"] is None


def test_describe_reports_missing_password_file_and_unbuilt_algo(homes):
    project, ctrader = homes
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").unlink()
    assert bc.describe_source("x", preset(), project, ctrader)["reason"] == "password file not found"
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").write_text("pw")
    (project / "cBot" / "GotobiBot.algo").unlink()
    assert bc.describe_source("x", preset(), project, ctrader)["reason"] == "GotobiBot.algo is not built"


def test_describe_unparsable_command():
    row = bc.describe_source("x", "echo hello", Path("/nonexistent"), Path("/nonexistent"))
    assert row["supported"] is False and "run <file>.algo" in row["reason"]


# --- safety invariants of build_container_spec (spec: "Safety invariants") ----------------------

def test_invariant_1_bridge_network_only(homes):
    spec = spec_for(homes)
    assert spec["network_mode"] == "bridge"
    assert set(spec) == {"image", "name", "command", "labels", "network_mode", "mem_limit", "nano_cpus",
                         "cpu_shares", "volumes", "detach", "auto_remove"}


def test_invariant_2_only_three_mounts(homes):
    project, ctrader = homes
    assert spec_for(homes)["volumes"] == {
        str(project / "cBot" / "GotobiBot.algo"): {"bind": "/algo/GotobiBot.algo", "mode": "ro"},
        str((ctrader / "ctrader_data" / "ctid_demo-demo_pwd").resolve()): {"bind": "/secrets/pwd", "mode": "ro"},
        "agentfx-bt-cache": {"bind": "/bt-cache", "mode": "rw"},
    }


def test_invariant_3_locked_params_come_last_and_win(homes):
    command = spec_for(homes)["command"]
    locked = bc.locked_params("gotobi", 7)
    assert command[-len(locked):] == [f"--{k}={v}" for k, v in locked.items()]
    assert "--CommandPollMs=2000" not in command
    assert "--ApiUrl=http://127.0.0.1:8000/trade" not in command
    assert "--BotId=cbot-demo-demo-usdjpy-fix-gotobi" not in command
    assert "--BotId=bt-7" in command and "--AccountLabel=backtest" in command
    assert "--StopAtrMultiplier=2.0" in command and "--MaxSpreadPips=3.0" in command


def test_invariant_4_name_and_label(homes):
    spec = spec_for(homes)
    assert spec["name"] == "bt-7" and spec["labels"] == {"agentfx.backtest": "7"}


def test_invariant_5_resource_limits(homes):
    spec = spec_for(homes)
    assert (spec["mem_limit"], spec["nano_cpus"], spec["cpu_shares"]) == ("1g", 2_000_000_000, 256)
    assert spec["detach"] is True and spec["auto_remove"] is False


def test_invariant_6_list_command_without_secrets(homes):
    command = spec_for(homes)["command"]
    assert isinstance(command, list) and all(isinstance(a, str) for a in command)
    assert command[:2] == ["backtest", "/algo/GotobiBot.algo"]
    assert "--pwd-file=/secrets/pwd" in command
    joined = " ".join(command)
    assert "s3cret-password" not in joined


def test_dates_balance_and_report_flags(homes):
    command = spec_for(homes)["command"]
    for flag in ("--start=24/07/2026", "--end=23/09/2026", "--data-mode=ticks", "--data-dir=/bt-cache",
                 "--balance=10000", "--commission-auto", "--report-json=/tmp/report.json", "--full-access",
                 "--exit-on-stop", "--symbol=USDJPY", "--period=m15", "--account=10115236"):
        assert flag in command, flag
    assert not any(a.startswith("--spread=") for a in command)


def test_m1_adds_the_spread(homes):
    command = spec_for(homes, data_mode="m1", spread_pips=1.2)["command"]
    assert "--data-mode=m1" in command and "--spread=1.2" in command


@pytest.mark.parametrize("over", [{"strategy": "other"}, {"data_mode": "tick-csv"}, {"algo": "../evil.algo"}])
def test_refuses_jobs_it_must_not_run(homes, over):
    with pytest.raises(bc.SourceError):
        spec_for(homes, **over)
