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
    /// ECB-fix window bot (research E1 and F3: research/results/portfolio/round13_structural/PREREG_M_eurusd_midday.md,
    /// research/results/portfolio/round24_relaxed/PREREG_R24_relaxed_hold.md).
    ///
    /// EUR is sold into the 14:15 CET ECB reference rate, so EURUSD drifts down over the London midday. E1 sells EURUSD
    /// at 11:00 London and buys it back at 13:00 London on every weekday but 24/12-1/1. F3 does the same only on
    /// USD-TOP days: the mean log change of USDJPY and USDCHF (mid) from 18:00 New York on the previous weekday to
    /// 07:00 London is at or above the 67th percentile (linear) of the same score over the previous 250 weekdays, with
    /// at least 60 of them known. A score needs both quotes of both symbols, each the last quote in the 11 minutes
    /// before its time (the research's M1 bar ending at the time or up to 10 bars before it); Friday 18:00 New York has
    /// none (the market is closed), so F3 never trades a Monday.
    ///
    /// The selector needs mid prices at two minutes a day, which cTrader's bid bars cannot give (the 18:00 New York
    /// spread is wide after the rollover; bid instead of mid moves ~6 % of the F3 days). So the bot records the live
    /// bid/ask of the selector symbols at those minutes in QuoteLogFile, reads the history from it and from SeedFile
    /// (research/tools/ecb_usd_top_seed.py, the research data's quotes), and falls back to the bid close of an M15
    /// bar only for a minute neither holds (it logs when it does).
    ///
    /// One position at a time, held two hours. The lot is fixed (Lots), never read off the account. The broker stop
    /// (EmergencyStopPips) is not part of the rule: it is a far guard for a bot or VPS that dies with a position open.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class EcbWindowBot : Robot
    {
        #region Parameters
        [Parameter("Bot ID", Group = "General", DefaultValue = "EcbWindow")]
        public string BotId { get; set; }

        [Parameter("Account Identifier", Group = "General", DefaultValue = "demo")]
        public string AccountLabel { get; set; }

        [Parameter("Show Detailed Logs", Group = "General", DefaultValue = true)]
        public bool ShowLogs { get; set; }

        // true = F3 (USD-TOP days only), false = E1 (every weekday). E1 still logs and reports the USD-TOP flag, so
        // its trades on USD-TOP days can be scored as F3.
        [Parameter("USD-TOP Days Only (F3; off = E1)", Group = "Rule", DefaultValue = true)]
        public bool UsdTopOnly { get; set; }

        [Parameter("Entry Hour (London)", Group = "Rule", DefaultValue = 11, MinValue = 0, MaxValue = 23)]
        public int EntryHourLondon { get; set; }

        [Parameter("Entry Minute (London)", Group = "Rule", DefaultValue = 0, MinValue = 0, MaxValue = 59)]
        public int EntryMinuteLondon { get; set; }

        [Parameter("Exit Hour (London)", Group = "Rule", DefaultValue = 13, MinValue = 0, MaxValue = 23)]
        public int ExitHourLondon { get; set; }

        [Parameter("Exit Minute (London)", Group = "Rule", DefaultValue = 0, MinValue = 0, MaxValue = 59)]
        public int ExitMinuteLondon { get; set; }

        // The rule sells at the 11:00 quote; one minute late cost E1 all of its HOLD net, so a day whose order cannot
        // go out within this many seconds is skipped, not chased.
        [Parameter("Entry Grace (seconds)", Group = "Rule", DefaultValue = 60, MinValue = 0, MaxValue = 300)]
        public int EntryGraceSeconds { get; set; }

        [Parameter("Selector Symbols", Group = "Rule", DefaultValue = "USDJPY,USDCHF")]
        public string SelectorSymbols { get; set; }

        [Parameter("Selector From Hour (New York, previous weekday)", Group = "Rule", DefaultValue = 18, MinValue = 0, MaxValue = 23)]
        public int SelectorFromHourNewYork { get; set; }

        [Parameter("Selector To Hour (London)", Group = "Rule", DefaultValue = 7, MinValue = 0, MaxValue = 23)]
        public int SelectorToHourLondon { get; set; }

        [Parameter("Selector Percentile", Group = "Rule", DefaultValue = 67, MinValue = 1, MaxValue = 99)]
        public double SelectorPercentile { get; set; }

        [Parameter("Selector History (weekdays)", Group = "Rule", DefaultValue = 250, MinValue = 20, MaxValue = 1000)]
        public int SelectorHistoryWeekdays { get; set; }

        [Parameter("Selector Min History (scores)", Group = "Rule", DefaultValue = 60, MinValue = 1, MaxValue = 1000)]
        public int SelectorMinHistory { get; set; }

        // The research priced minute X at the M1 bar ending at X or up to this many bars before it, so a quote counts
        // when it is less than this + 1 minutes old.
        [Parameter("Quote Max Age (M1 bars)", Group = "Rule", DefaultValue = 10, MinValue = 1, MaxValue = 60)]
        public int QuoteMaxAgeMinutes { get; set; }

        // Days not to trade besides 24/12-1/1 (always skipped), e.g. "2026-12-23".
        [Parameter("Skip Dates (yyyy-MM-dd, comma separated)", Group = "Rule", DefaultValue = "")]
        public string SkipDates { get; set; }

        [Parameter("Lots", Group = "Risk", DefaultValue = 0.01, MinValue = 0.01, MaxValue = 10.0)]
        public double Lots { get; set; }

        // Not part of the rule (it has none): a far broker stop for a dead bot. 0 = none.
        [Parameter("Broker Stop (pips, 0 = none)", Group = "Risk", DefaultValue = 100, MinValue = 0, MaxValue = 1000)]
        public double EmergencyStopPips { get; set; }

        [Parameter("Order Retry (seconds)", Group = "Risk", DefaultValue = 2, MinValue = 1, MaxValue = 60)]
        public int OrderRetrySeconds { get; set; }

        // Last line of defence after a restart or a missed exit; the window itself lasts two hours.
        [Parameter("Max Hold (minutes)", Group = "Risk", DefaultValue = 180, MinValue = 10, MaxValue = 7200)]
        public int MaxHoldMinutes { get; set; }

        [Parameter("Seed Quotes File", Group = "Data", DefaultValue = "/workspace/cBot/seeds/ecb_usd_top_seed.csv")]
        public string SeedFile { get; set; }

        // Empty = /root/ctrader_data/<BotId>_usd_top_quotes.csv (the cTrader home volume, kept across restarts).
        [Parameter("Quote Log File (empty = per bot)", Group = "Data", DefaultValue = "")]
        public string QuoteLogFile { get; set; }

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

        private TimeZoneInfo _london;
        private TimeZoneInfo _newYork;
        private string[] _selectorSymbols = new string[0];
        private readonly HashSet<DateTime> _skipDates = new HashSet<DateTime>();
        private readonly HashSet<DateTime> _daysDone = new HashSet<DateTime>();
        private readonly Dictionary<DateTime, Decision> _decisions = new Dictionary<DateTime, Decision>();
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();
        private readonly Dictionary<int, SentQuote> _closeQuotes = new Dictionary<int, SentQuote>();
        private readonly Dictionary<int, Decision> _positionDecisions = new Dictionary<int, Decision>();
        private DateTime _lastAttemptAt = DateTime.MinValue;
        private bool _orderPending;
        private DateTime _orderPendingSince;
        private DateTime _startedAt;
        private DateTime _lastTickAt = DateTime.MinValue;
        private DateTime _lastBarHandled = DateTime.MinValue;
        private DateTime _lastTickTelemetryTime = DateTime.MinValue;
        private volatile bool _isStopped;

        // Selector quotes: "SYMBOL|yyyy-MM-ddTHH:mm" (UTC) -> mid, null = known to have no quote within the max age.
        private readonly Dictionary<string, QuoteRec> _quotes = new Dictionary<string, QuoteRec>();
        private readonly Dictionary<string, LastQuote> _lastSelectorQuote = new Dictionary<string, LastQuote>();
        private readonly Dictionary<string, Bars> _fallbackBars = new Dictionary<string, Bars>();
        private string _quoteLogPath;

        private readonly HttpClient _httpClient = new HttpClient(new SocketsHttpHandler { PooledConnectionIdleTimeout = TimeSpan.FromSeconds(4) })
        {
            Timeout = TimeSpan.FromSeconds(60)
        };

        private class QuoteRec
        {
            public double? Mid;
            public string Source;   // "seed", "live", "bars"
        }

        private class LastQuote
        {
            public double Bid;
            public double Ask;
            public DateTime At;
        }

        /// <summary>A day's USD-TOP verdict: its score, the threshold from the history, how many scores it rests
        /// on, and where the quotes came from.</summary>
        private class Decision
        {
            public DateTime Day;
            public double? Score;
            public double? Threshold;
            public int HistoryCount;
            public bool UsdTop;
            public string Sources;
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
            _london = FindZone("Europe/London", "GMT Standard Time");
            _newYork = FindZone("America/New_York", "Eastern Standard Time");
            _startedAt = Server.Time;

            _selectorSymbols = (SelectorSymbols ?? "").Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                                                      .Select(s => s.Trim().ToUpperInvariant()).ToArray();
            foreach (var part in (SkipDates ?? "").Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
            {
                if (DateTime.TryParseExact(part.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var d))
                    _skipDates.Add(d.Date);
                else
                    Print($"[EcbWindow] Skip date '{part}' is not yyyy-MM-dd; ignored");
            }

            LoadQuotes(SeedFile, "seed");
            _quoteLogPath = string.IsNullOrWhiteSpace(QuoteLogFile) ? $"/root/ctrader_data/{BotId}_usd_top_quotes.csv" : QuoteLogFile.Trim();
            LoadQuotes(_quoteLogPath, "live");

            foreach (var name in _selectorSymbols)
            {
                var sym = Symbols.GetSymbol(name);
                if (sym == null)
                {
                    Print($"[EcbWindow] Selector symbol {name} not found; USD-TOP scores will be missing");
                    continue;
                }
                string captured = name;
                sym.Tick += args => OnSelectorTick(captured, sym);
            }

            Print($"[EcbWindow] Starting '{BotId}' on {SymbolName}: {(UsdTopOnly ? "F3 (USD-TOP days)" : "E1 (every weekday)")}, " +
                  $"sell {EntryHourLondon:00}:{EntryMinuteLondon:00} -> buy {ExitHourLondon:00}:{ExitMinuteLondon:00} London, " +
                  $"{Lots:F2} lots, broker stop {(EmergencyStopPips > 0 ? $"{EmergencyStopPips:F0} pips" : "none")}; " +
                  $"selector {string.Join("+", _selectorSymbols)} {SelectorFromHourNewYork:00}:00 New York -> {SelectorToHourLondon:00}:00 London, " +
                  $"p{SelectorPercentile} of {SelectorHistoryWeekdays} weekdays; {_quotes.Count} quotes loaded");

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
            CaptureDueQuotes(null);
            Evaluate();
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
            Print($"[EcbWindow] Stopped on {SymbolName}.");
            _httpClient?.Dispose();
        }
        #endregion

        #region Calendar
        /// <summary>The system's zone, or (no tz database in the container) one built from today's rules: London BST from
        /// the last Sunday of March 01:00 to the last Sunday of October 02:00 local; New York EDT from the second Sunday
        /// of March to the first Sunday of November, 02:00 local.</summary>
        private TimeZoneInfo FindZone(string ianaId, string windowsId)
        {
            foreach (var id in new[] { ianaId, windowsId })
            {
                try { return TimeZoneInfo.FindSystemTimeZoneById(id); }
                catch (Exception) { }
            }
            Print($"[EcbWindow] Time zone {ianaId} not found; using built-in DST rules");
            bool london = ianaId == "Europe/London";
            var start = london
                ? TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 1, 0, 0), 3, 5, DayOfWeek.Sunday)
                : TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 2, 0, 0), 3, 2, DayOfWeek.Sunday);
            var end = london
                ? TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 2, 0, 0), 10, 5, DayOfWeek.Sunday)
                : TimeZoneInfo.TransitionTime.CreateFloatingDateRule(new DateTime(1, 1, 1, 2, 0, 0), 11, 1, DayOfWeek.Sunday);
            var rule = TimeZoneInfo.AdjustmentRule.CreateAdjustmentRule(new DateTime(2007, 1, 1), DateTime.MaxValue.Date,
                                                                         TimeSpan.FromHours(1), start, end);
            var offset = TimeSpan.FromHours(london ? 0 : -5);
            return TimeZoneInfo.CreateCustomTimeZone(ianaId, offset, ianaId, ianaId, ianaId + " DST", new[] { rule });
        }

        private static DateTime AsUtc(DateTime t) => DateTime.SpecifyKind(t, DateTimeKind.Utc);

        /// <summary>`hour`:`minute` local time of `date` in `zone`, as UTC.</summary>
        private static DateTime LocalToUtc(DateTime date, int hour, int minute, TimeZoneInfo zone) =>
            DateTime.SpecifyKind(TimeZoneInfo.ConvertTimeToUtc(
                DateTime.SpecifyKind(date.Date.AddHours(hour).AddMinutes(minute), DateTimeKind.Unspecified), zone), DateTimeKind.Utc);

        private DateTime LondonDate(DateTime utc) => TimeZoneInfo.ConvertTimeFromUtc(AsUtc(utc), _london).Date;

        private DateTime NewYorkDate(DateTime utc) => TimeZoneInfo.ConvertTimeFromUtc(AsUtc(utc), _newYork).Date;

        private static bool IsWeekday(DateTime d) => d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday;

        private static DateTime PreviousWeekday(DateTime d)
        {
            var p = d.Date.AddDays(-1);
            while (!IsWeekday(p)) p = p.AddDays(-1);
            return p;
        }

        /// <summary>24 December to 1 January: the research's E1 and F3 skip them.</summary>
        public static bool IsChristmasWindow(DateTime d) => (d.Month == 12 && d.Day >= 24) || (d.Month == 1 && d.Day == 1);

        private bool IsTradingDay(DateTime londonDate) =>
            IsWeekday(londonDate) && !IsChristmasWindow(londonDate) && !_skipDates.Contains(londonDate.Date);

        private DateTime EntryTime(DateTime londonDate) => LocalToUtc(londonDate, EntryHourLondon, EntryMinuteLondon, _london);

        private DateTime ExitTime(DateTime londonDate) => LocalToUtc(londonDate, ExitHourLondon, ExitMinuteLondon, _london);

        private DateTime SelectorFrom(DateTime day) => LocalToUtc(PreviousWeekday(day), SelectorFromHourNewYork, 0, _newYork);

        private DateTime SelectorTo(DateTime day) => LocalToUtc(day, SelectorToHourLondon, 0, _london);
        #endregion

        #region USD-TOP selector
        private static string QuoteKey(string symbol, DateTime utc) => $"{symbol}|{utc:yyyy-MM-ddTHH:mm}";

        /// <summary>Reads "time_utc,symbol,bid,ask" rows; an empty bid/ask is a minute known to have no quote. A
        /// later file overrides an earlier one minute by minute.</summary>
        private void LoadQuotes(string path, string source)
        {
            if (string.IsNullOrWhiteSpace(path)) return;
            try
            {
                if (!System.IO.File.Exists(path))
                {
                    Print($"[EcbWindow] No {source} quote file at {path}");
                    return;
                }
                int n = 0;
                foreach (var line in System.IO.File.ReadLines(path))
                {
                    var f = line.Split(',');
                    if (f.Length < 4 || !DateTime.TryParseExact(f[0].Trim(), "yyyy-MM-ddTHH:mm", CultureInfo.InvariantCulture,
                                                                 DateTimeStyles.None, out var t))
                        continue;   // header or a broken line
                    double? mid = null;
                    if (double.TryParse(f[2], NumberStyles.Float, CultureInfo.InvariantCulture, out var bid)
                        && double.TryParse(f[3], NumberStyles.Float, CultureInfo.InvariantCulture, out var ask) && bid > 0 && ask > 0)
                        mid = (bid + ask) / 2;
                    _quotes[QuoteKey(f[1].Trim().ToUpperInvariant(), t)] = new QuoteRec { Mid = mid, Source = source };
                    n++;
                }
                Print($"[EcbWindow] Loaded {n} {source} quotes from {path}");
            }
            catch (Exception ex)
            {
                Print($"[EcbWindow] Could not read {source} quotes from {path}: {ex.Message}");
            }
        }

        private void OnSelectorTick(string name, Symbol sym)
        {
            if (_isStopped) return;
            CaptureDueQuotes(name);   // a minute this tick passes is captured with the quote before it
            _lastSelectorQuote[name] = new LastQuote { Bid = sym.Bid, Ask = sym.Ask, At = Server.Time };
        }

        /// <summary>The selector minutes around now: 18:00 New York of the last two New York weekdays and 07:00 London
        /// of the last two London weekdays.</summary>
        private IEnumerable<DateTime> SelectorMinutes(DateTime now)
        {
            var ny = NewYorkDate(now);
            var lon = LondonDate(now);
            for (int k = 0; k <= 1; k++)
            {
                if (IsWeekday(ny.AddDays(-k))) yield return LocalToUtc(ny.AddDays(-k), SelectorFromHourNewYork, 0, _newYork);
                if (IsWeekday(lon.AddDays(-k))) yield return LocalToUtc(lon.AddDays(-k), SelectorToHourLondon, 0, _london);
            }
        }

        /// <summary>Freezes the last quote before each selector minute that has passed (all symbols, or only
        /// `onlySymbol` from its own tick). Only minutes the bot watched for the whole max age are captured live; the
        /// rest come from the files or, failing that, the bars.</summary>
        private void CaptureDueQuotes(string onlySymbol)
        {
            var now = Server.Time;
            foreach (var x in SelectorMinutes(now))
            {
                if (now < x || _startedAt > QuoteWindowStart(x)) continue;
                foreach (var name in _selectorSymbols)
                {
                    if (onlySymbol != null && name != onlySymbol) continue;
                    string key = QuoteKey(name, x);
                    if (_quotes.TryGetValue(key, out var have) && have.Source == "live") continue;
                    _lastSelectorQuote.TryGetValue(name, out var q);
                    bool ok = q != null && q.At < x && q.At >= QuoteWindowStart(x);
                    _quotes[key] = new QuoteRec { Mid = ok ? (q.Bid + q.Ask) / 2 : (double?)null, Source = "live" };
                    AppendQuote(x, name, ok ? q : null);
                }
            }
        }

        /// <summary>The earliest tick that may price minute x: the start of the M1 bar QuoteMaxAgeMinutes bars before
        /// the one ending at x.</summary>
        private DateTime QuoteWindowStart(DateTime x) => x.AddMinutes(-(QuoteMaxAgeMinutes + 1));

        private void AppendQuote(DateTime x, string name, LastQuote q)
        {
            if (RunningMode != RunningMode.RealTime) return;
            try
            {
                bool fresh = !System.IO.File.Exists(_quoteLogPath);
                using (var w = new StreamWriter(_quoteLogPath, append: true))
                {
                    if (fresh) w.WriteLine("time_utc,symbol,bid,ask");
                    w.WriteLine(q == null
                        ? $"{x:yyyy-MM-ddTHH:mm},{name},,"
                        : string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-ddTHH:mm},{1},{2},{3}", x, name, q.Bid, q.Ask));
                }
                if (ShowLogs)
                    Print(q == null ? $"[EcbWindow] {name} {x:yyyy-MM-dd HH:mm} UTC: no quote in the last {QuoteMaxAgeMinutes + 1} min"
                                    : $"[EcbWindow] {name} {x:yyyy-MM-dd HH:mm} UTC: {q.Bid}/{q.Ask} (at {q.At:HH:mm:ss})");
            }
            catch (Exception ex)
            {
                Print($"[EcbWindow] Could not write {_quoteLogPath}: {ex.Message}");
            }
        }

        /// <summary>The mid of `symbol` at minute `x` (the last quote before it, at most the max age old): from the
        /// live log or the seed, else the bid close of the M15 bar ending at x. Null when there is none.</summary>
        private double? PriceAt(string symbol, DateTime x, ref string sources)
        {
            if (_quotes.TryGetValue(QuoteKey(symbol, x), out var rec))
            {
                AddSource(ref sources, rec.Source);
                return rec.Mid;
            }
            if (x > Server.Time) return null;
            if (!_fallbackBars.TryGetValue(symbol, out var bars))
            {
                bars = MarketData.GetBars(TimeFrame.Minute15, symbol);
                _fallbackBars[symbol] = bars;
            }
            int i = bars.OpenTimes.GetIndexByExactTime(x.AddMinutes(-15));
            if (i < 0) return null;
            AddSource(ref sources, "bars");
            return bars.ClosePrices[i];
        }

        private static void AddSource(ref string sources, string source)
        {
            if (sources == null) sources = source;
            else if (!sources.Split('+').Contains(source)) sources += "+" + source;
        }

        /// <summary>Mean log change of the selector symbols from 18:00 New York of the previous weekday to 07:00
        /// London on `day`; null when a quote is missing.</summary>
        private double? Score(DateTime day, ref string sources)
        {
            if (_selectorSymbols.Length == 0) return null;
            DateTime a = SelectorFrom(day), b = SelectorTo(day);
            double sum = 0;
            foreach (var name in _selectorSymbols)
            {
                double? pa = PriceAt(name, a, ref sources), pb = PriceAt(name, b, ref sources);
                if (!pa.HasValue || !pb.HasValue || pa.Value <= 0 || pb.Value <= 0) return null;
                sum += Math.Log(pb.Value / pa.Value);
            }
            return sum / _selectorSymbols.Length;
        }

        /// <summary>numpy.percentile's default (linear interpolation between closest ranks).</summary>
        public static double Percentile(List<double> values, double q)
        {
            var s = values.OrderBy(v => v).ToList();
            double pos = (s.Count - 1) * q / 100.0;
            int lo = (int)Math.Floor(pos);
            int hi = Math.Min(lo + 1, s.Count - 1);
            return s[lo] + (s[hi] - s[lo]) * (pos - lo);
        }

        /// <summary>The USD-TOP verdict for `day`, computed once its 07:00 London quotes exist and then kept.</summary>
        private Decision Decide(DateTime day)
        {
            if (_decisions.TryGetValue(day, out var known)) return known;
            string sources = null;
            var d = new Decision { Day = day, Score = Score(day, ref sources) };
            var history = new List<double>();
            var h = day;
            for (int i = 0; i < SelectorHistoryWeekdays; i++)
            {
                h = PreviousWeekday(h);
                string historySources = null;
                double? s = Score(h, ref historySources);
                if (s.HasValue) history.Add(s.Value);
                if (historySources != null) AddSourceList(ref sources, historySources);
            }
            d.HistoryCount = history.Count;
            if (d.Score.HasValue && history.Count >= SelectorMinHistory)
            {
                d.Threshold = Percentile(history, SelectorPercentile);
                d.UsdTop = d.Score.Value >= d.Threshold.Value;
            }
            d.Sources = sources ?? "none";
            _decisions[day] = d;
            Print($"[EcbWindow] {day:yyyy-MM-dd} USD-TOP {(d.UsdTop ? "yes" : "no")}: score {Bp(d.Score)} vs p{SelectorPercentile} {Bp(d.Threshold)} " +
                  $"of {d.HistoryCount} scores (quotes: {d.Sources})");
            return d;
        }

        private static void AddSourceList(ref string sources, string list)
        {
            foreach (var s in list.Split('+')) AddSource(ref sources, s);
        }

        private static string Bp(double? logChange) => logChange.HasValue ? $"{logChange.Value * 1e4:+0.00;-0.00} bp" : "n/a";
        #endregion

        #region Strategy
        private void Evaluate()
        {
            if (_isStopped) return;
            try
            {
                var now = Server.Time;
                CloseDueWindows(now);
                if (!HasFreshQuote(now)) return;

                var day = LondonDate(now);
                if (!IsTradingDay(day) || _daysDone.Contains(day)) return;
                var entry = EntryTime(day);
                if (now < entry) return;
                if (now > entry.AddSeconds(EntryGraceSeconds))
                {
                    if (!WindowAlreadyTraded(day))
                        Print($"[EcbWindow] {day:yyyy-MM-dd}: no entry within {EntryGraceSeconds} s of {EntryHourLondon:00}:{EntryMinuteLondon:00} London; day skipped");
                    _daysDone.Add(day);
                    return;
                }
                TryOpen(day);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[EcbWindow Evaluate Error] {ex.Message}");
            }
        }

        private bool HasFreshQuote(DateTime now) => (now - _lastTickAt).TotalSeconds <= MaxQuoteAgeSeconds;

        /// <summary>Closes own positions whose window ended (13:00 London of their entry day) or that are older
        /// than MaxHoldMinutes.</summary>
        private void CloseDueWindows(DateTime now)
        {
            foreach (var pos in GetBotPositions())
            {
                string reason = null;
                var exit = ExitTime(LondonDate(pos.EntryTime));
                if (pos.EntryTime < exit && now >= exit)
                    reason = $"Window exit ({ExitHourLondon:00}:{ExitMinuteLondon:00} London)";
                else if (now - pos.EntryTime >= TimeSpan.FromMinutes(MaxHoldMinutes))
                    reason = $"Max hold ({MaxHoldMinutes} min)";
                if (reason == null) continue;
                if (!HasFreshQuote(now) || !Symbol.MarketHours.IsOpened()) continue;   // closes on the first live quote
                var result = CloseWithReason(pos, reason);
                if (result == null || !result.IsSuccessful)
                    Print($"[EcbWindow] Could not close #{pos.Id} ({reason}): {(result != null ? result.Error.ToString() : "no result")}");
            }
        }

        private void TryOpen(DateTime day)
        {
            if (_orderPending)
            {
                if ((Server.Time - _orderPendingSince).TotalSeconds < 30) return;
                _orderPending = false;
            }
            if (GetBotPositions().Count > 0) return;   // one position at a time
            if (!Symbol.MarketHours.IsOpened()) return;
            if ((Server.Time - _lastAttemptAt).TotalSeconds < OrderRetrySeconds) return;
            _lastAttemptAt = Server.Time;

            if (WindowAlreadyTraded(day))
            {
                _daysDone.Add(day);
                return;
            }

            var decision = Decide(day);
            if (UsdTopOnly && !decision.UsdTop)
            {
                _daysDone.Add(day);
                return;
            }

            double volume = Math.Max(Symbol.VolumeInUnitsMin, Symbol.NormalizeVolumeInUnits(Lots * Symbol.LotSize, RoundingMode.Down));
            if (DashboardPauseBlocks($"{day:yyyy-MM-dd} entry")) return;
            var quote = new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask, SentAt = System.Diagnostics.Stopwatch.GetTimestamp() };
            double? stopPips = EmergencyStopPips > 0 ? EmergencyStopPips : (double?)null;
            _orderPending = true;
            _orderPendingSince = Server.Time;
            ExecuteMarketOrderAsync(TradeType.Sell, SymbolName, volume, null, stopPips, null, null, result =>
            {
                _orderPending = false;
                quote.LatencyMs = ElapsedMs(quote.SentAt);
                if (result != null && result.IsSuccessful && result.Position != null)
                {
                    _daysDone.Add(day);
                    _positionDecisions[result.Position.Id] = decision;
                    Print($"[EcbWindow] Opened #{result.Position.Id} Sell {volume / Symbol.LotSize:F2} lots {SymbolName} @ {result.Position.EntryPrice} " +
                          $"({RuleName(decision)}); {FillNote(TradeType.Sell, result.Position.EntryPrice, quote)}");
                    ReportPositionOpen(result.Position, EmergencyStopPips, $"ECB window short ({RuleName(decision)})", decision, quote);
                }
                else
                {
                    Print($"[EcbWindow] {day:yyyy-MM-dd}: order failed ({(result != null ? result.Error.ToString() : "no result")}) after {quote.LatencyMs:F0} ms; " +
                          $"retrying in {OrderRetrySeconds} s within the grace");
                }
            });
        }

        private string RuleName(Decision d) => UsdTopOnly ? "F3, USD-TOP day" : (d != null && d.UsdTop ? "E1, USD-TOP day" : "E1");

        /// <summary>True when this bot already sold in `day`'s window (open, or closed in History).</summary>
        private bool WindowAlreadyTraded(DateTime day)
        {
            DateTime from = EntryTime(day).AddMinutes(-1), to = ExitTime(day);
            if (GetBotPositions().Any(p => p.TradeType == TradeType.Sell && p.EntryTime >= from && p.EntryTime < to)) return true;
            return History.Any(h => h.SymbolName == SymbolName && h.TradeType == TradeType.Sell && h.EntryTime >= from && h.EntryTime < to);
        }

        /// <summary>"quote 1.17300/1.17301, slippage +0.1 pips, 212 ms": slippage in pips against the trader.</summary>
        private string FillNote(TradeType side, double fill, SentQuote quote)
        {
            double slippage = (side == TradeType.Buy ? fill - quote.Ask : quote.Bid - fill) / Symbol.PipSize;
            return $"quote {quote.Bid}/{quote.Ask}, slippage {slippage:+0.0;-0.0;0.0} pips, {quote.LatencyMs:F0} ms";
        }

        private static double ElapsedMs(long since) =>
            (System.Diagnostics.Stopwatch.GetTimestamp() - since) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;

        /// <summary>This bot's positions: every position on its symbol. One bot trades each symbol of an account and
        /// nothing is traded there by hand.</summary>
        private List<Position> GetBotPositions() => Positions.Where(p => p.SymbolName == SymbolName).ToList();

        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            var quote = new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask, SentAt = System.Diagnostics.Stopwatch.GetTimestamp() };
            var result = ClosePosition(pos);
            quote.LatencyMs = ElapsedMs(quote.SentAt);
            if (result != null && result.IsSuccessful) _closeQuotes[pos.Id] = quote;
            return result;
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
                    string reason;
                    if (args.Reason == PositionCloseReason.StopLoss)
                        reason = $"StopLoss (broker guard, {EmergencyStopPips:F0} pips)";
                    else if (args.Reason == PositionCloseReason.Closed)
                        reason = hasBotReason ? botReason : "Closed outside the bot (cTrader)";
                    else
                        reason = args.Reason.ToString();

                    _positionDecisions.Remove(pos.Id);
                    string fillNote = _closeQuotes.TryGetValue(pos.Id, out var closeQuote)
                        ? $" @ {exitPrice}; {FillNote(pos.TradeType == TradeType.Buy ? TradeType.Sell : TradeType.Buy, exitPrice, closeQuote)}" : "";
                    _closeQuotes.Remove(pos.Id);
                    Print($"[EcbWindow] Closed #{pos.Id} {pos.TradeType}: {reason}, net {pos.NetProfit:F2}{fillNote}");
                    ReportPositionClosed(pos, pos.NetProfit, reason, exitPrice, pos.Pips);
                    SendLiveTickTelemetry(force: true);
                }
                catch (Exception ex)
                {
                    if (ShowLogs) Print($"[OnPositionClosed Error] {ex.Message}");
                }
            });
        }

        private void ReportPositionOpen(Position position, double slPips, string reason, Decision decision, SentQuote quote)
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
                    sl_price = position.StopLoss,
                    tp_price = position.TakeProfit,
                    sl_pips = Math.Round(slPips, 1),
                    tp_pips = 0.0,
                    reason,
                    entry_indicators = JsonSerializer.Serialize(new
                    {
                        rule = UsdTopOnly ? "F3" : "E1",
                        usd_top = decision?.UsdTop ?? false,
                        score_bp = decision?.Score.HasValue == true ? (double?)Math.Round(decision.Score.Value * 1e4, 2) : null,
                        threshold_bp = decision?.Threshold.HasValue == true ? (double?)Math.Round(decision.Threshold.Value * 1e4, 2) : null,
                        history = decision?.HistoryCount ?? 0,
                        quotes = decision?.Sources,
                        quote_bid = quote.Bid,
                        quote_ask = quote.Ask,
                        latency_ms = Math.Round(quote.LatencyMs, 0),
                        spread = Math.Round((quote.Ask - quote.Bid) / Symbol.PipSize, 2)
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
                    sl_pips = Math.Round(EmergencyStopPips, 1),
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
