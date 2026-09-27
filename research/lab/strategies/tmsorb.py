"""AiAgentBot (TMS+ORB) in the lab, with the AI replaced by "approve every candidate the server's cycle gate
lets through" and the AI's position management by its prompt rules and the server's close validation.

Sources: cBot/AiAgentBot.cs (Heikin-Ashi TDI and Stochastic, the H1 macro bias with its cross lock and flip
hysteresis, ORB, session, ExecuteDecision's SL/TP, ManageExits, CheckMaxGiveback, CheckSessionEnd, the post-TP
gate, BiasFlipExit) and app/trade_gates.py + app/trade_prompts.py (evaluate_cycle_gate, validate_tms_close_decision, the prompt's rules 1-2:
close on session "ending" or on the chart exit signal). An approved candidate trades in the macro bias
direction. Switched off to honour the lab's account rules: the loss-streak gate, MaxDollarRiskPerTrade and the
min-lot guards (fixed units). Not modelled: the US-index alignment gate (it needs other bots' positions),
AI ADJUST, the LLM's own judgement. The exits use the last closed bar's ATR (the bot reads the forming bar's)."""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from research.indicators import atr_sma, ema
from research.lab import costs
from research.lab.cbot import cbot_params, preset
from research.lab.engine import NAN, Ctx, Pos
from research.lab.strategies.judas import europe_dst, us_dst
from research.ticks import _first_hit
from research.specs import normalize_units

NY = ZoneInfo("America/New_York")
PERIOD_MIN = {"m5": 5, "m15": 15}
# cBot/AiAgentBot.cs private constants
GIVEBACK_ARM_ATR, GIVEBACK_ARM_RISK, GIVEBACK_ARM_PEAK_ATR = 0.4, 0.5, 1.5
TIER2_TP_FRACTION, POST_TP_MIN_EXIT_ATR = 0.65, 0.5
# app/trade_gates.py (pinned to the source by the tests)
BREAKOUT_DISTANCE_LIMITS = (
    # (symbol tokens, prompt label, direct ATR x, direct cap, absolute ATR x, absolute cap)
    (("USTEC", "NAS100"), "USTEC/NAS100", 1.3, 700.0, 3.2, 2100.0),
    (("US30", "DJ30"), "US30/DJ30", 1.5, 950.0, 3.4, 2800.0),
    (("US500", "SPX500"), "US500/SPX500", 1.4, 150.0, 3.4, 450.0),
    (("DE40", "GER40"), "DE40/GER40", 1.5, 700.0, 3.4, 1900.0),
    (("UK100", "GB100"), "UK100/GB100", 1.5, 550.0, 3.4, 1600.0),
    (("JP225", "NIKKEI", "JPN225"), "JP225/Nikkei", 1.8, 3000.0, 3.8, 7000.0),
    (("HK50", "HSI"), "HK50/HangSeng", 1.5, 800.0, 3.4, 2200.0),
    (("XAU", "GOLD"), "Gold", 1.8, 1500.0, 3.6, 3500.0),
    (("BTC", "CRYPTO"), "BTC/Crypto", 1.5, 37500.0, 3.5, 130000.0),
    (("ETH", "SOL", "XRP"), "ETH/SOL/XRP", 1.5, 5250.0, 3.5, 35000.0),
    (("JPY",), "JPY Crosses", 1.6, 55.0, 3.6, 120.0),
    (("EURUSD", "GBPUSD", "USDCAD", "AUDUSD", "NZDUSD", "USDCHF"), "Forex Majors", 1.5, 30.0, 3.4, 70.0),
)
MAX_BARS_SINCE_BREAKOUT_MODEL2 = 20
CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT, CHOPPY_OVERRIDE_MAX_OR_FLIPS, CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR = 3, 7, 0.5
TMS_CLOSE_MIN_ADVERSE_SL_RATIO, TMS_CLOSE_MIN_PROFIT_SL_RATIO = 0.60, 1.00
US_INDEX_SYMBOLS = ("US30", "DJ30", "USTEC", "NAS100", "US500", "SPX500")      # app/portfolio.py


def resolve_breakout_limits(symbol: str, atr_pips: Optional[float]) -> Tuple[float, float]:
    sym = symbol.upper()
    row = next((r for r in BREAKOUT_DISTANCE_LIMITS if any(tok in sym for tok in r[0])), BREAKOUT_DISTANCE_LIMITS[-1])
    _, _, direct_atr, direct_cap, abs_atr, abs_cap = row
    if atr_pips and atr_pips > 0:
        return min(atr_pips * direct_atr, direct_cap), min(atr_pips * abs_atr, abs_cap)
    return direct_cap, abs_cap


