import csv
import datetime as dt
import json
import math
import os
from decimal import Decimal

import pytest

from app import a2_live as A

N = 1_800_000_000.0     # notice post time (epoch s)
DAY = 86400


def info(symbol, step="0.01", min_qty="0.01", max_qty="100000", min_notional="5", age_d=100):
    return {"symbol": symbol, "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING",
            "onboardDate": (N - age_d * DAY) * 1000,
            "filters": [{"filterType": "MARKET_LOT_SIZE", "stepSize": step, "minQty": min_qty, "maxQty": max_qty},
                        {"filterType": "MIN_NOTIONAL", "notional": min_notional}]}


class Clock:
    def __init__(self, t):
        self.t = t

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += max(s, 0)


class FakeFutures:
    def __init__(self, symbols, books, fail=None):
        self.symbols, self.books, self.fail = symbols, books, fail or {}
        self.orders, self.prepared = [], []

    def exchange_info(self):
        return {"symbols": self.symbols}

    def book(self, symbol):
        return self.books[symbol]

    def set_cross(self, symbol):
        self.prepared.append(("cross", symbol))

    def set_leverage(self, symbol, lev):
        self.prepared.append(("lev", symbol, lev))

    def order(self, symbol, side, qty, reduce_only=False):
        self.orders.append((symbol, side, qty, reduce_only))
        err = self.fail.get((symbol, side, reduce_only))
        if err:
            raise err
        bid, ask = self.books[symbol]
        return {"avgPrice": str(ask if side == "BUY" else bid), "executedQty": qty, "status": "FILLED"}


class FakeUpbit:
    def __init__(self, open_after_polls=2):
        self.polls, self.after = 0, open_after_polls

    def first_candle(self, coin):
        self.polls += 1
        return "2027-01-15T06:05:00" if self.polls > self.after else None


def make(tmp_path, live=True, symbols=None, books=None, fail=None, upbit=None, **cfg):
    clock = Clock(N + 1.5)
    fut = FakeFutures(symbols or [info("HYPEUSDT"), info("BTCUSDT", step="0.001", min_qty="0.001")],
                      books or {"HYPEUSDT": (74.70, 74.75), "BTCUSDT": (74_690.0, 74_690.5)}, fail)
    conf = A.Config(live=live, key="k", secret="s", notional=1000.0, state_dir=str(tmp_path / "st"),
                    capture_dir=str(tmp_path), **cfg)
    sent = []
    ex = A.Executor(conf, fut, upbit or FakeUpbit(), A.Store(conf.state_dir), now=clock.now, sleep=clock.sleep,
                    notify=sent.append)
    return ex, fut, clock, sent


# ---------------------------------------------------------------------------------------------------------- notices
def test_notice_parsing_matches_the_capture():
    t = "[거래] 하이퍼리퀴드(HYPE) 신규 거래지원 안내 (KRW, BTC, USDT 마켓) 🔗 공지사항 확인하기"
    assert A.krw_listing(t)
    assert A.krw_tickers(t) == ["HYPE"]
    assert not A.krw_listing("[거래] 하이퍼리퀴드(HYPE) 거래지원 종료 안내 (KRW 마켓)")
    assert A.krw_tickers("[거래] 에이(AAA)(BTC 마켓), 비(BBB)(KRW 마켓) 신규 거래지원 안내") == ["BBB"]


