"""Request and response models of the /trade endpoint (the cBot market snapshot and the agent decision).

Split out of app/server.py, which re-exports every name here.
"""
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.bot_controls import sanitize_bot_id  # shared with the dashboard's bot-facing routes

# ---- Data Models (from cBot) ----
class BarData(BaseModel):
    # TMS Heikin-Ashi / Stoch / TDI fields
    ha_color: Optional[str] = None
    tdi_green: Optional[float] = None
    tdi_red: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None

    # Standard OHLCV fields (used in Judas Sweep / SMC)
    time: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

class TmsSignals(BaseModel):
    # Bias
    bias: str = "NEUTRAL"  # "BULLISH"/"BEARISH" cross lock; NEUTRAL only before the first confirmed cross
    bars_since_cross: int = 0
    cross_direction: Optional[str] = None
    # FlowRsiBot: "cross_lock", or "ema" when its lock was older than MaxMacroLockAgeBars and
    # `bias` is the macro EMA trend instead. None from bots that only send the lock.
    bias_source: Optional[str] = None

    # Current signals
    cross_up: bool = False
    cross_down: bool = False
    ha_turned_green: bool = False
    ha_turned_red: bool = False
    stoch_bull: bool = False
    stoch_bear: bool = False
    angle_ok_long: bool = False
    angle_ok_short: bool = False
    within_window: bool = False

    # Entry signals (all conditions met)
    price_above_ema: bool = False
    price_below_ema: bool = False
    long_entry: bool = False
    short_entry: bool = False

    # Exit signals
    exit_long: bool = False
    exit_short: bool = False
    exit_reason: str = ""

    # TDI level
    tdi_level: str = "neutral"

    # TF Green State (current chart timeframe momentum)
    green_tf_value: float = 50.0
    green_tf_slope: float = 0.0  # positive = rising, negative = falling

    # TDI Bounce Detection (dnse-kash)
    tdi_bounce_bull: bool = False
    tdi_bounce_bear: bool = False

    # Post-TP Gate State
    post_tp_gate_active: bool = False
    post_tp_gate_side: Optional[str] = None

class MarketRegimeInfo(BaseModel):
    regime: str = "forming"  # "forming", "trending", "choppy", "mixed"
    er_session: Optional[float] = None
    er_recent: Optional[float] = None
    or_flips: int = 0

class OrbData(BaseModel):
    or_high: float = 0.0
    or_low: float = 0.0
    or_mid: float = 0.0
    or_width: float = 0.0
    or_complete: bool = False
    breakout_direction: Optional[str] = None  # "up", "down", null
    breakout_price: float = 0.0
    breakout_distance_pips: float = 0.0  # how far price is beyond OR boundary
    bars_since_breakout: int = 0
    in_entry_window: bool = False
    is_decisive: bool = False  # breakout_distance >= MinDecisiveBreakoutPips
    price_position: str = "inside"

class PositionInfo(BaseModel):
    side: Optional[str] = None  # "BUY", "SELL"
    type: Optional[str] = None  # Alias for side used in some cBots
    id: Optional[int] = None
    entry_price: float = 0.0
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_pips: float = 0.0
    pnl: Optional[float] = None  # Alias for unrealized_pnl
    pnl_pips: Optional[float] = None  # Alias for unrealized_pnl_pips
    pips: Optional[float] = None  # Alias for unrealized_pnl_pips (the tick route's name)
    mfe_pips: float = 0.0  # Maximum Favorable Excursion
    giveback_pips: float = 0.0  # MFE - current profit
    sl_price: float = 0.0
    tp_price: float = 0.0
    sl: Optional[float] = None
    tp: Optional[float] = None
    bars_held: int = 0
    duration_minutes: float = 0.0
    volume: Optional[float] = None

    @property
    def resolved_side(self) -> str:
        return (self.side or self.type or "BUY").upper()

    @property
    def resolved_pnl(self) -> float:
        return self.unrealized_pnl if self.unrealized_pnl != 0.0 else (self.pnl or 0.0)

    @property
    def resolved_pnl_pips(self) -> float:
        """The position's P&L in pips, under whichever name the reporting cBot used.

        AiAgentBot sends `unrealized_pnl_pips`; FlowRsiBot and AsianRangeJudasSweepBot use the
        short names they already use on the tick route (`pnl_pips` / `pips`), matching their
        `pnl` alias for the money. Only the bot can produce this figure - the server has no pip
        size and no FX rate - so an unreported name has to fall through to the next alias
        instead of the 0.0 default, which is what printed a flat "(0.0p)" next to a correct
        dollar amount on the dashboard. A pips field the bot did send is authoritative even
        when it is exactly 0.0, hence the membership test rather than a truthiness one.
        """
        if "unrealized_pnl_pips" in self.model_fields_set:
            return self.unrealized_pnl_pips
        for alias in (self.pnl_pips, self.pips):
            if alias is not None:
                return alias
        return self.unrealized_pnl_pips

class SessionInfo(BaseModel):
    session_name: str = "london"  # "london", "newyork", "tokyo", etc.
    phase: str = "active"  # "pre", "active", "ending", "closed"
    minutes_to_end: int = 0
    is_trading_time: bool = True