# ---------------------------------------------------------------- indicators
def heikin_ashi(o, h, l, c):
    hc = (o + h + l + c) / 4.0
    ho = np.empty(len(o))
    ho[0] = (o[0] + c[0]) / 2.0
    for i in range(1, len(o)):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2.0
    return ho, np.maximum(h, np.maximum(ho, hc)), np.minimum(l, np.minimum(ho, hc)), hc


def _rsi(ag: float, al: float) -> float:
    return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)


def tdi(hc, rsi_p: int, red_p: int):
    """UpdateTdi: RSI of the HA close (SMA seed, then Wilder), red = SMA(red_p) of it; NaN during warm-up."""
    n = len(hc)
    g = np.full(n, np.nan)
    d = np.diff(hc, prepend=hc[0])
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    if n > rsi_p:
        ag, al = gain[1:rsi_p + 1].mean(), loss[1:rsi_p + 1].mean()
        g[rsi_p] = _rsi(ag, al)
        for i in range(rsi_p + 1, n):
            ag = (ag * (rsi_p - 1) + gain[i]) / rsi_p
            al = (al * (rsi_p - 1) + loss[i]) / rsi_p
            g[i] = _rsi(ag, al)
    red = np.full(n, np.nan)
    w = rsi_p + red_p - 1
    if n > w:
        red[w:] = sliding_window_view(g, red_p).mean(axis=1)[w - red_p + 1:]
    return g, red


