"""The strategy catalog: every strategy the project runs or has researched - what it does, where it came from,
what was found, and the code the lab runs for it. New research adds an entry here (and a function in
research/lab/strategies/ when it is new code).

  python -m research.lab.catalog [RUN_DIR ...]   -> research/STRATEGIES.md (with each RUN_DIR/cells.csv's results;
                                                   a strategy in a later run replaces its earlier result)"""
import csv
import hashlib
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from research.lab.strategies import judas2, literature, rules, tms_orb2
from research.lab.strategies.flowrsi import flowrsi
from research.lab.strategies.judas import judas
from research.lab.strategies.tmsorb import tms_orb
from research.lab.universe import ALL, FX, FX_REAL, INDICES

ALL_VARIANTS = ("real", "mirror", "shuffle")
REAL_ONLY = ("real",)
US_INDICES = ("US30", "USTEC")
MEF_PAIRS = ("EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDJPY")
STATUSES = ("live", "candidate", "rejected", "not_applicable")
OUT = Path(__file__).resolve().parents[1] / "STRATEGIES.md"


@dataclass(frozen=True)
class StrategyInfo:
    id: str
    name: str
    status: str                     # live | candidate | rejected | not_applicable
    origin: str
    family: str
    timeframe: str
    rules: str
    findings: Tuple[str, ...] = ()
    fn: Optional[Callable] = None   # fn(ctx, **params); None = catalogued only
    params: Dict = field(default_factory=dict)
    symbols: Tuple[str, ...] = ALL
    variants: Tuple[str, ...] = ALL_VARIANTS
    label: str = ""

    @property
    def runnable(self) -> bool:
        return self.fn is not None

    def run(self, ctx) -> None:
        self.fn(ctx, **self.params)


FLOWRSI_RULES = (
    "M15. Fast RSI(7) crosses the slow RSI(14) inside the zone (buy 25-50, sell 50-75) within 3 bars and is still "
    "crossed; SMC filter: a buy needs discount, a bullish FVG or a liquidity sweep (premium / bearish FVG / sweep "
    "for a sell). SL at the swing +/- 0.5 ATR with a pip floor, TP 1.5R; break-even at 1R with a 50 % partial, "
    "trailing from 1.2R. Macro TMS filter off (the replica does not model it; phase 1 showed it hurts).")
FLOWRSI_FINDINGS = (
    "2026-09-25 cTrader baseline #27-#41 (live presets, $2000, 01/01-24/09/2026): all 14 trading pairs negative, "
    "pooled -0.13R (t -7.3); 45 % of positions reach the partial.",
    "Macro TMS off: better on 11/14 pairs, pooled -0.084R, still negative (phase 1, jobs #42-#96).",
    "Offline fixed-lot sim, 15 pairs 2025-09/2026, no caps: -$67k (C1) / -$86k (C0); every pair negative in $.",
)
E_DESC = {
    "E1a": "the live cross traded in the opposite direction",
    "E1b": "fade only the crosses taken with slow RSI < 30 / > 70",
    "E2a": "RSI(14) pullback through 40/60 in the H1 EMA50 trend",
    "E2b": "RSI(14) pullback through 40/60 in the H4 EMA50 trend",
    "E3a": "RSI(2) < 10 / > 90 in the H1 trend",
    "E3b": "RSI(2) < 10 / > 90, no trend filter",
    "E4a": "close back inside Bollinger(20, 2) with ADX(14) < 20",
    "E4b": "close back inside Bollinger(20, 2), no ADX filter",
    "E5a": "Donchian 20 breakout in the H4 trend",
    "E5b": "Donchian 48 breakout in the H4 trend",
}
EXIT_DESC = {"X1": "fixed stop at the ATR level, TP 1.5R, no break-even or trailing",
             "X2": "FlowRSI's exits (break-even + partial at 1R, trailing)"}
SCREEN_FINDING = ("Entry screening 2026-09-25 (15 pairs, 2025 and 2026 on ticks, $2000, bar t >= 2 in 2025, Jan-May "
                  "and Jun-Sep 2026): negative in every period, none beat the random control; random entries cost "
                  "-0.03R (indices, BTC, XAU) to -0.16R (JPY crosses, ETH) per trade.")
BANK_FINDING = ("552-config bank on 2025-2026 (M1 engine): 0 configs with t >= 2 in 2025, Jan-May and Jun-Sep 2026. "
                "This entry is the family's best pooled 2025 cell, frozen for the lab.")


