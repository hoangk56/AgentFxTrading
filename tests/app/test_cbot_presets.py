import calendar
import re
import shlex
from datetime import date, timedelta
from pathlib import Path

import pytest

from app.cbot_presets import (
    DEFAULT_IMAGE, GOTOBI_SKIP_DATES, PRESETS, SESSION_SLUGS, STRATEGIES, SYMBOLS,
    build_run_command, container_name, describe_cell, installed_cells, presets_payload,
)
from tests._paths import REPO_ROOT, CBOT_DIR

ROOT = "/home/forge/AgentFxTrading"
HOME = "/home/forge/ctrader"
DEMO = {"id": 1, "slug": "demo-main", "ctid_email": "me@example.com", "account_number": "10101649",
        "account_type": "demo", "label": "Demo Main", "pwd_file": "/root/ctrader_data/ctid_demo-main_pwd"}
LIVE = {"id": 2, "slug": "live-ic", "ctid_email": "me@example.com", "account_number": "6094347",
        "account_type": "live", "label": "IC", "pwd_file": "/root/ctrader_data/ctid_live-ic_pwd"}

# The matrix: Gotobi on the three JPY pairs the research validated
# (research/results/portfolio/swing_lab_v2_2026-09-27.md) = 3 cells.
GOTOBI_SYMBOLS = ("USDJPY", "EURJPY", "GBPJPY")
EXPECTED_MATRIX = {sym: {"gotobi"} for sym in GOTOBI_SYMBOLS}


def test_matrix_covers_every_strategy_on_its_symbols():
    assert len(PRESETS) == 3
    actual = {}
    for strategy, symbol in PRESETS:
        actual.setdefault(symbol, set()).add(strategy)
    assert actual == EXPECTED_MATRIX
    assert SYMBOLS == ["USDJPY", "EURJPY", "GBPJPY"]


def test_every_cell_is_well_formed():
    assert set(STRATEGIES) == {"gotobi"}
    for (strategy, symbol), cell in PRESETS.items():
        assert strategy in STRATEGIES
        assert symbol == symbol.upper()
        assert cell["period"] == "m15", (strategy, symbol)
        assert cell["session"], (strategy, symbol)
        assert cell["params"], (strategy, symbol)


def test_gotobi_golden_command():
    cmd = build_run_command(DEMO, "gotobi", "GBPJPY", ROOT, HOME)
    assert cmd == (
        "docker run -d --name cbot-demo-main-gbpjpy-fix-gotobi --restart unless-stopped --network host "
        f"-v {ROOT}:/workspace -v {HOME}:/root {DEFAULT_IMAGE} run /workspace/cBot/GotobiBot.algo "
        "--ctid=me@example.com --pwd-file=/root/ctrader_data/ctid_demo-main_pwd --account=10101649 "
        "--symbol=GBPJPY --period=m15 --full-access "
        '--BotId="cbot-demo-main-gbpjpy-fix-gotobi" --ApiUrl="http://127.0.0.1:8000/trade" --AccountLabel="Demo Main" '
        '--RiskPerTradeMoney=100.0 --MaxSpreadPips=4.0 '
        '--SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31"'
    )


def test_gotobi_cells_carry_only_risk_spread_and_skip_dates():
    """The schedule and the stop are the research's (cBot defaults); a cell must not re-tune them per symbol."""
    for sym in GOTOBI_SYMBOLS:
        assert set(PRESETS[("gotobi", sym)]["params"]) == {"RiskPerTradeMoney", "MaxSpreadPips", "SkipDates"}, sym
        assert PRESETS[("gotobi", sym)]["params"]["SkipDates"] == GOTOBI_SKIP_DATES, sym


def _is_gotobi(d: date) -> bool:
    """GotobiBot.IsGotobi: the 5th/10th/15th/20th/25th or the month's last day, a weekend one moved to the Friday before."""
    last = calendar.monthrange(d.year, d.month)[1]
    for day in (5, 10, 15, 20, 25, last):
        moved = date(d.year, d.month, day)
        while moved.weekday() >= 5:
            moved -= timedelta(days=1)
        if moved == d:
            return True
    return False


