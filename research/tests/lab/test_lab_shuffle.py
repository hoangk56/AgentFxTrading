from datetime import date, timedelta

import pytest

np = pytest.importorskip("numpy")

from research.lab import feed  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402

W0 = 2900                                   # a lab week number (Saturday 1970-01-03 + 2900 weeks)
PRICES = {W0: (100.0, 104.0, 110.0), W0 + 1: (110.0, 105.0, 99.0), W0 + 2: (100.0, 111.0, 120.0)}


def _week_ticks(w, prices):
    sat = feed.SAT0_MS + w * feed.WEEK_MS
    ts = [sat + 2 * feed.DAY_MS, sat + 4 * feed.DAY_MS, sat + 6 * feed.DAY_MS - 3_600_000]   # Mon, Wed, Fri 23:00
    return ts, list(prices)


@pytest.fixture
def fake(monkeypatch):
    ts, px = [], []
    for w, p in PRICES.items():
        a, b = _week_ticks(w, p)
        ts += a
        px += b
    ts, px = np.array(ts, np.int64), np.array(px, float)
    monkeypatch.setattr(feed, "load_m1", lambda s: {"ts": ts, "o": px, "c": px})

    def load_ticks(symbol, a, b):
        keep = (ts >= day_ms(a)) & (ts < day_ms(b) + feed.DAY_MS)
        return Ticks(ts[keep], px[keep], px[keep] + 0.01)

    monkeypatch.setattr(feed, "load_ticks", load_ticks)
    feed.shuffler.cache_clear()
    yield ts, px
    feed.shuffler.cache_clear()


def _weeks_of(t):
    w = feed.week_of(t.ts)
    return [(t.bid[w == k][0], t.bid[w == k][-1]) for k in np.unique(w)]


def test_shuffle_keeps_weekly_returns_and_clock_positions(fake):
    ts, px = fake
    sh = feed.WeekShuffle("X", seed=3)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    t = sh.ticks(a, a + timedelta(days=20))
    got = sorted(round(last / first, 9) for first, last in _weeks_of(t))
    want = sorted(round(p[2] / p[0], 9) for p in PRICES.values())
    assert got == want
    assert sorted((t.ts - feed.SAT0_MS) % feed.WEEK_MS) == sorted((ts - feed.SAT0_MS) % feed.WEEK_MS)
    assert np.all(np.diff(t.ts) > 0)
    assert np.allclose(t.ask - t.bid, 0.01 * sh.scale[np.repeat(np.arange(3), 3)])


def test_each_week_opens_at_the_previous_close_times_its_own_gap(fake):
    sh = feed.WeekShuffle("X", seed=3)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    weeks = _weeks_of(sh.ticks(a, a + timedelta(days=20)))
    first = np.array([p[0] for p in PRICES.values()])
    last = np.array([p[2] for p in PRICES.values()])
    gap = np.r_[1.0, first[1:] / last[:-1]]
    assert weeks[0][0] == pytest.approx(100.0)
    for k in (1, 2):
        assert weeks[k][0] == pytest.approx(weeks[k - 1][1] * gap[sh.src[k]])


def test_load_chunk_accepts_the_shuffle_variant(fake, monkeypatch):
    btc = feed.instrument("BTCUSD")
    monkeypatch.setattr(feed, "instrument", lambda s: btc)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    monkeypatch.setattr(feed, "year_span", lambda y: (a, a + timedelta(days=20)))
    ch = feed.load_chunk("X", "shuffle:3", 2025, warmup_days=0, tail_days=0)
    assert ch is not None and ch.variant == "shuffle:3" and len(ch.t) == 9