def stoch(hc, hh, hl, k_p: int, d_p: int, slow: int):
    """UpdateStoch on Heikin-Ashi prices: raw %K over k_p bars (a partial window at the start), %K = SMA(slow),
    %D = SMA(d_p) of %K; NaN during warm-up."""
    n = len(hc)
    lo = sliding_window_view(np.r_[np.full(k_p - 1, np.inf), hl], k_p).min(axis=1)
    hi = sliding_window_view(np.r_[np.full(k_p - 1, -np.inf), hh], k_p).max(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = np.where(hi > lo, 100.0 * (hc - lo) / (hi - lo), 50.0)
    k = np.full(n, np.nan)
    if n >= slow:
        k[slow - 1:] = sliding_window_view(raw, slow).mean(axis=1)
    d = np.full(n, np.nan)
    w = slow + d_p - 2
    if n > w:
        d[w:] = sliding_window_view(k[slow - 1:], d_p).mean(axis=1)
    return k, d


def chart_tms(b, p) -> dict:
    """GetTmsSignals on every chart bar (the cross memory runs forward over all bars)."""
    ho, hh, hl, hc = heikin_ashi(b.o, b.h, b.l, b.c)
    g, r = tdi(hc, p["RsiPeriod"], p["RedPeriod"])
    k, d = stoch(hc, hh, hl, p["StochKPeriod"], p["StochDPeriod"], p["StochSlowing"])
    e = ema(b.c, p["EmaPeriod"])
    n = len(b)
    idx = np.arange(n)
    g1, g2, r1 = np.r_[np.nan, g[:-1]], np.r_[np.nan, np.nan, g[:-2]], np.r_[np.nan, r[:-1]]
    green = hc > ho
    green1, green2 = np.r_[False, green[:-1]], np.r_[False, False, green[:-2]]
    valid = np.isfinite(g) & np.isfinite(r) & (idx >= 1)
    with np.errstate(invalid="ignore"):
        above, below = valid & (b.c > e) & (hc > e), valid & (b.c < e) & (hc < e)
        tg = valid & ((green & ~green1) | (green1 & ~green2))
        trd = valid & ((~green & green1) | (~green1 & green2))
        up, dn = valid & (g1 <= r1) & (g > r), valid & (g1 >= r1) & (g < r)
        last = np.maximum.accumulate(np.where(up | dn, idx, -1))
        last_dir = np.where(last >= 0, np.where(up, 1, -1)[np.maximum(last, 0)], 0)
        since = np.where(last >= 0, idx - last, 999)
        mad = p["MinAngleDelta"]
        ang_l = valid & ((g - g2) >= mad if mad > 0 else True)
        ang_s = valid & ((g2 - g) >= mad if mad > 0 else True)
        window = (since >= 1) & (since <= p["MaxBarsAfterCross"])
        sb, sr = valid & (k > d), valid & (k < d)
        x_dn = ((g1 >= r1) & (g < r)) | ((g < r) & (r - g >= 0.5))
        ob = ((g1 >= 68) | (g2 >= 68)) & (g < 60) & (g1 - g >= 3.0) & (~above | trd)
        x_up = ((g1 <= r1) & (g > r)) | ((g > r) & (g - r >= 0.5))
        os_ = ((g1 <= 32) | (g2 <= 32)) & (g > 40) & (g - g1 >= 3.0) & (~below | tg)
        dist, dist1 = np.abs(g - r), np.abs(g1 - r1)
        thr, on = p["BounceDistanceThreshold"], bool(p["BounceTradeEnabled"])
        near = (dist1 <= thr) & (dist > dist1)
        return dict(
            g=np.where(valid, g, 50.0), slope=np.where(valid, g - g1, 0.0), above=above, below=below,
            turned_green=tg, turned_red=trd, stoch_bull=sb, stoch_bear=sr, ang_l=ang_l, ang_s=ang_s,
            long_entry=valid & (last_dir == 1) & window & tg & sb & ang_l & above,
            short_entry=valid & (last_dir == -1) & window & trd & sr & ang_s & below,
            exit_long=valid & (x_dn | ob | ((g < r) & ~above & (trd | ~green))),
            exit_short=valid & (x_up | os_ | ((g > r) & ~below & (tg | green))),
            bounce_bull=valid & on & (g > r) & (g > g1) & near & above & ~trd,
            bounce_bear=valid & on & (g < r) & (g < g1) & near & below & ~tg)


# ---------------------------------------------------------------- macro (H1) bias
def hysteresis(cand, confirmed, last_flip_ms, closed_ms, sep_ok, p):
    """The macro bias flip rule: (bias, confirmed, last_flip_ms). cand 0 = no confirmed cross yet."""
    lock_ok = last_flip_ms is None or (closed_ms - last_flip_ms) / 3_600_000 >= p["MinBarsBetweenFlips"]
    if cand == 0:
        return (confirmed or 0), confirmed, last_flip_ms
    if cand == confirmed:
        return cand, confirmed, last_flip_ms
    if confirmed is None or (sep_ok and lock_ok):
        return cand, cand, closed_ms
    return confirmed, confirmed, last_flip_ms


def _window_rsi(hc, P):
    out = np.full(len(hc), 50.0)
    d = np.diff(hc, prepend=hc[0])
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    if len(hc) > P:
        ag, al = gain[1:P + 1].sum() / P, loss[1:P + 1].sum() / P
        out[P] = _rsi(ag, al)
        for k in range(P + 1, len(hc)):
            ag, al = (ag * (P - 1) + gain[k]) / P, (al * (P - 1) + loss[k]) / P
            out[k] = _rsi(ag, al)
    return out


def _window_red(rsi, R):
    out = rsi.copy()
    if len(rsi) > R:
        out[R:] = sliding_window_view(rsi, R).mean(axis=1)[1:]
    return out


class MacroTms:
    """GetMacroTmsSignals evaluated at every closed H1 bar h over its 120-bar window (recomputed from the
    window start, as the bot does), with the cross lock and the flip hysteresis carried forward."""

    def __init__(self, hb, p):
        n = len(hb)
        self.bias = np.zeros(n, np.int8)
        self.exit_long, self.exit_short = np.zeros(n, bool), np.zeros(n, bool)
        self.bounce_bull, self.bounce_bear = np.zeros(n, bool), np.zeros(n, bool)
        rp, rd = p["RsiPeriod"], p["RedPeriod"]
        thr, on = p["BounceDistanceThreshold"], bool(p["BounceTradeEnabled"])
        cross, confirmed, last_flip = 0, None, None
        for h in range(n):
            count = h + 2                                    # the forming bar is the window's last element
            if count < rp + rd + 35:
                continue
            s = count - min(count, 120)
            w = slice(s, h + 1)
            ho, hh, hl, hc = heikin_ashi(hb.o[w], hb.h[w], hb.l[w], hb.c[w])
            rsi = _window_rsi(hc, rp)
            red = _window_red(rsi, rd)
            k, d = (np.nan_to_num(x, nan=50.0) for x in stoch(hc, hh, hl, p["StochKPeriod"], p["StochDPeriod"],
                                                             p["StochSlowing"]))
            last = len(hc) - 1
            prev = last - 1
            if prev < 1:
                continue
            g, g1, r, r1 = rsi[last], rsi[prev], red[last], red[prev]
            green, green1 = hc[last] > ho[last], hc[prev] > ho[prev]
            tg, trd = green and not green1, (not green) and green1
            for j in range(last, 0, -1):
                if rsi[j - 1] <= red[j - 1] and rsi[j] > red[j] and hc[j] > ho[j] and k[j] > d[j]:
                    cross = 1
                    break
                if rsi[j - 1] >= red[j - 1] and rsi[j] < red[j] and hc[j] < ho[j] and k[j] < d[j]:
                    cross = -1
                    break
            bias, confirmed, last_flip = hysteresis(cross, confirmed, last_flip, int(hb.open_time[h]),
                                                    abs(g - r) >= p["MinTdiFlipSeparation"], p)
            self.bias[h] = bias
            self.exit_long[h] = (g1 >= r1 and g < r) or (bias == -1 and trd)
            self.exit_short[h] = (g1 <= r1 and g > r) or (bias == 1 and tg)
            near = abs(g1 - r1) <= thr and abs(g - r) > abs(g1 - r1)
            self.bounce_bull[h] = on and g > r and g > g1 and near and not trd
            self.bounce_bear[h] = on and g < r and g < g1 and near and not tg


# ---------------------------------------------------------------- ORB, session, regime
def adjusted_hour(dt: datetime, base: int, rule: str) -> int:
    """GetAdjustedHour: winter UTC hours move one hour earlier in summer."""
    if rule == "None" or base == 0:
        return base
    dst = us_dst(dt) if rule == "US" else (europe_dst(dt) if rule == "Europe" else False)
    return base - 1 if dst else base


def orb_states(b, p, pip: float) -> dict:
    """UpdateOrb after each chart bar: range of the first OrbOpeningRangeMinutes from the session open, complete
    once the window has passed with a wide enough range, breakout direction and bar (reset every UTC day)."""
    n = len(b)
    out = dict(hi=np.full(n, -np.inf), lo=np.full(n, np.inf), complete=np.zeros(n, bool),
               dir=np.zeros(n, np.int8), bar=np.full(n, -1))
    day, hi, lo, done, direction, k = None, -np.inf, np.inf, False, 0, -1
    buf = p["OrbBufferPips"] * pip
    for i in range(n):
        dt = datetime.fromtimestamp(b.open_time[i] / 1000, timezone.utc)
        if dt.date() != day:
            day, hi, lo, done, direction, k = dt.date(), -np.inf, np.inf, False, 0, -1
        start = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"]) * 60 + p["OrbStartMinute"]
        end = start + p["OrbOpeningRangeMinutes"]
        mins = dt.hour * 60 + dt.minute
        if start <= mins < end:
            hi, lo = max(hi, float(b.h[i])), min(lo, float(b.l[i]))
        if mins >= end and not done and hi > -np.inf and (hi - lo) / pip >= p["MinOrWidthPips"]:
            done = True
        if done:
            if b.c[i] > hi + buf and direction != 1:
                direction, k = 1, i
            elif b.c[i] < lo - buf and direction != -1:
                direction, k = -1, i
        out["hi"][i], out["lo"][i], out["complete"][i], out["dir"][i], out["bar"][i] = hi, lo, done, direction, k
    return out


@dataclass
class OrbView:
    complete: bool
    direction: int
    dist: float
    decisive: bool
    since: int
    in_window: bool


def orb_data(orb: dict, i: int, mid: float, p, pip: float) -> OrbView:
    """GetOrbData at the close of bar i with the current mid: a breakout whose price is back inside is dead."""
    hi, lo, d, k = float(orb["hi"][i]), float(orb["lo"][i]), int(orb["dir"][i]), int(orb["bar"][i])
    since = i - k if k >= 0 else 0
    dist = (mid - hi) / pip if d == 1 and hi > -np.inf else ((lo - mid) / pip if d == -1 and lo < np.inf else 0.0)
    direction = d if dist > 0 else 0
    dist = max(dist, 0.0)
    return OrbView(bool(orb["complete"][i]), direction, dist, dist >= p["MinDecisiveBreakoutPips"], since,
                   0 <= since <= p["MaxBarsAfterBreakout"])


def _session_minutes(dt: datetime, p) -> Tuple[int, int]:
    start = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"]) * 60 + p["OrbStartMinute"]
    end = adjusted_hour(dt, p["SessionEndHour"], p["SessionDstRule"]) * 60 + p["SessionEndMinute"]
    return start, (start + 540 if p["SessionEndHour"] == 0 else end)


def session_info(ms: int, p) -> Tuple[str, bool]:
    """GetSessionInfo: (phase, is_trading_time); "ending" = the last 15 minutes."""
    dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
    now = dt.hour * 60 + dt.minute
    start, end = _session_minutes(dt, p)
    over = start > end
    active = (now >= start or now < end) if over else (start <= now < end)
    to_end = ((1440 - now + end) if (over and now >= start) else end - now) if active else 0
    ending = active and to_end <= 15
    if not active and ((end <= now < start) if over else now < start):
        return "pre", False
    if active and not ending:
        return "active", True
    return ("ending", True) if ending else ("closed", False)


def session_end_ms(ms: int, p) -> int:
    """When CheckSessionEnd flattens a position opened at ms (sessions within one UTC day)."""
    dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
    start, end = _session_minutes(dt, p)
    if start > end:
        raise ValueError("overnight sessions are not modelled")
    return int(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp() * 1000) + end * 60_000


def _er(x) -> float:
    path = float(np.abs(np.diff(x)).sum())
    return abs(float(x[-1] - x[0])) / path if path > 1e-7 else 0.0


def market_regime(b, i: int, now_ms: int, or_hi: float, or_lo: float, p) -> Tuple[str, int]:
    """GetMarketRegime: efficiency ratios of the session's closes and the count of failed ORB breakouts."""
    dt = datetime.fromtimestamp(now_ms / 1000, timezone.utc)
    sh = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"])
    start = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc) + timedelta(hours=sh, minutes=p["OrbStartMinute"])
    if dt < start and sh > 12:
        start -= timedelta(days=1)
    closes = b.c[int(np.searchsorted(b.open_time, int(start.timestamp() * 1000), side="left")):i + 1]
    if len(closes) < 6:
        return "forming", 0
    er_s, er_r = _er(closes), _er(closes[-12:])
    flips = 0
    if or_hi > -np.inf and or_lo < np.inf:
        zone = None
        for c in closes:
            z = "A" if c > or_hi else ("B" if c < or_lo else "I")
            flips += zone in ("A", "B") and z == "I"
            zone = z if z != "I" else zone
    if er_s >= 0.35 or (er_r >= 0.45 and flips <= 3):
        return "trending", flips
    return ("choppy" if flips >= 5 else "mixed"), flips


