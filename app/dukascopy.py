"""Dukascopy bid candles for the paper desk (app/paper_desk_runner.py): M1 files, aggregated to hours.

datafeed.dukascopy.com/datafeed/<SYM>/<YYYY>/<MM0>/<DD>/BID_candles_min_1.bi5 (MM0 is zero based; the per-day hourly
files answer 404 for recent days), LZMA, records
'>5if' = seconds into the day, open, close, low, high, volume; prices are integers scaled by SCALE. It needs a browser
User-Agent (else 429), a new connection is slow (15-35 s) and a kept-alive one fast, and a missing file answers 503
(not 404), but a rate-limited client gets 503 too, so a day is called missing only after MISSING_AFTER 503s on fresh
connections, and an empty weekday is never cached (a Saturday is: there is no trading). A finished day's file never
changes, so finished days with data are cached on disk and fetched once.
"""
from __future__ import annotations

import datetime as dt
import http.client
import json
import lzma
import os
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HOST = "datafeed.dukascopy.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
MISSING_AFTER = 5

# paper-desk symbol -> (Dukascopy instrument, price scale)
INSTRUMENTS: Dict[str, Tuple[str, float]] = {
    "EURUSD": ("EURUSD", 1e5),
    "USDJPY": ("USDJPY", 1e3),
    "GBPJPY": ("GBPJPY", 1e3),
    "XAUUSD": ("XAUUSD", 1e3),
    "US500": ("USA500IDXUSD", 1e3),
    "BTCUSD": ("BTCUSD", 1e3),
}

RECORD = struct.Struct(">5if")       # seconds into the day, open, close, low, high, volume

# An hourly bar is (ts, open, high, low, close); ts is the UTC ms of the hour start.
Bar = Tuple[int, float, float, float, float]


class Dukascopy:
    def __init__(self, cache_dir: Path, timeout: float = 60.0):
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self._conn: Optional[http.client.HTTPSConnection] = None

    def _request(self, path: str) -> Tuple[int, bytes]:
        for _ in range(2):
            if self._conn is None:
                self._conn = http.client.HTTPSConnection(HOST, timeout=self.timeout)
            try:
                self._conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
                r = self._conn.getresponse()
                return r.status, r.read()
            except Exception:
                self.close()
        raise RuntimeError(f"Dukascopy request failed: {path}")

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _download(self, instrument: str, day: dt.date) -> Optional[bytes]:
        path = f"/datafeed/{instrument}/{day.year}/{day.month - 1:02d}/{day.day:02d}/BID_candles_min_1.bi5"
        misses = 0
        for attempt in range(10):
            try:
                status, body = self._request(path)
            except RuntimeError:          # timeout or reset: a new connection after a pause
                self.close()
                time.sleep(2 * (attempt + 1))
                continue
            if status == 200:
                return body
            if status == 404:
                return b""              # not published (yet) or no such day
            if status == 503:
                misses += 1
                if misses >= MISSING_AFTER:
                    return b""            # no trading that day
                self.close()              # a 503 sticks to its connection
                time.sleep(2.0 * misses)
            else:
                self.close()
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"Dukascopy gave up on {path}")

    @staticmethod
    def parse(raw: bytes, day: dt.date, scale: float) -> List[Bar]:
        if not raw:
            return []
        d = lzma.decompress(raw)
        day0 = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
        hours: Dict[int, List[float]] = {}
        for i in range(len(d) // RECORD.size):
            t, o, c, lo, hi, vol = RECORD.unpack_from(d, i * RECORD.size)
            if vol <= 0:                       # zero-volume minutes are no trading
                continue
            h = hours.get(t // 3600)
            if h is None:
                hours[t // 3600] = [o / scale, hi / scale, lo / scale, c / scale]
            else:
                h[1], h[2], h[3] = max(h[1], hi / scale), min(h[2], lo / scale), c / scale
        return [(day0 + k * 3600_000, *v) for k, v in sorted(hours.items())]

    def day(self, symbol: str, day: dt.date, today: Optional[dt.date] = None) -> List[Bar]:
        """The day's hourly candles (possibly empty). A day before `today` (UTC) is read from / written to the cache."""
        instrument, scale = INSTRUMENTS[symbol]
        today = today or dt.datetime.now(dt.timezone.utc).date()
        fn = self.cache_dir / symbol / f"{day.isoformat()}.json"
        if day < today and fn.exists():
            return [tuple(b) for b in json.loads(fn.read_text())]
        out = self.parse(self._download(instrument, day), day, scale)
        if day < today and (out or day.weekday() == 5):
            fn.parent.mkdir(parents=True, exist_ok=True)
            fn.write_text(json.dumps(out))
        return out

    def range(self, symbol: str, first: dt.date, last: dt.date, today: Optional[dt.date] = None) -> List[Bar]:
        out: List[Bar] = []
        d = first
        while d <= last:
            out += self.day(symbol, d, today)
            d += dt.timedelta(days=1)
        return out


def cache_dir_from_env() -> Path:
    return Path(os.environ.get("PAPER_DESK_DATA", "data/paper_desk")) / "duka"