def test_gotobi_skip_dates_are_gotobi_days_the_bot_parses():
    # A date that is not a gotobi day, or not yyyy-MM-dd, would be skipped silently (the cBot only logs it), so the
    # holiday it was meant for would be traded.
    dates = GOTOBI_SKIP_DATES.split(",")
    assert dates == sorted(set(dates))
    for text in dates:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", text), text
        assert _is_gotobi(date.fromisoformat(text)), f"{text} is not a gotobi day"
    # The cBot's default, which a --SkipDates value replaces (broker closed at the fix on Christmas 2026).
    assert "2026-12-25" in dates


def test_container_name_carries_the_session():
    assert container_name("demo-main", "gotobi", "USDJPY") == "cbot-demo-main-usdjpy-fix-gotobi"
    assert container_name("live-ic", "gotobi", "GBPJPY") == "cbot-live-ic-gbpjpy-fix-gotobi"


def test_every_preset_session_has_a_slug_in_its_name():
    for (strategy, symbol), cell in PRESETS.items():
        name = container_name("demo-main", strategy, symbol)
        assert f"-{SESSION_SLUGS[cell['session']]}" in name, (strategy, symbol)
        assert name.endswith(SESSION_SLUGS[cell["session"]] + STRATEGIES[strategy]["suffix"]), name


def test_live_vs_demo_naming():
    # /api/bots detects live bots by "live-" in the name; demo names must not contain it
    assert "live-" in container_name("live-ic", "gotobi", "USDJPY")
    assert "live" not in container_name("demo-main", "gotobi", "USDJPY")


def test_every_command_survives_shlex_and_has_docker_essentials():
    for (strategy, symbol) in PRESETS:
        cmd = build_run_command(LIVE, strategy, symbol, ROOT, HOME)
        assert "\n" not in cmd and "\\" not in cmd
        parts = shlex.split(cmd)
        assert parts[:3] == ["docker", "run", "-d"]
        assert "--name" in parts and parts[parts.index("--name") + 1] == container_name("live-ic", strategy, symbol)
        assert parts.count("-v") == 2
        assert f"{ROOT}:/workspace" in parts and f"{HOME}:/root" in parts
        assert f"--symbol={symbol}" in parts
        assert f"--period={PRESETS[(strategy, symbol)]['period']}" in parts
        assert f"--BotId={container_name('live-ic', strategy, symbol)}" in parts   # quotes stripped by shlex
        assert "--AccountLabel=IC" in parts
        assert f"/workspace/cBot/{STRATEGIES[strategy]['algo']}" in parts


def test_custom_image_and_describe_cell():
    cmd = build_run_command(DEMO, "gotobi", "EURJPY", ROOT, HOME, image="ghcr.io/spotware/ctrader-console:1.2")
    assert " ghcr.io/spotware/ctrader-console:1.2 run " in cmd
    assert describe_cell("gotobi", "EURJPY", "Demo Main") == "Gotobi Fix EURJPY m15 — Demo Main"


def test_presets_payload_shape():
    payload = presets_payload()
    assert payload["strategies"] == STRATEGIES
    assert payload["symbols"] == SYMBOLS
    assert len(payload["cells"]) == 3
    cell = next(c for c in payload["cells"] if c["symbol"] == "GBPJPY")
    assert cell == {"symbol": "GBPJPY", "strategy": "gotobi", "period": "m15", "session": "Tokyo fix"}
    for c in payload["cells"]:
        assert set(c) == {"symbol", "strategy", "period", "session"}
        assert "params" not in c


def test_installed_cells_maps_config_names_back_to_cell_and_account():
    names = {
        "cbot-demo-main-usdjpy-fix-gotobi",       # DEMO gotobi USDJPY
        "cbot-live-ic-usdjpy-fix-gotobi",         # LIVE gotobi USDJPY (same cell, second account)
        "cbot-live-ic-ethusd-h4-donchian",        # the removed Crypto Donchian: not a preset name, ignored
        "cbot-live-ic-xauusd-newyork",            # a removed strategy's name: not a preset name, ignored
        "cbot-manual-thing",                      # hand-made config: not a preset name, ignored
    }
    rows = installed_cells([DEMO, LIVE], names)
    assert rows == [
        {"symbol": "USDJPY", "strategy": "gotobi", "name": "cbot-demo-main-usdjpy-fix-gotobi",
         "account_id": 1, "account_label": "Demo Main", "account_type": "demo"},
        {"symbol": "USDJPY", "strategy": "gotobi", "name": "cbot-live-ic-usdjpy-fix-gotobi",
         "account_id": 2, "account_label": "IC", "account_type": "live"},
    ]


