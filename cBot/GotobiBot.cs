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
    /// effect). An instance holds at most one position at a time and never longer than one leg (7 h at most).
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

        // Last line of defence after a restart or a missed exit: legs close at their planned time; anything the bot
        // owns that is older than this is closed too. Far inside the 5-day limit.
        [Parameter("Max Hold (hours)", Group = "Risk", DefaultValue = 12, MinValue = 1, MaxValue = 120)]
        public int MaxHoldHours { get; set; }

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

        private AverageTrueRange _atr;
        private readonly HashSet<DateTime> _skipDates = new HashSet<DateTime>();
        private readonly HashSet<string> _legsDone = new HashSet<string>();
        private readonly Dictionary<string, DateTime> _lastAttemptAt = new Dictionary<string, DateTime>();
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();
        private readonly Dictionary<int, double> _initialSlPips = new Dictionary<int, double>();
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

            _atr = Indicators.AverageTrueRange(MarketData.GetBars(TimeFrame.Hour), AtrPeriod, MovingAverageType.Simple);

            foreach (var part in (SkipDates ?? "").Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
            {
                if (DateTime.TryParseExact(part.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var d))
                    _skipDates.Add(d.Date);
                else
                    Print($"[Gotobi] Skip date '{part}' is not yyyy-MM-dd; ignored");
            }

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

        private static string LegTag(Leg leg, DateTime day) => $"{(leg == Leg.Long ? LongTag : ShortTag)} {day:yyyy-MM-dd}";

        private static bool TryParseLegTag(string comment, out Leg leg, out DateTime day)
        {
            leg = Leg.Long;
            day = DateTime.MinValue;
            if (string.IsNullOrEmpty(comment)) return false;
            var parts = comment.Split(' ');
            if (parts.Length != 2) return false;
            if (parts[0] == LongTag) leg = Leg.Long;
            else if (parts[0] == ShortTag) leg = Leg.Short;
            else return false;
            return DateTime.TryParseExact(parts[1], "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out day);
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
                CloseDueLegs(now);

                // Long leg for tomorrow's gotobi day: from 18:00 UTC today (03:00 Tokyo tomorrow) to the latest entry.
                var tomorrow = now.Date.AddDays(1);
                if (TradeLong && IsTradingDay(tomorrow) && now >= LongEntryTime(tomorrow) && now <= LongEntryLatest(tomorrow)
                    && now < FixTime(tomorrow))
                    TryOpenLeg(Leg.Long, tomorrow);

                // Short leg at today's fix, only within the grace minutes after it.
                var today = now.Date;
                if (TradeShort && IsTradingDay(today) && now >= FixTime(today)
                    && now <= FixTime(today).AddMinutes(ShortEntryGraceMinutes) && now < ShortExitTime(today))
                    TryOpenLeg(Leg.Short, today);
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
                string reason = null;
                if (TryParseLegTag(pos.Comment, out var leg, out var day))
                {
                    if (leg == Leg.Long && now >= FixTime(day)) reason = "Fix exit (09:55 Tokyo)";
                    else if (leg == Leg.Short && now >= ShortExitTime(day)) reason = "Session exit (11:55 Tokyo)";
                }
                if (reason == null && now - pos.EntryTime >= TimeSpan.FromHours(MaxHoldHours))
                    reason = $"Max hold ({MaxHoldHours} h)";
                if (reason == null) continue;

                var result = CloseWithReason(pos, reason);
                if (result == null || !result.IsSuccessful)
                    Print($"[Gotobi] Could not close #{pos.Id} ({reason}): {(result != null ? result.Error.ToString() : "no result")}");
            }
        }

        /// <summary>One attempt per leg and gotobi day, including after a stop-out; retried every 30 s while the
        /// spread is too wide or the order fails, until the leg's window closes.</summary>
        private void TryOpenLeg(Leg leg, DateTime day)
        {
            string tag = LegTag(leg, day);
            if (_legsDone.Contains(tag)) return;
            if (GetBotPositions().Count > 0) return;   // one position at a time; the long closes before the short opens
            // A Monday gotobi day's long window opens on Sunday 18:00 UTC, before the FX week does; wait for the
            // first quote after the open (as the research did) instead of filling on Friday's stale price. The
            // schedule alone is not enough: a backtest's can say "open" an hour before the first tick, so Evaluate()
            // also waits for a fresh quote (HasFreshQuote).
            if (!Symbol.MarketHours.IsOpened()) return;

            if (_lastAttemptAt.TryGetValue(tag, out var last) && (Server.Time - last).TotalSeconds < 30) return;
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
            double volume = VolumeForRisk(stopPips);
            if (volume <= 0)
            {
                Print($"[Gotobi] {tag}: the minimum lot would risk more than {MaxMinLotRiskMultiple} x ${RiskPerTradeMoney:F2} at a {stopPips:F1}-pip stop; leg skipped");
                _legsDone.Add(tag);
                return;
            }

            var tradeType = leg == Leg.Long ? TradeType.Buy : TradeType.Sell;
            if (DashboardPauseBlocks($"{tag} entry")) return;
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, BotId, stopPips, null, tag);
            if (result != null && result.IsSuccessful && result.Position != null)
            {
                _legsDone.Add(tag);
                _initialSlPips[result.Position.Id] = stopPips;
                string reason = leg == Leg.Long ? "Gotobi long into the 09:55 Tokyo fix" : "Gotobi short after the 09:55 Tokyo fix";
                Print($"[Gotobi] Opened #{result.Position.Id} {tradeType} {volume / Symbol.LotSize:F2} lots {SymbolName} @ {result.Position.EntryPrice}, " +
                      $"stop {stopPips:F1} pips ({tag})");
                ReportPositionOpen(result.Position, stopPips, reason);
            }
            else
            {
                Print($"[Gotobi] {tag}: order failed ({(result != null ? result.Error.ToString() : "no result")}); retrying in 30 s");
            }
        }

        /// <summary>True when this bot already opened `tag` on this symbol: still open, or closed (History).</summary>
        private bool LegAlreadyTraded(string tag)
        {
            if (GetBotPositions().Any(p => p.Comment == tag)) return true;
            return History.Any(h => h.Label == BotId && h.SymbolName == SymbolName && h.Comment == tag);
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

        private List<Position> GetBotPositions()
        {
            return Positions.FindAll(BotId, SymbolName).ToList();
        }

        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            return ClosePosition(pos);
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
                        tp_pnl = (double?)null,
                        label = p.Label
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
                    if (pos == null || pos.Label != BotId || pos.SymbolName != SymbolName) return;

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
                        reason = $"StopLoss ({StopAtrMultiplier} x ATR{AtrPeriod} H1)";
                    else if (args.Reason == PositionCloseReason.Closed)
                        reason = hasBotReason ? botReason : "Closed outside the bot (cTrader)";
                    else
                        reason = args.Reason.ToString();

                    Print($"[Gotobi] Closed #{pos.Id} {pos.TradeType} {pos.Comment}: {reason}, net {pos.NetProfit:F2}");
                    ReportPositionClosed(pos, pos.NetProfit, reason, exitPrice, pos.Pips);
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
                    sl_price = position.StopLoss,
                    tp_price = position.TakeProfit,
                    sl_pips = Math.Round(slPips, 1),
                    tp_pips = 0.0,
                    reason,
                    entry_indicators = JsonSerializer.Serialize(new
                    {
                        leg = position.Comment,
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
                    sl_price = position.StopLoss,
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