# ---- Judas Sweep / Smart Money Concepts (SMC) Data Models ----
class StrategyData(BaseModel):
    tema1: float = 0.0
    tema2: float = 0.0
    rsi: float = 0.0
    adx: float = 0.0
    atr: float = 0.0
    recent_high: float = 0.0
    recent_low: float = 0.0
    asian_high: float = 0.0
    asian_low: float = 0.0
    asian_range_pips: float = 0.0
    # Structural invalidation state mirrored from the cBot's Judas Structural Guard:
    # a decisive M15 close beyond the boundary turns the sweep level into a breakout
    # level, so the mean-reversion side is dead for the rest of the Asian session.
    asian_low_broken: bool = False
    asian_high_broken: bool = False
    # Exact Symbol.PipSize from the cBot; 0.0 means an older bot that omitted it.
    pip_size: float = 0.0
    killzone_session: str = "NONE"
    bias_direction: str = "NONE"
    traditional_signal: str = "NONE"
    signal_window_bars: int = 0

class SwingStructure(BaseModel):
    last_swing_high: float = 0.0
    swing_high_type: Optional[str] = None
    last_swing_low: float = 0.0
    swing_low_type: Optional[str] = None
    prev_swing_high: float = 0.0
    prev_swing_low: float = 0.0
    market_structure: Optional[str] = None

class TimeframeContext(BaseModel):
    timeframe: Optional[str] = None
    fast_tema: float = 0.0
    slow_tema: float = 0.0
    rsi: float = 0.0
    trend_bias: Optional[str] = None
    high_35: float = 0.0
    low_35: float = 0.0
    close: float = 0.0
    swing_structure: Optional[SwingStructure] = None

class MultiTimeframeData(BaseModel):
    current_tf: Optional[TimeframeContext] = None
    h1_tf: Optional[TimeframeContext] = None
    h4_tf: Optional[TimeframeContext] = None

class ActivePosition(BaseModel):
    id: Optional[int] = None
    symbol: Optional[str] = None
    trade_type: Optional[str] = None
    volume: float = 0.0
    entry_price: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    entry_time: Optional[str] = None

class HistoricalTrade(BaseModel):
    position_id: Optional[int] = None
    symbol: Optional[str] = None
    trade_type: Optional[str] = None
    volume: float = 0.0
    entry_price: float = 0.0
    exit_price: float = 0.0
    pnl: float = 0.0
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None

class MarketSnapshot(BaseModel):
    request_id: Optional[str] = None
    bot_id: str = "default"  # Bot identifier for portfolio tracking
    symbol: str
    timeframe: str
    tms_timeframe: Optional[str] = "Hour"
    ask: float
    bid: float
    atr_pips: Optional[float] = None
    spread_pips: Optional[float] = None
    # Exact Symbol.PipSize from the cBot. FlowRsiBot has always sent this at the top
    # level; without the field Pydantic dropped it and the server fell back to the
    # per-asset-class table, which cannot know a broker's digit convention.
    pip_size: float = 0.0
    bars: List[BarData] = []
    tms: Optional[TmsSignals] = None
    chart_tms: Optional[TmsSignals] = None
    orb: Optional[OrbData] = None
    market: Optional[MarketRegimeInfo] = None
    position: Optional[PositionInfo] = None
    session: Optional[SessionInfo] = None
    strategy: Optional[StrategyData] = None
    # FlowRSI / Nested RSI SMC Engine fields
    fast_rsi: Optional[float] = None
    slow_rsi: Optional[float] = None
    rsi_cross_signal: Optional[str] = None
    in_fvg_zone: Optional[bool] = None
    fvg_type: Optional[str] = None
    is_discount: Optional[bool] = None
    is_premium: Optional[bool] = None
    liquidity_swept: Optional[bool] = None
    swept_liquidity_type: Optional[str] = None
    technical_sl_price: Optional[float] = None
    technical_tp_price: Optional[float] = None
    technical_risk_reward: Optional[float] = None
    candidate_action: Optional[str] = None
    multi_timeframe: Optional[MultiTimeframeData] = None
    active_positions: Optional[List[ActivePosition]] = None
    recent_history: Optional[List[HistoricalTrade]] = None
    loss_streak: int = 0
    day_pnl: float = 0.0
    trades_today: int = 0
    account_id: Optional[str] = None
    account_number: str = "0"
    account_type: str = "demo"
    account_label: Optional[str] = None
    account_balance: float = 10000.0
    account_equity: float = 10000.0
    # Used margin as cTrader reports it (Account.Margin). None from a cBot build that predates
    # the field, in which case check_risk falls back to its per-lot estimate.
    account_margin: Optional[float] = None

    @field_validator("bot_id", mode="before")
    @classmethod
    def clean_bot_id(cls, v):
        return sanitize_bot_id(v)

    @field_validator("account_label", mode="before")
    @classmethod
    def clean_account_label(cls, v):
        if not v:
            return None
        cleaned = str(v).strip().strip("\"'“”`")
        return cleaned or None

# ---- Output Format ----
class AgentDecision(BaseModel):
    action: str  # "BUY", "SELL", "CLOSE_ALL", "HOLD", "ADJUST"
    volume_lots: Optional[float] = 0.01
    sl_pips: Optional[float] = 0.0
    tp_pips: Optional[float] = 0.0
    new_sl_price: Optional[float] = 0.0
    new_tp_price: Optional[float] = 0.0
    confidence: Optional[float] = 80.0
    reason: str = ""
    request_id: Optional[str] = None
    bot_id: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None

    @field_validator("volume_lots", "sl_pips", "tp_pips", "new_sl_price", "new_tp_price", "confidence", mode="before")
    @classmethod
    def coerce_none_to_default(cls, v, info):
        defaults = {
            "volume_lots": 0.01,
            "sl_pips": 0.0,
            "tp_pips": 0.0,
            "new_sl_price": 0.0,
            "new_tp_price": 0.0,
            "confidence": 80.0,
        }
        if v is None or v == "":
            return defaults.get(info.field_name, 0.0)
        try:
            return float(v)
        except (ValueError, TypeError):
            return defaults.get(info.field_name, 0.0)