def _flowrsi_entries() -> List[StrategyInfo]:
    out = [StrategyInfo("FLOWRSI", "FlowRSI (live bot, Macro TMS off)", "live",
                        "cBot/FlowRsiBot.cs + app/cbot_presets.py; replica research/flowrsi/sim.py", "RSI cross + SMC", "M15",
                        FLOWRSI_RULES, FLOWRSI_FINDINGS, flowrsi, dict(name="C0", exit_mode="X2"),
                        label="replica calibrated on cTrader #43-#56, #93 (>= 93 % of entries matched)"),
           StrategyInfo("FLOWRSI-C1", "FlowRSI with the wider SL floor", "rejected", "FlowRSI phase 1, H2 (2026-09-25)",
                        "RSI cross + SMC", "M15", FLOWRSI_RULES + " MinSlFloorPips 25 (FX) / 30 (JPY).",
                        ("Phase 1: -0.134R -> -0.080R on 8 forex pairs, still negative.",), flowrsi,
                        dict(name="C1", exit_mode="X2"), label="replica")]
    for e, desc in E_DESC.items():
        for x in ("X1", "X2"):
            out.append(StrategyInfo(f"FLOWRSI-{e}-{x}", f"FlowRSI entry {e}, exit {x}", "rejected",
                                    "FlowRSI entry screening (2026-09-25, research/flowrsi/signals.py)", "entry screening",
                                    "M15", f"M15 entry: {desc}. Exit: {EXIT_DESC[x]}.", (SCREEN_FINDING,), flowrsi,
                                    dict(name=e, exit_mode=x), label="replica"))
    return out


JUDAS = StrategyInfo(
    "JUDAS", "Asian Range Judas Sweep (live bot)", "live",
    "cBot/AsianRangeJudasSweepBot.cs + app/trade_gates.py evaluate_judas_sweep_gate", "liquidity sweep", "M15",
    "Asian range = high/low of the 00:00-06:00 UTC bars. In the London (07-10 UTC summer) or New York (12:30-16 UTC "
    "summer) killzone, a bar that spikes beyond the range by the sweep buffer and closes back inside with a rejection "
    "wick >= 35 % of the bar opens a 3-bar signal window; the trade goes back into the range. Guards: range inside "
    "the preset and the server band, one trade per side per Asian session, the side locked after a decisive close "
    "beyond the range (an open position on that side is closed), entry within 25 % of the range from the swept "
    "level. SL = preset stoplossPip raised to max(AiSlMinFloorPips, 0.8 ATR14), TP = takeprofitPip, break-even at 1.5R.",
    ("Live on the demo account since 2026-09; entries only through the AI gate, so it was never backtested before "
     "the lab.",),
    judas, label="port, uncalibrated: the AI gate approves every candidate; AI SL/TP = the preset fallbacks")

TMSORB = StrategyInfo(
    "TMSORB", "TMS + ORB (live AiAgentBot)", "live",
    "cBot/AiAgentBot.cs + app/trade_gates.py evaluate_cycle_gate / validate_tms_close_decision",
    "ORB breakout + TDI bias", "M15 (USTEC M5), H1 bias",
    "Opening range = the first 15 minutes of the session (Tokyo 00:00, London 08:00, New York 13:00, US indices 14:30 "
    "UTC in winter, DST-adjusted). Macro bias = the last confirmed H1 TDI cross (RSI6 of Heikin-Ashi vs its SMA6, with "
    "HA colour and Stoch 6/6/4), with flip hysteresis. The server's cycle gate: in session and outside the NYSE-open "
    "buffer, bias set, post-TP gate clear, a decisive ORB breakout in the bias direction inside the entry window (or a "
    "TDI bounce / EMA-retest model 2), breakout-distance caps, choppy-market gate. Entry in the bias direction; SL 1.5 "
    "ATR clamped to [0.8, 3] ATR and widened to the far side of the range, TP >= SL x 4/3 (none in a trending "
    "session). Exits: break-even + 50 % partial at 1.2 ATR, ATR trailing with a tier 2, MFE giveback lock, session-end "
    "flatten, the AI's exit-signal / session-ending close (server-validated), bias-flip exit.",
    ("Live on the demo account since 2026-09; the AI decides every entry, so it was never backtested before the lab.",),
    tms_orb, label="port, uncalibrated: the AI approves every gate-passing candidate; loss-streak and dollar-risk "
                   "guards off")

REFRESH_ORIGIN = "strategy refresh 2026-09-26 (docs/superpowers/specs/2026-09-26-strategy-refresh-design.md)"
REFRESH_PENDING = ("Pre-registered 2026-09-26 (research/results/prereg_v2.md); result pending in lab run v2.",)
NO_CRYPTO = tuple(s for s in ALL if s not in ("BTCUSD", "ETHUSD"))
NO_MIRROR = ("real", "shuffle")
ORB_RULES = ("Opening range = bid high/low of the first 15 minutes of the session (local: Tokyo 09:00, London 08:00, "
             "Frankfurt 09:00, New York FX 08:00, New York cash 09:30; BTC/ETH on the cash open). For 3 hours after "
             "it the first tick beyond the range is a breakout; SL at the other side; no target; exit at the session "
             "end (Tokyo 15:00, London 16:30, Frankfurt 17:30, New York 16:00); one trade per session; skipped when "
             "the range is under 3 median spreads.")
TMS_STATE = (" Only breakouts in the direction of the H1 TMS state (last closed H1 bar: bull = TDI green (SMA2 of "
             "RSI13) > red (SMA7), green > 50, Heiken Ashi bullish; bear mirrored); a skipped side re-arms once bid "
             "is back inside the range.")
TMS_RULES = ("TMS (Trading Made Simple): TDI green (SMA2 of RSI13) crosses red (SMA7); enter at the close of candle 1, "
             "else candle 2, if green is still across, the Heiken Ashi bar has the trade's colour and Stoch(8,3,3) %K "
             "is on the trade's side of %D; never candle 3+. SL beyond the last 5 bars' low / high (+ spread for "
             "sells); exit at the bar close where green crosses back; no target.")
