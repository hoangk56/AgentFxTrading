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
    /// Crypto Donchian breakout on H4 (research C1, research/results/portfolio/swing_lab_v2_2026-09-27.md).
    ///
    /// On an H4 close above the prior 55-bar high the bot buys (below the prior 55-bar low it sells). Every
    /// qualifying bar is an entry, so a breakout that keeps going stacks up to 3 positions. A position leaves on the
    /// first of: an H4 close below the prior 20-bar low (shorts: above the prior 20-bar high), its stop at 3 x ATR20(H4)
    /// from the fill, or 5 days after entry. Crypto keeps trending at this horizon where indices, metals, energies and
    /// FX do not (time-series momentum); the rule was the only trend rule of the research that worked, and only there.
    ///
    /// Status: forward test only. It passed 2018-2021 (R +0.276) and 2022-2024 (R +0.227) but not its 2025-2026 holdout
    /// (R -0.025; BTCUSD -0.151, ETHUSD +0.123), so run it small, on demo first, with the kill switch in mind.
    ///
    /// The H4 bars are UTC-aligned (00:00, 04:00, ... UTC) as in the research, built by the bot from H1 bars: the
    /// broker's own H4 bars start at 21/22:00 UTC (its server day), and the research's result moved with the bar phase
    /// (2025-26 R -0.025 at 0 h, +0.117 at 1 h, +0.077 at 2 h, +0.094 at 3 h), so the registered phase is kept.
    ///
    /// Run one instance per symbol: BTCUSD, ETHUSD. Sizing never reads the account: a trade risks `RiskPerTradeMoney`
    /// x a breakout-strength multiplier in [0.5, 2] (the breakout distance in ATR against the median of the earlier
    /// breakouts on this symbol) at its stop, so the lot follows volatility around that default risk, not equity.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class CryptoDonchianBot : Robot
    {
        #region Parameters
        [Parameter("Bot ID", Group = "General", DefaultValue = "CryptoDonchian")]
        public string BotId { get; set; }

        [Parameter("Account Identifier", Group = "General", DefaultValue = "demo")]
        public string AccountLabel { get; set; }

        [Parameter("Show Detailed Logs", Group = "General", DefaultValue = true)]
        public bool ShowLogs { get; set; }

        [Parameter("Entry Channel (H4 bars)", Group = "Strategy (H4)", DefaultValue = 55, MinValue = 5, MaxValue = 500)]
        public int EntryPeriod { get; set; }

        [Parameter("Exit Channel (H4 bars)", Group = "Strategy (H4)", DefaultValue = 20, MinValue = 2, MaxValue = 500)]
        public int ExitPeriod { get; set; }

        [Parameter("Trade Short Breakouts", Group = "Strategy (H4)", DefaultValue = true)]
        public bool TradeShorts { get; set; }

        // The research filled at the first M1 open after the bar close. A fill this much later still counts (a wide
        // spread, a restart, a failed order); after it the signal is dropped. Entries delayed a whole bar kept most of
        // the edge (R +0.26 vs +0.28 in 2018-2021), so this is a safety net, not a tuned value.
        [Parameter("Entry Window (minutes after the bar close)", Group = "Strategy (H4)", DefaultValue = 30, MinValue = 1, MaxValue = 239)]
        public int EntryWindowMinutes { get; set; }

        [Parameter("Max Open Positions", Group = "Strategy (H4)", DefaultValue = 3, MinValue = 1, MaxValue = 3)]
        public int MaxPositions { get; set; }

        // The research's $100. Much less cannot size BTCUSD: its minimum 0.01 BTC already risks ~$30-40 at the stop.
        [Parameter("Default Risk per Trade ($)", Group = "Risk", DefaultValue = 100.0, MinValue = 1.0)]
        public double RiskPerTradeMoney { get; set; }

        [Parameter("Stop (x ATR of H4)", Group = "Risk", DefaultValue = 3.0, MinValue = 0.5, MaxValue = 10.0)]
        public double StopAtrMultiplier { get; set; }

        [Parameter("ATR Period (H4, simple)", Group = "Risk", DefaultValue = 20, MinValue = 2, MaxValue = 200)]
        public int AtrPeriod { get; set; }

        // Off: every trade risks the default. On: default x clip(breakout / median breakout, 0.5, 2), the research's.
        [Parameter("Scale Lot by Breakout Strength", Group = "Risk", DefaultValue = true)]
        public bool ScaleByStrength { get; set; }

        // H4 bars loaded at start for the breakout median (5000 bars ~ 2.3 years of crypto, ~230 breakouts). The
        // median hardly moves after a year: the research's expanding median and a trailing 100-breakout one gave the
        // same R in every era.
        [Parameter("Strength History (H4 bars)", Group = "Risk", DefaultValue = 5000, MinValue = 100, MaxValue = 50000)]
        public int StrengthHistoryBars { get; set; }

        // When the risk buys less than the minimum lot, trade the minimum only if it risks at most this multiple of
        // that risk; otherwise skip the signal.
        [Parameter("Max Min-Lot Risk (x trade risk)", Group = "Risk", DefaultValue = 1.5, MinValue = 1.0, MaxValue = 5.0)]
        public double MaxMinLotRiskMultiple { get; set; }

        [Parameter("Max Lots per Trade", Group = "Risk", DefaultValue = 5.0, MinValue = 0.01)]
        public double MaxLotsPerTrade { get; set; }

        // Crypto pips differ per symbol and broker, so the spread cap is a share of the stop distance. At IC in
        // 2024-2026 the spread at entry was 0.4-2.6 % of the stop (99th percentile under 6 %); ETHUSD in 2018-2020
        // quoted 15-35 %, which this cap skips (set 1.0 to reproduce the research there).
        [Parameter("Max Spread (share of the stop)", Group = "Risk", DefaultValue = 0.10, MinValue = 0.001, MaxValue = 1.0)]
        public double MaxSpreadStopFraction { get; set; }

        // The brief's 5-day limit. The research closed at the last minute before 5 days; so does the bot.
        [Parameter("Max Hold (hours)", Group = "Risk", DefaultValue = 120, MinValue = 4, MaxValue = 120)]
        public int MaxHoldHours { get; set; }

        // Stops new entries when the mean R of this bot's last N closed trades is below the threshold (R = net profit
        // / the $ risk at entry, read from the position comment). It does not resume on its own: raise N, lower the
        // threshold or set 0 to trade again. Off by default: on 2018-2026 a 100-trade switch would have stopped ETHUSD
        // in January 2020 and missed +$12,000 after it (research/results/portfolio/crypto_donchian_cbot_2026-09-27.md).
        [Parameter("Kill Switch: Trades (0 = off)", Group = "Kill Switch", DefaultValue = 0, MinValue = 0, MaxValue = 1000)]
        public int KillSwitchTrades { get; set; }

        [Parameter("Kill Switch: Min Mean R", Group = "Kill Switch", DefaultValue = 0.0, MinValue = -5.0, MaxValue = 5.0)]
        public double KillSwitchMinR { get; set; }

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
        private const string LongTag = "DONCH-L";
        private const string ShortTag = "DONCH-S";
        private const string ManualCloseReason = "Manual close (dashboard)";
        // research/swing/swing.py: SCALE_MIN, SCALE_MAX, SCALE_MIN_HISTORY.
        private const double ScaleMin = 0.5;
        private const double ScaleMax = 2.0;
        private const int ScaleMinHistory = 10;

        private class PendingEntry
        {
            public int Side;
            public DateTime BarTime;
            public string Tag;
            public double Level;        // the broken channel edge
            public double Atr;
            public double Strength;     // breakout distance in ATR
            public double Median;       // median strength of the earlier breakouts (NaN = too few)
            public double Scale;
            public DateTime Deadline;
        }

        // UTC H4 bars aggregated from H1, closed bars only. _barRevealed[i] = open time of the first H1 bar after bar
        // i, i.e. when the bot learned that bar i had closed (its signal is filled from then, as the research's
        // "next M1 open").
        private Bars _h1;
        private readonly List<DateTime> _barTime = new List<DateTime>();
        private readonly List<DateTime> _barRevealed = new List<DateTime>();
        private readonly List<double> _barHigh = new List<double>();
        private readonly List<double> _barLow = new List<double>();
        private readonly List<double> _barClose = new List<double>();
        private int _nextH1;
        private bool _hasOpenBar;
        private DateTime _openBarTime;
        private double _openBarHigh, _openBarLow, _openBarClose;
        private PendingEntry _pending;
        private DateTime _lastClosedBarTime = DateTime.MinValue;
        private DateTime _scannedThrough = DateTime.MinValue;
        private readonly List<double> _strengths = new List<double>();
        private readonly HashSet<string> _entriesDone = new HashSet<string>();
        private readonly Dictionary<string, DateTime> _lastAttemptAt = new Dictionary<string, DateTime>();
        private readonly Dictionary<int, string> _dueExits = new Dictionary<int, string>();
        private readonly Dictionary<int, DateTime> _lastCloseAttemptAt = new Dictionary<int, DateTime>();
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();
        private readonly Dictionary<int, double> _initialSlPips = new Dictionary<int, double>();
        private bool _killed;
        // Evaluate() also runs from the 1 s timer, which fires without ticks. During a weekend break Symbol.Bid/Ask
        // still hold the last quote before it, so a spread check, an order or a close would use a stale price
        // (GotobiBot backtests #366-#374). Nothing trades until a quote at most MaxQuoteAgeSeconds old has arrived.
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
            Print($"[Donchian] Starting '{BotId}' on {SymbolName}: H4 close beyond the prior {EntryPeriod}-bar channel " +
                  $"(shorts {(TradeShorts ? "on" : "off")}), exit beyond the prior {ExitPeriod}-bar channel, stop {StopAtrMultiplier} x ATR{AtrPeriod}(H4), " +
                  $"max {MaxHoldHours} h, cap {MaxPositions}, risk ${RiskPerTradeMoney:F2}{(ScaleByStrength ? " x breakout strength" : "")}");

            _h1 = MarketData.GetBars(TimeFrame.Hour);
            try
            {
                for (int i = 0; i < 400 && _h1.Count < 4 * StrengthHistoryBars; i++)
                    if (_h1.LoadMoreHistory() <= 0) break;
            }
            catch (Exception ex)
            {
                Print($"[Donchian] Could not load more H1 history: {ex.Message}");
            }
            SyncH4Bars();
            Print($"[Donchian] {_barTime.Count} UTC H4 bars from {(_barTime.Count > 0 ? _barTime[0].ToString("yyyy-MM-dd HH:mm") : "-")} ({_h1.Count} H1 bars)");

            Positions.Closed += OnPositionClosed;
            RefreshKillSwitch();
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
            // Positions keep their stop; a restart closes any whose exit bar or 5-day limit has passed meanwhile.
            _isStopped = true;
            StopCommandPoll();
            Positions.Closed -= OnPositionClosed;
            Print($"[Donchian] Stopped on {SymbolName}.");
            _httpClient?.Dispose();
        }
        #endregion

        #region Channel
        /// <summary>Start of the UTC 4-hour bucket holding `t` (00:00, 04:00, ... 20:00), research/swing/swing.H4.</summary>
        public static DateTime H4BucketStart(DateTime t) => t.Date.AddHours(t.Hour / 4 * 4);

        /// <summary>Folds newly closed H1 bars into UTC H4 bars. A bar closes once an H1 bar of a later bucket exists;
        /// the forming H1 bar only reveals that, its prices are not used until it closes.</summary>
        private void SyncH4Bars()
        {
            int forming = _h1.Count - 1;
            for (; _nextH1 < forming; _nextH1++)
            {
                DateTime start = H4BucketStart(_h1.OpenTimes[_nextH1]);
                if (_hasOpenBar && start != _openBarTime) CloseOpenBar(_h1.OpenTimes[_nextH1]);
                if (!_hasOpenBar)
                {
                    _hasOpenBar = true;
                    _openBarTime = start;
                    _openBarHigh = _h1.HighPrices[_nextH1];
                    _openBarLow = _h1.LowPrices[_nextH1];
                }
                else
                {
                    _openBarHigh = Math.Max(_openBarHigh, _h1.HighPrices[_nextH1]);
                    _openBarLow = Math.Min(_openBarLow, _h1.LowPrices[_nextH1]);
                }
                _openBarClose = _h1.ClosePrices[_nextH1];
            }
            if (_hasOpenBar && forming >= 0 && H4BucketStart(_h1.OpenTimes[forming]) != _openBarTime)
                CloseOpenBar(_h1.OpenTimes[forming]);
        }

        private void CloseOpenBar(DateTime revealedAt)
        {
            _barTime.Add(_openBarTime);
            _barRevealed.Add(revealedAt);
            _barHigh.Add(_openBarHigh);
            _barLow.Add(_openBarLow);
            _barClose.Add(_openBarClose);
            _hasOpenBar = false;
        }

        /// <summary>SMA of the true range over the AtrPeriod bars ending at bar i, bar i included
        /// (research/indicators.atr_sma = AverageTrueRange(n, Simple)). NaN before enough bars.</summary>
        private double Atr(int i)
        {
            if (i < AtrPeriod) return double.NaN;
            double sum = 0;
            for (int j = i - AtrPeriod + 1; j <= i; j++)
            {
                double prevClose = _barClose[j - 1];
                sum += Math.Max(_barHigh[j], prevClose) - Math.Min(_barLow[j], prevClose);
            }
            return sum / AtrPeriod;
        }

        /// <summary>max(High[i-n .. i-1]): the channel before bar i (research/indicators.prior_max).</summary>
        private double PriorHigh(int i, int n)
        {
            double v = double.MinValue;
            for (int j = i - n; j < i; j++) v = Math.Max(v, _barHigh[j]);
            return v;
        }

        /// <summary>min(Low[i-n .. i-1]) (research/indicators.prior_min).</summary>
        private double PriorLow(int i, int n)
        {
            double v = double.MaxValue;
            for (int j = i - n; j < i; j++) v = Math.Min(v, _barLow[j]);
            return v;
        }

        /// <summary>Entry signal of closed bar i (research/swing/swing_rules.donchian): +1 on a close above the prior
        /// EntryPeriod-bar high, -1 on a close below the prior low (with TradeShorts), else 0. Strength = the
        /// breakout's distance past the channel in ATR.</summary>
        private int EntrySignal(int i, out double level, out double atr, out double strength)
        {
            level = double.NaN;
            strength = 0;
            atr = Atr(i);
            if (i < EntryPeriod || double.IsNaN(atr) || atr <= 0) return 0;
            double close = _barClose[i];
            double hh = PriorHigh(i, EntryPeriod);
            if (close > hh)
            {
                level = hh;
                strength = (close - hh) / atr + 1e-9;
                return 1;
            }
            if (!TradeShorts) return 0;
            double ll = PriorLow(i, EntryPeriod);
            if (close < ll)
            {
                level = ll;
                strength = (ll - close) / atr + 1e-9;
                return -1;
            }
            return 0;
        }

        /// <summary>Exit signal of closed bar i for a position on `side`: a close below the prior ExitPeriod-bar low
        /// (longs) or above the prior high (shorts).</summary>
        private bool ExitSignal(int i, int side)
        {
            if (i < ExitPeriod) return false;
            double close = _barClose[i];
            return side > 0 ? close < PriorLow(i, ExitPeriod) : close > PriorHigh(i, ExitPeriod);
        }

        private static double Median(List<double> values)
        {
            var s = values.OrderBy(v => v).ToList();
            int n = s.Count;
            return n % 2 == 1 ? s[n / 2] : (s[n / 2 - 1] + s[n / 2]) / 2.0;
        }

        /// <summary>research/swing/swing._scale: strength / median of this symbol's earlier breakouts, clipped to
        /// [0.5, 2]; 1 until there are ScaleMinHistory of them.</summary>
        private double ScaleFor(double strength, out double median)
        {
            median = _strengths.Count >= ScaleMinHistory ? Median(_strengths) : double.NaN;
            if (!ScaleByStrength || double.IsNaN(median) || median <= 0) return 1.0;
            return Math.Max(ScaleMin, Math.Min(ScaleMax, strength / median));
        }

        private static string EntryTag(int side, DateTime barTime) =>
            $"{(side > 0 ? LongTag : ShortTag)} {barTime.ToString("yyyy-MM-ddTHH:mm", CultureInfo.InvariantCulture)}";

        /// <summary>Position comment: "DONCH-L 2026-09-27T04:00 risk=87.50" = side, signal bar, $ risk at the stop.</summary>
        private static bool TryParseComment(string comment, out int side, out double riskMoney)
        {
            side = 0;
            riskMoney = double.NaN;
            if (string.IsNullOrEmpty(comment)) return false;
            var parts = comment.Split(' ');
            if (parts.Length < 2) return false;
            if (parts[0] == LongTag) side = 1;
            else if (parts[0] == ShortTag) side = -1;
            else return false;
            if (parts.Length >= 3 && parts[2].StartsWith("risk="))
                double.TryParse(parts[2].Substring(5), NumberStyles.Float, CultureInfo.InvariantCulture, out riskMoney);
            return true;
        }
        #endregion

        #region Strategy
        private void Evaluate()
        {
            if (_isStopped) return;
            try
            {
                var now = Server.Time;
                HandleClosedBars();
                if (!HasFreshQuote(now)) return;   // no quote since the last break
                CloseDuePositions(now);             // exits first: a short breakout also closes the longs
                TryOpenPending(now);
            }
            catch (Exception ex)
            {
                if (ShowLogs) Print($"[Donchian Evaluate Error] {ex.Message}");
            }
        }

        private bool HasFreshQuote(DateTime now) => (now - _lastTickAt).TotalSeconds <= MaxQuoteAgeSeconds;

        /// <summary>Once per closed H4 bar (and once at start): records the breakouts up to it for the strength
        /// median, marks own positions whose exit bar has closed since their entry, and queues the bar's entry.</summary>
        private void HandleClosedBars()
        {
            SyncH4Bars();
            int last = _barTime.Count - 1;
            if (last < 1) return;
            DateTime lastTime = _barTime[last];
            if (lastTime == _lastClosedBarTime) return;
            _lastClosedBarTime = lastTime;

            int first = last;
            while (first > 0 && _barTime[first - 1] > _scannedThrough) first--;
            for (int i = first; i <= last; i++)
            {
                int side = EntrySignal(i, out double level, out double atr, out double strength);
                // At start the last closed bar may be hours old; its entry is only taken inside the window.
                if (side != 0 && i == last && Server.Time <= _barRevealed[i].AddMinutes(EntryWindowMinutes))
                {
                    double scale = ScaleFor(strength, out double median);
                    _pending = new PendingEntry
                    {
                        Side = side, BarTime = _barTime[i], Tag = EntryTag(side, _barTime[i]), Level = level,
                        Atr = atr, Strength = strength, Median = median, Scale = scale,
                        Deadline = _barRevealed[i].AddMinutes(EntryWindowMinutes)
                    };
                    if (ShowLogs)
                        Print($"[Donchian] {_pending.Tag}: close {_barClose[i]} {(side > 0 ? ">" : "<")} {EntryPeriod}-bar {(side > 0 ? "high" : "low")} {level}, " +
                              $"strength {strength:F2} ATR (median {median:F2}) -> {scale:F2} x risk");
                }
                if (side != 0) _strengths.Add(strength);
                _scannedThrough = _barTime[i];
            }

            MarkSignalExits(last);
        }

        /// <summary>An own position exits when any H4 bar that closed after its entry closed beyond the exit
        /// channel. Scanning every such bar (at most MaxHoldHours / 4) makes a restart catch exits it slept through.</summary>
        private void MarkSignalExits(int last)
        {
            foreach (var pos in GetBotPositions())
            {
                if (_dueExits.ContainsKey(pos.Id)) continue;
                int side = pos.TradeType == TradeType.Buy ? 1 : -1;
                for (int j = last; j >= 1 && _barRevealed[j] > pos.EntryTime; j--)
                {
                    if (!ExitSignal(j, side)) continue;
                    _dueExits[pos.Id] = side > 0
                        ? $"Donchian exit (H4 close below the {ExitPeriod}-bar low)"
                        : $"Donchian exit (H4 close above the {ExitPeriod}-bar high)";
                    break;
                }
            }
        }

        private TimeSpan HoldLimit => TimeSpan.FromHours(MaxHoldHours) - TimeSpan.FromMinutes(1);

        // How long before a market close the bot checks whether a position's hold limit falls inside the break.
        private const double PreCloseMinutes = 5;

        /// <summary>True when the market closes within PreCloseMinutes and does not reopen before `deadline`: a
        /// position due in the break must go now or it would be held past 5 days (the research closed at the last
        /// minute before the deadline). Uses the symbol's trading sessions; a backtest applies today's sessions to
        /// every year, so it cannot see the weekend closures crypto had until April 2024.</summary>
        private bool ClosedThrough(DateTime now, DateTime deadline)
        {
            var hours = Symbol.MarketHours;
            if (!hours.IsOpened()) return false;
            DateTime closeAt = now + hours.TimeTillClose();
            if (closeAt - now > TimeSpan.FromMinutes(PreCloseMinutes) || closeAt >= deadline) return false;
            for (DateTime t = closeAt.AddMinutes(1); t < deadline; t = t.AddMinutes(10))
                if (hours.IsOpened(t)) return false;
            return !hours.IsOpened(deadline);
        }

        /// <summary>Closes own positions with a due exit signal, any held for HoldLimit (5 days less a minute), and
        /// any whose limit falls in the market break that is about to start.</summary>
        private void CloseDuePositions(DateTime now)
        {
            foreach (var pos in GetBotPositions())
            {
                if (!_dueExits.TryGetValue(pos.Id, out var reason))
                {
                    DateTime deadline = pos.EntryTime + HoldLimit;
                    if (now >= deadline) reason = $"Max hold ({MaxHoldHours} h)";
                    else if (ClosedThrough(now, deadline)) reason = $"Max hold ({MaxHoldHours} h falls in the market break)";
                    else continue;
                }
                if (_lastCloseAttemptAt.TryGetValue(pos.Id, out var last) && (now - last).TotalSeconds < 10) continue;
                _lastCloseAttemptAt[pos.Id] = now;

                var result = CloseWithReason(pos, reason);
                if (result == null || !result.IsSuccessful)
                    Print($"[Donchian] Could not close #{pos.Id} ({reason}): {(result != null ? result.Error.ToString() : "no result")}");
            }
        }

        /// <summary>One attempt per signal bar, including after a stop-out; retried every 30 s while the spread is
        /// too wide or the order fails, until the entry window closes.</summary>
        private void TryOpenPending(DateTime now)
        {
            var p = _pending;
            if (p == null) return;
            if (now > p.Deadline)
            {
                if (!_entriesDone.Contains(p.Tag) && !EntryAlreadyTraded(p.Tag))
                    Print($"[Donchian] {p.Tag}: not filled within {EntryWindowMinutes} min of the bar close; dropped");
                _pending = null;
                return;
            }
            if (_entriesDone.Contains(p.Tag)) return;
            if (!Symbol.MarketHours.IsOpened()) return;

            if (_lastAttemptAt.TryGetValue(p.Tag, out var last) && (now - last).TotalSeconds < 30) return;
            _lastAttemptAt[p.Tag] = now;

            if (EntryAlreadyTraded(p.Tag))
            {
                _entriesDone.Add(p.Tag);
                return;
            }
            if (_killed)
            {
                Print($"[Donchian] {p.Tag}: kill switch on (mean R of the last {KillSwitchTrades} trades < {KillSwitchMinR}); skipped");
                _entriesDone.Add(p.Tag);
                return;
            }

            var own = GetBotPositions();
            if (own.Count >= MaxPositions)
            {
                // A due exit frees a slot at the same bar close (research: close before open); wait for it.
                if (own.Any(pos => _dueExits.ContainsKey(pos.Id))) return;
                if (ShowLogs) Print($"[Donchian] {p.Tag}: {own.Count} positions open (cap {MaxPositions}); skipped");
                _entriesDone.Add(p.Tag);
                return;
            }

            double stopDistance = StopAtrMultiplier * p.Atr;
            double spread = Symbol.Ask - Symbol.Bid;
            if (spread > MaxSpreadStopFraction * stopDistance)
            {
                if ((now - _lastSpreadLogAt).TotalSeconds >= 60)
                {
                    _lastSpreadLogAt = now;
                    Print($"[Donchian] {p.Tag}: spread {spread} > {MaxSpreadStopFraction:P1} of the {stopDistance:F2} stop; waiting");
                }
                return;
            }

            double stopPips = stopDistance / Symbol.PipSize;
            double riskMoney = RiskPerTradeMoney * p.Scale;
            double volume = VolumeForRisk(stopPips, riskMoney);
            if (volume <= 0)
            {
                Print($"[Donchian] {p.Tag}: the minimum lot would risk more than {MaxMinLotRiskMultiple} x ${riskMoney:F2} at a {stopPips:F1}-pip stop; skipped");
                _entriesDone.Add(p.Tag);
                return;
            }

            if (DashboardPauseBlocks($"{p.Tag} entry")) return;
            var tradeType = p.Side > 0 ? TradeType.Buy : TradeType.Sell;
            double bookedRisk = volume * stopPips * Symbol.PipValue;
            string comment = $"{p.Tag} risk={bookedRisk.ToString("F2", CultureInfo.InvariantCulture)}";
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, BotId, stopPips, null, comment);
            if (result != null && result.IsSuccessful && result.Position != null)
            {
                _entriesDone.Add(p.Tag);
                _initialSlPips[result.Position.Id] = stopPips;
                string reason = p.Side > 0
                    ? $"Donchian breakout: H4 close above the {EntryPeriod}-bar high"
                    : $"Donchian breakout: H4 close below the {EntryPeriod}-bar low";
                Print($"[Donchian] Opened #{result.Position.Id} {tradeType} {volume / Symbol.LotSize:F2} lots {SymbolName} @ {result.Position.EntryPrice}, " +
                      $"stop {stopDistance:F2} ({p.Tag}, {p.Scale:F2} x risk, ${bookedRisk:F2})");
                ReportPositionOpen(result.Position, stopPips, reason, p);
            }
            else
            {
                Print($"[Donchian] {p.Tag}: order failed ({(result != null ? result.Error.ToString() : "no result")}); retrying in 30 s");
            }
        }

        /// <summary>True when this bot already opened the signal bar `tag` on this symbol: still open, or closed.</summary>
        private bool EntryAlreadyTraded(string tag)
        {
            string prefix = tag + " ";
            if (GetBotPositions().Any(pos => pos.Comment != null && (pos.Comment == tag || pos.Comment.StartsWith(prefix)))) return true;
            return History.Any(h => h.Label == BotId && h.SymbolName == SymbolName && h.Comment != null
                                    && (h.Comment == tag || h.Comment.StartsWith(prefix)));
        }

        /// <summary>Units risking `riskMoney` at `stopPips`, rounded down to the volume step and capped at
        /// MaxLotsPerTrade. 0 when even the minimum lot would risk more than MaxMinLotRiskMultiple x that risk.</summary>
        private double VolumeForRisk(double stopPips, double riskMoney)
        {
            double riskPerUnit = stopPips * Symbol.PipValue;
            if (riskPerUnit <= 0) return 0;
            double units = Symbol.NormalizeVolumeInUnits(riskMoney / riskPerUnit, RoundingMode.Down);
            units = Math.Min(units, Symbol.NormalizeVolumeInUnits(MaxLotsPerTrade * Symbol.LotSize, RoundingMode.Down));
            if (units < Symbol.VolumeInUnitsMin)
            {
                double minRisk = Symbol.VolumeInUnitsMin * riskPerUnit;
                return minRisk <= riskMoney * MaxMinLotRiskMultiple ? Symbol.VolumeInUnitsMin : 0;
            }
            return units;
        }

        /// <summary>Mean R of this bot's last KillSwitchTrades closed trades (History; R = net / $ risk in the
        /// comment) against KillSwitchMinR. Logged when it changes.</summary>
        private void RefreshKillSwitch()
        {
            bool killed = false;
            if (KillSwitchTrades > 0)
            {
                var rs = new List<double>();
                foreach (var h in History.Where(h => h.Label == BotId && h.SymbolName == SymbolName).OrderBy(h => h.ClosingTime))
                    if (TryParseComment(h.Comment, out _, out double risk) && risk > 0)
                        rs.Add(h.NetProfit / risk);
                if (rs.Count >= KillSwitchTrades)
                {
                    double mean = rs.Skip(rs.Count - KillSwitchTrades).Average();
                    killed = mean < KillSwitchMinR;
                    if (killed && !_killed)
                        Print($"[Donchian] KILL SWITCH: mean R of the last {KillSwitchTrades} trades is {mean:F3} < {KillSwitchMinR}; no new entries");
                }
            }
            _killed = killed;
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
                    _dueExits.Remove(pos.Id);
                    _lastCloseAttemptAt.Remove(pos.Id);
                    string reason;
                    if (args.Reason == PositionCloseReason.StopLoss)
                        reason = $"StopLoss ({StopAtrMultiplier} x ATR{AtrPeriod} H4)";
                    else if (args.Reason == PositionCloseReason.Closed)
                        reason = hasBotReason ? botReason : "Closed outside the bot (cTrader)";
                    else
                        reason = args.Reason.ToString();

                    Print($"[Donchian] Closed #{pos.Id} {pos.TradeType} {pos.Comment}: {reason}, net {pos.NetProfit:F2}");
                    ReportPositionClosed(pos, pos.NetProfit, reason, exitPrice, pos.Pips);
                    SendLiveTickTelemetry(force: true);
                    RefreshKillSwitch();
                }
                catch (Exception ex)
                {
                    if (ShowLogs) Print($"[OnPositionClosed Error] {ex.Message}");
                }
            });
        }

        private void ReportPositionOpen(Position position, double slPips, string reason, PendingEntry signal)
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
                        signal = position.Comment,
                        channel_edge = signal.Level,
                        atr_h4 = Math.Round(signal.Atr, 5),
                        strength_atr = Math.Round(signal.Strength, 3),
                        median_strength = double.IsNaN(signal.Median) ? (double?)null : Math.Round(signal.Median, 3),
                        risk_scale = Math.Round(signal.Scale, 3),
                        spread = Math.Round(Symbol.Ask - Symbol.Bid, 5)
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
