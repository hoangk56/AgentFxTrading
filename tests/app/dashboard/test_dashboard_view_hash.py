"""The open dashboard view is kept in the URL hash, so F5 and Back/Forward stay on it instead of going to Overview."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, dashboard_page

client = TestClient(app)
NODE = shutil.which("node")
VIEWS = ("dashboard", "backtest", "docker", "ledger", "calendar", "logs")


def _function(src: str, name: str) -> str:
    start = src.index(f"function {name}(")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


def test_nav_links_carry_the_view_hash_and_the_page_restores_it():
    page = dashboard_page(client)
    for name in ("ledger", "logs"):
        assert f'href="#{name}" class="nav-item" data-target="view-{name}"' in page
    # Redesign D step 3: six menu items; Backtest and Dự đoán AI are tabs of Nghiên cứu, still at their own hashes
    assert 'href="#research" class="nav-item" data-target="view-research"' in page
    assert page.count('class="nav-item') == 6 and "nav-item--more" not in page and "nav-more-btn" not in page
    for name in ("research", "paper-desk", "backtest"):
        assert page.count(f'<a href="#{name}" data-target="view-{name}" class="rs-tab') == 3, name
    assert "'view-paper-desk': 'view-research', 'view-backtest': 'view-research'" in page
    # Xếp hạng joined Bot (2026-11-01): no view of its own; its old hash opens Bot (see viewFromHash's aliases)
    assert 'view-leaderboard' not in page and "leaderboard: 'docker'" in page
    assert 'href="#docker" class="nav-item" data-target="view-docker"' in page   # Bots lives in the sidebar
    assert "openView(item.getAttribute('data-target'))" in page and "topbar-docker-btn" not in page
    assert "window.addEventListener('popstate', () => switchView(viewFromHash(location.hash)))" in page
    assert "const initialView = viewFromHash(location.hash);" in page


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_view_from_hash_and_open_view():
    src = DASHBOARD_JS.read_text(encoding="utf-8")
    functions = "\n".join(_function(src, n) for n in ("viewFromHash", "openView"))
    script = f"""
const els = {{}};
for (const v of {json.dumps(VIEWS)}) els['view-' + v] = {{id: 'view-' + v, classList: {{contains: c => c === 'view-section'}}}};
els['view-other'] = {{id: 'view-other', classList: {{contains: () => false}}}};   // an element that is not a view
const document = {{getElementById: id => els[id] || null}};
const location = {{pathname: '/demo/dashboard', search: '?x=1', hash: ''}};
const pushed = [], switched = [];
const history = {{pushState: (s, t, url) => {{ pushed.push(url); location.hash = url.startsWith('#') ? url : ''; }}}};
function switchView(id) {{ switched.push(id); }}
{functions}
const read = Object.fromEntries(['', '#', '#backtest', '#docker', '#dashboard', '#nope', '#other', '#"]', '#calendar', '#gotobi', '#leaderboard']
    .map(h => [h, viewFromHash(h)]));
openView('view-ledger');      // pushes #ledger
openView('view-ledger');      // already there: no new history entry
openView('view-dashboard');   // back to the bare URL
console.log(JSON.stringify({{read, pushed, switched}}));
"""
    out = subprocess.run([NODE, "-e", script], capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    assert got["read"] == {"": "view-dashboard", "#": "view-dashboard", "#backtest": "view-backtest",
                           "#docker": "view-docker", "#dashboard": "view-dashboard", "#nope": "view-dashboard",
                           "#other": "view-dashboard", '#"]': "view-dashboard",
                           "#calendar": "view-calendar", "#gotobi": "view-calendar",
                           "#leaderboard": "view-docker"}
    assert got["pushed"] == ["#ledger", "/demo/dashboard?x=1"]
    assert got["switched"] == ["view-ledger", "view-ledger", "view-dashboard"]