JUDAS_RULES = ("ICT: Asian range = M5 high/low 20:00-00:00 New York. In the London killzone (02:00-05:00 New York) a "
               "run beyond one side (sweep extreme H*), then an M5 close through the latest fractal swing before H* "
               "(market structure shift) with a fair value gap between the H* bar and the shift bar; limit at the "
               "gap's near edge until the killzone ends; SL beyond H* (+ spread for sells); TP the other side of the "
               "Asian range, placed only if TP >= SL distance; exit 12:00 New York; one filled trade per day; "
               "BTC/ETH excluded.")
REFRESH = [
    StrategyInfo("T1-ORB", "Opening range breakout (Crabel)", "candidate", REFRESH_ORIGIN, "ORB breakout",
                 "15-min range, ticks", ORB_RULES, REFRESH_PENDING, tms_orb2.orb),
    StrategyInfo("T2-TMSORB", "TMS + ORB", "candidate", REFRESH_ORIGIN, "ORB breakout + TMS bias",
                 "15-min range, H1 bias", ORB_RULES + TMS_STATE, REFRESH_PENDING, tms_orb2.orb, dict(tms=True)),
    StrategyInfo("T3-TMSORB-X", "TMS + ORB, TMS exit", "candidate", REFRESH_ORIGIN, "ORB breakout + TMS bias",
                 "15-min range, H1 bias",
                 ORB_RULES + TMS_STATE + " Also exits at the first H1 close with green crossed against the trade.",
                 REFRESH_PENDING, tms_orb2.orb, dict(tms=True, tms_exit=True)),
    StrategyInfo("T4-TMS-H4", "TMS system on H4", "candidate", REFRESH_ORIGIN, "TDI cross + Heiken Ashi", "H4",
                 TMS_RULES, REFRESH_PENDING, tms_orb2.tms_system, dict(tf=240)),
    StrategyInfo("T5-TMS-H1", "TMS system on H1", "candidate", REFRESH_ORIGIN, "TDI cross + Heiken Ashi", "H1",
                 TMS_RULES, REFRESH_PENDING, tms_orb2.tms_system, dict(tf=60)),
    StrategyInfo("J1-ICT", "Judas sweep, ICT model", "candidate", REFRESH_ORIGIN, "liquidity sweep", "M5",
                 JUDAS_RULES, REFRESH_PENDING, judas2.judas_ict, symbols=NO_CRYPTO),
    StrategyInfo("J2-ICT-MO", "Judas sweep, ICT + midnight open", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M5", JUDAS_RULES + " Sells only above the New York midnight open, buys only below it.",
                 REFRESH_PENDING, judas2.judas_ict, dict(midnight_filter=True), symbols=NO_CRYPTO),
    StrategyInfo("J3-ICT-2R", "Judas sweep, ICT, TP 2R", "candidate", REFRESH_ORIGIN, "liquidity sweep", "M5",
                 JUDAS_RULES + " TP = 2 x the stop distance instead of the range side (no TP check).",
                 REFRESH_PENDING, judas2.judas_ict, dict(tp_mode="2r"), symbols=NO_CRYPTO),
    StrategyInfo("J4-ICT-2KZ", "Judas sweep, ICT, London + NY AM", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M5", JUDAS_RULES + " Also the New York AM killzone 07:00-10:00, same range, still one trade a day.",
                 REFRESH_PENDING, judas2.judas_ict, dict(killzones=("london", "nyam")), symbols=NO_CRYPTO),
    StrategyInfo("J5-SWEEP", "Judas sweep-and-close (no MSS/FVG)", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M15",
                 "Asian range 20:00-00:00 New York. An M15 bar in the London killzone that trades beyond the range and "
                 "closes back inside is faded at the next tick; SL beyond the killzone's extreme so far (+ spread for "
                 "sells); TP the other side of the range, skipped when nearer than the stop; exit 12:00 New York; one "
                 "trade per day. Ablation of J1's structure-shift step.",
                 REFRESH_PENDING, judas2.judas_sweep_close, symbols=NO_CRYPTO),
    StrategyInfo("N1-FIX", "FX fixing reversal (London fix)", "candidate",
                 REFRESH_ORIGIN + "; Krohn, Mueller & Whelan (J. Finance 2024)", "flow", "clock",
                 "Weekdays: long USD 14:00 -> 16:00 London, short USD 16:00 -> 18:00 London; SL 3 x ATR20(H1).",
                 REFRESH_PENDING, literature.fix_reversal, symbols=MEF_PAIRS, variants=NO_MIRROR),
    StrategyInfo("N2-GOTOBI", "Gotobi Tokyo-fix USDJPY", "candidate",
                 REFRESH_ORIGIN + "; Bessho, Sugimoto & Suzuki (2023)", "flow", "clock",
                 "On the 5th/10th/15th/20th/25th/last day (weekend -> Friday before): long USDJPY 03:00 -> 09:55 Tokyo, "
                 "short 09:55 -> 11:55 Tokyo; SL 3 x ATR20(H1).",
                 REFRESH_PENDING, literature.gotobi, symbols=("USDJPY",), variants=NO_MIRROR),
    StrategyInfo("N3-IMOM", "Market intraday momentum", "candidate",
                 REFRESH_ORIGIN + "; Gao, Han, Li & Zhou (JFE 2018)", "intraday momentum", "30 min",
                 "Sign of the return from the previous session close to open + 30 minutes, traded over the session's "
                 "last 30 minutes (US30/USTEC New York 9:30-16:00, DE40 Berlin 9:00-17:30, UK100 London 8:00-16:30); "
                 "SL 2 x ATR20(30-min bars).",
                 REFRESH_PENDING, literature.intraday_momentum, symbols=INDICES),
    StrategyInfo("N4-LBO", "London breakout of the Asian range", "candidate", REFRESH_ORIGIN, "breakout",
                 "ticks",
                 "Range = bid high/low 00:00-07:00 London; the first breakout 07:00-10:00 London is followed; SL at the "
                 "range midpoint; no target; exit 16:00 London; one trade per day; skipped under 3 median spreads.",
                 REFRESH_PENDING, literature.london_breakout, symbols=FX + ("XAUUSD",)),
]
REFRESH_IDS = tuple(s.id for s in REFRESH)
# research/results/lab/v2/verdict.md (research/lab/verdict.py); gross / costs = holdout mean R before costs and the
# commission + swap per trade in R.
VERDICT_V2 = {
    'T1-ORB': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 9,816 trades, mean '
        'net -0.078R (t -3.8), gross -0.017R, costs 0.061R; 2025 $+4,447, 2026 $-4,914; 2023-24 -0.078R; '
        'control 100 %; mirror $-704; 32% of 22 symbols positive (best ETHUSD $+4,534). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth'
        ' >= 60 %.'),
    'T2-TMSORB': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 5,685 trades, mean '
        'net -0.071R (t -2.7), gross -0.010R, costs 0.061R; 2025 $+3,693, 2026 $-1,975; 2023-24 -0.081R; '
        'control 100 %; mirror $-411; 41% of 22 symbols positive (best ETHUSD $+4,252). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth'
        ' >= 60 %.'),
    'T3-TMSORB-X': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 5,685 trades, mean '
        'net -0.087R (t -3.6), gross -0.026R, costs 0.061R; 2025 $+2,289, 2026 $-1,663; 2023-24 -0.078R; '
        'control 100 %; mirror $-1,018; 32% of 22 symbols positive (best ETHUSD $+4,108). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth'
        ' >= 60 %.'),
    'T4-TMS-H4': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 10,194 trades, mean '
        'net -0.059R (t -5.2), gross -0.030R, costs 0.029R; 2025 $-32,031, 2026 $+3,177; 2023-24 -0.034R; '
        'control 95 %; mirror $-11,273; 18% of 22 symbols positive (best XAUUSD $+7,327). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth'
        ' >= 60 %.'),
    'T5-TMS-H1': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 40,606 trades, mean '
        'net -0.125R (t -20.8), gross -0.090R, costs 0.035R; 2025 $-70,038, 2026 $-57,351; 2023-24 -0.115R; '
        'control 0 %; mirror $-42,830; 9% of 22 symbols positive (best XAUUSD $+1,731). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; beats >= 95 % of '
        'control seeds; mirror net > 0; breadth >= 60 %.'),
    'J1-ICT': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 2,355 trades, mean '
        'net -0.131R (t -2.7), gross -0.026R, costs 0.105R; 2025 $-2,074, 2026 $-875; 2023-24 -0.191R; '
        'control 90 %; mirror $-1,147; 25% of 20 symbols positive (best UK100 $+339). Failed: holdout >= 100 '
        'trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; beats >= 95 % of control '
        'seeds; mirror net > 0; breadth >= 60 %.'),
    'J2-ICT-MO': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 2,117 trades, mean '
        'net -0.128R (t -2.4), gross -0.020R, costs 0.108R; 2025 $-1,833, 2026 $-637; 2023-24 -0.195R; '
        'control 100 %; mirror $-936; 20% of 20 symbols positive (best UK100 $+475). Failed: holdout >= 100 '
        'trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth >= '
        '60 %.'),
    'J3-ICT-2R': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 2,625 trades, mean '
        'net -0.114R (t -3.8), gross -0.016R, costs 0.099R; 2025 $-1,790, 2026 $-323; 2023-24 -0.170R; '
        'control 100 %; mirror $-1,167; 25% of 20 symbols positive (best XAUUSD $+365). Failed: holdout >= '
        '100 trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth'
        ' >= 60 %.'),
    'J4-ICT-2KZ': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 4,494 trades, mean '
        'net -0.156R (t -4.3), gross -0.030R, costs 0.126R; 2025 $-2,733, 2026 $-1,801; 2023-24 -0.213R; '
        'control 100 %; mirror $-1,830; 10% of 20 symbols positive (best US30 $+455). Failed: holdout >= 100 '
        'trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth >= '
        '60 %.'),
    'J5-SWEEP': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 5,502 trades, mean '
        'net -0.210R (t -6.0), gross -0.062R, costs 0.147R; 2025 $-3,325, 2026 $-1,823; 2023-24 -0.197R; '
        'control 100 %; mirror $-2,041; 20% of 20 symbols positive (best DE40 $+271). Failed: holdout >= 100 '
        'trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth >= '
        '60 %.'),
    'N1-FIX': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 4,490 trades, mean '
        'net -0.048R (t -7.2), gross -0.029R, costs 0.019R; 2025 $-5,258, 2026 $-2,397; 2023-24 -0.013R; '
        'control 5 %; 0% of 5 symbols positive (best AUDUSD $-1,215). Failed: holdout >= 100 trades, mean R >'
        ' 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; beats >= 95 % of control seeds; breadth >= '
        '60 %.'),
    'N2-GOTOBI': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 248 trades, mean net '
        '+0.035R (t +1.2), gross +0.044R, costs 0.009R; 2025 $+161, 2026 $+107; 2023-24 +0.041R; control 95 '
        '%; 100% of 1 symbols positive (best USDJPY $+268). Failed: holdout >= 100 trades, mean R > 0, t >= '
        '2.5.'),
    'N3-IMOM': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 1,735 trades, mean '
        'net -0.017R (t -2.0), gross -0.017R, costs 0.000R; 2025 $-505, 2026 $-757; 2023-24 -0.018R; control '
        '60 %; mirror $-783; 25% of 4 symbols positive (best USTEC $+44). Failed: holdout >= 100 trades, mean'
        ' R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; beats >= 95 % of control seeds; mirror '
        'net > 0; breadth >= 60 %.'),
    'N4-LBO': (
        'Lab run v2 (2026-09-26, pre-registered bar): failed. Holdout 2025-01..2026-09: 5,872 trades, mean '
        'net -0.070R (t -3.0), gross -0.012R, costs 0.059R; 2025 $-4,253, 2026 $+71; 2023-24 -0.096R; control'
        ' 100 %; mirror $-1,203; 19% of 16 symbols positive (best XAUUSD $+1,762). Failed: holdout >= 100 '
        'trades, mean R > 0, t >= 2.5; 2025 > 0 and 2026 > 0; 2023-24 mean R > 0; mirror net > 0; breadth >= '
        '60 %.'),
}
REFRESH = [replace(s, status="candidate" if VERDICT_V2[s.id].split(": ", 1)[1].startswith("passed") else "rejected",
                   findings=(VERDICT_V2[s.id],)) for s in REFRESH]
