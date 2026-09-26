"""Cash-session days for the index CFDs: M1 row indices of the session open/close per local trading day."""
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

import numpy as np

SESSIONS = {
    "US30": ("America/New_York", time(9, 30), time(16, 0)),
    "USTEC": ("America/New_York", time(9, 30), time(16, 0)),
    "DE40": ("Europe/Berlin", time(9, 0), time(17, 30)),
    "UK100": ("Europe/London", time(8, 0), time(16, 30)),
}


def session_days(m: dict, symbol: str, tz_name=None, t_open=None, t_close=None):
    """[(day, k_open, k_close)]: first M1 row at/after the open, last row before the close; days whose
    open minute is missing are skipped."""
    if tz_name is None:
        tz_name, t_open, t_close = SESSIONS[symbol]
    tz = ZoneInfo(tz_name)
    ts = m["ts"]
    first = datetime.fromtimestamp(ts[0] / 1000, timezone.utc).astimezone(tz).date()
    last = datetime.fromtimestamp(ts[-1] / 1000, timezone.utc).astimezone(tz).date()
    out = []
    d = first
    one = np.timedelta64(1, "D")
    while d <= last:
        if d.weekday() < 5:
            a = int(datetime.combine(d, t_open, tz).timestamp() * 1000)
            b = int(datetime.combine(d, t_close, tz).timestamp() * 1000)
            ka = int(np.searchsorted(ts, a))
            kb = int(np.searchsorted(ts, b)) - 1
            if ka < len(ts) and ts[ka] == a and kb > ka + 30:
                out.append((d, ka, kb))
        d = (np.datetime64(d) + one).astype(object)
    return out
