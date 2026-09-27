"""Repository paths for the test suite.

Tests live at different depths under tests/, so none of them should count ``.parent`` hops from
``__file__``; import these instead (``from tests._paths import CBOT_DIR``). The repo root is on
sys.path through ``pythonpath = .`` in the root pytest.ini.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CBOT_DIR = REPO_ROOT / "cBot"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
DASHBOARD_HTML = REPO_ROOT / "templates" / "dashboard.html"
DASHBOARD_JS = REPO_ROOT / "static" / "js" / "dashboard.js"   # the dashboard's page script


def dashboard_page(client, path: str = "/demo/dashboard") -> str:
    """What the browser gets for the dashboard: the rendered template followed by its page script."""
    html = client.get(path).text
    assert '<script src="/static/js/dashboard.js' in html
    script = client.get("/static/js/dashboard.js")
    assert script.status_code == 200
    return html + "\n" + script.text