DROPPED = [
    StrategyInfo("PREFOMC", "Pre-FOMC announcement drift", "rejected",
                 "literature (Lucca & Moench 2015), refresh 2026-09-26", "calendar", "event",
                 "Long US equity indices over the 24 hours before scheduled FOMC announcements.",
                 ("Not run: the drift disappeared after 2015 (Kurov, Wolfe & Gilbert).",)),
    StrategyInfo("WKGAP", "FX weekend-gap fade", "rejected", "trading lore, refresh 2026-09-26", "gap fade", "weekly",
                 "Fade the Sunday-open gap of FX pairs towards Friday's close.",
                 ("Not run: gaps above 20 pips are rare and the Sunday-open spread is wide.",)),
    StrategyInfo("CARRY", "FX carry", "rejected", "literature (Lustig & Verdelhan), refresh 2026-09-26", "carry",
                 "weekly", "Long the highest-swap pairs, short the lowest, rebalanced weekly.",
                 ("Not run: the lab's swaps are the 2026 rates held constant, so 2023-25 carry cannot be measured.",)),
]

RESEARCH = [
    StrategyInfo("BTC-S1", "Shock-bar momentum", "rejected", "strategy search round 1 (2026-09-25), pre-registered",
                 "momentum", "M15",
                 "A bar whose close moved more than 2.5 x ATR20 (SMA of TR) is followed at the next tick; SL and TP 2 x "
                 "ATR from the fill; time exit after 12 bars.",
                 ("Sep-Dec 2024 unseen +0.22R (t 1.8); 2025 +0.10R, 2026 YTD +0.09R (ticks, $2000); 2023 +0.000R -> "
                  "pooled 2023-24 t 1.0: failed the confirmation bar.",
                  "Fixed lot 0.1: $ -103 / +1164 / +2154 / +260 for 2023..2026; beat random entries in 20/20 seeds (2025)."),
                 rules.shock_follow, dict(tf=15, Z=2.5, H=12, SLK=2.0, TPK=2.0)),
    StrategyInfo("XAU-T1", "H4 Donchian 30 trend", "rejected", "strategy search round 1 (2026-09-25), pre-registered",
                 "trend following", "H4",
                 "First H4 close beyond the prior 30-bar high/low -> follow at the next tick; SL 1.5 x ATR20, no target, "
                 "time exit after 12 bars.",
                 ("Jul-Dec 2024 +0.46R; 2023 +0.10R, 2024 +0.09R (t 0.5); shorts negative -> mostly gold beta.",
                  "Fixed lot 0.01: $ +39 / +154 / +283 / +665 for 2023..2026."),
                 rules.bank_rule, dict(kind="donch", mode=1, tf="H4", N=30, H=12, SLK=1.5, warm=31)),
    StrategyInfo("TOM", "Turn of the month", "rejected", "literature, round 2 (2026-09-25)", "calendar", "cash session",
                 "Long over the cash session on the last and the first three trading days of each month; SL 3 %.",
                 ("2025 +0.041R, 2026 +0.088R (t 3.0); 2023 +0.047R but the other days +0.021R; 2024 -0.014R: failed.",),
                 rules.turn_of_month, symbols=INDICES),
    StrategyInfo("K1", "FX weekly fade", "rejected", "round 1, pre-registered (strategy_prereg.md)", "mean reversion",
                 "D1",
                 "z = (C - C[5]) / ATR20(D1); |z| > 1.5 -> trade against z 2 h after the New York close; SL 3 x ATR from "
                 "the signal close, no target, exit after 5 D1 bars.",
                 ("2025 +0.10R (t 2.6, 8/8 pairs) -> 2026 -0.07R (1/8 pairs); 72-cell grid 0 % positive in 2026: "
                  "regime flip.",),
                 rules.weekly_fade, dict(SLK=3.0), symbols=FX),
    StrategyInfo("K1b", "FX weekly fade, SL 2 ATR", "rejected", "K1's sizing variant", "mean reversion", "D1",
                 "K1 with the stop at 2 x ATR.", ("Reported with K1; same verdict.",),
                 rules.weekly_fade, dict(SLK=2.0), symbols=FX),
    StrategyInfo("K2", "Index opening range (60 min)", "rejected", "round 1, pre-registered", "breakout", "cash session",
                 "Direction of the first 60 minutes of the cash session, entered at its end, stop at the other end of "
                 "the range, exit at the close.",
                 ("2025 +0.13R (t 2.3, best of 16 ORB variants) -> 2026 +0.005R: failed.",),
                 rules.opening_range, symbols=INDICES),
    StrategyInfo("VB1", "Index volatility breakout", "rejected", "round 2, pre-registered", "breakout", "cash session",
                 "Stop entries at the open +/- 0.35 x the mean range of the last 5 sessions; the first side touched "
                 "trades; SL at the open; exit at the close.",
                 ("2025 +0.10R (t 2.1), Jan-May 2026 +0.08R, Jun-Sep 2026 -0.14R: failed.",),
                 rules.vol_breakout, symbols=INDICES),
    StrategyInfo("LC1", "US last-30-minute fade", "rejected", "round 2, pre-registered", "intraday reversal", "30 min",
                 "Fade C(15:30) - C(10:00) New York from 15:30 to the 16:00 close; SL 2 x ATR20 (30 min).",
                 ("2025 +0.040R (t 2.2), 2026 +0.022R (t 1.3); Jul-Dec 2024 -0.001R: failed.",),
                 rules.last30_fade, symbols=US_INDICES),
    StrategyInfo("GF1", "US opening-gap fade", "rejected", "round 2, pre-registered", "intraday reversal", "M1",
                 "An opening gap larger than 0.1 x the mean session range is faded at 9:31 New York, TP at the previous "
                 "close, SL the gap's size beyond the open, exit at the close.",
                 ("2026 +0.046R (t 0.8): failed.",), rules.gap_fade, symbols=US_INDICES),
    StrategyInfo("OD1", "Overnight drift", "rejected", "literature (Boyarchenko, Larsen, Whelan 2023), round 2",
                 "calendar", "H1", "Long US30 / USTEC from 02:00 to 03:00 New York on weekdays; SL 2 x ATR20(H1).",
                 ("2025 -0.006R, 2026 +0.029R (t 2.6): sign flip, failed.",), rules.overnight_drift,
                 symbols=US_INDICES),
    StrategyInfo("MEF", "Month-end London fix USD flow", "rejected", "literature (Melvin & Prins 2015), round 2", "flow",
                 "H1",
                 "Last business day of the month, 10:00 -> 16:00 London: sell USD if US30 beat DE40 in USD over the "
                 "month, else buy it; SL 2 x ATR20(H1).",
                 ("20 events in 2025-26, +0.15R (t 1.0): too few to judge.",), rules.month_end_fix,
                 symbols=MEF_PAIRS, variants=REAL_ONLY),
    StrategyInfo("FXM1", "FX fade/follow regime switch", "rejected", "round 2, pre-registered", "meta", "D1",
                 "K1's signal traded in the direction the base fade earned over the last 120 days on the 8 FX pairs.",
                 ("May-Dec 2025 +0.11R (t 2.9), Jan-May 2026 -0.10R (t -2.3), Jun-Sep 2026 0.00R: failed.",),
                 rules.regime_fade, symbols=FX, variants=REAL_ONLY),
    StrategyInfo("X1", "Cross-sectional FX reversal", "rejected", "round 2, pre-registered", "cross-sectional", "H4",
                 "Currency strengths from the 8 pairs' 30-bar H4 returns; every 30 bars the 3 pairs with the largest "
                 "ATR-scaled strength gap are traded against it for 30 bars, no stop.",
                 ("2025 +0.74 ATR/trade (t 2.4) -> 2026 -0.09: failed.",), rules.cross_sectional_reversal,
                 symbols=FX_REAL, variants=REAL_ONLY),
    StrategyInfo("WF1", "Walk-forward ridge model", "rejected", "round 2, pre-registered", "machine learning", "M15",
                 "Ridge on 14 causal features, refit monthly on the prior 6 months; trade the top decile of |prediction| "
                 "in its direction, SL 2 x ATR20, exit after 4 bars.",
                 ("M15 all symbols -0.084R (t -17.5); low-cost group -0.005R; H1 -0.037R: failed.",),
                 rules.walk_forward_ridge),
]


