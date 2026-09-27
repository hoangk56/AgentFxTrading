"""The portfolio manager has one home, app.portfolio.portfolio_manager, read through
get_portfolio_manager() at call time. A module that keeps its own reference (or a test that
patches a copy such as app.server.portfolio_manager) splits /trade from the gates it calls:
the test then checks one manager while half the code talks to another."""
import re

from tests._paths import REPO_ROOT

# `portfolio_manager.<attr>` not preceded by `get_` or a dot, i.e. a module-level copy in use
_BARE_USE = re.compile(r"(?<![\w.])portfolio_manager\.\w")


def test_app_code_reads_the_manager_through_the_getter():
    offenders = []
    for path in sorted((REPO_ROOT / "app").glob("*.py")):
        if path.name == "portfolio.py":        # the owner of the global
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _BARE_USE.search(line.split("#", 1)[0]):
                offenders.append(f"{path.name}:{n}: {line.strip()}")
    assert not offenders, "use get_portfolio_manager():\n" + "\n".join(offenders)


def test_tests_patch_the_manager_where_it_lives():
    patterns = ('"app.server.portfolio_manager"', 'server_mod, "portfolio_manager"', "server, \"portfolio_manager\"")
    offenders = [f"{p.relative_to(REPO_ROOT)}: {pat}"
                 for p in sorted((REPO_ROOT / "tests").rglob("test_*.py")) if p.name != "test_portfolio_singleton.py"
                 for pat in patterns if pat in p.read_text(encoding="utf-8")]
    assert not offenders, "patch app.portfolio.portfolio_manager instead:\n" + "\n".join(offenders)