def test_read_posts_keeps_listings_once(tmp_path):
    p = tmp_path / "pull_log.csv"
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["msg_id", "post_utc", "text"])
        w.writeheader()
        w.writerow({"msg_id": 1, "post_utc": "2026-11-10T04:50:01.000+00:00",
                    "text": "[거래] 하이퍼리퀴드(HYPE) 신규 거래지원 안내 (KRW, BTC, USDT 마켓)"})
        w.writerow({"msg_id": 1, "post_utc": "2026-11-10T04:50:01.000+00:00",
                    "text": "[거래] 하이퍼리퀴드(HYPE) 신규 거래지원 안내 (KRW, BTC, USDT 마켓)"})
        w.writerow({"msg_id": 2, "post_utc": "2026-11-10T05:00:00.000+00:00", "text": "[안내] 점검"})
    posts = A.read_posts(str(p))
    assert [m for m, _, _ in posts] == [1]
    assert posts[0][1] == dt.datetime(2026, 11, 10, 4, 50, 1, tzinfo=dt.timezone.utc).timestamp()


# ----------------------------------------------------------------------------------------------------------- sizing
def test_leg_qty_floors_to_step_and_respects_minimums():
    i = info("X", step="0.1", min_qty="0.1", max_qty="50", min_notional="5")
    assert A.leg_qty(100, 3.0, i) == Decimal("33.3")
    assert A.leg_qty(1000, 3.0, i) == Decimal("50")          # capped at the market max
    assert A.leg_qty(4, 3.0, i) == 0                          # below min notional
    assert A.qty_str(Decimal("33.30")) == "33.3"


def test_net_bp_is_long_alt_minus_btc_less_fees():
    assert A.net_bp(100, 110, 50_000, 50_000) == pytest.approx(1000 - 20)
    assert A.net_bp(100, 100, 50_000, 55_000) == pytest.approx(-1000 - 20)


def test_config_refuses_live_without_key_or_size():
    assert A.Config(live=True).problems()
    assert not A.Config(live=False).problems()
    assert not A.Config(live=True, key="k", secret="s", notional=500).problems()
    c = A.Config.from_env({"A2_LIVE": "1", "A2_BINANCE_KEY": "k", "A2_BINANCE_SECRET": "s", "A2_NOTIONAL_USDT": "800"})
    assert c.live and c.notional == 800 and c.leverage == 3


# ------------------------------------------------------------------------------------------------------------ entry
def test_live_entry_at_n_plus_5_and_exit_at_krw_open(tmp_path):
    ex, fut, clock, sent = make(tmp_path)
    ev = ex.handle(7, "HYPE", N)
    assert ev is not None
    assert clock.t >= N + A.ENTRY_DELAY_S
    # phase-in: first trades at a quarter of 1,000 USDT
    assert ev["notional"] == 250.0
    assert sorted(fut.orders[:2]) == sorted([("HYPEUSDT", "BUY", "3.34", False), ("BTCUSDT", "SELL", "0.003", False)])
    assert ("lev", "HYPEUSDT", 3) in fut.prepared and ("cross", "BTCUSDT") in fut.prepared
    ex.watch_exit("7:HYPE")
    closes = [o for o in fut.orders if o[3]]
    assert sorted(closes) == sorted([("HYPEUSDT", "SELL", "3.34", True), ("BTCUSDT", "BUY", "0.003", True)])
    rows = ex.store.trades()
    assert rows[-1]["exit_reason"] == "krw open" and rows[-1]["krw_open_utc"] == "2027-01-15T06:05:00"
    assert float(rows[-1]["net_bp"]) == pytest.approx(A.net_bp(74.75, 74.70, 74_690.0, 74_690.5), abs=0.1)
    assert ex.store.open_events() == {}
    assert any("vào HYPE" in s for s in sent) and any("đóng HYPE" in s for s in sent)


def test_dry_run_sends_no_signed_call(tmp_path):
    ex, fut, clock, _ = make(tmp_path, live=False)
    ev = ex.handle(7, "HYPE", N)
    assert ev["mode"] == "dry" and ev["notional"] == 1000.0
    ex.watch_exit("7:HYPE")
    assert fut.orders == [] and fut.prepared == []
    assert ex.store.trades()[-1]["exit_reason"] == "krw open"