def test_installed_cells_is_empty_without_accounts_or_configs():
    assert installed_cells([], {"cbot-demo-main-usdjpy-fix-gotobi"}) == []
    assert installed_cells([DEMO, LIVE], set()) == []


# --- docs ↔ preset drift guard ---------------------------------------------------
# docs/docker-instances.md spells out all 3 cells as `docker run` commands. Those blocks are what a
# user copies by hand, so a preset edit that forgets them ships docs that silently disagree with what
# the dashboard generates. Compare the strategy flags only: the doc uses placeholder credentials and a
# `demo` account slug.
INSTANCES_DOC = REPO_ROOT / "docs" / "docker-instances.md"
_INFRA_FLAGS = {"ctid", "pwd-file", "account", "symbol", "period", "full-access",
                "BotId", "ApiUrl", "AccountLabel"}
_ALGO_TO_STRATEGY = {spec["algo"]: name for name, spec in STRATEGIES.items()}


def _strategy_flags(command: str) -> dict:
    """The tuned `--Flag=value` pairs of a docker run, with line continuations folded and infra dropped."""
    flat = re.sub(r"\s+", " ", command.replace("\\\n", " "))
    return {key: value for key, value in re.findall(r'--([A-Za-z0-9_-]+)=("[^"]*"|\S+)', flat)
            if key not in _INFRA_FLAGS}


def _documented_cells(path: Path) -> dict:
    """(strategy, symbol) -> strategy flags, for every cBot `docker run` block in one markdown file."""
    cells = {}
    for block in re.findall(r"```bash\n(.*?)```", path.read_text(), re.S):
        algo = re.search(r"/workspace/cBot/(\S+\.algo)", block)
        symbol = re.search(r"--symbol=(\S+)", block)
        if not (algo and symbol) or algo.group(1) not in _ALGO_TO_STRATEGY:
            continue
        key = (_ALGO_TO_STRATEGY[algo.group(1)], symbol.group(1))
        assert key not in cells, f"{path.name} documents {key} twice"
        cells[key] = _strategy_flags(block)
    return cells


def test_instances_doc_exists():
    assert INSTANCES_DOC.is_file(), "docs/docker-instances.md is the instance catalog; it must exist"


def test_instances_doc_covers_every_cell():
    assert set(_documented_cells(INSTANCES_DOC)) == set(PRESETS), (
        "docs/docker-instances.md must document all 3 preset cells, no more and no fewer")


@pytest.mark.parametrize(("strategy", "symbol"), sorted(PRESETS), ids=lambda v: v)
def test_instances_doc_matches_the_presets(strategy, symbol):
    documented = _documented_cells(INSTANCES_DOC)[(strategy, symbol)]
    generated = _strategy_flags(build_run_command(DEMO, strategy, symbol, ROOT, HOME))
    assert documented == generated, (
        f"docs/docker-instances.md disagrees with app/cbot_presets.py for {strategy} {symbol}: "
        f"{ {k: (generated.get(k), documented.get(k)) for k in set(generated) | set(documented) if generated.get(k) != documented.get(k)} }"
    )


# --- no symbol-name branching in the cBots ------------------------------------------
# Per-symbol tuning lives in the presets above. A cBot that branches on SymbolName ("XAU", "JPY",
# "US30") silently overrides the preset flags and cannot be swept in a backtest.
_SYMBOL_BRANCH = re.compile(
    r'Contains\("(XAU|GOLD|XAG|SILVER|JPY|US30|DJ30|USTEC|NAS100|DE40|GER40|UK100|GB100|BTC|ETH)"\)')


@pytest.mark.parametrize("cs_name", ["GotobiBot.cs"])
def test_cbots_do_not_branch_on_the_symbol_name(cs_name):
    src = (CBOT_DIR / cs_name).read_text(encoding="utf-8")
    hits = [m.group(0) for m in _SYMBOL_BRANCH.finditer(src)]
    assert not hits, f"{cs_name} branches on the symbol name {hits}; make it a [Parameter] and set it in the presets"
