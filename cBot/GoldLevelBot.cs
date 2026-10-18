using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    /// <summary>
    /// Gold round-level bot (research G1-XAU50: research/results/portfolio/round27_levels_opens/PREREG_G_gold_round50_cascade.md;
    /// the tested engine is prereg_code/engine.py.txt and fills.py.txt next to it).
    ///
    /// Stop orders cluster just beyond round numbers (Osler 2003, 2005), so when gold breaks a $50 level it has not traded
    /// beyond for a day, the stops it sets off carry it further for a while. The bot rests a stop order just past such a
    /// level and closes at market 30 minutes after it triggers. The rule passed its 2025-26 holdout at the DEMO tier only.
    ///
    /// The rule (every number is a parameter whose default is the registered value):
    /// - It runs on every $10 level and trades only the multiples of $50. The other levels are armed and triggered from
    ///   the ticks without an order, because their triggers count for the busy window and the level memory.
    /// - Arming happens only while not busy (60 minutes after the last trigger), from 18:10 New York of the previous day
    ///   to 15:54 New York, not within 15 minutes of a High-impact USD release (CalendarFile), and not within 15 minutes
    ///   after the session's first tick or a tick gap of more than 60 minutes. It takes the nearest level within $2 of
    ///   the mid: an upper one above the highest tick mid of the previous 1,440 clock minutes, or a lower one below the
    ///   lowest. A level that triggered in the previous 1,440 minutes is skipped, and nothing arms until the mid leaves
    ///   its band. Nor does a level arm when its order would be marketable.
    /// - Order: buy stop at L + 0.5 x s60 above, sell stop at L - 0.5 x s60 below. s60 is the median last-tick spread of
    ///   the 60 clock minutes before the arming minute, fixed at arming. The order is cancelled when the mid leaves the $2
    ///   band or an exclusion starts (the real order CancelLeadSeconds before it).
    /// - A trigger (ask >= stop for a buy, bid <= stop for a sell) makes the bot busy for 60 minutes. A traded level's
    ///   position is closed at market 30 minutes after the trigger. The rule has no protective stop.
    ///
    /// At start the bot loads about two days of tick history and runs the rule over it without trading. A restart thus
    /// resumes with the rule's own state: the 24-hour envelope, the busy window, the levels that triggered and an armed
    /// level. Lots are fixed (Lots), never read off the account. The broker stop (EmergencyStopUsd) is not part of the
    /// rule: it is a far guard for a bot or VPS that dies with a position open. Every traded trigger goes to TradeLogFile
    /// next to the research fill model's prices (the first tick ModelLatencyMs after the trigger and after the exit time),
    /// which is what the registered demo stop rule reads.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class GoldLevelBot : Robot
    {
        #region Parameters
        [Parameter("Bot ID", Group = "General", DefaultValue = "GoldLevel")]
        public string BotId { get; set; }

        [Parameter("Account Identifier", Group = "General", DefaultValue = "demo")]
        public string AccountLabel { get; set; }

        [Parameter("Show Detailed Logs", Group = "General", DefaultValue = true)]
        public bool ShowLogs { get; set; }

        [Parameter("Level Grid ($)", Group = "Rule", DefaultValue = 10.0, MinValue = 0.01)]
        public double LevelStep { get; set; }

        // Only these levels get an order; the rest of the grid is armed and triggered virtually.
        [Parameter("Traded Levels (multiples of $)", Group = "Rule", DefaultValue = 50.0, MinValue = 0.01)]
        public double TradedMultiple { get; set; }

        [Parameter("Arm Band ($ from the level)", Group = "Rule", DefaultValue = 2.0, MinValue = 0.01)]
        public double ArmBand { get; set; }

        [Parameter("Stop Offset (x s60)", Group = "Rule", DefaultValue = 0.5, MinValue = 0.0, MaxValue = 10.0)]
        public double StopOffsetSpreads { get; set; }

        [Parameter("Hold (minutes after the trigger)", Group = "Rule", DefaultValue = 30, MinValue = 1, MaxValue = 240)]
        public int HoldMinutes { get; set; }

        [Parameter("Busy After a Trigger (minutes)", Group = "Rule", DefaultValue = 60, MinValue = 1, MaxValue = 1440)]
        public int BusyMinutes { get; set; }

        [Parameter("Fresh Window (minutes)", Group = "Rule", DefaultValue = 1440, MinValue = 60, MaxValue = 10080)]
        public int FreshWindowMinutes { get; set; }

        [Parameter("Level Memory (minutes)", Group = "Rule", DefaultValue = 1440, MinValue = 0, MaxValue = 10080)]
        public int LevelMemoryMinutes { get; set; }

        [Parameter("Spread Window (minutes)", Group = "Rule", DefaultValue = 60, MinValue = 1, MaxValue = 1440)]
        public int SpreadWindowMinutes { get; set; }

        [Parameter("Arming From Hour (New York, previous day)", Group = "Rule", DefaultValue = 18, MinValue = 0, MaxValue = 23)]
        public int ArmFromHourNewYork { get; set; }

        [Parameter("Arming From Minute (New York)", Group = "Rule", DefaultValue = 10, MinValue = 0, MaxValue = 59)]
        public int ArmFromMinuteNewYork { get; set; }

        [Parameter("Arming To Hour (New York)", Group = "Rule", DefaultValue = 15, MinValue = 0, MaxValue = 23)]
        public int ArmToHourNewYork { get; set; }

        [Parameter("Arming To Minute (New York)", Group = "Rule", DefaultValue = 54, MinValue = 0, MaxValue = 59)]
        public int ArmToMinuteNewYork { get; set; }

        [Parameter("Release Exclusion (+/- minutes)", Group = "Rule", DefaultValue = 15, MinValue = 0, MaxValue = 120)]
        public int NewsExclusionMinutes { get; set; }

        [Parameter("Tick Gap (minutes)", Group = "Rule", DefaultValue = 60, MinValue = 1, MaxValue = 1440)]
        public int GapMinutes { get; set; }

        [Parameter("No Arming After a Gap (minutes)", Group = "Rule", DefaultValue = 15, MinValue = 0, MaxValue = 240)]
        public int GapCooldownMinutes { get; set; }

        // "utc_minute,event" rows plus "# valid_through=yyyy-MM-dd" (research/tools/usd_high_calendar_seed.py).
        [Parameter("Release Calendar File", Group = "Rule", DefaultValue = "/workspace/cBot/seeds/usd_high_calendar.csv")]
        public string CalendarFile { get; set; }

        [Parameter("Cancel Lead (seconds before an exclusion)", Group = "Execution", DefaultValue = 2, MinValue = 0, MaxValue = 60)]
        public int CancelLeadSeconds { get; set; }

        [Parameter("Fill Wait (seconds after the trigger)", Group = "Execution", DefaultValue = 5, MinValue = 1, MaxValue = 60)]
        public int FillWaitSeconds { get; set; }

        // The research's fill model: the first tick at or after the trigger (and the exit time) + this latency.
        [Parameter("Model Latency (ms)", Group = "Execution", DefaultValue = 250, MinValue = 0, MaxValue = 5000)]
        public int ModelLatencyMs { get; set; }

        [Parameter("Order Retry (seconds)", Group = "Execution", DefaultValue = 2, MinValue = 1, MaxValue = 60)]
        public int OrderRetrySeconds { get; set; }

        [Parameter("Lots", Group = "Risk", DefaultValue = 0.01, MinValue = 0.01, MaxValue = 10.0)]
        public double Lots { get; set; }

        // Not part of the rule (it has none): a far broker stop for a dead bot. 0 = none.
        [Parameter("Broker Stop ($ from entry, 0 = none)", Group = "Risk", DefaultValue = 100.0, MinValue = 0.0, MaxValue = 1000.0)]
        public double EmergencyStopUsd { get; set; }

        // Last line of defence after a restart or a missed exit; the rule itself holds 30 minutes.
        [Parameter("Max Hold (minutes)", Group = "Risk", DefaultValue = 90, MinValue = 10, MaxValue = 7200)]
        public int MaxHoldMinutes { get; set; }

        [Parameter("Replay Tick History at Start", Group = "Data", DefaultValue = true)]
        public bool ReplayHistory { get; set; }

        // Empty = /root/ctrader_data/<BotId>_trades.csv (the cTrader home volume, kept across restarts).
        [Parameter("Trade Log File (empty = per bot)", Group = "Data", DefaultValue = "")]
        public string TradeLogFile { get; set; }

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
        private const string ManualCloseReason = "Manual close (dashboard)";
        private const double MaxQuoteAgeSeconds = 60;
        // engine.SessionFeed: the session of New York day d runs from the arming start of d-1 to 17:00 New York of d.
        private static readonly TimeSpan SessionEndNewYork = new TimeSpan(17, 0, 0);
        // fills.COMM: the research's round-trip commission, used for the model's net in the trade log.
        private const double ModelCommissionBp = 0.6;
        private const int TradeLogFlushMinutes = 10;
        private const int MaxRejections = 3;            // refused orders per arm before the bot stops asking

        private TimeZoneInfo _newYork;
        private bool _live;                      // false while the start-up replay runs: the rule acts, nothing trades
        private string _tradeLogPath;

        // High-impact USD release minutes (UTC), sorted, and the last New York day they are known for
        private List<DateTime> _releases = new List<DateTime>();
        private DateTime? _calendarValidThrough;
        private DateTime _calendarLoadedAt = DateTime.MinValue;
        private DateTime _lastCalendarWarnAt = DateTime.MinValue;

        // The minute envelope (engine.Minutes): per UTC minute the max / min tick mid and the last tick's spread.
        private MinuteRec[] _ring;
        private readonly List<double> _spreadBuf = new List<double>();
        private long _curMinute = long.MinValue;
        private double _curMax = double.NegativeInfinity;
        private double _curMin = double.PositiveInfinity;
        private double _curLastSpread;
        private int _curCount;
        private double _wUp = double.NegativeInfinity;   // highest mid of the FreshWindowMinutes before this minute
        private double _wDn = double.PositiveInfinity;   // lowest
        private double _s60 = double.NaN;                // median last-tick spread of the SpreadWindowMinutes before it
        private long _coverageFromMinute = long.MaxValue;   // the first minute the bot has every tick of

        // The tick clock: sessions and gaps (engine.session_arrays).
        private DateTime _lastTickAt = DateTime.MinValue;
        private DateTime? _lastSession;
        private DateTime _gapAt = DateTime.MinValue;

        // The rule's state (engine.gen_events): the busy window and level memory persist, the arm lives in one session.
        private ArmMode _mode = ArmMode.Idle;
        private Arm _arm;
        private DateTime _busyUntil = DateTime.MinValue;
        private readonly Dictionary<long, DateTime> _triggered = new Dictionary<long, DateTime>();
        private TradeRec _lastRuleTrade;         // the last traded-level trigger, live or replayed

        // Orders and positions.
        private Working _working;                // the armed traded level's stop order
        private DateTime _nextPlaceAt = DateTime.MinValue;
        private readonly Dictionary<int, Working> _cancelling = new Dictionary<int, Working>();
        private readonly Dictionary<int, TradeRec> _openTrades = new Dictionary<int, TradeRec>();
        private readonly List<TradeRec> _pendingLog = new List<TradeRec>();     // trades to write once finished
        private readonly List<TradeRec> _modelWatch = new List<TradeRec>();     // trades still waiting for a model price
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();
        private readonly Dictionary<int, DateTime> _nextCloseAt = new Dictionary<int, DateTime>();
        private readonly Dictionary<int, SentQuote> _closeQuotes = new Dictionary<int, SentQuote>();
        private DateTime _lastBarHandled = DateTime.MinValue;
        private DateTime _lastTickTelemetryTime = DateTime.MinValue;
        private volatile bool _isStopped;

        private readonly HttpClient _httpClient = new HttpClient(new SocketsHttpHandler { PooledConnectionIdleTimeout = TimeSpan.FromSeconds(4) })
        {
            Timeout = TimeSpan.FromSeconds(60)
        };

        private enum ArmMode
        {
            Idle,
            Armed,      // the order (real for a traded level, virtual otherwise) rests at Arm.Stop
            Blocked     // the level triggered in the last LevelMemoryMinutes: nothing arms until the mid leaves its band
        }

        private class MinuteRec
        {
            public long Minute = long.MinValue;
            public double Max;
            public double Min;
            public double LastSpread;
        }

        private class Arm
        {
            public double Level;
            public int Side;              // +1: an upper level, buy stop; -1: a lower level, sell stop
            public double Stop;           // the rule's stop, L +/- StopOffsetSpreads x s60
            public double OrderPrice;     // the stop rounded outward to the tick, so the broker triggers on the same ticks
            public double S60;
            public DateTime At;
            public long Key;              // the level in cents
            public bool Traded;           // a multiple of TradedMultiple
            public string NoOrderReason;  // why a traded level has no order (logged once)
            public bool CancelledOutside; // its order was cancelled by hand or by the broker: not placed again
            public int Rejections;        // the broker refused its order this many times
        }

        /// <summary>One traded-level trigger: the rule's numbers, the model's prices, the real fill and close.</summary>
        private class TradeRec
        {
            public Arm Arm;
            public int Side;
            public DateTime TriggerAt;
            public double TriggerBid;
            public double TriggerAsk;
            public DateTime ExitDue;
            public DateTime? ModelEntryAt;
            public double? ModelEntry;
            public double? ModelEntryMid;
            public DateTime? ModelExitAt;
            public double? ModelExit;
            public double? ModelExitMid;
            public int? PositionId;
            public double Lots;
            public DateTime? FillAt;
            public double? FillPrice;
            public DateTime? CloseAt;
            public double? ClosePrice;
            public string CloseReason;
            public double? NetProfit;
            public bool Missed;
            public string Note = "";
            public bool Logged;
        }

        /// <summary>The stop order of the armed traded level, from placing to fill or cancel.</summary>
        private class Working
        {
            public Arm Arm;
            public PendingOrder Order;    // null while placing
            public bool Placing;
            public bool CancelWanted;
            public string CancelReason;
            public TradeRec Trade;        // set once the rule triggered
            public DateTime FillDeadline;
        }

        private class SentQuote
        {
            public double Bid;
            public double Ask;
            public long SentAt;
            public double LatencyMs;
        }
        #endregion

        #region Lifecycle
        protected override void OnStart()
        {
            _newYork = FindZone("America/New_York", "Eastern Standard Time");
            _ring = new MinuteRec[Math.Max(FreshWindowMinutes, SpreadWindowMinutes) + 2];
            for (int i = 0; i < _ring.Length; i++) _ring[i] = new MinuteRec();
            _tradeLogPath = string.IsNullOrWhiteSpace(TradeLogFile) ? $"/root/ctrader_data/{BotId}_trades.csv" : TradeLogFile.Trim();
            LoadCalendar();

            Print($"[GoldLevel] Starting '{BotId}' on {SymbolName}: ${LevelStep:F0} grid, trading multiples of ${TradedMultiple:F0}; " +
                  $"arm within ${ArmBand:F2}, stop {StopOffsetSpreads:F2} x s{SpreadWindowMinutes} past the level, exit {HoldMinutes} min " +
                  $"after the trigger, busy {BusyMinutes} min; arming {ArmFromHourNewYork:00}:{ArmFromMinuteNewYork:00} -> " +
                  $"{ArmToHourNewYork:00}:{ArmToMinuteNewYork:00} New York, +/-{NewsExclusionMinutes} min of USD releases; " +
                  $"{Lots:F2} lots, broker stop {(EmergencyStopUsd > 0 ? $"${EmergencyStopUsd:F0}" : "none")}");

            // Information only. In a backtest Symbol.MarketHours.IsOpened() said closed in the first hour after the
            // summer reopen (22:02 UTC) while quotes and fills were there (7 of the 228 holdout triggers), so orders
            // and closes go by fresh quotes and the broker's answer, not by the schedule.
            Print($"[GoldLevel] {SymbolName} sessions (UTC): " + string.Join(", ", Symbol.MarketHours.Sessions.Select(x =>
                  $"{x.StartDay.ToString().Substring(0, 3)} {x.StartTime:hh\\:mm}-{x.EndDay.ToString().Substring(0, 3)} {x.EndTime:hh\\:mm}")));

            Positions.Closed += OnPositionClosed;
            PendingOrders.Filled += OnOrderFilled;
            PendingOrders.Cancelled += OnOrderCancelled;

            ReplayTickHistory();
            _live = true;
            AdoptAfterStart();

            StartCommandPoll();
            Timer.Start(TimeSpan.FromSeconds(1));
        }

        protected override void OnTick()
        {
            if (_isStopped) return;
            try
            {
                var now = Server.Time;
                ProcessTick(now, Symbol.Bid, Symbol.Ask);
                ManageOrders(now);
                ManageExits(now);
                FinishTrades(now);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[GoldLevel Tick Error] {ex.Message}");
            }
            SendLiveTickTelemetry();
        }

        protected override void OnTimer()
        {
            if (_isStopped) return;
            try
            {
                var now = Server.Time;
                if ((now - _calendarLoadedAt).TotalMinutes >= 60) LoadCalendar();
                ManageOrders(now);
                ManageExits(now);
                FinishTrades(now);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[GoldLevel Timer Error] {ex.Message}");
            }
            SendLiveTickTelemetry();
        }

        protected override void OnBarClosed()
        {
            _lastBarHandled = Server.Time;
        }

        protected override void OnStop()
        {
            _isStopped = true;
            StopCommandPoll();
            Positions.Closed -= OnPositionClosed;
            PendingOrders.Filled -= OnOrderFilled;
            PendingOrders.Cancelled -= OnOrderCancelled;
            Print($"[GoldLevel] Stopped on {SymbolName}.");
            _httpClient?.Dispose();
        }
        #endregion

        #region Calendar
        /// <summary>The system's zone, or (no tz database in the container) one built from today's rules: New York EDT
        /// from the second Sunday of March to the first Sunday of November, 02:00 local.</summary>
        private TimeZoneInfo FindZone(string ianaId, string windowsId)
        {
            foreach (var id in new[] { ianaId, windowsId })
            {
                try { return TimeZoneInfo.FindSystemTimeZoneById(id); }
                catch (Exception) { }
            }
            Print($"[GoldLevel] Time zone {ianaId} not found; using built-in DST rules");
            var start = TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 2, 0, 0), 3, 2, DayOfWeek.Sunday);
            var end = TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 2, 0, 0), 11, 1, DayOfWeek.Sunday);
            var rule = TimeZoneInfo.AdjustmentRule.CreateAdjustmentRule(new DateTime(2007, 1, 1), DateTime.MaxValue.Date,
                                                                         TimeSpan.FromHours(1), start, end);
            return TimeZoneInfo.CreateCustomTimeZone(ianaId, TimeSpan.FromHours(-5), ianaId, ianaId, ianaId + " DST", new[] { rule });
        }

        private static DateTime AsUtc(DateTime t) => DateTime.SpecifyKind(t, DateTimeKind.Utc);

        /// <summary>`hour`:`minute` local time of `date` in `zone`, as UTC.</summary>
        private static DateTime LocalToUtc(DateTime date, int hour, int minute, TimeZoneInfo zone) =>
            DateTime.SpecifyKind(TimeZoneInfo.ConvertTimeToUtc(
                DateTime.SpecifyKind(date.Date.AddHours(hour).AddMinutes(minute), DateTimeKind.Unspecified), zone), DateTimeKind.Utc);

        private static bool IsWeekday(DateTime d) => d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday;

        /// <summary>The New York trading day d whose session (arming start of d-1 .. 17:00 New York of d) holds `utc`;
        /// null outside every session and for Saturday or Sunday sessions (engine.SessionFeed).</summary>
        private DateTime? SessionDay(DateTime utc)
        {
            var ny = TimeZoneInfo.ConvertTimeFromUtc(AsUtc(utc), _newYork);
            var tod = ny.TimeOfDay;
            DateTime d;
            if (tod >= new TimeSpan(ArmFromHourNewYork, ArmFromMinuteNewYork, 0)) d = ny.Date.AddDays(1);
            else if (tod <= SessionEndNewYork) d = ny.Date;
            else return null;
            return IsWeekday(d) ? d : (DateTime?)null;
        }

        private DateTime _boundsDay = DateTime.MinValue, _armFrom, _armTo;

        private void Bounds(DateTime d)
        {
            if (d == _boundsDay) return;
            _boundsDay = d;
            _armFrom = LocalToUtc(d.AddDays(-1), ArmFromHourNewYork, ArmFromMinuteNewYork, _newYork);
            _armTo = LocalToUtc(d, ArmToHourNewYork, ArmToMinuteNewYork, _newYork);
        }

        private DateTime ArmFrom(DateTime d) { Bounds(d); return _armFrom; }

        private DateTime ArmTo(DateTime d) { Bounds(d); return _armTo; }

        /// <summary>Reads "utc_minute,event" rows (yyyy-MM-ddTHH:mm UTC) and a "# valid_through=yyyy-MM-dd" line, the
        /// last New York day whose scheduled releases the file holds. Arming stops after that day. A failed reload keeps
        /// the calendar already loaded.</summary>
        private void LoadCalendar()
        {
            _calendarLoadedAt = Server.Time;
            try
            {
                var list = new List<DateTime>();
                DateTime? valid = null;
                foreach (var raw in System.IO.File.ReadLines(CalendarFile))
                {
                    var line = raw.Trim();
                    if (line.StartsWith("#"))
                    {
                        int at = line.IndexOf("valid_through=", StringComparison.Ordinal);
                        if (at >= 0 && DateTime.TryParseExact(line.Substring(at + "valid_through=".Length).Trim(), "yyyy-MM-dd",
                                                              CultureInfo.InvariantCulture, DateTimeStyles.None, out var v))
                            valid = v.Date;
                        continue;
                    }
                    var first = line.Split(',')[0].Trim();
                    if (DateTime.TryParseExact(first, "yyyy-MM-ddTHH:mm", CultureInfo.InvariantCulture, DateTimeStyles.None, out var t))
                        list.Add(AsUtc(t));
                }
                list = list.Distinct().OrderBy(x => x).ToList();
                bool changed = list.Count != _releases.Count || valid != _calendarValidThrough;
                _releases = list;
                _calendarValidThrough = valid;
                if (changed)
                    Print($"[GoldLevel] Calendar {CalendarFile}: {list.Count} release minutes" +
                          (list.Count > 0 ? $" {list[0]:yyyy-MM-dd} .. {list[list.Count - 1]:yyyy-MM-dd}" : "") +
                          $", valid through {(valid.HasValue ? valid.Value.ToString("yyyy-MM-dd") : "(no valid_through line: arming stays off)")}");
            }
            catch (Exception ex)
            {
                Print($"[GoldLevel] Could not read the calendar {CalendarFile}: {ex.Message}" +
                      (_calendarValidThrough.HasValue ? "; keeping the one loaded" : "; arming stays off"));
            }
        }

        /// <summary>True when a release minute lies within NewsExclusionMinutes of t, both ends included.</summary>
        private bool NearRelease(DateTime t)
        {
            var w = TimeSpan.FromMinutes(NewsExclusionMinutes);
            DateTime from = t - w;
            int lo = 0, hi = _releases.Count;
            while (lo < hi)
            {
                int m = (lo + hi) / 2;
                if (_releases[m] < from) lo = m + 1; else hi = m;
            }
            return lo < _releases.Count && _releases[lo] <= t + w;
        }

        private bool CalendarCovers(DateTime sessionDay) => _calendarValidThrough.HasValue && sessionDay <= _calendarValidThrough.Value;
        #endregion

        #region Envelope
        private static long MinuteOf(DateTime t) => t.Ticks / TimeSpan.TicksPerMinute;

        private int Slot(long minute) => (int)(((minute % _ring.Length) + _ring.Length) % _ring.Length);

        /// <summary>Closes the minute in progress and computes the new minute's envelope: the highest / lowest mid of
        /// the FreshWindowMinutes before it and the median last-tick spread of the SpreadWindowMinutes before it
        /// (build_minutes_hold.py: W_up, W_dn, s60). Minutes without ticks are skipped; with no spread in the window the
        /// last s60 carries on.</summary>
        private void RollMinute(long minute)
        {
            if (_curMinute != long.MinValue && _curCount > 0)
            {
                var r = _ring[Slot(_curMinute)];
                r.Minute = _curMinute;
                r.Max = _curMax;
                r.Min = _curMin;
                r.LastSpread = _curLastSpread;
            }
            _curMinute = minute;
            _curMax = double.NegativeInfinity;
            _curMin = double.PositiveInfinity;
            _curCount = 0;

            double hi = double.NegativeInfinity, lo = double.PositiveInfinity;
            for (long k = minute - FreshWindowMinutes; k < minute; k++)
            {
                var r = _ring[Slot(k)];
                if (r.Minute != k) continue;
                if (r.Max > hi) hi = r.Max;
                if (r.Min < lo) lo = r.Min;
            }
            _wUp = hi;
            _wDn = lo;

            _spreadBuf.Clear();
            for (long k = minute - SpreadWindowMinutes; k < minute; k++)
            {
                var r = _ring[Slot(k)];
                if (r.Minute == k) _spreadBuf.Add(r.LastSpread);
            }
            if (_spreadBuf.Count > 0) _s60 = Median(_spreadBuf);
        }

        /// <summary>numpy.median: the middle value, or the mean of the two middle values.</summary>
        public static double Median(List<double> values)
        {
            var s = values.OrderBy(v => v).ToList();
            int n = s.Count;
            return n % 2 == 1 ? s[n / 2] : (s[n / 2 - 1] + s[n / 2]) / 2.0;
        }
        #endregion

        #region Rule
        /// <summary>One tick through the rule, in the engine's order: the tick is judged against the envelope of the
        /// earlier ticks, then joins it. Live ticks and replayed history go through the same code.</summary>
        private void ProcessTick(DateTime t, double bid, double ask)
        {
            if (!(bid > 0) || !(ask > 0) || ask < bid) return;   // gcommon.DayLoader drops one-sided and crossed quotes
            if (t < _lastTickAt) return;                          // history and live ticks overlap at start
            long minute = MinuteOf(t);
            if (minute != _curMinute) RollMinute(minute);
            double mid = 0.5 * (bid + ask);

            var session = SessionDay(t);
            if (session.HasValue)
            {
                bool newSession = !_lastSession.HasValue || _lastSession.Value != session.Value;
                if (newSession && _mode != ArmMode.Idle)
                {
                    // an arm lives inside one session (gen_events runs per session); only the busy window and the
                    // level memory carry over
                    if (_mode == ArmMode.Armed) Disarm("session ended");
                    _mode = ArmMode.Idle;
                    _arm = null;
                }
                // the session's first tick and a tick after a gap start GapCooldownMinutes without arming
                if (newSession || (t - _lastTickAt).TotalMinutes > GapMinutes) _gapAt = t;
                Step(t, bid, ask, mid, ArmingAllowed(t, session.Value));
            }

            if (mid > _curMax) _curMax = mid;
            if (mid < _curMin) _curMin = mid;
            _curLastSpread = ask - bid;
            _curCount++;
            _lastTickAt = t;
            _lastSession = session;
            CaptureModelPrices(t, bid, ask);
        }

        /// <summary>engine.session_arrays' arming mask, plus the bot's own data needs: a calendar that covers the day
        /// and a full FreshWindowMinutes of ticks.</summary>
        private bool ArmingAllowed(DateTime t, DateTime sessionDay)
        {
            if (t < ArmFrom(sessionDay) || t >= ArmTo(sessionDay)) return false;
            if (_gapAt != DateTime.MinValue && (t - _gapAt).TotalMinutes < GapCooldownMinutes) return false;
            if (NearRelease(t)) return false;
            if (!CalendarCovers(sessionDay))
            {
                if (_live && (t - _lastCalendarWarnAt).TotalMinutes >= 60)
                {
                    _lastCalendarWarnAt = t;
                    Print($"[GoldLevel] The release calendar does not cover {sessionDay:yyyy-MM-dd}: no arming until {CalendarFile} is updated");
                }
                return false;
            }
            return MinuteOf(t) - FreshWindowMinutes >= _coverageFromMinute;
        }

        /// <summary>True when arming will not be allowed CancelLeadSeconds from now: a real order is cancelled (and none
        /// placed) that early, so the broker cannot fill it inside an exclusion.</summary>
        private bool ClosingSoon(DateTime now)
        {
            var t = now.AddSeconds(CancelLeadSeconds);
            var d = SessionDay(t);
            return !d.HasValue || t >= ArmTo(d.Value) || NearRelease(t) || !CalendarCovers(d.Value);
        }

        /// <summary>engine.gen_events for one tick: an armed level triggers or is cancelled; a blocked level waits for
        /// its cancel; otherwise, flat and not busy, the nearest fresh level within the band arms.</summary>
        private void Step(DateTime t, double bid, double ask, double mid, bool ok)
        {
            if (_mode != ArmMode.Idle)
            {
                var a = _arm;
                bool cancel = !ok || (a.Side > 0 ? mid < a.Level - ArmBand : mid > a.Level + ArmBand);
                if (!cancel)
                {
                    if (_mode == ArmMode.Armed && (a.Side > 0 ? ask >= a.Stop : bid <= a.Stop))
                        Trigger(t, bid, ask);
                    return;
                }
                if (_mode == ArmMode.Armed) Disarm(ok ? "the mid left the band" : "arming closed");
                _mode = ArmMode.Idle;
                _arm = null;
                // as in the engine, the cancelling tick may arm a level itself
            }
            if (!ok || t < _busyUntil || double.IsNaN(_s60)) return;

            double off = StopOffsetSpreads * _s60;
            double up = LevelStep * (Math.Floor(mid / LevelStep) + 1.0);     // the level above the mid (strictly)
            double dn = LevelStep * (Math.Ceiling(mid / LevelStep) - 1.0);   // the level below
            double high = Math.Max(_wUp, _curMax), low = Math.Min(_wDn, _curMin);
            bool armUp = up - mid <= ArmBand && up > high && !(ask >= up + off);
            bool armDn = mid - dn <= ArmBand && dn < low && !(bid <= dn - off);
            if (!armUp && !armDn) return;

            int side = armUp ? 1 : -1;
            double level = armUp ? up : dn;
            var arm = new Arm
            {
                Level = level,
                Side = side,
                S60 = _s60,
                At = t,
                Key = (long)Math.Round(level * 100),
                Traded = IsTradedLevel(level),
                Stop = side > 0 ? level + off : level - off
            };
            arm.OrderPrice = side > 0 ? CeilToTick(arm.Stop) : FloorToTick(arm.Stop);
            _arm = arm;
            if (_triggered.TryGetValue(arm.Key, out var last) && (t - last).TotalMinutes < LevelMemoryMinutes)
            {
                _mode = ArmMode.Blocked;
                return;
            }
            _mode = ArmMode.Armed;
            if (_live && ShowLogs && arm.Traded)
                Print($"[GoldLevel] Armed {(side > 0 ? "buy" : "sell")} stop {arm.OrderPrice} at the fresh ${level:F0} level " +
                      $"(mid {mid:F2}, s{SpreadWindowMinutes} {_s60:F3}, 24h {(side > 0 ? $"high {high:F2}" : $"low {low:F2}")})");
            if (_live && arm.Traded) TryPlace(t);
        }

        /// <summary>The rule's trigger: busy for BusyMinutes, the level remembered. A traded level becomes a trade whose
        /// stop order the broker filled on the same tick, or a missed one when no order was working.</summary>
        private void Trigger(DateTime t, double bid, double ask)
        {
            var a = _arm;
            _busyUntil = t.AddMinutes(BusyMinutes);
            _triggered[a.Key] = t;
            foreach (var k in _triggered.Where(kv => (t - kv.Value).TotalMinutes >= LevelMemoryMinutes).Select(kv => kv.Key).ToList())
                _triggered.Remove(k);
            _mode = ArmMode.Idle;
            _arm = null;
            if (!a.Traded) return;

            var trade = new TradeRec
            {
                Arm = a, Side = a.Side, TriggerAt = t, TriggerBid = bid, TriggerAsk = ask, ExitDue = t.AddMinutes(HoldMinutes),
                Lots = OrderVolume() / Symbol.LotSize
            };
            _lastRuleTrade = trade;
            _modelWatch.Add(trade);   // also in the replay: a position open at start keeps its model prices
            if (!_live) return;
            _pendingLog.Add(trade);
            Print($"[GoldLevel] Trigger: {(a.Side > 0 ? "up" : "down")} through ${a.Level:F0} (stop {a.OrderPrice}) at {t:yyyy-MM-dd HH:mm:ss.fff} UTC, quote {bid}/{ask}");
            if (_working != null && _working.Arm == a)
            {
                _working.Trade = trade;
                _working.FillDeadline = t.AddSeconds(FillWaitSeconds);
            }
            else
                MarkMissed(trade, a.NoOrderReason ?? "no order was working");
        }

        /// <summary>Cancels the armed level's real order (its virtual twin goes with it in Step).</summary>
        private void Disarm(string why)
        {
            if (_live && ShowLogs && _arm != null && _arm.Traded)
                Print($"[GoldLevel] Disarmed ${_arm.Level:F0}: {why}");
            if (_working != null && _working.Arm == _arm && _working.Trade == null) CancelWorking(why);
        }

        private bool IsTradedLevel(double level)
        {
            long k = (long)Math.Round(level / LevelStep);
            long every = Math.Max(1, (long)Math.Round(TradedMultiple / LevelStep));
            return k % every == 0;
        }

        private double CeilToTick(double price) => Math.Round(Math.Ceiling(price / Symbol.TickSize - 1e-7) * Symbol.TickSize, Symbol.Digits);

        private double FloorToTick(double price) => Math.Round(Math.Floor(price / Symbol.TickSize + 1e-7) * Symbol.TickSize, Symbol.Digits);

        private double OrderVolume() => Math.Max(Symbol.VolumeInUnitsMin, Symbol.NormalizeVolumeInUnits(Lots * Symbol.LotSize, RoundingMode.Down));

        private string DescribeState()
        {
            string arm = _mode == ArmMode.Idle ? "idle"
                : $"{(_mode == ArmMode.Armed ? "armed" : "blocked")} at ${_arm.Level:F0} ({(_arm.Traded ? "traded" : "virtual")}, since {_arm.At:HH:mm:ss})";
            return $"{arm}; busy until {(_busyUntil == DateTime.MinValue ? "-" : _busyUntil.ToString("yyyy-MM-dd HH:mm:ss"))}; " +
                   $"{_triggered.Count} levels triggered in the last {LevelMemoryMinutes} min; s{SpreadWindowMinutes} {_s60:F3}; " +
                   $"24h {_wDn:F2} .. {_wUp:F2}";
        }
        #endregion

        #region Start-up replay
        /// <summary>Runs the rule over the last FreshWindow + LevelMemory + SpreadWindow minutes of ticks without trading,
        /// so the envelope, the busy window, the level memory and an armed level are the rule's own. Without that much
        /// history the bot arms only once it has FreshWindowMinutes of ticks after the first one it has.</summary>
        private void ReplayTickHistory()
        {
            var now = Server.Time;
            var from = new DateTime(MinuteOf(now.AddMinutes(-(FreshWindowMinutes + LevelMemoryMinutes + SpreadWindowMinutes + 10))) * TimeSpan.TicksPerMinute, DateTimeKind.Utc);
            _coverageFromMinute = MinuteOf(now) + 1;
            if (!ReplayHistory) return;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            try
            {
                var ticks = MarketData.GetTicks();
                int loads = 0;
                while ((ticks.Count == 0 || ticks[0].Time > from) && loads < 10000 && sw.Elapsed.TotalSeconds < 300)
                {
                    loads++;
                    if (ticks.LoadMoreHistory() <= 0) break;
                }
                if (ticks.Count == 0)
                {
                    Print($"[GoldLevel] No tick history; arming starts {FreshWindowMinutes} min after the first live tick");
                    return;
                }
                bool complete = ticks[0].Time <= from;
                var first = complete ? from : ticks[0].Time;
                _coverageFromMinute = complete ? MinuteOf(from) : MinuteOf(first) + 1;
                int fed = 0, n = ticks.Count;
                for (int i = 0; i < n; i++)
                {
                    var tk = ticks[i];
                    if (tk.Time < from) continue;
                    if (tk.Time > now) break;
                    ProcessTick(tk.Time, tk.Bid, tk.Ask);
                    fed++;
                }
                Print($"[GoldLevel] Replayed {fed} ticks {first:yyyy-MM-dd HH:mm} .. {_lastTickAt:yyyy-MM-dd HH:mm:ss} UTC " +
                      $"({loads} history loads, {sw.Elapsed.TotalSeconds:F0} s, {(complete ? "complete" : "history starts later than wanted")}); {DescribeState()}");
            }
            catch (Exception ex)
            {
                Print($"[GoldLevel] Tick history replay failed ({ex.Message}); arming starts {FreshWindowMinutes} min after the first live tick");
                ResetRule();
                _coverageFromMinute = MinuteOf(Server.Time) + 1;
            }
        }

        private void ResetRule()
        {
            foreach (var r in _ring) r.Minute = long.MinValue;
            _curMinute = long.MinValue;
            _curMax = double.NegativeInfinity;
            _curMin = double.PositiveInfinity;
            _curCount = 0;
            _wUp = double.NegativeInfinity;
            _wDn = double.PositiveInfinity;
            _s60 = double.NaN;
            _lastTickAt = DateTime.MinValue;
            _lastSession = null;
            _gapAt = DateTime.MinValue;
            _mode = ArmMode.Idle;
            _arm = null;
            _busyUntil = DateTime.MinValue;
            _triggered.Clear();
            _lastRuleTrade = null;
        }

        /// <summary>After the replay: cancels own stop orders left by an earlier run (an armed traded level gets its order
        /// again on the next tick) and gives each open position its exit time, from the replayed trigger it came from or
        /// else from its entry time.</summary>
        private void AdoptAfterStart()
        {
            foreach (var order in GetBotOrders())
            {
                Print($"[GoldLevel] Cancelling #{order.Id} {order.TradeType} stop @ {order.TargetPrice} left by an earlier run");
                CancelPendingOrderAsync(order, r => { });
            }
            foreach (var pos in GetBotPositions())
            {
                var t = _lastRuleTrade;
                bool match = t != null && t.Side == SideOf(pos.TradeType) && Math.Abs((pos.EntryTime - t.TriggerAt).TotalMinutes) <= 5;
                var trade = match ? t : new TradeRec
                {
                    Side = SideOf(pos.TradeType), TriggerAt = pos.EntryTime, ExitDue = pos.EntryTime.AddMinutes(HoldMinutes),
                    Note = "open at start, no replayed trigger: exit from the entry time"
                };
                if (match) trade.Note = "open at start";
                trade.PositionId = pos.Id;
                trade.Lots = pos.VolumeInUnits / Symbol.LotSize;
                trade.FillAt = pos.EntryTime;
                trade.FillPrice = pos.EntryPrice;
                _openTrades[pos.Id] = trade;
                Print($"[GoldLevel] Position #{pos.Id} {pos.TradeType} @ {pos.EntryPrice} open at start; exit at {trade.ExitDue:yyyy-MM-dd HH:mm:ss} UTC ({trade.Note})");
            }
            _modelWatch.RemoveAll(tr => !_openTrades.ContainsValue(tr));
            if (_mode == ArmMode.Armed && _arm.Traded)
                Print($"[GoldLevel] Armed at ${_arm.Level:F0} since {_arm.At:HH:mm:ss}; its stop order goes out with the next tick");
        }
        #endregion

        #region Orders
        private List<PendingOrder> GetBotOrders() => PendingOrders.Where(o => o.SymbolName == SymbolName).ToList();

        /// <summary>Places the armed traded level's stop order when nothing stops it; why not is kept on the arm and
        /// logged once.</summary>
        private void TryPlace(DateTime now)
        {
            var a = _arm;
            if (_mode != ArmMode.Armed || a == null || !a.Traded || _working != null || a.CancelledOutside) return;
            if (a.Rejections >= MaxRejections) return;
            if (now < _nextPlaceAt) return;
            string why = null;
            if (GetBotPositions().Count > 0) why = "a position is still open";
            else if (!HasFreshQuote(now)) why = "no live quote";
            else if (ClosingSoon(now)) why = "an exclusion starts within the cancel lead";
            if (why != null)
            {
                if (a.NoOrderReason != why && ShowLogs) Print($"[GoldLevel] No order at ${a.Level:F0}: {why}");
                a.NoOrderReason = why;
                return;
            }
            if (DashboardPauseBlocks($"the ${a.Level:F0} stop order"))
            {
                a.NoOrderReason = "paused from the dashboard";
                return;
            }
            a.NoOrderReason = null;

            var w = new Working { Arm = a, Placing = true };
            _working = w;
            var type = a.Side > 0 ? TradeType.Buy : TradeType.Sell;
            double volume = OrderVolume();
            double? stop = EmergencyStopUsd > 0 ? EmergencyStopUsd / Symbol.PipSize : (double?)null;
            ProtectionType? protection = stop.HasValue ? ProtectionType.Relative : (ProtectionType?)null;
            string label = null, comment = null;
            double? takeProfit = null;
            DateTime? expiry = null;
            long sent = System.Diagnostics.Stopwatch.GetTimestamp();
            PlaceStopOrderAsync(type, SymbolName, volume, a.OrderPrice, label, stop, takeProfit, protection, expiry, comment, false,
                                StopTriggerMethod.Trade, StopTriggerMethod.Trade, result =>
            {
                w.Placing = false;
                if (result != null && result.IsSuccessful && result.PendingOrder != null)
                {
                    w.Order = result.PendingOrder;
                    if (ShowLogs) Print($"[GoldLevel] Placed #{w.Order.Id} {type} stop {volume / Symbol.LotSize:F2} lots @ {a.OrderPrice} in {ElapsedMs(sent):F0} ms");
                    if (w.CancelWanted) CancelOrder(w);
                    return;
                }
                string error = result != null ? result.Error.ToString() : "no result";
                a.Rejections++;
                Print($"[GoldLevel] Stop order at ${a.Level:F0} failed ({a.Rejections}/{MaxRejections}): {error}" +
                      (a.Rejections < MaxRejections ? $"; retrying in {OrderRetrySeconds} s while armed" : "; no more tries for this arm"));
                if (_working == w) _working = null;
                a.NoOrderReason = $"order rejected ({error})";
                _nextPlaceAt = Server.Time.AddSeconds(OrderRetrySeconds);
                if (w.Trade != null) MarkMissed(w.Trade, a.NoOrderReason);
            });
        }

        private void CancelWorking(string why)
        {
            var w = _working;
            if (w == null) return;
            _working = null;
            w.CancelWanted = true;
            w.CancelReason = why;
            if (w.Order != null) CancelOrder(w);   // still placing: the place callback cancels it
        }

        private void CancelOrder(Working w)
        {
            var order = w.Order;
            if (order == null) return;
            _cancelling[order.Id] = w;
            CancelPendingOrderAsync(order, r =>
            {
                if (r != null && r.IsSuccessful)
                {
                    _cancelling.Remove(order.Id);
                    if (ShowLogs) Print($"[GoldLevel] Cancelled #{order.Id} ({w.CancelReason})");
                }
                else
                    Print($"[GoldLevel] Cancel of #{order.Id} failed: {(r != null ? r.Error.ToString() : "no result")} (a fill comes as its own event)");
            });
        }

        /// <summary>On ticks and every second: cancels a waiting order when the dashboard pauses the bot, an exclusion
        /// is about to start or the quotes stop (the rule's gap), gives up on a triggered order that did not fill, and
        /// places the armed level's order when it has none.</summary>
        private void ManageOrders(DateTime now)
        {
            var w = _working;
            if (w == null)
            {
                TryPlace(now);
                return;
            }
            if (w.Trade == null)
            {
                string why = null;
                if (_dashboardPaused) why = "paused from the dashboard";
                else if (ClosingSoon(now)) why = "an exclusion starts";
                else if (_lastTickAt != DateTime.MinValue && (now - _lastTickAt).TotalMinutes > GapMinutes) why = $"no tick for {GapMinutes} min";
                if (why == null) return;
                if (w.Arm != null) w.Arm.NoOrderReason = why;
                CancelWorking(why);
            }
            else if (now > w.FillDeadline)
            {
                MarkMissed(w.Trade, $"no fill within {FillWaitSeconds} s of the trigger");
                CancelWorking("not filled");
            }
        }

        private void OnOrderFilled(PendingOrderFilledEventArgs args)
        {
            try
            {
                var order = args.PendingOrder;
                var pos = args.Position;
                if (pos == null || pos.SymbolName != SymbolName) return;
                var now = Server.Time;
                Working w = null;
                if (_working != null && _working.Order != null && order != null && _working.Order.Id == order.Id) w = _working;
                else if (order != null && _cancelling.TryGetValue(order.Id, out var c))
                {
                    w = c;
                    _cancelling.Remove(order.Id);
                }

                var trade = w?.Trade;
                if (trade == null && w != null && w == _working && _mode == ArmMode.Armed && _arm == w.Arm)
                {
                    // the broker triggered on a tick the bot has not processed yet: that is the rule's trigger
                    Trigger(now, Symbol.Bid, Symbol.Ask);
                    trade = w.Trade;
                }
                if (trade == null)
                {
                    trade = new TradeRec
                    {
                        Arm = w?.Arm, Side = SideOf(pos.TradeType), TriggerAt = now, ExitDue = now.AddMinutes(HoldMinutes),
                        Note = w == null ? "filled order the bot did not place" : $"filled after the bot cancelled it ({w.CancelReason})"
                    };
                    _pendingLog.Add(trade);
                    _modelWatch.Add(trade);
                }
                if (_working == w) _working = null;
                trade.Missed = false;
                trade.PositionId = pos.Id;
                trade.Lots = pos.VolumeInUnits / Symbol.LotSize;
                trade.FillAt = now;
                trade.FillPrice = pos.EntryPrice;
                _openTrades[pos.Id] = trade;
                double slip = trade.Arm != null ? trade.Side * (pos.EntryPrice - trade.Arm.OrderPrice) : double.NaN;
                Print($"[GoldLevel] Opened #{pos.Id} {pos.TradeType} {trade.Lots:F2} lots @ {pos.EntryPrice} " +
                      $"({(trade.Arm != null ? $"stop {trade.Arm.OrderPrice}, slippage {slip:+0.00;-0.00;0.00}" : "no arm")}); exit at {trade.ExitDue:HH:mm:ss} UTC");
                ReportPositionOpen(pos, trade);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[OnOrderFilled Error] {ex.Message}");
            }
        }

        private void OnOrderCancelled(PendingOrderCancelledEventArgs args)
        {
            var order = args.PendingOrder;
            if (order == null || order.SymbolName != SymbolName) return;
            if (_cancelling.Remove(order.Id)) return;
            var w = _working;
            if (w == null || w.Order == null || w.Order.Id != order.Id) return;
            // cancelled by hand or by the broker, not by the bot: not placed again for this arm
            _working = null;
            if (w.Arm != null)
            {
                w.Arm.CancelledOutside = true;
                w.Arm.NoOrderReason = $"order cancelled outside the bot ({args.Reason})";
            }
            Print($"[GoldLevel] Order #{order.Id} cancelled outside the bot ({args.Reason})");
            if (w.Trade != null) MarkMissed(w.Trade, $"order cancelled outside the bot ({args.Reason})");
        }
        #endregion

        #region Positions and the trade log
        private static int SideOf(TradeType t) => t == TradeType.Buy ? 1 : -1;

        private bool HasFreshQuote(DateTime now) => (now - _lastTickAt).TotalSeconds <= MaxQuoteAgeSeconds;

        /// <summary>This bot's positions: every position on its symbol. One bot trades each symbol of an account and
        /// nothing is traded there by hand.</summary>
        private List<Position> GetBotPositions() => Positions.Where(p => p.SymbolName == SymbolName).ToList();

        /// <summary>Closes each own position HoldMinutes after its trigger (its entry for one the bot cannot place), or
        /// after MaxHoldMinutes in any case, on the first live quote.</summary>
        private void ManageExits(DateTime now)
        {
            foreach (var pos in GetBotPositions())
            {
                if (!_openTrades.TryGetValue(pos.Id, out var trade))
                {
                    if ((now - pos.EntryTime).TotalSeconds < 10) continue;   // its fill event has not been handled yet
                    trade = new TradeRec
                    {
                        Side = SideOf(pos.TradeType), TriggerAt = pos.EntryTime, ExitDue = pos.EntryTime.AddMinutes(HoldMinutes),
                        PositionId = pos.Id, Lots = pos.VolumeInUnits / Symbol.LotSize, FillAt = pos.EntryTime, FillPrice = pos.EntryPrice,
                        Note = "position the bot did not open: exit from its entry time"
                    };
                    _openTrades[pos.Id] = trade;
                    Print($"[GoldLevel] Position #{pos.Id} {pos.TradeType} @ {pos.EntryPrice} is not the bot's; closing it at {trade.ExitDue:HH:mm:ss} UTC");
                }
                string reason = null;
                if (now >= trade.ExitDue) reason = $"Hold exit ({HoldMinutes} min after the trigger)";
                else if (now - pos.EntryTime >= TimeSpan.FromMinutes(MaxHoldMinutes)) reason = $"Max hold ({MaxHoldMinutes} min)";
                if (reason == null) continue;
                if (_nextCloseAt.TryGetValue(pos.Id, out var next) && now < next) continue;
                if (!HasFreshQuote(now)) continue;   // closes on the first live quote
                _nextCloseAt[pos.Id] = now.AddSeconds(OrderRetrySeconds);
                var result = CloseWithReason(pos, reason);
                if (result == null || !result.IsSuccessful)
                    Print($"[GoldLevel] Could not close #{pos.Id} ({reason}): {(result != null ? result.Error.ToString() : "no result")}");
            }
        }

        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            var quote = new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask, SentAt = System.Diagnostics.Stopwatch.GetTimestamp() };
            var result = ClosePosition(pos);
            quote.LatencyMs = ElapsedMs(quote.SentAt);
            if (result != null && result.IsSuccessful) _closeQuotes[pos.Id] = quote;
            return result;
        }

        private static double ElapsedMs(long since) =>
            (System.Diagnostics.Stopwatch.GetTimestamp() - since) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;

        /// <summary>fills.fill_after / exit_at: the model enters at the first tick ModelLatencyMs after the trigger (ask
        /// for a buy, bid for a sell) and exits at the first tick ModelLatencyMs after the exit time. A price whose tick
        /// comes more than TradeLogFlushMinutes late (fills.GAP_MS) stays empty.</summary>
        private void CaptureModelPrices(DateTime t, double bid, double ask)
        {
            for (int i = _modelWatch.Count - 1; i >= 0; i--)
            {
                var tr = _modelWatch[i];
                var entryAt = tr.TriggerAt.AddMilliseconds(ModelLatencyMs);
                var exitAt = tr.ExitDue.AddMilliseconds(ModelLatencyMs);
                if (!tr.ModelEntry.HasValue && t >= entryAt && t <= entryAt.AddMinutes(TradeLogFlushMinutes))
                {
                    tr.ModelEntryAt = t;
                    tr.ModelEntry = tr.Side > 0 ? ask : bid;
                    tr.ModelEntryMid = 0.5 * (bid + ask);
                }
                if (!tr.ModelExit.HasValue && t >= exitAt && t <= exitAt.AddMinutes(TradeLogFlushMinutes))
                {
                    tr.ModelExitAt = t;
                    tr.ModelExit = tr.Side > 0 ? bid : ask;
                    tr.ModelExitMid = 0.5 * (bid + ask);
                }
                if (tr.ModelExit.HasValue || t > exitAt.AddMinutes(TradeLogFlushMinutes)) _modelWatch.RemoveAt(i);
            }
        }

        private void MarkMissed(TradeRec trade, string why)
        {
            if (trade.Missed || trade.PositionId.HasValue) return;
            trade.Missed = true;
            trade.Note = why;
            Print($"[GoldLevel] Missed trade at ${trade.Arm?.Level:F0} triggered {trade.TriggerAt:HH:mm:ss.fff}: {why}");
        }

        /// <summary>Writes each finished trade (closed, or missed) once its model exit is known or TradeLogFlushMinutes
        /// after its exit time.</summary>
        private void FinishTrades(DateTime now)
        {
            for (int i = _pendingLog.Count - 1; i >= 0; i--)
            {
                var tr = _pendingLog[i];
                bool done = tr.Missed || tr.CloseAt.HasValue;
                bool priced = tr.ModelExit.HasValue || now > tr.ExitDue.AddMinutes(TradeLogFlushMinutes);
                if (!done || !priced) continue;
                _pendingLog.RemoveAt(i);
                WriteTradeLog(tr);
            }
        }

        private const string TradeLogHeader =
            "trigger_utc,arm_utc,level,side,stop,order_price,s60,trigger_bid,trigger_ask,model_entry_utc,model_entry,model_entry_mid," +
            "model_exit_utc,model_exit,model_exit_mid,model_net_bp,position_id,lots,fill_utc,fill_price,close_utc,close_price,close_reason," +
            "fill_net_bp,entry_slip_vs_model,entry_slip_s60,net_profit,missed,note";

        private void WriteTradeLog(TradeRec tr)
        {
            if (tr.Logged) return;
            tr.Logged = true;
            var ci = CultureInfo.InvariantCulture;
            string F(double? v) => v.HasValue && !double.IsNaN(v.Value) ? v.Value.ToString("R", ci) : "";
            string T(DateTime? v) => v.HasValue ? v.Value.ToString("yyyy-MM-ddTHH:mm:ss.fff", ci) : "";
            string Q(string s) => string.IsNullOrEmpty(s) ? "" : "\"" + s.Replace("\"", "'") + "\"";
            double? modelNet = null, fillNet = null, slip = null, slipS = null;
            if (tr.ModelEntry.HasValue && tr.ModelExit.HasValue && tr.ModelEntryMid > 0)
                modelNet = tr.Side * (tr.ModelExit.Value - tr.ModelEntry.Value) / tr.ModelEntryMid.Value * 1e4 - ModelCommissionBp;
            if (tr.FillPrice.HasValue && tr.ClosePrice.HasValue && tr.FillPrice > 0)
                fillNet = tr.Side * (tr.ClosePrice.Value - tr.FillPrice.Value) / tr.FillPrice.Value * 1e4 - ModelCommissionBp;
            if (tr.FillPrice.HasValue && tr.ModelEntry.HasValue)
            {
                slip = tr.Side * (tr.FillPrice.Value - tr.ModelEntry.Value);
                if (tr.Arm != null && tr.Arm.S60 > 0) slipS = slip / tr.Arm.S60;
            }
            var a = tr.Arm;
            string row = string.Join(",", new[]
            {
                T(tr.TriggerAt), T(a?.At), F(a?.Level), tr.Side.ToString(ci), F(a?.Stop), F(a?.OrderPrice), F(a?.S60),
                F(a != null ? tr.TriggerBid : (double?)null), F(a != null ? tr.TriggerAsk : (double?)null),
                T(tr.ModelEntryAt), F(tr.ModelEntry), F(tr.ModelEntryMid), T(tr.ModelExitAt), F(tr.ModelExit), F(tr.ModelExitMid), F(modelNet),
                tr.PositionId.HasValue ? tr.PositionId.Value.ToString(ci) : "", F(tr.Lots), T(tr.FillAt), F(tr.FillPrice),
                T(tr.CloseAt), F(tr.ClosePrice), Q(tr.CloseReason), F(fillNet), F(slip), F(slipS), F(tr.NetProfit),
                tr.Missed ? "1" : "0", Q(tr.Note)
            });
            Print($"[GoldLevel] TRADE {row}");
            if (RunningMode != RunningMode.RealTime && string.IsNullOrWhiteSpace(TradeLogFile)) return;
            try
            {
                bool fresh = !System.IO.File.Exists(_tradeLogPath);
                using (var w = new StreamWriter(_tradeLogPath, append: true))
                {
                    if (fresh) w.WriteLine(TradeLogHeader);
                    w.WriteLine(row);
                }
            }
            catch (Exception ex)
            {
                Print($"[GoldLevel] Could not write {_tradeLogPath}: {ex.Message}");
            }
        }
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

        /// <summary>Runs on the cBot thread. Closes only this bot's own positions; close_all also cancels its waiting
        /// stop order, so nothing opens right after (the rule re-arms unless the bot is paused).</summary>
        private void ExecuteDashboardCommand(string baseUrl, DashboardCommand cmd)
        {
            var own = GetBotPositions();
            List<Position> targets;
            if (cmd.action == "close_all")
            {
                targets = own.ToList();
                CancelWorking(ManualCloseReason);
            }
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
        #endregion

        #region Server reporting
        private string ResolvedReportUrl() => !string.IsNullOrWhiteSpace(ReportUrl) ? ReportUrl.Trim() : ApiUrl.Replace("/trade", "/portfolio/report");

        private double BrokerStopPips() => EmergencyStopUsd > 0 ? EmergencyStopUsd / Symbol.PipSize : 0.0;

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
                        sl_price = p.StopLoss,
                        tp_price = p.TakeProfit,
                        sl_pnl = p.StopLoss.HasValue ? (double?)Math.Round(EstimatedNetProfitAt(p, p.StopLoss.Value), 2) : null,
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
                    _nextCloseAt.Remove(pos.Id);
                    string reason;
                    if (args.Reason == PositionCloseReason.StopLoss)
                        reason = $"StopLoss (broker guard, ${EmergencyStopUsd:F0})";
                    else if (args.Reason == PositionCloseReason.Closed)
                        reason = hasBotReason ? botReason : "Closed outside the bot (cTrader)";
                    else
                        reason = args.Reason.ToString();

                    string fillNote = _closeQuotes.TryGetValue(pos.Id, out var q)
                        ? $" @ {exitPrice}; quote {q.Bid}/{q.Ask}, {q.LatencyMs:F0} ms" : $" @ {exitPrice}";
                    _closeQuotes.Remove(pos.Id);
                    Print($"[GoldLevel] Closed #{pos.Id} {pos.TradeType}: {reason}, net {pos.NetProfit:F2}{fillNote}");

                    if (_openTrades.TryGetValue(pos.Id, out var trade))
                    {
                        _openTrades.Remove(pos.Id);
                        trade.CloseAt = Server.Time;
                        trade.ClosePrice = exitPrice;
                        trade.CloseReason = reason;
                        trade.NetProfit = pos.NetProfit;
                        if (!_pendingLog.Contains(trade)) _pendingLog.Add(trade);
                    }
                    ReportPositionClosed(pos, pos.NetProfit, reason, exitPrice, pos.Pips);
                    SendLiveTickTelemetry(force: true);
                }
                catch (Exception ex)
                {
                    if (ShowLogs) Print($"[OnPositionClosed Error] {ex.Message}");
                }
            });
        }

        private void ReportPositionOpen(Position position, TradeRec trade)
        {
            if (RunningMode != RunningMode.RealTime || _httpClient == null || position == null) return;
            try
            {
                int posId = position.Id;
                string posSide = position.TradeType.ToString();
                string posSymbol = position.SymbolName;
                var a = trade.Arm;
                string reason = a != null
                    ? $"Gold ${a.Level:F0} level break {(a.Side > 0 ? "up" : "down")} (stop {a.OrderPrice})"
                    : "Gold level break (no arm)";
                var report = new
                {
                    ctrader_id = posId,
                    bot_id = BotId,
                    action = "open",
                    symbol = posSymbol,
                    side = posSide,
                    volume = position.VolumeInUnits / Symbol.LotSize,
                    entry_price = position.EntryPrice,
                    sl_price = position.StopLoss,
                    tp_price = position.TakeProfit,
                    sl_pips = Math.Round(BrokerStopPips(), 1),
                    tp_pips = 0.0,
                    reason,
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
                    sl_price = position.StopLoss,
                    tp_price = position.TakeProfit,
                    sl_pips = Math.Round(BrokerStopPips(), 1),
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
