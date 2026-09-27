"""The log view colours a line by its level. The log format pads the level to 7 characters (`[ERROR  ]`), so a check
for `[ERROR]` alone never matched and error lines showed like any other."""
import json
import shutil
import subprocess

import pytest

from tests._paths import DASHBOARD_JS

NODE = shutil.which("node")


def _function(src: str, name: str) -> str:
    start = src.index(f"function {name}(")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_each_level_gets_its_colour():
    lines = {
        "error": "20:08:47 [ERROR  ] AgentFxTrading.Portfolio: Failed to close position: boom",
        "critical": "20:08:47 [CRITICAL] AgentFxTrading: disk full",
        "warning": "20:08:47 [WARNING] AgentFxTrading.Requests: HTTP 404 on GET /x: {}",
        "info": "20:08:47 [INFO   ] AgentFxTrading: Position registered",
        "event": "20:08:47 [INFO   ] AgentFxTrading: [PORTFOLIO EVENT] OPEN | 1/bot | EURUSD",
    }
    src = DASHBOARD_JS.read_text(encoding="utf-8")
    script = f"""
{_function(src, "colorizeLogLine")}
const lines = {json.dumps(lines)};
console.log(JSON.stringify(Object.fromEntries(Object.entries(lines).map(([k, l]) => [k, colorizeLogLine(l)]))));
"""
    got = json.loads(subprocess.run([NODE, "-e", script], capture_output=True, text=True, check=True).stdout)
    assert '<span class="log-tag-error">[ERROR  ]</span>' in got["error"]
    assert '<span class="log-tag-error">[CRITICAL]</span>' in got["critical"]
    assert '<span class="log-tag-warn">[WARNING]</span>' in got["warning"]
    assert "log-tag-" not in got["info"]
    assert '<span class="log-tag-event">[PORTFOLIO EVENT]</span>' in got["event"]
