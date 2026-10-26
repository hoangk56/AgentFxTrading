using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    /// <summary>
    /// Gotobi Tokyo-fix bot (research C3, research/results/portfolio/swing_lab_v2_2026-09-27.md).
    ///
    /// On gotobi days (the 5th, 10th, 15th, 20th, 25th and the last day of the month; a Saturday or Sunday moves to
    /// the Friday before) Japanese importers buy USD at the 09:55 Tokyo fixing, so the yen weakens into the fix and
    /// gives some of it back afterwards. The bot buys the chart symbol at 03:00 Tokyo (18:00 UTC the evening
    /// before), closes at the 09:55 fix (00:55 UTC), sells at the fix and closes at 11:55 Tokyo (02:55 UTC).
    /// Tokyo keeps no daylight saving time, so every time here is a fixed UTC time.
    ///
    /// Run one instance per symbol: USDJPY, EURJPY, GBPJPY (the three the research validated; AUDJPY showed no
    /// effect). An instance holds one leg at a time and never longer than one leg (7 h at most). At the fix the short
    /// is sent while the long closes, so for under a second both are open.
    ///
    /// Sizing never reads the account: every trade risks `RiskPerTradeMoney` at a stop of 3 x ATR20(H1), so the lot
    /// follows volatility around that default risk, not equity.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class GotobiBot : Robot
    {
        #region Parameters
        [Parameter("Bot ID", Group = "General", DefaultValue = "Gotobi")]
        public string BotId { get; set; }

        [Parameter("Account Identifier", Group = "General", DefaultValue = "demo")]
        public string AccountLabel { get; set; }

        [Parameter("Show Detailed Logs", Group = "General", DefaultValue = true)]
        public bool ShowLogs { get; set; }

        [Parameter("Trade the Long Leg (into the fix)", Group = "Schedule (UTC)", DefaultValue = true)]
        public bool TradeLong { get; set; }

        [Parameter("Trade the Short Leg (after the fix)", Group = "Schedule (UTC)", DefaultValue = true)]
        public bool TradeShort { get; set; }

        [Parameter("Long Entry Hour (UTC, day before)", Group = "Schedule (UTC)", DefaultValue = 18, MinValue = 0, MaxValue = 23)]
        public int LongEntryHourUtc { get; set; }

        [Parameter("Long Entry Minute (UTC)", Group = "Schedule (UTC)", DefaultValue = 0, MinValue = 0, MaxValue = 59)]
        public int LongEntryMinuteUtc { get; set; }

        // The long may still open until this time (weekend open on Sunday evening, a restart, a wide spread);
        // the research found the leg's start hardly matters between 17:00 and 21:00 UTC.
        // Each leg opens at its own time in Long Entry +/- this many minutes (drawn per symbol and day), so the three
        // pairs never enter on the same second and no entry hour repeats. 60 keeps it inside 17:00..19:00 UTC, part
        // of the 17:00..21:00 range the research found makes no difference.
        [Parameter("Long Entry Jitter (+/- minutes)", Group = "Schedule (UTC)", DefaultValue = 60, MinValue = 0, MaxValue = 180)]
        public int LongEntryJitterMinutes { get; set; }

        [Parameter("Long Entry Latest Hour (UTC, day before)", Group = "Schedule (UTC)", DefaultValue = 23, MinValue = 0, MaxValue = 23)]
        public int LongEntryLatestHourUtc { get; set; }

        [Parameter("Long Entry Latest Minute (UTC)", Group = "Schedule (UTC)", DefaultValue = 0, MinValue = 0, MaxValue = 59)]
        public int LongEntryLatestMinuteUtc { get; set; }

        [Parameter("Fix Hour (UTC)", Group = "Schedule (UTC)", DefaultValue = 0, MinValue = 0, MaxValue = 23)]
        public int FixHourUtc { get; set; }

        [Parameter("Fix Minute (UTC)", Group = "Schedule (UTC)", DefaultValue = 55, MinValue = 0, MaxValue = 59)]
        public int FixMinuteUtc { get; set; }

        // A short opened 10 minutes after the fix lost money in 2016-2021; do not chase the fix.
        [Parameter("Short Entry Grace (minutes after the fix)", Group = "Schedule (UTC)", DefaultValue = 3, MinValue = 0, MaxValue = 5)]
        public int ShortEntryGraceMinutes { get; set; }

        [Parameter("Short Exit Hour (UTC)", Group = "Schedule (UTC)", DefaultValue = 2, MinValue = 0, MaxValue = 23)]
        public int ShortExitHourUtc { get; set; }

        [Parameter("Short Exit Minute (UTC)", Group = "Schedule (UTC)", DefaultValue = 55, MinValue = 0, MaxValue = 59)]
        public int ShortExitMinuteUtc { get; set; }

        // Gotobi days to skip, e.g. Japanese public holidays (no Tokyo fix): "2026-11-03,2026-11-23".
        // Default: Christmas 2026 (a Friday gotobi day). The broker is closed at the 09:55 fix, so the long bought on
        // the 24th could not close until the market reopens after the weekend. A value passed in replaces this one.
        [Parameter("Skip Dates (yyyy-MM-dd, comma separated)", Group = "Schedule (UTC)", DefaultValue = "2026-12-25")]
        public string SkipDates { get; set; }

        [Parameter("Default Risk per Trade ($)", Group = "Risk", DefaultValue = 50.0, MinValue = 1.0)]
        public double RiskPerTradeMoney { get; set; }

        [Parameter("Stop (x ATR of H1)", Group = "Risk", DefaultValue = 3.0, MinValue = 0.5, MaxValue = 10.0)]
        public double StopAtrMultiplier { get; set; }

        [Parameter("ATR Period (H1, simple)", Group = "Risk", DefaultValue = 20, MinValue = 2, MaxValue = 200)]
        public int AtrPeriod { get; set; }

        // When the default risk buys less than the minimum lot, trade the minimum only if it risks at most this
        // multiple of the default; otherwise skip the leg.
        [Parameter("Max Min-Lot Risk (x default)", Group = "Risk", DefaultValue = 1.5, MinValue = 1.0, MaxValue = 5.0)]
        public double MaxMinLotRiskMultiple { get; set; }

        [Parameter("Max Lots per Trade", Group = "Risk", DefaultValue = 5.0, MinValue = 0.01)]
        public double MaxLotsPerTrade { get; set; }

        [Parameter("Max Spread (pips)", Group = "Risk", DefaultValue = 3.0, MinValue = 0.1)]
        public double MaxSpreadPips { get; set; }

        // A leg whose order failed, or whose spread was too wide, is tried again after this many seconds. The short
        // goes out at the fix, when the price moves fastest: on 05/10/2026 two live shorts failed with TechnicalError
        // and waited 30 s (research/results/portfolio/gotobi_live_fills_2026-10-06.md).
        [Parameter("Order Retry (seconds)", Group = "Risk", DefaultValue = 2, MinValue = 1, MaxValue = 60)]
        public int OrderRetrySeconds { get; set; }

        // Last line of defence after a restart or a missed exit: legs close at their planned time; anything the bot
        // owns that is older than this is closed too. Far inside the 5-day limit.
        [Parameter("Max Hold (hours)", Group = "Risk", DefaultValue = 12, MinValue = 1, MaxValue = 120)]
        public int MaxHoldHours { get; set; }

        // Camouflage: what the broker must not learn from the orders (see the "Camouflage" region).
        [Parameter("Camouflage (virtual stop, decoys)", Group = "Camouflage", DefaultValue = true)]
        public bool VirtualStop { get; set; }

        // The broker's stop is a random fraction of the real stop, never wider: a bot or VPS that dies loses at most
        // 1 R a position. A real leg therefore stops at the broker's stop, somewhat inside 3 x ATR; a decoy's tighter
        // virtual stop comes first.
        [Parameter("Broker Stop Min (x the stop)", Group = "Camouflage", DefaultValue = 0.8, MinValue = 0.1, MaxValue = 1.0)]
        public double EmergencyStopMin { get; set; }

        [Parameter("Broker Stop Max (x the stop)", Group = "Camouflage", DefaultValue = 1.0, MinValue = 0.1, MaxValue = 1.0)]
        public double EmergencyStopMax { get; set; }

        // Chance that a leg is traded as a decoy on a weekday that is not a gotobi day: same hours, same lot, but a
        // tight virtual stop, so most decoys lose a little. 0.8 gives ~2 decoys per real leg (~15 plain weekdays
        // against ~6 gotobi days a month). The same hours on plain days made ~0 R before costs in the research
        // (placebo), so a decoy costs its spread and commission.
        [Parameter("Decoy Leg Probability (plain weekdays)", Group = "Camouflage", DefaultValue = 0.8, MinValue = 0.0, MaxValue = 1.0)]
        public double DecoyLegProbability { get; set; }

        [Parameter("Decoy Stop (x ATR of H1)", Group = "Camouflage", DefaultValue = 0.5, MinValue = 0.1, MaxValue = 10.0)]
        public double DecoyStopAtrMultiplier { get; set; }

        // Share of the decoys traded at DecoySmallLots instead of a real leg's lot. A decoy at the real lot cost -$7.8
        // at $200 risk, one at 0.01 lot -$0.20 (research/results/portfolio/gotobi_camouflage_2026-09-30.md), so all
        // decoys are small by default: they still pull the visible win rate down, but a broker can tell them by size.
        [Parameter("Small Decoy Share", Group = "Camouflage", DefaultValue = 1.0, MinValue = 0.0, MaxValue = 1.0)]
        public double DecoySmallShare { get; set; }

        [Parameter("Small Decoy Lots", Group = "Camouflage", DefaultValue = 0.01, MinValue = 0.01)]
        public double DecoySmallLots { get; set; }

        [Parameter("Agent API URL", Group = "Server", DefaultValue = "http://127.0.0.1:8000/trade")]
        public string ApiUrl { get; set; }

        [Parameter("Telemetry Endpoint (empty = from API URL)", Group = "Server", DefaultValue = "")]
        public string TelemetryUrl { get; set; }

        [Parameter("Portfolio Report Endpoint (empty = from API URL)", Group = "Server", DefaultValue = "")]
        public string ReportUrl { get; set; }

        [Parameter("Command Poll (ms, 0=off)", Group = "Server", DefaultValue = 2000, MinValue = 0)]
        public int CommandPollMs { get; set; }
        #endregion

        #region State
        private enum Leg { Long, Short }

        private const string LongTag = "GOTOBI-L";
        private const string ShortTag = "GOTOBI-S";
        private const string ManualCloseReason = "Manual close (dashboard)";

        private Bars _h1;
        private AverageTrueRange _atr;
        // Each own position's leg: set when the bot opens it, read back off the position after a restart (LegOf).
        private readonly Dictionary<int, LegInfo> _legs = new Dictionary<int, LegInfo>();
        private readonly HashSet<DateTime> _skipDates = new HashSet<DateTime>();
        private readonly HashSet<string> _legsDone = new HashSet<string>();
        private readonly Dictionary<string, DateTime> _lastAttemptAt = new Dictionary<string, DateTime>();
        private readonly Dictionary<string, int> _orderFailures = new Dictionary<string, int>();
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();
        private readonly Dictionary<int, double> _initialSlPips = new Dictionary<int, double>();
        // A leg's order is asynchronous (ExecuteMarketOrderAsync): no other order goes out until its result arrives,
        // or until PendingOrderTimeoutSeconds have passed without one (then LegAlreadyTraded finds a fill it missed).
        private const double PendingOrderTimeoutSeconds = 30;
        private string _pendingOrderTag;
        private DateTime _pendingOrderSince;
        // The quote and the clock when each close was sent, for the slippage the close's log line reports.
        private readonly Dictionary<int, SentQuote> _closeQuotes = new Dictionary<int, SentQuote>();
        // The units each own position opened with (TrackOpenedUnits). A stop out or a partial close leaves the position
        // open on fewer units; the slices it closed are History deals that Positions.Closed does not carry (23/10/2026:
        // the broker stopped out the three live shorts in slices and -$660 of them went unreported).
        private readonly Dictionary<int, double> _openedUnits = new Dictionary<int, double>();
        // Evaluate() also runs from the 1 s timer, which fires without ticks. Before the first quote of the week (or
        // while the broker is closed on a holiday) Symbol.Bid/Ask still hold the last quote before the close, so the
        // spread check, an order and a close would all use that stale price (backtests #366-#374 filled USDJPY at
        // Friday's ask on winter Sundays at 21:01 UTC, an hour before the first tick). Nothing trades until a quote
        // at most MaxQuoteAgeSeconds old has arrived.
        private const double MaxQuoteAgeSeconds = 60;
        private DateTime _lastTickAt = DateTime.MinValue;
        private DateTime _lastBarHandled = DateTime.MinValue;
        private DateTime _lastTickTelemetryTime = DateTime.MinValue;
        private DateTime _lastSpreadLogAt = DateTime.MinValue;
        private volatile bool _isStopped;

        // uvicorn closes an idle keep-alive connection after 5 s; retire pooled ones before it does
        // (see tests/test_cbot_report_retry.py).
        private readonly HttpClient _httpClient = new HttpClient(new SocketsHttpHandler { PooledConnectionIdleTimeout = TimeSpan.FromSeconds(4) })
        {
            Timeout = TimeSpan.FromSeconds(60)
        };
        #endregion

        #region Lifecycle
        protected override void OnStart()
        {
            Print($"[Gotobi] Starting '{BotId}' on {SymbolName}: long {LongEntryHourUtc:00}:{LongEntryMinuteUtc:00} -> fix {FixHourUtc:00}:{FixMinuteUtc:00} UTC, " +
                  $"short -> {ShortExitHourUtc:00}:{ShortExitMinuteUtc:00} UTC, risk ${RiskPerTradeMoney:F2} at {StopAtrMultiplier} x ATR{AtrPeriod}(H1)");

            _h1 = MarketData.GetBars(TimeFrame.Hour);
            _atr = Indicators.AverageTrueRange(_h1, AtrPeriod, MovingAverageType.Simple);

            foreach (var part in (SkipDates ?? "").Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
            {
                if (DateTime.TryParseExact(part.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var d))
                    _skipDates.Add(d.Date);
                else
                    Print($"[Gotobi] Skip date '{part}' is not yyyy-MM-dd; ignored");
            }

            if (Camouflaged)
                Print($"[Gotobi] Camouflage: virtual stop, broker stop {EmergencyStopMin}-{EmergencyStopMax} x, " +
                      $"decoys p={DecoyLegProbability} at {DecoyStopAtrMultiplier} x ATR, entry +/-{LongEntryJitterMinutes} min");

            Positions.Closed += OnPositionClosed;
            StartCommandPoll();
            Timer.Start(TimeSpan.FromSeconds(1));
            Evaluate();
        }

        protected override void OnTick()
        {
            _lastTickAt = Server.Time;
            Evaluate();
            SendLiveTickTelemetry();
        }

        protected override void OnTimer()
        {
            Evaluate();
            SendLiveTickTelemetry();
        }

        protected override void OnBarClosed()
        {
            _lastBarHandled = Server.Time;
        }

        protected override void OnStop()
        {
            // Positions are left to their stop; a restart closes any leg whose planned exit has passed.
            _isStopped = true;
            StopCommandPoll();
            Positions.Closed -= OnPositionClosed;
            Print($"[Gotobi] Stopped on {SymbolName}.");
            _httpClient?.Dispose();
        }
        #endregion

        #region Calendar
        /// <summary>A gotobi day: the 5th/10th/15th/20th/25th or the month's last day, a weekend one moved to the
        /// Friday before (research/lab/strategies/literature.gotobi_days). Japanese holidays: see SkipDates.</summary>
        public static bool IsGotobi(DateTime date)
        {
            var d = date.Date;
            if (d.DayOfWeek == DayOfWeek.Saturday || d.DayOfWeek == DayOfWeek.Sunday) return false;
            int last = DateTime.DaysInMonth(d.Year, d.Month);
            foreach (int day in new[] { 5, 10, 15, 20, 25, last })
            {
                var moved = new DateTime(d.Year, d.Month, day);
                while (moved.DayOfWeek == DayOfWeek.Saturday || moved.DayOfWeek == DayOfWeek.Sunday)
                    moved = moved.AddDays(-1);
                if (moved == d) return true;
            }
            return false;
        }

        private bool IsTradingDay(DateTime date) => IsGotobi(date) && !_skipDates.Contains(date.Date);

        /// <summary>The 09:55 Tokyo fixing of gotobi day `day`, in UTC.</summary>
        private DateTime FixTime(DateTime day) => day.Date.AddHours(FixHourUtc).AddMinutes(FixMinuteUtc);

        private DateTime ShortExitTime(DateTime day) => day.Date.AddHours(ShortExitHourUtc).AddMinutes(ShortExitMinuteUtc);

        private DateTime LongEntryTime(DateTime day) => day.Date.AddDays(-1).AddHours(LongEntryHourUtc).AddMinutes(LongEntryMinuteUtc);

        private DateTime LongEntryLatest(DateTime day) => day.Date.AddDays(-1).AddHours(LongEntryLatestHourUtc).AddMinutes(LongEntryLatestMinuteUtc);

        /// <summary>A leg's identity, "GOTOBI-L 2026-10-05": one attempt per tag.</summary>
        private static string LegTag(Leg leg, DateTime day) => $"{(leg == Leg.Long ? LongTag : ShortTag)} {day:yyyy-MM-dd}";

        /// <summary>What the bot knows of an own position: its leg and gotobi day, its virtual stop (null = the broker's
        /// stop is the stop) and whether it is a decoy.</summary>
        private class LegInfo
        {
            public Leg Leg;
            public DateTime Day;
            public string Tag;
            public double? StopPips;     // virtual stop distance; null = the broker's stop is the stop
            public bool Decoy;
        }

        /// <summary>Bid and ask when an order was sent, and how long the broker took to fill it.</summary>
        private class SentQuote
        {
            public double Bid;
            public double Ask;
            public long SentAt;          // Stopwatch timestamp
            public double LatencyMs;
        }

        // Orders carry no label or comment, and the position's entry time comes from the fill, so the windows below
        // allow a few minutes past the latest time an order can be sent.
        private const int EntrySlackMinutes = 5;

        /// <summary>The leg a buy or sell entered at `entry` was opened as. A buy entered in a long window (the earliest
        /// jittered entry to the latest one, the evening before) is the long of the next day; a sell entered at a fix,
        /// within the grace minutes, the short of that day. The bot trades a day that is not a trading day only as a
        /// decoy. Null outside both windows: then only Max hold and the broker's stop apply.</summary>
        private LegInfo InferLeg(TradeType side, DateTime entry)
        {
            var leg = side == TradeType.Buy ? Leg.Long : Leg.Short;
            var day = side == TradeType.Buy ? entry.Date.AddDays(1) : entry.Date;
            bool inWindow = leg == Leg.Long
                ? entry >= LongEntryTime(day).AddMinutes(-LongEntryJitterMinutes) && entry <= LongEntryLatest(day).AddMinutes(EntrySlackMinutes)
                : entry >= FixTime(day) && entry <= FixTime(day).AddMinutes(ShortEntryGraceMinutes + EntrySlackMinutes);
            if (!inWindow) return null;
            return new LegInfo { Leg = leg, Day = day, Tag = LegTag(leg, day), Decoy = !IsTradingDay(day) };
        }

        /// <summary>An own position's leg: the one TryOpenLeg recorded, or after a restart InferLeg plus, with
        /// camouflage, the virtual stop rebuilt from the H1 ATR at the entry the way TryOpenLeg set it.</summary>
        private LegInfo LegOf(Position pos)
        {
            if (_legs.TryGetValue(pos.Id, out var known)) return known;
            var info = InferLeg(pos.TradeType, pos.EntryTime);
            if (info != null && Camouflaged)
            {
                double? atr = EntryAtr(pos.EntryTime);
                if (!atr.HasValue) return info;   // no H1 history yet: the broker's stop stands in until the next call
                info.StopPips = (info.Decoy ? DecoyStopAtrMultiplier : StopAtrMultiplier) * atr.Value / Symbol.PipSize;
            }
            _legs[pos.Id] = info;
            return info;
        }

        /// <summary>The ATR TryOpenLeg sized a position entered at `entry` on (_atr.Result.Last(1) then: the H1 bar
        /// before the one the entry fell in), or null without that history.</summary>
        private double? EntryAtr(DateTime entry)
        {
            int i = _h1.OpenTimes.GetIndexByTime(entry);
            if (i < 1) return null;
            double atr = _atr.Result[i - 1];
            return double.IsNaN(atr) || atr <= 0 ? (double?)null : atr;
        }
        #endregion

        #region Strategy
        private void Evaluate()
        {
            if (_isStopped) return;
            try
            {
                var now = Server.Time;
                if (!HasFreshQuote(now)) return;   // no quote yet this week, or the broker is closed

                // Short leg at today's fix, only within the grace minutes after it. Its order is sent before the long
                // is closed and does not wait for its fill, so both reach the broker together: a short sent after the
                // close filled ~0.5-1.2 pip worse than the backtest, which does both on one tick
                // (research/results/portfolio/gotobi_live_fills_2026-10-06.md).
                var today = now.Date;
                if (TradeShort && PlanLeg(Leg.Short, today, out bool shortDecoy) && now >= FixTime(today)
                    && now <= FixTime(today).AddMinutes(ShortEntryGraceMinutes) && now < ShortExitTime(today))
                    TryOpenLeg(Leg.Short, today, shortDecoy);

                CloseDueLegs(now);

                // Long leg for tomorrow's gotobi day: from 18:00 UTC today (03:00 Tokyo tomorrow) to the latest entry.
                var tomorrow = now.Date.AddDays(1);
                if (TradeLong && PlanLeg(Leg.Long, tomorrow, out bool longDecoy) && now >= JitteredLongEntry(tomorrow)
                    && now <= LongEntryLatest(tomorrow) && now < FixTime(tomorrow))
                    TryOpenLeg(Leg.Long, tomorrow, longDecoy);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[Gotobi Evaluate Error] {ex.Message}");
            }
        }

        /// <summary>True when a tick arrived at most MaxQuoteAgeSeconds ago, so Symbol.Bid/Ask are the market's
        /// current prices and not the last quote before a weekend or a holiday. A leg that is due waits for it.</summary>
        private bool HasFreshQuote(DateTime now) => (now - _lastTickAt).TotalSeconds <= MaxQuoteAgeSeconds;

        /// <summary>Closes every own position whose leg has reached its planned exit (the fix for a long, 11:55
        /// Tokyo for a short), and anything older than MaxHoldHours.</summary>
        private void CloseDueLegs(DateTime now)
        {
            foreach (var pos in GetBotPositions())
            {
                TrackOpenedUnits(pos);
                string reason = DueExitReason(pos, now);
                if (reason == null) continue;

                var result = CloseWithReason(pos, reason);
                if (result == null || !result.IsSuccessful)
                    Print($"[Gotobi] Could not close #{pos.Id} ({reason}): {(result != null ? result.Error.ToString() : "no result")}");
            }
        }

        /// <summary>Why `pos` must close now: its leg's planned exit, Max hold or its virtual stop. Null while it may
        /// stay open.</summary>
        private string DueExitReason(Position pos, DateTime now)
        {
            string reason = null;
            var info = LegOf(pos);
            if (info != null)
            {
                if (info.Leg == Leg.Long && now >= FixTime(info.Day)) reason = "Fix exit (09:55 Tokyo)";
                else if (info.Leg == Leg.Short && now >= ShortExitTime(info.Day)) reason = "Session exit (11:55 Tokyo)";
            }
            if (reason == null && now - pos.EntryTime >= TimeSpan.FromHours(MaxHoldHours))
                reason = $"Max hold ({MaxHoldHours} h)";
            if (reason == null && VirtualStopHit(pos, info))
                reason = info.Decoy ? $"StopLoss (virtual, {DecoyStopAtrMultiplier} x ATR{AtrPeriod} H1)"
                                    : $"StopLoss (virtual, {StopAtrMultiplier} x ATR{AtrPeriod} H1)";
            if (reason != null && info != null && info.Decoy) reason = "Decoy: " + reason;
            return reason;
        }

        /// <summary>One attempt per leg and gotobi day, including after a stop-out; retried every OrderRetrySeconds
        /// while the spread is too wide or the order fails, until the leg's window closes.</summary>
        private void TryOpenLeg(Leg leg, DateTime day, bool decoy)
        {
            string tag = LegTag(leg, day);
            if (_legsDone.Contains(tag)) return;
            if (_pendingOrderTag != null)
            {
                if ((Server.Time - _pendingOrderSince).TotalSeconds < PendingOrderTimeoutSeconds) return;
                Print($"[Gotobi] {_pendingOrderTag}: no order result after {PendingOrderTimeoutSeconds:F0} s; checking positions and history");
                _pendingOrderTag = null;
            }
            // One leg at a time. A position whose exit is due does not count: Evaluate() closes it right after, so at
            // the fix the short's order goes out while the long closes.
            if (GetBotPositions().Any(p => DueExitReason(p, Server.Time) == null)) return;
            // A Monday gotobi day's long window opens on Sunday 18:00 UTC, before the FX week does; wait for the
            // first quote after the open (as the research did) instead of filling on Friday's stale price. The
            // schedule alone is not enough: a backtest's can say "open" an hour before the first tick, so Evaluate()
            // also waits for a fresh quote (HasFreshQuote).
            if (!Symbol.MarketHours.IsOpened()) return;

            if (_lastAttemptAt.TryGetValue(tag, out var last) && (Server.Time - last).TotalSeconds < RetryDelaySeconds(tag)) return;
            _lastAttemptAt[tag] = Server.Time;

            if (LegAlreadyTraded(tag))
            {
                _legsDone.Add(tag);
                return;
            }

            double spreadPips = (Symbol.Ask - Symbol.Bid) / Symbol.PipSize;
            if (spreadPips > MaxSpreadPips)
            {
                if ((Server.Time - _lastSpreadLogAt).TotalSeconds >= 60)
                {
                    _lastSpreadLogAt = Server.Time;
                    Print($"[Gotobi] {tag}: spread {spreadPips:F1} pips > {MaxSpreadPips:F1}; waiting");
                }
                return;
            }

            double atr = _atr.Result.Last(1);
            if (double.IsNaN(atr) || atr <= 0)
            {
                Print($"[Gotobi] {tag}: no ATR yet; skipped");
                return;
            }
            double stopPips = StopAtrMultiplier * atr / Symbol.PipSize;
            double volume = VolumeForRisk(stopPips);            // a decoy trades the lot of a real leg ...
            if (decoy && Draw(tag, "size") < DecoySmallShare)   // ... or, for DecoySmallShare of them, a small lot
                volume = Math.Max(Symbol.VolumeInUnitsMin,
                                  Symbol.NormalizeVolumeInUnits(DecoySmallLots * Symbol.LotSize, RoundingMode.Down));
            if (volume <= 0)
            {
                Print($"[Gotobi] {tag}: the minimum lot would risk more than {MaxMinLotRiskMultiple} x ${RiskPerTradeMoney:F2} at a {stopPips:F1}-pip stop; leg skipped");
                _legsDone.Add(tag);
                return;
            }

            var tradeType = leg == Leg.Long ? TradeType.Buy : TradeType.Sell;
            if (DashboardPauseBlocks($"{tag} entry")) return;
            // With camouflage the broker gets a random fraction of the real stop (never wider); the real one, or a
            // decoy's tighter one, is a virtual stop the bot closes. The order carries no label and no comment, as one
            // placed by hand: the bot reads its legs back off the positions (LegOf).
            double orderStopPips = stopPips;
            double? virtualPips = null;
            if (Camouflaged)
            {
                virtualPips = decoy ? DecoyStopAtrMultiplier * atr / Symbol.PipSize : stopPips;
                orderStopPips = stopPips * (EmergencyStopMin + _random.NextDouble() * Math.Max(0, EmergencyStopMax - EmergencyStopMin));
            }
            var quote = new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask, SentAt = System.Diagnostics.Stopwatch.GetTimestamp() };
            _pendingOrderTag = tag;
            _pendingOrderSince = Server.Time;
            ExecuteMarketOrderAsync(tradeType, SymbolName, volume, null, orderStopPips, null, null, result =>
            {
                if (_pendingOrderTag == tag) _pendingOrderTag = null;
                quote.LatencyMs = ElapsedMs(quote.SentAt);
                if (result != null && result.IsSuccessful && result.Position != null)
                {
                    _legsDone.Add(tag);
                    _legs[result.Position.Id] = new LegInfo { Leg = leg, Day = day, Tag = tag, StopPips = virtualPips, Decoy = decoy };
                    double reportedStop = virtualPips ?? stopPips;
                    _initialSlPips[result.Position.Id] = reportedStop;
                    string reason = leg == Leg.Long ? "Gotobi long into the 09:55 Tokyo fix" : "Gotobi short after the 09:55 Tokyo fix";
                    if (decoy) reason = leg == Leg.Long ? "Decoy long (plain weekday)" : "Decoy short (plain weekday)";
                    Print($"[Gotobi] Opened #{result.Position.Id} {tradeType} {volume / Symbol.LotSize:F2} lots {SymbolName} @ {result.Position.EntryPrice}, " +
                          $"stop {reportedStop:F1} pips{(virtualPips.HasValue ? $" (virtual, broker {orderStopPips:F1})" : "")} ({tag}{(decoy ? ", decoy" : "")}); " +
                          FillNote(tradeType, result.Position.EntryPrice, quote));
                    ReportPositionOpen(result.Position, reportedStop, reason);
                }
                else
                {
                    _orderFailures[tag] = (_orderFailures.TryGetValue(tag, out var fails) ? fails : 0) + 1;
                    Print($"[Gotobi] {tag}: order failed ({(result != null ? result.Error.ToString() : "no result")}) after {quote.LatencyMs:F0} ms; retrying in {RetryDelaySeconds(tag):F0} s");
                }
            });
        }

        /// <summary>Seconds between two attempts at `tag`: OrderRetrySeconds, doubled after each failed order from the
        /// second on and capped at 60 s, so an order the broker keeps refusing (a long's window lasts 5 h) is not
        /// resent every few seconds. A spread too wide is no failure: it sends nothing.</summary>
        private double RetryDelaySeconds(string tag)
        {
            int fails = _orderFailures.TryGetValue(tag, out var n) ? n : 0;
            return Math.Min(60.0, OrderRetrySeconds * Math.Pow(2, Math.Max(0, fails - 1)));
        }

        /// <summary>How a fill compares with the quote when its order was sent: "quote 157.300/157.302, slippage
        /// +0.3 pips, 212 ms". Slippage is in pips against the trader (a buy above the ask, a sell below the bid).</summary>
        private string FillNote(TradeType side, double fill, SentQuote quote)
        {
            double slippage = (side == TradeType.Buy ? fill - quote.Ask : quote.Bid - fill) / Symbol.PipSize;
            return $"quote {quote.Bid}/{quote.Ask}, slippage {slippage:+0.0;-0.0;0.0} pips, {quote.LatencyMs:F0} ms";
        }

        private static double ElapsedMs(long since) =>
            (System.Diagnostics.Stopwatch.GetTimestamp() - since) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;

        /// <summary>True when this bot already opened `tag` on this symbol: still open, or closed (History, read off
        /// each trade's side and entry time like an open position).</summary>
        private bool LegAlreadyTraded(string tag)
        {
            if (GetBotPositions().Any(p => LegOf(p)?.Tag == tag)) return true;
            return History.Any(h => h.SymbolName == SymbolName && InferLeg(h.TradeType, h.EntryTime)?.Tag == tag);
        }

        /// <summary>Units risking RiskPerTradeMoney at `stopPips`, rounded down to the volume step and capped at
        /// MaxLotsPerTrade. 0 when even the minimum lot would risk more than MaxMinLotRiskMultiple x the default.</summary>
        private double VolumeForRisk(double stopPips)
        {
            double riskPerUnit = stopPips * Symbol.PipValue;
            if (riskPerUnit <= 0) return 0;
            double units = Symbol.NormalizeVolumeInUnits(RiskPerTradeMoney / riskPerUnit, RoundingMode.Down);
            units = Math.Min(units, Symbol.NormalizeVolumeInUnits(MaxLotsPerTrade * Symbol.LotSize, RoundingMode.Down));
            if (units < Symbol.VolumeInUnitsMin)
            {
                double minRisk = Symbol.VolumeInUnitsMin * riskPerUnit;
                return minRisk <= RiskPerTradeMoney * MaxMinLotRiskMultiple ? Symbol.VolumeInUnitsMin : 0;
            }
            return units;
        }

        /// <summary>This bot's positions: every position on its symbol. One bot trades each symbol of an account and
        /// nothing is traded there by hand, so the orders need no label to tell them apart.</summary>
        private List<Position> GetBotPositions() => Positions.Where(p => p.SymbolName == SymbolName).ToList();

        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            var quote = new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask, SentAt = System.Diagnostics.Stopwatch.GetTimestamp() };
            var result = ClosePosition(pos);
            quote.LatencyMs = ElapsedMs(quote.SentAt);
            if (result != null && result.IsSuccessful) _closeQuotes[pos.Id] = quote;   // read by OnPositionClosed
            return result;
        }
        #endregion

        #region Camouflage
        // The broker sees every order, so it could read the strategy off them: a stop of exactly 3 x ATR, entries on
        // gotobi days only, three pairs opening on the same second, a steady win rate. The bot therefore sends a
        // random 0.8-1 x fraction of the stop to the broker, opens each long at its own jittered time, and trades
        // ~2 decoy legs per real one on plain weekdays: same hours, a small lot (DecoySmallShare), broker stop drawn
        // the same way, but a tight virtual stop the bot closes, so most decoys lose a little. Nothing on the order
        // says which leg is a decoy or where its stop is: the bot works both out from the position (LegOf).
        private readonly Random _random = new Random();

        private bool Camouflaged => VirtualStop;

        /// <summary>Uniform [0, 1) drawn from the bot, symbol, leg and purpose, so a restart makes the same choice. The
        /// broker sees neither the BotId nor the code, so it cannot predict it.</summary>
        private double Draw(string tag, string purpose)
        {
            var hash = System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes($"{BotId}|{SymbolName}|{tag}|{purpose}"));
            return BitConverter.ToUInt32(hash, 0) / 4294967296.0;
        }

        /// <summary>True when `leg` of `day` is traded: a real leg on a gotobi day, or (camouflage on) a decoy on a
        /// plain weekday with probability DecoyLegProbability. No decoy on a skipped day or at Christmas / New Year,
        /// when the broker may be closed at the fix.</summary>
        private bool PlanLeg(Leg leg, DateTime day, out bool decoy)
        {
            decoy = false;
            if (IsTradingDay(day)) return true;
            if (!Camouflaged || DecoyLegProbability <= 0) return false;
            if (day.DayOfWeek == DayOfWeek.Saturday || day.DayOfWeek == DayOfWeek.Sunday) return false;
            if (IsGotobi(day) || _skipDates.Contains(day.Date)) return false;
            if ((day.Month == 12 && day.Day == 25) || (day.Month == 1 && day.Day == 1)) return false;
            decoy = Draw(LegTag(leg, day), "decoy") < DecoyLegProbability;
            return decoy;
        }

        /// <summary>This symbol's long entry for `day`: Long Entry +/- LongEntryJitterMinutes.</summary>
        private DateTime JitteredLongEntry(DateTime day)
        {
            double offset = (Draw(LegTag(Leg.Long, day), "entry") * 2 - 1) * LongEntryJitterMinutes;
            return LongEntryTime(day).AddMinutes(Math.Round(offset));
        }

        /// <summary>The virtual stop's price, or null when the position has none (its broker stop is the stop).</summary>
        private double? VirtualStopPrice(Position pos, LegInfo info)
        {
            if (info == null || !info.StopPips.HasValue) return null;
            double distance = info.StopPips.Value * Symbol.PipSize;
            return pos.TradeType == TradeType.Buy ? pos.EntryPrice - distance : pos.EntryPrice + distance;
        }

        private bool VirtualStopHit(Position pos, LegInfo info)
        {
            double? stop = VirtualStopPrice(pos, info);
            if (!stop.HasValue) return false;
            return pos.TradeType == TradeType.Buy ? Symbol.Bid <= stop.Value : Symbol.Ask >= stop.Value;
        }

        /// <summary>The stop the bot works to: the virtual one, else the broker's.</summary>
        private double? StopPriceOf(Position pos) => VirtualStopPrice(pos, LegOf(pos)) ?? pos.StopLoss;
        #endregion

        #region Dashboard commands
        private class DashboardCommand
        {
            public string id { get; set; }
            public string action { get; set; }
            public long? position_id { get; set; }
        }

        private class DashboardCommandPoll
        {
            public bool paused { get; set; }
            public List<DashboardCommand> commands { get; set; }
        }

        private CancellationTokenSource _commandPollCts;
        private HttpClient _commandHttp;
        private volatile bool _dashboardPaused;
        private readonly HashSet<string> _handledCommandIds = new HashSet<string>();
        private DateTime _lastCommandPollErrorAt = DateTime.MinValue;
        private DateTime _lastPauseLogAt = DateTime.MinValue;

        private void StartCommandPoll()
        {
            if (RunningMode != RunningMode.RealTime || CommandPollMs <= 0) return;
            var baseUrl = BuildCommandBaseUrl();
            if (baseUrl == null) return;

            _commandHttp = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            _commandPollCts = new CancellationTokenSource();
            var token = _commandPollCts.Token;
            var http = _commandHttp;
            var pollUrl = $"{baseUrl}/api/cbot/commands?bot_id={Uri.EscapeDataString(BotId)}";
            Task.Run(() => CommandPollLoopAsync(http, baseUrl, pollUrl, token), token);
            Print($"[Dashboard] Polling {pollUrl} every {CommandPollMs} ms");
        }

        private void StopCommandPoll()
        {
            try { _commandPollCts?.Cancel(); } catch { }
            _commandPollCts = null;
        }

        private string BuildCommandBaseUrl()
        {
            var baseUrl = ApiUrl;
            if (string.IsNullOrWhiteSpace(baseUrl)) return null;

            baseUrl = baseUrl.Trim().Trim('"', '\'', '“', '”', '‘', '’', '`');
            const string tradePath = "/trade";
            if (baseUrl.EndsWith(tradePath)) baseUrl = baseUrl.Substring(0, baseUrl.Length - tradePath.Length);
            baseUrl = baseUrl.TrimEnd('/');
            return baseUrl.StartsWith("http://") || baseUrl.StartsWith("https://") ? baseUrl : null;
        }

        private async Task CommandPollLoopAsync(HttpClient http, string baseUrl, string pollUrl, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var response = await http.GetAsync(pollUrl, token);
                    response.EnsureSuccessStatusCode();
                    var body = await response.Content.ReadAsStringAsync();
                    var poll = JsonSerializer.Deserialize<DashboardCommandPoll>(body);
                    if (poll != null)
                    {
                        _dashboardPaused = poll.paused;
                        foreach (var cmd in poll.commands ?? new List<DashboardCommand>())
                        {
                            if (cmd == null || string.IsNullOrEmpty(cmd.id)) continue;
                            bool isNew;
                            lock (_handledCommandIds) { isNew = _handledCommandIds.Add(cmd.id); }
                            if (!isNew) continue;
                            var command = cmd;
                            BeginInvokeOnMainThread(() => ExecuteDashboardCommand(baseUrl, command));
                        }
                    }
                }
                catch (OperationCanceledException) when (token.IsCancellationRequested) { break; }
                catch (Exception ex)
                {
                    if ((DateTime.UtcNow - _lastCommandPollErrorAt).TotalSeconds >= 60)
                    {
                        _lastCommandPollErrorAt = DateTime.UtcNow;
                        Print($"[Dashboard] Command poll failed: {ex.GetType().Name}: {ex.Message}");
                    }
                }

                try { await Task.Delay(CommandPollMs, token); } catch { break; }
            }
            try { http.Dispose(); } catch { }
        }

        /// <summary>Runs on the cBot thread. Closes only this bot's own positions.</summary>
        private void ExecuteDashboardCommand(string baseUrl, DashboardCommand cmd)
        {
            var own = GetBotPositions();
            List<Position> targets;
            if (cmd.action == "close_all")
                targets = own.ToList();
            else if (cmd.action == "close_position")
                targets = own.Where(p => p.Id == cmd.position_id).ToList();
            else
            {
                PostCommandResult(baseUrl, cmd.id, "failed", $"unknown action '{cmd.action}'", 0, 0);
                return;
            }

            if (cmd.action == "close_position" && targets.Count == 0)
            {
                Print($"[Dashboard] Close #{cmd.position_id}: not among this bot's open positions");
                PostCommandResult(baseUrl, cmd.id, "failed", $"position {cmd.position_id} not found among this bot's open positions", 0, 0);
                return;
            }

            int closed = 0;
            var errors = new List<string>();
            foreach (var pos in targets)
            {
                var result = CloseWithReason(pos, ManualCloseReason);
                if (result != null && result.IsSuccessful) closed++;
                else errors.Add($"#{pos.Id} {(result != null ? result.Error.ToString() : "no result")}");
            }

            string message = errors.Count == 0 ? $"closed {closed}" : $"closed {closed}, failed: {string.Join(", ", errors)}";
            Print($"[Dashboard] {cmd.action}: {message}");
            PostCommandResult(baseUrl, cmd.id, errors.Count == 0 ? "done" : "failed", message, closed, errors.Count);
        }

        private void PostCommandResult(string baseUrl, string commandId, string status, string message, int closed, int failed)
        {
            var http = _commandHttp;
            if (http == null) return;
            var json = JsonSerializer.Serialize(new { bot_id = BotId, status, message, closed, failed });
            var url = $"{baseUrl}/api/cbot/commands/{Uri.EscapeDataString(commandId)}/result";
            Task.Run(async () =>
            {
                try
                {
                    await http.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                }
                catch (Exception ex)
                {
                    Print($"[Dashboard] Could not report command {commandId}: {ex.Message}");
                }
            });
        }

        /// <summary>True while the dashboard has paused this bot's new entries (logged once a minute).</summary>
        private bool DashboardPauseBlocks(string what)
        {
            if (!_dashboardPaused) return false;
            if ((DateTime.UtcNow - _lastPauseLogAt).TotalSeconds >= 60)
            {
                _lastPauseLogAt = DateTime.UtcNow;
                Print($"[Dashboard] Paused from the dashboard: {what} skipped");
            }
            return true;
        }
        #endregion

        #region Server reporting
        private string ResolvedReportUrl() => !string.IsNullOrWhiteSpace(ReportUrl) ? ReportUrl.Trim() : ApiUrl.Replace("/trade", "/portfolio/report");

        private double EstimatedNetProfitAt(Position pos, double price)
        {
            double pipsDiff = pos.TradeType == TradeType.Buy
                ? (price - pos.EntryPrice) / Symbol.PipSize
                : (pos.EntryPrice - price) / Symbol.PipSize;
            double fees = Math.Abs(pos.Commissions) * 2.0 + (pos.Swap < 0 ? Math.Abs(pos.Swap) : 0.0);
            return pipsDiff * pos.VolumeInUnits * Symbol.PipValue - fees;
        }

        private void SendLiveTickTelemetry(bool force = false)
        {
            if (RunningMode != RunningMode.RealTime || _httpClient == null) return;
            if (!force && (DateTime.UtcNow - _lastTickTelemetryTime).TotalSeconds < 10.0) return;
            _lastTickTelemetryTime = DateTime.UtcNow;

            try
            {
                var posList = new List<object>();
                foreach (var p in GetBotPositions())
                {
                    posList.Add(new
                    {
                        id = p.Id,
                        symbol = p.SymbolName,
                        side = p.TradeType.ToString(),
                        volume = p.VolumeInUnits / Symbol.LotSize,
                        entry_price = p.EntryPrice,
                        current_price = p.TradeType == TradeType.Buy ? Symbol.Bid : Symbol.Ask,
                        net_profit = p.NetProfit,
                        pips = p.Pips,
                        sl_price = StopPriceOf(p),
                        tp_price = p.TakeProfit,
                        sl_pnl = StopPriceOf(p) is double stop ? (double?)Math.Round(EstimatedNetProfitAt(p, stop), 2) : null,
                        tp_pnl = (double?)null
                    });
                }

                var telemetry = new
                {
                    bot_id = BotId,
                    account_number = Account.Number.ToString(),
                    symbol = SymbolName,
                    bid = Symbol.Bid,
                    ask = Symbol.Ask,
                    equity = Account.Equity,
                    balance = Account.Balance,
                    positions = posList,
                    last_bar = _lastBarHandled == DateTime.MinValue ? null : _lastBarHandled.ToString("yyyy-MM-ddTHH:mm:ss")
                };

                string tickUrl = !string.IsNullOrWhiteSpace(TelemetryUrl) ? TelemetryUrl.Trim() : ApiUrl.Replace("/trade", "/api/tick");
                var content = new StringContent(JsonSerializer.Serialize(telemetry), Encoding.UTF8, "application/json");
                Task.Run(async () =>
                {
                    try { await _httpClient.PostAsync(tickUrl, content); }
                    catch { }
                });
            }
            catch
            {
                // background telemetry failures are not fatal
            }
        }

        /// <summary>The price the position's close traded at, or null when History has not booked the deal yet.</summary>
        private double? FinalClosingPrice(Position pos)
        {
            try
            {
                var cutoff = Server.Time.AddSeconds(-60);
                double tolerance = Symbol.VolumeInUnitsMin / 2.0;
                var deal = History
                    .Where(h => h.PositionId == pos.Id
                                && h.ClosingTime >= cutoff
                                && Math.Abs(h.VolumeInUnits - pos.VolumeInUnits) <= tolerance)
                    .OrderByDescending(h => h.ClosingTime)
                    .FirstOrDefault();
                if (deal != null && deal.ClosingPrice > 0)
                    return deal.ClosingPrice;
            }
            catch { }
            return null;
        }

        /// <summary>Records, once and while `pos` is open, the units it opened with: what it holds now plus what History
        /// has already closed of it.</summary>
        private void TrackOpenedUnits(Position pos)
        {
            if (_openedUnits.ContainsKey(pos.Id)) return;
            _openedUnits[pos.Id] = pos.VolumeInUnits + History.Where(h => h.PositionId == pos.Id).Sum(h => h.VolumeInUnits);
        }

        /// <summary>The net of the slices taken off `pos` before its final close: its earliest History deals, up to the
        /// units it lost while open. 0 when nothing was taken off, or when the bot never saw it open.</summary>
        private double PartialClosesNet(Position pos)
        {
            if (!_openedUnits.TryGetValue(pos.Id, out var opened)) return 0;
            _openedUnits.Remove(pos.Id);
            double taken = opened - pos.VolumeInUnits;
            double tolerance = Symbol.VolumeInUnitsMin / 2.0;
            double units = 0, net = 0;
            foreach (var h in History.Where(h => h.PositionId == pos.Id).OrderBy(h => h.ClosingTime))
            {
                if (units >= taken - tolerance) break;
                units += h.VolumeInUnits;
                net += h.NetProfit;
            }
            return net;
        }

        private void OnPositionClosed(PositionClosedEventArgs args)
        {
            BeginInvokeOnMainThread(() =>
            {
                try
                {
                    var pos = args.Position;
                    if (pos == null || pos.SymbolName != SymbolName) return;

                    double exitPrice = pos.TradeType == TradeType.Buy ? Symbol.Bid : Symbol.Ask;
                    if (args.Reason == PositionCloseReason.TakeProfit && pos.TakeProfit.HasValue)
                        exitPrice = pos.TakeProfit.Value;
                    else if (args.Reason == PositionCloseReason.StopLoss && pos.StopLoss.HasValue)
                        exitPrice = pos.StopLoss.Value;
                    double? bookedExit = FinalClosingPrice(pos);
                    if (bookedExit.HasValue)
                        exitPrice = bookedExit.Value;

                    bool hasBotReason = _closeReasons.TryGetValue(pos.Id, out var botReason);
                    _closeReasons.Remove(pos.Id);
                    var info = LegOf(pos);
                    string reason;
                    if (args.Reason == PositionCloseReason.StopLoss)
                        reason = info != null && info.StopPips.HasValue
                            ? $"{(info.Decoy ? "Decoy: " : "")}StopLoss (broker, {EmergencyStopMin}-{EmergencyStopMax} x the {StopAtrMultiplier} x ATR{AtrPeriod} H1 stop)"
                            : $"StopLoss ({StopAtrMultiplier} x ATR{AtrPeriod} H1)";
                    else if (args.Reason == PositionCloseReason.Closed)
                        reason = hasBotReason ? botReason : "Closed outside the bot (cTrader)";
                    else
                        reason = args.Reason.ToString();

                    _legs.Remove(pos.Id);
                    // A close the bot sent: the exit against the quote then (a long closes on the bid, a short on the ask).
                    string fillNote = _closeQuotes.TryGetValue(pos.Id, out var closeQuote)
                        ? $" @ {exitPrice}; {FillNote(pos.TradeType == TradeType.Buy ? TradeType.Sell : TradeType.Buy, exitPrice, closeQuote)}" : "";
                    _closeQuotes.Remove(pos.Id);
                    double slices = PartialClosesNet(pos);
                    double net = pos.NetProfit + slices;
                    string slicesNote = slices != 0 ? $" ({slices:F2} of it closed earlier in slices)" : "";
                    Print($"[Gotobi] Closed #{pos.Id} {pos.TradeType} {info?.Tag ?? "(no leg)"}{(info != null && info.Decoy ? " decoy" : "")}: {reason}, net {net:F2}{slicesNote}{fillNote}");
                    if (info != null && info.StopPips.HasValue && !_initialSlPips.ContainsKey(pos.Id))
                        _initialSlPips[pos.Id] = info.StopPips.Value;       // opened before a restart
                    ReportPositionClosed(pos, net, reason, exitPrice, pos.Pips);
                    SendLiveTickTelemetry(force: true);
                }
                catch (Exception ex)
                {
                    if (ShowLogs) Print($"[OnPositionClosed Error] {ex.Message}");
                }
            });
        }

        private void ReportPositionOpen(Position position, double slPips, string reason)
        {
            if (RunningMode != RunningMode.RealTime || _httpClient == null || position == null) return;
            try
            {
                int posId = position.Id;
                string posSide = position.TradeType.ToString();
                string posSymbol = position.SymbolName;
                var report = new
                {
                    ctrader_id = posId,
                    bot_id = BotId,
                    action = "open",
                    symbol = posSymbol,
                    side = posSide,
                    volume = position.VolumeInUnits / Symbol.LotSize,
                    entry_price = position.EntryPrice,
                    sl_price = StopPriceOf(position),
                    tp_price = position.TakeProfit,
                    sl_pips = Math.Round(slPips, 1),
                    tp_pips = 0.0,
                    reason,
                    entry_indicators = JsonSerializer.Serialize(new
                    {
                        leg = LegOf(position)?.Tag,
                        decoy = LegOf(position)?.Decoy ?? false,
                        atr_h1 = Math.Round(_atr.Result.Last(1), 5),
                        spread = Math.Round((Symbol.Ask - Symbol.Bid) / Symbol.PipSize, 1)
                    }),
                    entry_time = position.EntryTime.ToUniversalTime().ToString("o"),
                    account_number = Account.Number.ToString(),
                    account_type = Account.IsLive ? "live" : "demo",
                    account_label = Account.BrokerName,
                    account_balance = Account.Balance,
                    account_equity = Account.Equity
                };

                var json = JsonSerializer.Serialize(report);
                var url = ResolvedReportUrl();
                Task.Run(async () =>
                {
                    string error = await PostReportAsync(url, json);
                    if (error == null && !ShowLogs) return;
                    BeginInvokeOnMainThread(() =>
                    {
                        if (error == null)
                            Print($"[Portfolio Hub] Reported position open: #{posId} {posSide} {posSymbol}");
                        else
                            Print($"[Portfolio Hub] Failed to report position open: #{posId} {posSide} {posSymbol}: {error}");
                    });
                });
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[ReportPositionOpen Error] {ex.Message}");
            }
        }

        private void ReportPositionClosed(Position position, double pnl, string reason, double exitPrice, double pips)
        {
            if (RunningMode != RunningMode.RealTime || _httpClient == null || position == null) return;
            try
            {
                int posId = position.Id;
                string posSide = position.TradeType.ToString();
                double initialSlPips = _initialSlPips.TryGetValue(posId, out var sl) ? Math.Round(sl, 1) : 0.0;
                _initialSlPips.Remove(posId);
                var report = new
                {
                    ctrader_id = posId,
                    bot_id = BotId,
                    action = "close",
                    symbol = position.SymbolName,
                    side = posSide,
                    volume = position.VolumeInUnits / Symbol.LotSize,
                    entry_price = position.EntryPrice,
                    exit_price = exitPrice,
                    sl_price = StopPriceOf(position),
                    tp_price = position.TakeProfit,
                    sl_pips = initialSlPips,
                    pnl,
                    pips = Math.Round(pips, 1),
                    reason = string.IsNullOrWhiteSpace(reason) ? "Closed" : reason,
                    entry_time = position.EntryTime.ToUniversalTime().ToString("o"),
                    exit_time = DateTime.UtcNow.ToString("o"),
                    account_number = Account.Number.ToString(),
                    account_type = Account.IsLive ? "live" : "demo",
                    account_label = Account.BrokerName,
                    account_balance = Account.Balance,
                    account_equity = Account.Equity
                };

                var json = JsonSerializer.Serialize(report);
                var url = ResolvedReportUrl();
                Task.Run(async () =>
                {
                    string error = await PostReportAsync(url, json);
                    if (error == null && !ShowLogs) return;
                    BeginInvokeOnMainThread(() =>
                    {
                        if (error == null)
                            Print($"[Portfolio Hub] Reported position closed: #{posId} {posSide} PnL: {pnl:F2}");
                        else
                            Print($"[Portfolio Hub] Failed to report position closed: #{posId} {posSide} PnL: {pnl:F2}: {error}");
                    });
                });
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[ReportPositionClosed Error] {ex.Message}");
            }
        }

        // The server ignores a replayed open/close (matched on ctrader_id), so retrying cannot book a trade twice.
        private static readonly int[] ReportRetryDelaysSeconds = { 2, 4, 8, 16 };

        /// <summary>Posts a report, retrying on failure. Returns null once delivered, else the last error.</summary>
        private async Task<string> PostReportAsync(string url, string json)
        {
            string lastError = null;
            for (int attempt = 0; attempt <= ReportRetryDelaysSeconds.Length; attempt++)
            {
                if (attempt > 0)
                    await Task.Delay(TimeSpan.FromSeconds(ReportRetryDelaysSeconds[attempt - 1]));
                try
                {
                    using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
                    using (var response = await _httpClient.PostAsync(url, content))
                    {
                        if (response.IsSuccessStatusCode) return null;
                        lastError = $"HTTP {(int)response.StatusCode}";
                    }
                }
                catch (Exception ex)
                {
                    lastError = ex.InnerException != null ? $"{ex.Message} ({ex.InnerException.Message})" : ex.Message;
                }
            }
            return $"{lastError} (after {ReportRetryDelaysSeconds.Length + 1} attempts)";
        }
        #endregion
    }
}
