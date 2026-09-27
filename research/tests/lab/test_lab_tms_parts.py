import ast
import math
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks  # noqa: E402
from research.bars import build_bars  # noqa: E402
from research.lab.cbot import cbot_params  # noqa: E402
from research.lab.strategies import tmsorb as tm  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
NAN = math.nan


def _tdi_loop(hc, P, R):                              # AiAgentBot.UpdateTdi, transcribed
    n = len(hc)
    g, red = [NAN] * n, [NAN] * n
    gs = ls = ag = al = 0.0
    for i in range(1, n):
        d = hc[i] - hc[i - 1]
        gain, loss = max(d, 0.0), max(-d, 0.0)
        if i <= P:
            gs, ls = gs + gain, ls + loss
            if i == P:
                ag, al = gs / P, ls / P
                g[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
        else:
            ag, al = (ag * (P - 1) + gain) / P, (al * (P - 1) + loss) / P
            g[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
        if not math.isnan(g[i]) and i >= P + R - 1:
            red[i] = sum(g[i - R + 1:i + 1]) / R
    return np.array(g), np.array(red)


def _stoch_loop(hc, hh, hl, K, D, S):                 # AiAgentBot.UpdateStoch, transcribed
    n = len(hc)
    raw, k, d = [0.0] * n, [NAN] * n, [NAN] * n
    for i in range(n):
        lo, hi = min(hl[max(0, i - K + 1):i + 1]), max(hh[max(0, i - K + 1):i + 1])
        raw[i] = 100 * (hc[i] - lo) / (hi - lo) if hi > lo else 50.0
        if i >= S - 1:
            k[i] = sum(raw[i - S + 1:i + 1]) / S
        if i >= S + D - 2:
            d[i] = sum(k[i - D + 1:i + 1]) / D
    return np.array(k), np.array(d)


def test_tdi_and_stoch_match_the_cbot_loops():
    rng = np.random.default_rng(0)
    c = 1.1 + np.cumsum(rng.normal(0, 1e-4, 300))
    o = np.r_[c[0], c[:-1]]
    h, l = np.maximum(o, c) + 5e-5, np.minimum(o, c) - 5e-5
    ho, hh, hl, hc = tm.heikin_ashi(o, h, l, c)
    assert ho[1] == pytest.approx((ho[0] + hc[0]) / 2) and hc[5] == pytest.approx((o[5] + h[5] + l[5] + c[5]) / 4)
    g, r = tm.tdi(hc, 6, 6)
    g2, r2 = _tdi_loop(hc, 6, 6)
    np.testing.assert_allclose(g, g2, equal_nan=True)
    np.testing.assert_allclose(r, r2, equal_nan=True)
    k, d = tm.stoch(hc, hh, hl, 6, 6, 4)
    k2, d2 = _stoch_loop(hc, hh, hl, 6, 6, 4)
    np.testing.assert_allclose(k, k2, equal_nan=True)
    np.testing.assert_allclose(d, d2, equal_nan=True)


def test_macro_bias_hysteresis():
    p = {"MinBarsBetweenFlips": 2}
    H = 3_600_000
    assert tm.hysteresis(1, None, None, 0, False, p) == (1, 1, 0)             # first confirmed cross
    assert tm.hysteresis(-1, 1, 0, 1 * H, True, p) == (1, 1, 0)               # lockout: flip ignored
    assert tm.hysteresis(-1, 1, 0, 3 * H, False, p) == (1, 1, 0)              # separation too small
    assert tm.hysteresis(-1, 1, 0, 3 * H, True, p) == (-1, -1, 3 * H)         # flip accepted
    assert tm.hysteresis(0, -1, 5, 10, True, p) == (-1, -1, 5)                # no cross: hold the bias


def test_orb_states_and_view_tokyo():
    p = cbot_params("tms_orb", "USDJPY")               # OR 00:00-00:15 UTC, width >= 8 pips, buffer 1.5
    bars = [(150.00, 150.10, 149.98, 150.05), (150.05, 150.09, 150.03, 150.08),
            (150.08, 150.14, 150.07, 150.13), (150.13, 150.21, 150.12, 150.20)]
    ts, px = bar_ticks(day_ms(date(2025, 6, 2)), 15, bars)
    b = build_bars(Ticks(ts, px, px + 0.01), 15)
    orb = tm.orb_states(b, p, 0.01)
    assert not orb["complete"][0] and orb["complete"][1]
    assert orb["dir"][2] == 1 and orb["bar"][3] == 2 and orb["hi"][3] == pytest.approx(150.10)
    v = tm.orb_data(orb, 3, 150.20, p, 0.01)
    assert v.direction == 1 and v.dist == pytest.approx(10.0) and v.decisive and v.since == 1 and v.in_window
    assert tm.orb_data(orb, 3, 150.05, p, 0.01).direction == 0                # back inside: breakout dead


def _utc(*a):
    return int(datetime(*a, tzinfo=timezone.utc).timestamp() * 1000)


def test_session_phases_and_end():
    tokyo, london = cbot_params("tms_orb", "USDJPY"), cbot_params("tms_orb", "EURUSD")
    assert tm.session_info(_utc(2025, 6, 2, 8, 44), tokyo) == ("active", True)
    assert tm.session_info(_utc(2025, 6, 2, 8, 46), tokyo) == ("ending", True)
    assert tm.session_info(_utc(2025, 6, 2, 9, 0), tokyo) == ("closed", False)
    assert tm.session_info(_utc(2025, 7, 1, 7, 0), london) == ("active", True)      # 08:00 London summer = 07 UTC
    assert tm.session_info(_utc(2025, 7, 1, 6, 59), london) == ("pre", False)
    assert tm.session_end_ms(_utc(2025, 7, 1, 10, 0), london) == _utc(2025, 7, 1, 16, 0)


def test_entry_levels_use_the_or_boundary_and_the_tp_ratio():
    p = cbot_params("tms_orb", "EURUSD")
    sl, tp = tm.entry_levels(1, 1.1008, 1.1010, 10.0, 1.1030, 1.0990, p, 0.0001)
    assert sl == pytest.approx(21.0) and tp == pytest.approx(28.0)             # OR low + 1 pip buffer; 21 x 4/3


def _chart(**kw):
    base = dict(g=55.0, slope=1.0, above=True, below=False, turned_green=False, turned_red=False, stoch_bull=True,
                stoch_bear=False, ang_l=True, ang_s=True, long_entry=False, short_entry=False, exit_long=False,
                exit_short=False, bounce_bull=False, bounce_bear=False)
    base.update(kw)
    return {k: np.array([v]) for k, v in base.items()}


def test_cycle_gate():
    now = _utc(2025, 7, 1, 9, 0)
    ok = tm.OrbView(True, 1, 5.0, True, 1, True)
    gate = tm.PostTp()

    def run(sym="EURUSD", bias=1, od=ok, ch=None, regime="mixed", flips=0, at=now, g=gate):
        return tm.cycle_gate(sym, at, "active", True, "london", bias, g, od, ch or _chart(), 0, 10.0, regime, flips)

    assert run() == 1
    assert run(bias=0) == 0
    assert run(od=tm.OrbView(True, -1, 5.0, True, 1, True)) == 0                          # against the bias
    assert run(od=tm.OrbView(True, 1, 40.0, True, 1, True)) == 0                          # > 3.4 ATR absolute cap
    assert run(od=tm.OrbView(True, 1, 1.0, False, 1, True), ch=_chart(above=False)) == 0  # weak, no bounce
    assert run(regime="choppy", flips=6, od=tm.OrbView(True, 1, 5.0, True, 5, True)) == 0
    assert run(sym="US30", at=_utc(2025, 7, 1, 13, 30)) == 0                              # before 9:45 New York
    armed = tm.PostTp(True, 1, 1.1)
    assert run(g=armed) == 0


def test_close_validation():
    assert tm.close_valid(1, 1.1000, 1.0980, 1.0995, 1.0997, macro_exit=True)
    assert not tm.close_valid(1, 1.1000, 1.0980, 1.0995, 1.0997, macro_exit=False)       # 25 % adverse
    assert tm.close_valid(1, 1.1000, 1.0980, 1.0987, 1.0989, macro_exit=False)           # 65 % adverse
    assert tm.close_valid(1, 1.1000, 1.0980, 1.1021, 1.1023, macro_exit=False)           # >= 1R profit


def test_constants_match_the_sources():
    src = (ROOT / "app" / "trade_gates.py").read_text()
    block = src[src.index("BREAKOUT_DISTANCE_LIMITS = (") + len("BREAKOUT_DISTANCE_LIMITS = "):]
    assert ast.literal_eval(block[:block.index("\n)\n") + 2]) == tm.BREAKOUT_DISTANCE_LIMITS
    for line in ("MAX_BARS_SINCE_BREAKOUT_MODEL2 = 20", "CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT = 3",
                 "CHOPPY_OVERRIDE_MAX_OR_FLIPS = 7", "CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR = 0.5",
                 "TMS_CLOSE_MIN_ADVERSE_SL_RATIO = 0.60", "TMS_CLOSE_MIN_PROFIT_SL_RATIO = 1.00"):
        assert line in src, line
    assert 'US_INDEX_SYMBOLS = {"US30", "DJ30", "USTEC", "NAS100", "US500", "SPX500"}' in \
        (ROOT / "app" / "portfolio.py").read_text()
    cs = (ROOT / "cBot" / "AiAgentBot.cs").read_text()
    for line in ("GivebackArmAtrFraction = 0.4", "GivebackArmRiskFraction = 0.5", "GivebackArmPeakAtr = 1.5",
                 "Tier2TpFraction = 0.65", "PostTpGateMinExitAtr = 0.5"):
        assert line in cs, line