def _bank_rules(kw: dict) -> str:
    way = "follow" if kw["mode"] > 0 else "fade"
    if kw["kind"] == "zmove":
        sig = f"C - C[{kw['L']}] beyond {kw['Z']} x ATR20"
    elif kw["kind"] == "donch":
        sig = f"first close beyond the prior {kw['N']}-bar high/low"
    else:
        sig = f"RSI({kw['P']}) above {100 - kw['lo']:g} / below {kw['lo']:g}"
    tp = f"TP {kw['TPK']} x ATR" if kw["TPK"] else "no target"
    return f"{kw['tf']}: {sig} -> {way}; SL {kw['SLK']} x ATR20 from the fill, {tp}, exit after {kw['H']} bars."


def _bank_entries() -> List[StrategyInfo]:
    out = []
    for name, r25 in zip(rules.BANK_CONFIGS, rules.BANK_2025_R):
        kw = rules.parse_bank(name)
        kind = {"zmove": "z-move", "donch": "Donchian", "rsi": "RSI"}[kw["kind"]]
        way = "follow" if kw["mode"] > 0 else "fade"
        out.append(StrategyInfo(f"BANK-{name}", f"Bank: {kind} {way} {kw['tf']}", "rejected",
                                "rule bank (research/scan/bank.py, 2026-09-25)", f"{kind} {way}", kw["tf"],
                                _bank_rules(kw), (BANK_FINDING, f"Pooled 2025 mean R of this cell: {r25:+.3f}."),
                                rules.bank_rule, kw))
    return out


