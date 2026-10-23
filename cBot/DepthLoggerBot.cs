using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using cAlgo.API;

namespace cAlgo.Robots
{
    /// <summary>
    /// Depth-of-market recorder. It never trades: it only reads the order book of a few symbols during short UTC
    /// windows and appends each snapshot to a CSV, so the cost of a large market order at the Gotobi minutes (18:00,
    /// 00:55 and 02:55 UTC) can be measured offline (research/tools/depth_cost.py). The cTrader tick history has no
    /// volumes, so this is the only way to see how deep the book is at those minutes.
    ///
    /// A snapshot is written on a book update, at most one per MinIntervalMs per symbol, and once a second from a
    /// timer so a quiet book still leaves rows. One file per symbol and UTC day: OutputDir/depth_SYMBOL_yyyyMMdd.csv,
    /// columns ts_ms (UTC), src (U = update, T = timer), bids and asks as "price:units" pairs joined by '|', best first.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class DepthLoggerBot : Robot
    {
        [Parameter("Symbols", DefaultValue = "USDJPY,EURJPY,GBPJPY")]
        public string SymbolList { get; set; }

        [Parameter("Windows (UTC, HH:mm-HH:mm)", DefaultValue = "17:58-18:03,00:53-00:58,02:53-02:58")]
        public string WindowList { get; set; }

        [Parameter("Min Interval (ms)", DefaultValue = 200, MinValue = 0)]
        public int MinIntervalMs { get; set; }

        [Parameter("Max Levels", DefaultValue = 20, MinValue = 1)]
        public int MaxLevels { get; set; }

        [Parameter("Output Dir", DefaultValue = "/root/depth_logs")]
        public string OutputDir { get; set; }

        private readonly Dictionary<string, MarketDepth> _depths = new Dictionary<string, MarketDepth>();
        private readonly Dictionary<string, DateTime> _lastWrite = new Dictionary<string, DateTime>();
        private readonly Dictionary<string, int> _rows = new Dictionary<string, int>();
        private readonly Dictionary<string, StreamWriter> _writers = new Dictionary<string, StreamWriter>();
        private readonly Dictionary<string, string> _writerDay = new Dictionary<string, string>();
        private readonly List<Tuple<TimeSpan, TimeSpan>> _windows = new List<Tuple<TimeSpan, TimeSpan>>();
        private bool _wasInWindow;

        protected override void OnStart()
        {
            foreach (var w in WindowList.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
            {
                var parts = w.Split('-');
                _windows.Add(Tuple.Create(TimeSpan.ParseExact(parts[0], @"hh\:mm", CultureInfo.InvariantCulture),
                                          TimeSpan.ParseExact(parts[1], @"hh\:mm", CultureInfo.InvariantCulture)));
            }
            Directory.CreateDirectory(OutputDir);

            foreach (var name in SymbolList.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
            {
                var sym = name;
                var depth = MarketData.GetMarketDepth(sym);
                _depths[sym] = depth;
                _lastWrite[sym] = DateTime.MinValue;
                _rows[sym] = 0;
                depth.Updated += () => OnDepthUpdated(sym);
            }
            Timer.Start(TimeSpan.FromSeconds(1));
            Print($"[Depth] recording {string.Join(",", _depths.Keys)} in {WindowList} UTC to {OutputDir}, every update "
                  + $"(at most one per {MinIntervalMs} ms) plus 1 s, {MaxLevels} levels a side");
        }

        private bool InWindow(DateTime now)
        {
            var t = now.TimeOfDay;
            return _windows.Any(w => t >= w.Item1 && t < w.Item2);
        }

        private void OnDepthUpdated(string sym)
        {
            var now = Server.Time;
            if (!InWindow(now) || (now - _lastWrite[sym]).TotalMilliseconds < MinIntervalMs)
                return;
            Write(sym, now, "U");
        }

        protected override void OnTimer()
        {
            var now = Server.Time;
            var inWindow = InWindow(now);
            if (inWindow)
            {
                foreach (var sym in _depths.Keys)
                    Write(sym, now, "T");
            }
            else if (_wasInWindow)
            {
                Print("[Depth] window closed: " + string.Join(", ", _rows.Select(kv => $"{kv.Key} {kv.Value} rows")));
                foreach (var sym in _rows.Keys.ToList())
                    _rows[sym] = 0;
                foreach (var writer in _writers.Values)
                    writer.Flush();
            }
            _wasInWindow = inWindow;
        }

        private void Write(string sym, DateTime now, string src)
        {
            var depth = _depths[sym];
            var bids = depth.BidEntries.OrderByDescending(e => e.Price).Take(MaxLevels);
            var asks = depth.AskEntries.OrderBy(e => e.Price).Take(MaxLevels);
            var ms = (long)(now - DateTime.UnixEpoch).TotalMilliseconds;
            var line = $"{ms},{src},{Levels(bids)},{Levels(asks)}";

            var day = now.ToString("yyyyMMdd", CultureInfo.InvariantCulture);
            if (!_writers.TryGetValue(sym, out var writer) || _writerDay[sym] != day)
            {
                writer?.Dispose();
                var path = Path.Combine(OutputDir, $"depth_{sym}_{day}.csv");
                var isNew = !System.IO.File.Exists(path);
                writer = new StreamWriter(path, append: true, Encoding.ASCII);
                if (isNew)
                    writer.WriteLine("ts_ms,src,bids,asks");
                _writers[sym] = writer;
                _writerDay[sym] = day;
            }
            writer.WriteLine(line);
            _lastWrite[sym] = now;
            _rows[sym]++;
        }

        private static string Levels(IEnumerable<MarketDepthEntry> entries) =>
            string.Join("|", entries.Select(e => e.Price.ToString(CultureInfo.InvariantCulture) + ":"
                                                 + e.VolumeInUnits.ToString("0", CultureInfo.InvariantCulture)));

        protected override void OnStop()
        {
            foreach (var writer in _writers.Values)
                writer.Dispose();
        }
    }
}