# ---------------------------------------------------------------- post-TP gate, cycle gate, levels
@dataclass
class PostTp:
    active: bool = False
    side: int = 0
    extreme: float = 0.0

    def on_close(self, ctx: Ctx, pos: Pos, p, atr: float) -> None:
        """OnPositionClosed: arm after a profitable exit that captured >= 0.5 ATR."""
        if not p["EnablePostTpGate"]:
            return
        j, px, _, _ = pos.deals[-1]
        exit_pips = (px - pos.entry) * pos.side / ctx.inst.pip
        fee_pips = ctx.inst.comm_per_unit / (ctx.inst.pip * costs.usd_per_quote(ctx.inst.quote_ccy, int(ctx.t.ts[j])))
        if exit_pips > fee_pips and exit_pips >= POST_TP_MIN_EXIT_ATR * atr:
            self.active, self.side = True, pos.side
            self.extreme = float(ctx.t.bid[j] if pos.side > 0 else ctx.t.ask[j])

    def release(self, bias, bid, ask, atr, pip, orb, i, ch, macro, mh, p) -> None:
        """CheckPostTpGateRelease: bias flip, a pullback, an OR touch, or a TDI bounce after a small pullback."""
        if not self.active:
            return
        if self.side == 1 and bid > self.extreme:
            self.extreme = bid
        if self.side == -1 and ask < self.extreme:
            self.extreme = ask
        pull = (self.extreme - bid) / pip if self.side == 1 else (ask - self.extreme) / pip
        m_bull = mh >= 0 and bool(macro.bounce_bull[mh])
        m_bear = mh >= 0 and bool(macro.bounce_bear[mh])
        released = (bias == -self.side or pull >= p["PostTpPullbackAtr"] * atr
                    or (bool(orb["complete"][i]) and ((self.side == 1 and bid <= orb["hi"][i])
                                                      or (self.side == -1 and ask >= orb["lo"][i])))
                    or (pull >= 0.3 * atr and ((self.side == 1 and (bool(ch["bounce_bull"][i]) or m_bull))
                                               or (self.side == -1 and (bool(ch["bounce_bear"][i]) or m_bear)))))
        if released:
            self.active, self.side = False, 0