def test_full_size_after_the_phase_in(tmp_path):
    ex, fut, clock, _ = make(tmp_path, phasein_trades=1)
    ex.store.append_trade({"mode": "live", "alt_entry": 1.0, "exit_reason": "krw open"})
    assert ex.notional() == 1000.0


@pytest.mark.parametrize("symbols,reason", [
    ([info("BTCUSDT", step="0.001", min_qty="0.001")], "no Binance USDT-M perp"),
    ([info("HYPEUSDT", age_d=3), info("BTCUSDT", step="0.001", min_qty="0.001")], "d old"),
])
def test_skips_are_recorded_without_orders(tmp_path, symbols, reason):
    ex, fut, clock, _ = make(tmp_path, symbols=symbols)
    assert ex.handle(7, "HYPE", N) is None
    assert fut.orders == []
    assert reason in ex.store.trades()[-1]["note"]


def test_late_notice_is_skipped(tmp_path):
    ex, fut, clock, _ = make(tmp_path)
    clock.t = N + 12
    assert ex.handle(7, "HYPE", N) is None
    assert fut.orders == [] and "late" in ex.store.trades()[-1]["note"]


def test_stop_file_and_max_open_block_new_entries(tmp_path):
    ex, fut, clock, _ = make(tmp_path, max_open=1)
    ex.handle(7, "HYPE", N)
    clock.t = N + 1.5
    assert ex.handle(8, "HYPE", N) is None
    assert "already open" in ex.store.trades()[-1]["note"]
    open(os.path.join(ex.store.folder, "STOP_A2"), "w").close()
    assert ex.handle(9, "HYPE", N) is None
    assert "STOP_A2" in ex.store.trades()[-1]["note"]


def test_one_leg_failing_unwinds_the_other(tmp_path):
    err = A.HttpError(400, json.dumps({"code": -2019, "msg": "Margin is insufficient."}), "/fapi/v1/order")
    ex, fut, clock, _ = make(tmp_path, fail={("BTCUSDT", "SELL", False): err})
    assert ex.handle(7, "HYPE", N) is None
    assert ("HYPEUSDT", "SELL", "3.34", True) in fut.orders           # the filled long was closed
    assert ex.store.open_events() == {}
    assert "entry failed" in ex.store.trades()[-1]["note"]


def test_close_treats_nothing_to_reduce_as_closed(tmp_path):
    ex, fut, clock, _ = make(tmp_path)
    ex.handle(7, "HYPE", N)
    fut.fail[("BTCUSDT", "BUY", True)] = A.HttpError(400, json.dumps({"code": -2022, "msg": "ReduceOnly"}), "")
    ev = ex.close("7:HYPE", "close-all")
    assert math.isnan(ev["btc_exit"]) and "net_bp" not in ev
    assert ex.store.open_events() == {}


def test_max_hold_closes_when_upbit_never_opens(tmp_path):
    ex, fut, clock, _ = make(tmp_path, upbit=FakeUpbit(open_after_polls=10**9), max_hold_h=0.01)
    ex.handle(7, "HYPE", N)
    ex.watch_exit("7:HYPE")
    assert ex.store.trades()[-1]["exit_reason"] == "max hold"


def test_open_events_survive_a_restart(tmp_path):
    ex, fut, clock, _ = make(tmp_path)
    ex.handle(7, "HYPE", N)
    again = A.Store(ex.store.folder)
    assert list(again.open_events()) == ["7:HYPE"]
    assert again.live_entries() == 1


def test_signed_request_carries_signature_and_key():
    seen = {}

    def http(method, url, headers=None, timeout=5):
        seen.update(method=method, url=url, headers=headers)
        return {"dualSidePosition": False}
    f = A.Futures("KEY", "SECRET", http=http)
    assert f.dual_side() is False
    assert seen["method"] == "GET" and "signature=" in seen["url"] and "timestamp=" in seen["url"]
    assert seen["headers"] == {"X-MBX-APIKEY": "KEY"}
    assert "SECRET" not in seen["url"]