INFO = [
    StrategyInfo("PAIRS", "Pairs / stat-arb", "not_applicable", "round 2 (2026-09-25)", "statistical arbitrage",
                 "M15/H1",
                 "Rolling-OLS z-score of the log spread of 14 related pairs (US30-USTEC, DE40-UK100, EURUSD-GBPUSD, "
                 "EURJPY-GBPJPY, BTC-ETH, ...); trade both legs.",
                 ("Nothing in 2025, not even before costs.",
                  "Needs two legs open at once: outside the lab's one-position rule.")),
    StrategyInfo("LEADLAG", "Cross-asset lead-lag", "rejected", "round 2 (2026-09-25)", "lead-lag", "M1/M5",
                 "Trade a follower (DE40, UK100, USTEC) on the leader's last M1/M5 move (US indices, DE40, BTC).",
                 ("Correlations of +2..4 % but only 1-2 spreads in size; rules ~0. Not coded in the lab.",)),
    StrategyInfo("HOD", "Hour-of-day drift", "rejected", "round 1 (2026-09-25)", "calendar", "H1",
                 "Trade the average return of each hour of the day.",
                 ("The only persistent pattern is the 17:00 New York rollover spread dip: not tradeable. Not coded.",)),
    StrategyInfo("NOISE", "Noise-area intraday momentum", "rejected", "round 1, literature", "intraday momentum",
                 "30 min", "Trade index breakouts of the average intraday move envelope.", ("2025 t < 1. Not coded.",)),
]