def cycle_gate(sym, now_ms, phase, active, session_name, bias, gate, od, ch, i, atr_pips, regime, flips) -> int:
    """evaluate_cycle_gate for a flat bot: the side the approve-all AI takes (the macro bias), or 0."""
    if not active or phase in ("pre", "closed"):
        return 0
    s = sym.upper()
    us_idx = any(tok in s for tok in US_INDEX_SYMBOLS)
    gold = "XAU" in s or "GOLD" in s
    name = session_name.lower()
    if "newyork" in name or "ny" in name or us_idx or gold:
        ny = datetime.fromtimestamp(now_ms / 1000, NY)
        m = ny.hour * 60 + ny.minute
        if (us_idx and m < 585) or 550 <= m <= 575:
            return 0
    if bias == 0:
        return 0
    if gate.active and (gate.side == bias or gate.side == 0):
        return 0
    if not od.complete or od.direction == 0:
        return 0
    if bias == 1:
        bounce = (ch["bounce_bull"][i] and ch["above"][i]) or (
            ch["above"][i] and ch["slope"][i] > 0 and ch["g"][i] >= 48.0 and not ch["turned_red"][i]
            and (ch["long_entry"][i] or ch["stoch_bull"][i] or ch["ang_l"][i]))
    else:
        bounce = (ch["bounce_bear"][i] and ch["below"][i]) or (
            ch["below"][i] and ch["slope"][i] < 0 and ch["g"][i] <= 52.0 and not ch["turned_green"][i]
            and (ch["short_entry"][i] or ch["stoch_bear"][i] or ch["ang_s"][i]))
    bounce = bool(bounce)
    atr_ref = round(atr_pips, 1) if atr_pips > 0 else None
    direct, absolute = resolve_breakout_limits(s, atr_ref)
    if od.dist > absolute or (od.dist > direct and not bounce):
        return 0
    if gold and od.dist < 150.0 and not bounce:
        return 0
    if not od.decisive and not bounce:
        return 0
    if not od.in_window and (od.since > MAX_BARS_SINCE_BREAKOUT_MODEL2 or not bounce):
        return 0
    if od.direction != bias:
        return 0
    if regime == "choppy" and flips >= 5:
        fresh = False
        if (od.since <= CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT and flips <= CHOPPY_OVERRIDE_MAX_OR_FLIPS
                and (atr_ref is None or od.dist >= CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR * atr_ref)):
            if od.direction == 1:
                fresh = bool(ch["above"][i] and ch["slope"][i] > 0 and not ch["turned_red"][i])
            else:
                fresh = bool(ch["below"][i] and ch["slope"][i] < 0 and not ch["turned_green"][i])
        if not fresh:
            return 0
    return bias


