"""F0 forward runner (round66_fast_execution/F0/coord/forward/fwd_f0.py): the registered code is unchanged, the runner
changes only folder / date literals of the scripts it executes, its blind event builder equals F's rule.trades, and
the evaluation date rule refuses until the PREREG's conditions hold. No market data is needed."""
import ast
import importlib.util
import re
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
F0 = ROOT / "research" / "results" / "portfolio" / "round66_fast_execution" / "F0"
RUNNER = F0 / "coord" / "forward" / "fwd_f0.py"


@pytest.fixture(scope="module")
def fwd():
    spec = importlib.util.spec_from_file_location("fwd_f0_under_test", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_registered_files_still_hash_as_in_the_prereg(fwd):
    text = (F0 / "PREREG_F0_bar_close_fade.md").read_text(encoding="utf-8")
    listed = dict(re.findall(r"^- `(research/[^`]+)` ([0-9a-f]{16})$", text, re.M))
    assert fwd.HASHED.items() <= listed.items()
    for rel, h in {**fwd.HASHED, **fwd.EXTRA_HASHED}.items():
        assert fwd.sha16(ROOT / rel) == h, rel


def test_runner_hash_is_appended_to_the_prereg(fwd):
    text = (F0 / "PREREG_F0_bar_close_fade.md").read_text(encoding="utf-8")
    assert fwd.sha16(RUNNER) in text
    assert fwd.result_section_empty()


def _literals(node):
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant)]


def _masked(src):
    tree = ast.parse(src.strip())
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant):
            n.value = None
    return ast.dump(tree)


def test_patches_change_only_folder_and_date_literals(fwd):
    end = 1801440000000
    for fname, pairs in fwd.patches(end).items():
        src = (Path(fwd.FC) / fname).read_text(encoding="utf-8")
        for old, new in pairs:
            assert src.count(old) == 1, old
            expr = lambda s: s if "=" in s.split("(")[0] else f"_x = {s}"  # noqa: E731
            assert _masked(expr(old)) == _masked(expr(new)), (old, new)
            changed = [(a, b) for a, b in zip(_literals(ast.parse(expr(old))), _literals(ast.parse(expr(new)))) if a != b]
            assert changed, (old, new)
            for a, b in changed:
                if isinstance(a, str):
                    assert isinstance(b, str) and b.startswith("f0_forward"), (a, b)
                else:
                    assert isinstance(a, int) and isinstance(b, int) and b in (end, fwd.FWD0), (a, b)


def _synthetic(tmp_path, rng):
    """3 days of 1m bars for BTC and 4 coins with planted wicks: idio, BTC-driven, thin bar, failed guard, repeats
    within 60 bars, one too close to the end and one whose exit falls in a gap > 5 minutes."""
    T0 = 1717200000000  # 2024-06-01
    NM = 3 * 1440
    m = T0 // 60000 + np.arange(NM)
    names = ["BTCUSDT", "AAAUSDT", "BBBUSDT", "CCCUSDT", "DDDUSDT"]
    for k, s in enumerate(names):
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, NM)))
        o = np.r_[c[0], c[:-1]]
        n = np.full(NM, 50); qv = np.full(NM, 1e5)
        keep = np.ones(NM, bool)
        if s == "BTCUSDT":
            c[2000:] *= 0.95; o[2001:] *= 0.95  # BTC drop at 2000: coins dropping then are not idiosyncratic
        else:
            for e, sgn in ((300 + 7 * k, -1), (330 + 7 * k, -1), (900, 1), (2000, -1), (1500 + k, -1), (NM - 40, -1)):
                c[e:] *= 1 + sgn * 0.06; o[e + 1:] *= 1 + sgn * 0.06  # next open stays beyond half-way
            n[900] = 3 if s == "AAAUSDT" else 50  # thin event bar
            if s == "BBBUSDT":
                o[1503] = c[1501]  # guard fails at e = 1502: bar e+1 opens back at the pre-move level
            if s == "CCCUSDT":
                keep[1503 + 55:1503 + 70] = False  # exit gap > 5 min
        z = dict(m=m[keep].astype(np.int32), o=o[keep].astype(np.float32), h=np.maximum(o, c)[keep].astype(np.float32),
                 l=np.minimum(o, c)[keep].astype(np.float32), c=c[keep].astype(np.float32), n=n[keep].astype(np.int32),
                 qv=qv[keep].astype(np.float32))
        np.savez(tmp_path / f"{s}_2024-06.npz", **z)
    return T0, T0 + NM * 60000, names


def test_events_only_equals_rule_trades_on_synthetic_data(fwd, tmp_path, monkeypatch):
    rng = np.random.default_rng(66)
    T0, END, names = _synthetic(tmp_path, rng)
    monkeypatch.setattr(fwd.rule, "FUND_DIRS", [str(tmp_path)])
    nd = (END - fwd.rule.H0) // fwd.DAY + 1
    U = np.ones((len(names), nd), bool); RK = np.tile(np.arange(len(names))[:, None] * 7, (1, nd))
    T = fwd.rule.trades(str(tmp_path), U, RK, names, T0, END, names, END)
    E = fwd.events_only(str(tmp_path), U, RK, names, T0, END, names, END)
    a = sorted(zip(T["sym"].astype(int).tolist(), T["t"].astype(int).tolist()))
    b = sorted(zip(E["sym"].tolist(), E["t"].tolist()))
    assert len(a) >= 6
    assert a == b


def test_eval_gate_follows_the_registered_date_rule(fwd):
    D = fwd.DAY
    feb1, mar1 = 1801440000000, 1803859200000
    assert fwd.eval_gate(feb1 - D, feb1, lambda m: 999)[0] is None          # month not over yet
    assert fwd.eval_gate(feb1, feb1 - D, lambda m: 999)[0] is None          # data not complete through Jan 31
    assert fwd.eval_gate(feb1, feb1, lambda m: 999)[0] == feb1               # 3 full months and n >= 333
    assert fwd.eval_gate(feb1, feb1, lambda m: 300)[0] is None               # n short: wait for the next month end
    assert fwd.eval_gate(mar1, mar1, lambda m: 300 if m < mar1 else 333)[0] == mar1
    assert fwd.eval_gate(fwd.CAP_END - D, fwd.CAP_END, lambda m: 100)[0] is None
    assert fwd.eval_gate(fwd.CAP_END, fwd.CAP_END, lambda m: 100)[0] == fwd.CAP_END
    assert fwd.full_months(feb1) == 3 and fwd.full_months(feb1 - D) == 2


def test_progress_prints_counts_only(fwd):
    t = np.array([10, 900, 5000]); day = (fwd.FWD0 + t * 60000) // fwd.DAY
    txt = "\n".join(fwd.progress_lines(t, day, fwd.FWD0 + 4 * fwd.DAY, 3)).lower()
    assert "events so far: 3" in txt and "projected" in txt
    for word in (" bp", "net", "mean", "t-stat", " t ", "win rate", "return", "p&l", "sharpe"):
        assert word not in txt, word