# 2026-09-27 retest on 2016-2022 (out of sample for strategies designed on 2023-2026), unchanged lab code, 15 real
# symbols; bar and verdicts in research/results/portfolio/prereg_swing_v2.md (R-series).
_RT = "Retest 2016-2022 (2026-09-27, unchanged code, out of sample; research/results/portfolio/prereg_swing_v2.md): "
RETEST_2016_2022 = {
    "N2-GOTOBI": _RT + "passed: 1,002 trades, +0.078R (t +5.7), 7/7 years positive, 10/10 random seeds beaten. "
                 "Ported to research/swing/swing.py with historical swaps: IS 2016-21 +0.066R, VAL 2022-24 +0.054R, "
                 "HOLD +0.038R; placebo (non-gotobi days) ~0. Basket with EURJPY/GBPJPY = C3, passed its holdout "
                 "(research/results/portfolio/swing_lab_v2_2026-09-27.md).",
    "N3-IMOM": _RT + "failed: 6,978 trades, -0.041R (t -8.1), 2/7 years.",
    "TOM": _RT + "failed: 1,316 trades, -0.006R (t -0.7), 2/7 years.",
    "K2": _RT + "failed: 7,138 trades, -0.034R (t -2.0), 2/7 years.",
    "VB1": _RT + "failed: 6,572 trades, +0.023R (t +1.3), 5/7 years.",
    "LC1": _RT + "failed: 3,591 trades, -0.060R (t -7.9), 0/7 years.",
    "GF1": _RT + "failed: 2,944 trades, -0.036R (t -2.0), 1/7 years.",
    "OD1": _RT + "failed: 3,603 trades, -0.048R (t -11.2), 1/7 years.",
    "MEF": _RT + "failed: 415 trades, -0.040R (t -0.7), 2/7 years.",
    "BANK-zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0": _RT + "failed: 334 trades, +0.021R (t +0.4), 5/7 years.",
    "BANK-rsiR_D1_P2_lo5_H3_SL1.5_TPNone": _RT + "failed: 2,293 trades, -0.035R (t -2.1), 3/7 years.",
    "BANK-donchR_D1_N10_H6_SL1.5_TPNone": _RT + "failed: 2,242 trades, -0.053R (t -2.5), 2/7 years.",
}