def entry_levels(side, bid, ask, atr, or_hi, or_lo, p, pip) -> Tuple[float, float]:
    """ExecuteDecision's SL/TP in pips (UseAtr), without the dollar-risk guard that shrinks the stop."""
    price = ask if side > 0 else bid
    sl, tp = atr * p["AtrSlMultiplier"], atr * p["AtrTpMultiplier"]
    max_sl = p["MaxSlAtr"] * atr
    sl = max(p["MinSlAtr"] * atr, min(max_sl, sl))
    if p["UseOrBoundarySl"]:
        or_sl = None
        if side > 0 and or_lo < np.inf:
            or_sl = (price - or_lo) / pip + p["OrbBufferPips"]
        elif side < 0 and or_hi > -np.inf:
            or_sl = (or_hi - price) / pip + p["OrbBufferPips"]
        if or_sl is not None and or_sl > 0:
            sl = max(sl, min(max_sl, or_sl))
    sl = min(sl, max_sl)
    if p["MaxAbsoluteSlPips"] > 0:
        sl = min(sl, p["MaxAbsoluteSlPips"])
    ratio = p["AtrTpMultiplier"] / p["AtrSlMultiplier"] if p["AtrTpMultiplier"] > 0 and p["AtrSlMultiplier"] > 0 else 1.5
    return sl, max(p["MinTpAtr"] * atr, max(tp, sl * ratio))


def close_valid(side, entry, sl, bid, ask, macro_exit) -> bool:
    """validate_tms_close_decision: an AI CLOSE_ALL stands on a macro exit signal, >= 60 % of the stop distance
    in drawdown, or >= 1R of profit."""
    if macro_exit:
        return True
    sl_dist = abs(entry - sl)
    if sl_dist <= 0:
        return True
    adverse = (entry - bid) if side > 0 else (ask - entry)
    profit = (bid - entry) if side > 0 else (entry - ask)
    return adverse >= TMS_CLOSE_MIN_ADVERSE_SL_RATIO * sl_dist or profit >= TMS_CLOSE_MIN_PROFIT_SL_RATIO * sl_dist


# ---------------------------------------------------------------- the open position, tick by tick
@dataclass
class Hold:
    pos: Pos
    cur: int              # next tick to process
    atr: float            # ATR (pips) of the last closed chart bar
    eod_ms: int
    init_risk: float      # pips
    mfe: float = -np.inf
    be_done: bool = False


