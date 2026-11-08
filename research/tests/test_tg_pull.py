"""Pure parts of the active MTProto fetcher for @upbit_news (round 74 TG2, tg_pull.py): end-time parsing, period and
FloodWait rules, result parsing, first-receipt logging, and the poll loop on fake Telethon-like objects and a fake
clock (no network, Telethon not needed)."""
import asyncio
import csv
import datetime as dt
import importlib.util
import os

import pytest

PATH = os.path.join(os.path.dirname(__file__), "..", "results", "portfolio", "round74_tg_stamps", "TG2", "code",
                    "tg_pull.py")


@pytest.fixture(scope="module")
def tp():
    spec = importlib.util.spec_from_file_location("tg_pull", PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T0 = dt.datetime(2026, 11, 2, 13, 3, 3, tzinfo=dt.timezone.utc)


# Telethon-like fakes: the code classifies results by class name only.
class Message:
    def __init__(self, id, date, message=""):
        self.id, self.date, self.message = id, date, message


class MessageEmpty:
    def __init__(self, id):
        self.id = id


class MessageService:
    def __init__(self, id, date):
        self.id, self.date = id, date


class ChannelDifferenceEmpty:
    def __init__(self, pts, timeout=None):
        self.pts, self.timeout = pts, timeout


class ChannelDifference:
    def __init__(self, pts, new_messages, timeout=None):
        self.pts, self.new_messages, self.timeout = pts, new_messages, timeout


class Dialog:
    def __init__(self, pts):
        self.pts = pts


class ChannelDifferenceTooLong:
    def __init__(self, pts, messages):
        self.dialog, self.messages, self.timeout = Dialog(pts), messages, None


def test_parse_until(tp):
    assert tp.parse_until("2026-11-09T00:00Z") == dt.datetime(2026, 11, 9, tzinfo=dt.timezone.utc).timestamp()
    with pytest.raises(ValueError):
        tp.parse_until(None)
    with pytest.raises(ValueError):
        tp.parse_until("2026-11-09T00:00")  # no zone


def test_period_rules(tp):
    assert tp.clamp_period(0.2) == 1.0
    assert tp.clamp_period(2) == 2.0
    assert tp.clamp_period(500) == 60.0
    assert tp.after_flood(2.0, 5) == (4.0, False)
    assert tp.after_flood(40.0, 301) == (60.0, True)
    assert tp.after_flood(2.0, 300) == (4.0, False)


def test_diff_result(tp):
    assert tp.diff_result(ChannelDifferenceEmpty(10, 30)) == ("ChannelDifferenceEmpty", 10, [], 30)
    k, pts, posts, tmo = tp.diff_result(ChannelDifference(12, [Message(2057, T0, "[거래] x"),
                                                               MessageService(2058, T0)]))
    assert (k, pts, tmo) == ("ChannelDifference", 12, None)
    assert posts == [(2057, T0.timestamp(), "[거래] x")]
    assert tp.diff_result(ChannelDifferenceTooLong(99, [Message(3, T0)]))[1] == 99


def test_row_and_seen(tp):
    r = tp.row(2056, T0.timestamp(), T0.timestamp() + 1.25, "diff", 0.08, 2.0,
               "[거래] 퍼퍼(PUFFER)  KRW 마켓\n디지털 자산 추가")
    assert r["recv_minus_post_s"] == 1.25 and r["krw_listing"] == 1 and r["method"] == "diff"
    assert r["post_utc"] == "2026-11-02T13:03:03.000+00:00" and "\n" not in r["text"]
    s = tp.Seen(floor=2056)
    assert not s.new("diff", 2056)  # known at start
    assert s.new("diff", 2057) and not s.new("diff", 2057) and s.new("ids", 2057)


class Clock:
    def __init__(self, t):
        self.t = t

    def now(self):
        return self.t

    async def sleep(self, d):
        self.t += d


def make_call(tp, clock, script):
    """script: list of results/exceptions for successive diff/ids calls (each call costs 0.1 s)."""
    calls = []

    async def call(name, **kw):
        calls.append((name, kw))
        if name == "full":
            return 5
        if name == "last":
            return 2056
        clock.t += 0.1
        if script:
            x = script.pop(0)
        else:
            x = ChannelDifferenceEmpty(kw["pts"]) if name == "diff" else [MessageEmpty(i) for i in kw["ids"]]
        if isinstance(x, Exception):
            raise x
        return x
    return call, calls


def run_poller(tp, tmp_path, script, method="diff", dur=20.0, period=2.0, on_post=None):
    start = T0.timestamp() + 0.5
    clock = Clock(start)
    call, calls = make_call(tp, clock, script)
    p = tp.Poller(call, start + dur, period, method, here=str(tmp_path), now=clock.now, sleep=clock.sleep,
                  on_post=on_post)
    res = asyncio.run(p.run())
    log = os.path.join(tmp_path, "pull_log.csv")
    rows = list(csv.DictReader(open(log))) if os.path.exists(log) else []
    return res, rows, calls, p


def test_poller_logs_first_receipt(tp, tmp_path):
    post = T0 + dt.timedelta(seconds=2)
    script = [ChannelDifferenceEmpty(5, 30), ChannelDifference(6, [Message(2057, post, "[입출금] a")]),
              ChannelDifference(7, [Message(2057, post, "[입출금] a")])]  # repeat must not be logged twice
    res, rows, calls, _ = run_poller(tp, tmp_path, script)
    assert res == "end"
    assert [r["msg_id"] for r in rows] == ["2057"]
    assert float(rows[0]["recv_minus_post_s"]) == pytest.approx(0.5 + 2 + 0.1 - 2, abs=1e-6)
    diffs = [kw["pts"] for n, kw in calls if n == "diff"]
    assert diffs[:3] == [5, 5, 6]  # pts carried forward
    assert len(diffs) == 10  # 20 s at 2 s


def test_poller_flood_doubles_and_stops(tp, tmp_path):
    res, rows, calls, p = run_poller(tp, tmp_path, [tp.FloodWait(5)], dur=60)
    assert res == "end" and p.period == 4.0
    res, rows, calls, p = run_poller(tp, tmp_path, [tp.FloodWait(301)], dur=60)
    assert res == "flood" and os.path.exists(os.path.join(tmp_path, "STOP_PULL"))


def test_poller_auth_stop_and_stop_file(tp, tmp_path):
    res, *_ = run_poller(tp, tmp_path, [tp.AuthStop("AuthKeyDuplicatedError")])
    assert res == "auth"
    res, rows, calls, _ = run_poller(tp, tmp_path, [])  # STOP_PULL now present
    assert res == "stop-file" and not [c for c in calls if c[0] == "diff"]


def test_poller_ids_cursor_skips_service(tp, tmp_path):
    post = T0 + dt.timedelta(seconds=3)
    script = [[MessageEmpty(2057), MessageEmpty(2058)],
              [MessageService(2057, post), MessageEmpty(2058)],
              [Message(2058, post, "b"), MessageEmpty(2059)]]
    res, rows, calls, _ = run_poller(tp, tmp_path, script, method="ids", dur=8)
    ids = [kw["ids"] for n, kw in calls if n == "ids"]
    assert ids[:3] == [[2057, 2058], [2057, 2058], [2058, 2059]]
    assert [r["msg_id"] for r in rows] == ["2058"] and rows[0]["method"] == "ids"


def test_poller_alt_each_method_finds_post(tp, tmp_path):
    post = T0 + dt.timedelta(seconds=1)
    script = [ChannelDifference(6, [Message(2057, post, "a")]), [Message(2057, post, "a"), MessageEmpty(2058)]]
    res, rows, calls, _ = run_poller(tp, tmp_path, script, method="alt", dur=4)
    assert sorted((r["method"], r["msg_id"]) for r in rows) == [("diff", "2057"), ("ids", "2057")]


def test_transient_streak_stops(tp, tmp_path):
    res, *_ = run_poller(tp, tmp_path, [tp.Transient("x")] * 40, dur=200, period=1.0)
    assert res == "errors"


PUSH = os.path.join(os.path.dirname(__file__), "..", "results", "portfolio", "round73_telegram_capture", "TG", "coord",
                    "tg_push.py")


def test_krw_tickers_same_as_push(tp):
    spec = importlib.util.spec_from_file_location("tg_push", PUSH)
    push = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(push)
    titles = ["[거래] 콜렉터크립트(CARDS) 신규 거래지원 안내 (KRW, BTC, USDT 마켓)",
              "[거래] 셀레스티아(TIA)(KRW, BTC, USDT 마켓), 아이오넷(IO)(BTC, USDT 마켓) 디지털 자산 추가",
              "[거래] 퍼퍼(PUFFER) KRW 마켓 디지털 자산 추가", "[입출금] 지캐시(ZEC) 출금 일시 중단 안내"]
    for t in titles:
        assert tp.krw_tickers(t) == push.krw_tickers(t) and tp.krw_listing(t) == push.krw_listing(t)
    assert tp.krw_tickers(titles[1]) == ["TIA"]


def test_on_post_once_per_post_and_never_stops_capture(tp, tmp_path):
    post = T0 + dt.timedelta(seconds=1)
    got = []

    def on_post(mid, post_t, recv_t, text):
        got.append((mid, text))
        raise RuntimeError("paper side broke")

    script = [ChannelDifference(6, [Message(2057, post, "a")]), [Message(2057, post, "a"), MessageEmpty(2058)],
              ChannelDifference(7, [Message(2059, post, "b")])]
    res, rows, *_ = run_poller(tp, tmp_path, script, method="alt", dur=6, on_post=on_post)
    assert res == "end" and got == [(2057, "a"), (2059, "b")]  # ids saw 2057 again: no second call
    assert len(rows) == 3
    assert "on_post error RuntimeError" in open(os.path.join(tmp_path, "pull_heartbeat.log")).read()


class HB:
    def __init__(self):
        self.lines = []

    def write(self, s):
        self.lines.append(s)


def test_perps_find_and_paper_rows(tp, tmp_path):
    onboard = (T0 - dt.timedelta(days=30)).timestamp() * 1000
    info = {"symbols": [{"symbol": "1000PEPEUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT",
                         "status": "TRADING", "onboardDate": onboard},
                        {"symbol": "OLDUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "SETTLING",
                         "onboardDate": onboard}]}
    perps = tp.Perps(fetch=lambda: info)
    assert perps.find("PEPE")["symbol"] == "1000PEPEUSDT" and perps.find("OLD") is None
    books = {"1000PEPEUSDT": (0.0099, 0.0101), "BTCUSDT": (100000.0, 100001.0)}
    hb, post = HB(), T0.timestamp()  # long past: no wait for N + 5 s
    asyncio.run(tp.paper(2071, "PEPE", post, post + 1.9, perps, hb, here=str(tmp_path), book=books.__getitem__))
    asyncio.run(tp.paper(2071, "OLD", post, post + 1.9, perps, hb, here=str(tmp_path), book=books.__getitem__))
    asyncio.run(tp.paper(2072, "PEPE", post, post + 1.9, perps, hb, here=str(tmp_path), book=lambda s: 1 / 0))
    rows = list(csv.DictReader(open(os.path.join(tmp_path, "pull_paper.csv"))))
    assert rows[0]["perp"] == "1000PEPEUSDT" and rows[0]["eligible"] == "1" and rows[0]["perp_age_d"] == "30.0"
    assert rows[0]["entry_alt_ask"] == "0.0101" and rows[0]["entry_btc_bid"] == "100000.0"
    assert rows[0]["entry_alt_spread_bp"] == "200.0" and rows[0]["note"] == ""
    assert rows[1]["note"] == "no Binance USDT-M perp" and rows[1]["perp"] == ""
    assert rows[2]["note"].startswith("ZeroDivisionError") and hb.lines