def _with_retest(s: StrategyInfo) -> StrategyInfo:
    if s.id not in RETEST_2016_2022:
        return s
    status = "candidate" if s.id == "N2-GOTOBI" else s.status
    return replace(s, status=status, findings=s.findings + (RETEST_2016_2022[s.id],))


CATALOG: List[StrategyInfo] = [_with_retest(s) for s in
                               [*_flowrsi_entries(), JUDAS, TMSORB, *REFRESH, *RESEARCH, *_bank_entries(), *INFO,
                                *DROPPED]]


def by_id() -> Dict[str, StrategyInfo]:
    return {s.id: s for s in CATALOG}


def runnable_ids() -> List[str]:
    return [s.id for s in CATALOG if s.runnable]


def catalog_hash() -> str:
    text = "|".join(f"{s.id}:{s.fn.__name__ if s.fn else ''}:{sorted(s.params.items())}:{s.symbols}:{s.variants}:"
                    f"{s.rules}" for s in CATALOG)
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _lab_results(run_dirs) -> Dict[str, dict]:
    out = {}
    for run_dir in run_dirs:
        path = Path(run_dir) / "cells.csv"
        if not path.exists():
            continue
        run = {}
        with open(path) as fh:
            for row in csv.DictReader(fh):
                s = run.setdefault(row["strategy"], dict(run=Path(run_dir).name, net=0.0, cells=0, pos=0, every=0,
                                                         flags=0, best=("", -1e18)))
                net = float(row["net"])
                s["net"] += net
                s["cells"] += 1
                s["pos"] += net > 0
                s["every"] += row["pos_every_year"] == "True"
                s["flags"] += row["all_flags"] == "True"
                if net > s["best"][1]:
                    s["best"] = (row["symbol"], net)
        out.update(run)
    return out


def _symbols(s: StrategyInfo) -> str:
    named = {ALL: "all 22", FX: "FX 15", NO_CRYPTO: "all 22 but BTC/ETH", FX + ("XAUUSD",): "FX 15 + XAUUSD"}
    return named.get(s.symbols, ", ".join(s.symbols))


def render_markdown(run_dirs=()) -> str:
    run_dirs = [run_dirs] if isinstance(run_dirs, (str, Path)) else list(run_dirs or ())
    lab = _lab_results(run_dirs)
    names = ", ".join(f"`{Path(d).name}`" for d in run_dirs)
    src = (f" and the lab run {names}" if len(run_dirs) == 1 else
           f" and the lab runs {names} (a strategy in a later run replaces its earlier result)" if run_dirs else "")
    lines = ["# Strategy catalog", "",
             f"_Generated by `python -m research.lab.catalog` from `research/lab/catalog.py`{src}. Edit the catalog, "
             "not this file._", "",
             "Lab rules: $10k, fixed lots per symbol, no loss limits, one position per strategy x symbol, tick level, "
             "2023-01 .. 2026-09 (docs/superpowers/specs/2026-09-25-strategy-lab-design.md).", "",
             "| id | name | status | family | TF | symbols | lab net $ | cells + | all flags |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in CATALOG:
        r = lab.get(s.id)
        cols = f"{r['net']:+,.0f} | {r['pos']}/{r['cells']} | {r['flags']}" if r else " | | "
        lines.append(f"| {s.id} | {s.name} | {s.status} | {s.family} | {s.timeframe} | {_symbols(s)} | {cols} |")
    lines.append("")
    for s in CATALOG:
        lines += [f"## {s.id} — {s.name}", "", f"- Status: **{s.status}**" + (f" ({s.label})" if s.label else ""),
                  f"- Origin: {s.origin}", f"- Family / timeframe: {s.family} / {s.timeframe}", f"- Rules: {s.rules}"]
        if s.params:
            lines.append(f"- Parameters: `{s.params}`")
        lines.append(f"- Lab: `{s.fn.__module__}.{s.fn.__name__}` on {_symbols(s)}, variants {', '.join(s.variants)}"
                     if s.runnable else "- Lab: not run")
        lines += [f"- Finding: {f}" for f in s.findings]
        r = lab.get(s.id)
        if r:
            lines.append(f"- Latest lab run `{r['run']}`: net ${r['net']:+,.0f} over {r['cells']} symbols, {r['pos']} positive, "
                         f"{r['every']} positive every year, {r['flags']} with all four flags; best {r['best'][0]} "
                         f"${r['best'][1]:+,.0f}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    OUT.write_text(render_markdown(argv))
    print(OUT)


if __name__ == "__main__":
    main()