def tier2(profit, atr, total_tp, p) -> bool:
    """IsTier2Reached."""
    return ((p["Tier2TriggerAtr"] > 0 and profit >= p["Tier2TriggerAtr"] * atr)
            or (p["Tier2TriggerPips"] > 0 and profit >= p["Tier2TriggerPips"])
            or (total_tp > 0 and profit >= TIER2_TP_FRACTION * total_tp))


def giveback_arm(atr, init_risk, p) -> float:
    """CheckMaxGiveback's activation threshold (pips of peak profit)."""
    x = GIVEBACK_ARM_ATR * atr
    if p["BreakevenTriggerAtr"] > 0:
        x = max(x, p["BreakevenTriggerAtr"] * atr)
    if init_risk > 0:
        x = max(x, init_risk * GIVEBACK_ARM_RISK)
    return max(x, p["GivebackArmMinPips"], GIVEBACK_ARM_PEAK_ATR * atr)


def _close_all(ctx: Ctx, hd: Hold, j: int, why: str) -> str:
    ctx.close(hd.pos, j, why)
    ctx.finish(hd.pos)
    return why


def _tick(ctx: Ctx, hd: Hold, j: int, p, spec, digits: int) -> Optional[str]:
    """One tick: the broker's SL/TP, then OnTick (memory, ManageExits, CheckMaxGiveback, CheckSessionEnd)."""
    t, pos, pip, a = ctx.t, hd.pos, ctx.inst.pip, hd.atr
    side = pos.side
    px = float(t.bid[j] if side > 0 else t.ask[j])
    if (px - pos.sl) * side <= 0:
        return _close_all(ctx, hd, j, "sl")
    if math.isfinite(pos.tp) and (px - pos.tp) * side >= 0:
        return _close_all(ctx, hd, j, "tp")
    pnl = (px - pos.entry) * side / pip
    hd.mfe = max(hd.mfe, pnl)
    total_tp = abs(pos.tp - pos.entry) / pip if math.isfinite(pos.tp) else 0.0
    if p["BreakevenTriggerAtr"] > 0 and pnl >= p["BreakevenTriggerAtr"] * a and not hd.be_done:
        be_sl = pos.entry + side * p["BreakevenOffsetAtr"] * a * pip
        if (be_sl - pos.sl) * side > 0 and (be_sl - px) * side < 0:
            pos.sl, hd.be_done = be_sl, True
            ratio = p["PartialCloseRatio"]
            if 0 < ratio < 1:
                vol = normalize_units(pos.units * ratio, spec)
                if vol >= spec.min_units and pos.units - vol >= spec.min_units:
                    ctx.close(pos, j, "partial", vol)
    if p["TrailTriggerAtr"] > 0 and pnl >= p["TrailTriggerAtr"] * a:
        dist = (min(p["TrailDistanceAtr"], p["Tier2TrailDistanceAtr"]) if tier2(pnl, a, total_tp, p)
                else p["TrailDistanceAtr"]) * a
        cand = round(px - side * dist * pip, digits)
        if (cand - pos.sl) * side >= max(ctx.inst.tick_size, 0.1 * dist * pip) and (cand - px) * side < 0:
            pos.sl = cand
    if hd.mfe >= giveback_arm(a, hd.init_risk, p):
        gb = hd.mfe - pnl
        ratio = max(p["MaxGivebackMfeRatio"], 0.45) if p["MaxGivebackMfeRatio"] > 0 else 0.0
        if tier2(hd.mfe, a, total_tp, p):
            ratio = p["Tier2GivebackMfeRatio"]
        if ratio > 0 and gb >= hd.mfe * ratio:
            return _close_all(ctx, hd, j, "giveback")
        if p["MaxGivebackAtr"] > 0 and gb >= p["MaxGivebackAtr"] * a:
            return _close_all(ctx, hd, j, "giveback_atr")
    if t.ts[j] >= hd.eod_ms:
        return _close_all(ctx, hd, j, "eod")
    return None


