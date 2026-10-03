"""The broker must not read the bot or the strategy off an order: with the tag key the cBot labels their orders with
an opaque id and encrypts the comment ("Trade tags" region), and still recognises what they opened before the key.

The Mac has no dotnet, so like the other cBot tests these read the C# source; scripts/trade_tags.py is the same scheme
in Python and is tested directly. The build itself is checked on the VPS with ctrader-console.
"""
import re

import pytest

from scripts.trade_tags import label, seal, unseal
from tests._paths import CBOT_DIR

BOTS = ["GotobiBot.cs"]
KEY = b"0123456789abcdef-test-key"


def _src(name):
    return (CBOT_DIR / name).read_text(encoding="utf-8")


def _region(src):
    return src[src.index("        #region Trade tags"):src.index("        #region Dashboard commands")]


@pytest.mark.parametrize("bot", BOTS)
def test_orders_carry_the_opaque_label_and_a_sealed_comment(bot):
    src = _src(bot)
    orders = re.findall(r"ExecuteMarketOrder\(([^;]*)\);", src)
    assert len(orders) == 1
    args = [a.strip() for a in orders[0].split(",")]
    assert args[3] == "_label" and args[6].startswith("Seal(")


@pytest.mark.parametrize("bot", BOTS)
def test_the_plain_botid_never_identifies_a_position_alone(bot):
    src = _src(bot)
    assert "Label == BotId" not in src.replace("label == BotId", "")   # only IsOwnLabel compares with BotId
    assert "Label != BotId" not in src
    assert "private bool IsOwnLabel(string label) => label == _label || label == BotId;" in src
    # positions opened before the key (plain BotId) stay this bot's
    assert "if (_label != BotId) own.AddRange(Positions.FindAll(BotId, SymbolName));" in src
    # every comment the bot reads goes through Unseal
    for m in re.finditer(r"\b\w+\.Comment\b", src):
        assert src[m.start() - 7:m.start()] == "Unseal(" or "IsTag(" in src[m.start() - 6:m.start()], \
            src[m.start() - 60:m.end() + 10]


@pytest.mark.parametrize("bot", BOTS)
def test_the_key_is_used_live_only_and_read_before_anything_trades(bot):
    src = _src(bot)
    init = _region(src)
    assert "if (RunningMode != RunningMode.RealTime || string.IsNullOrWhiteSpace(TagKeyFile)) return;" in init
    on_start = src[src.index("protected override void OnStart()"):src.index("protected override void OnTick()")]
    assert on_start.index("InitTradeTags();") < on_start.index("Positions.Closed += OnPositionClosed;")
    assert 'DefaultValue = "/root/ctrader_data/trade_tag_key"' in src


def test_python_mirror_derives_the_labels_the_cbot_does():
    region = _region(_src(BOTS[0]))
    assert '"t" + Convert.ToHexString(TagMac(Encoding.UTF8.GetBytes("label|" + BotId)), 0, 6).ToLowerInvariant()' in region
    assert "private const int TagNonceBytes = 8;" in region
    assert "BitConverter.GetBytes(counter)" in region
    a, b = label(KEY, "cbot-demo-usdjpy-fix-gotobi"), label(KEY, "cbot-live-usdjpy-fix-gotobi")
    assert re.fullmatch(r"t[0-9a-f]{12}", a) and a != b
    assert "gotobi" not in a and label(b"another-key-0123456", "cbot-demo-usdjpy-fix-gotobi") != a


@pytest.mark.parametrize("tag", ["GOTOBI-L 2026-10-05", "DONCH-S 2026-09-27T04:00 risk=87.50"])
def test_sealed_comment_hides_the_tag_and_round_trips(tag):
    sealed = seal(KEY, tag)
    assert " " not in sealed and "GOTOBI" not in sealed and "DONCH" not in sealed
    assert seal(KEY, tag) != sealed                                  # a fresh nonce per order
    assert unseal(KEY, sealed) == tag
    assert unseal(KEY, tag) == tag                                   # a plain comment from before the key
    assert unseal(b"another-key-0123456", sealed) != tag