def run_ticks(ctx: Ctx, hd: Hold, end: int, p) -> Optional[str]:
    """Ticks [hd.cur, end) of the open position; the exit reason once it is closed. Until break-even, trailing
    or the giveback lock can arm, only the SL, the TP, the arming level and the session end can act, so the
    loop jumps there with a vectorised search."""
    t, pos, pip = ctx.t, hd.pos, ctx.inst.pip
    side, spec = pos.side, ctx.inst.spec()
    digits = max(0, round(-math.log10(ctx.inst.tick_size)))
    price = t.bid if side > 0 else t.ask
    eod_tick = ctx.tick_at(hd.eod_ms)
    end = min(end, len(t))
    while hd.cur < end:
        a = hd.atr
        be = p["BreakevenTriggerAtr"] * a if p["BreakevenTriggerAtr"] > 0 else np.inf
        tr_ = p["TrailTriggerAtr"] * a if p["TrailTriggerAtr"] > 0 else np.inf
        arm = min(be, tr_, giveback_arm(a, hd.init_risk, p))
        if not hd.be_done and hd.mfe < arm:
            lvl = pos.entry + side * arm * pip
            tp = pos.tp if math.isfinite(pos.tp) else side * np.inf
            lo, hi = (pos.sl, min(tp, lvl)) if side > 0 else (max(tp, lvl), pos.sl)
            seg = min(end, eod_tick)
            j = _first_hit(price[:seg], hd.cur, lo, hi)
            if j >= seg:
                hd.cur = seg
                if seg < end:
                    return _close_all(ctx, hd, seg, "eod")
                return None
        else:
            j = hd.cur
        why = _tick(ctx, hd, j, p, spec, digits)
        hd.cur = j + 1
        if why:
            return why
    return None


# ---------------------------------------------------------------- the bar loop
def tms_orb(ctx: Ctx, **overrides) -> None:
    sym, t, pip = ctx.ch.symbol, ctx.t, ctx.inst.pip
    p = cbot_params("tms_orb", sym, **overrides)
    if p["TmsTimeFrame"] != "Hour" or not p["UseAtr"]:
        raise ValueError("the TMS+ORB port models TmsTimeFrame=Hour with ATR stops only")
    b, hb = ctx.bars(PERIOD_MIN[preset("tms_orb", sym)["period"]]), ctx.bars(60)
    ch, macro, orb = chart_tms(b, p), MacroTms(hb, p), orb_states(b, p, pip)
    atr = atr_sma(b.h, b.l, b.c, p["AtrPeriod"])
    gate, hd, prev_atr = PostTp(), None, 10.0
    for i in range(3, len(b)):
        e = int(b.event_tick[i])
        if e >= len(t):
            break
        if hd is not None:
            hd.atr = prev_atr
            if run_ticks(ctx, hd, e, p):
                gate.on_close(ctx, hd.pos, p, prev_atr)
                hd = None
        a_pips = float(atr[i]) / pip if math.isfinite(atr[i]) and atr[i] > 0 else 10.0
        prev_atr = a_pips
        now = int(t.ts[e])
        phase, active = session_info(now, p)
        if hd is None and (not active or phase in ("closed", "ending")):
            continue                                            # the cBot's cost gate: no request sent
        mh = int(np.searchsorted(hb.close_time, now, side="right")) - 1
        bias = int(macro.bias[mh]) if mh >= 0 else 0
        bid, ask = float(t.bid[e]), float(t.ask[e])
        gate.release(bias, bid, ask, a_pips, pip, orb, i, ch, macro, mh, p)
        if hd is not None:
            pos = hd.pos
            want = phase == "ending" or bool((ch["exit_long"] if pos.side > 0 else ch["exit_short"])[i])
            m_exit = mh >= 0 and bool((macro.exit_long if pos.side > 0 else macro.exit_short)[mh])
            if want and close_valid(pos.side, pos.entry, pos.sl, bid, ask, m_exit):
                why = "ai_close"
            elif p["BiasFlipExit"] and bias == -pos.side:
                why = "bias_flip"
            else:
                continue
            _close_all(ctx, hd, e, why)
            gate.on_close(ctx, pos, p, a_pips)
            hd = None
            continue
        od = orb_data(orb, i, (bid + ask) / 2.0, p, pip)
        regime, flips = market_regime(b, i, now, float(orb["hi"][i]), float(orb["lo"][i]), p)
        side = cycle_gate(sym, now, phase, active, str(p["SessionName"]), bias, gate, od, ch, i, a_pips, regime, flips)
        if not side or not ctx.can_enter(e) or (gate.active and gate.side == side):
            continue
        if p["MaxBreakoutDistanceAtr"] > 0 and od.dist > p["MaxBreakoutDistanceAtr"] * a_pips:
            continue
        if int(orb["dir"][i]) == -side:
            continue
        sl_p, tp_p = entry_levels(side, bid, ask, a_pips, float(orb["hi"][i]), float(orb["lo"][i]), p, pip)
        pos = ctx.open(e, side)
        pos.sl = pos.sl0 = pos.entry - side * sl_p * pip
        pos.tp = pos.tp0 = NAN if (p["TrendTpDisabled"] and regime == "trending") else pos.entry + side * tp_p * pip
        hd = Hold(pos, e + 1, a_pips, session_end_ms(now, p), sl_p)
    if hd is not None:
        _close_all(ctx, hd, len(t) - 1, "tail")
