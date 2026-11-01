"""Basis B demo: the registered rule's pure functions, an hourly tick against a fake Binance, and the stop status."""
import datetime as dt
import math

import pytest

from app import basis_b as R
from app import basis_b_runner as runner
from app import basis_b_status as st
from app import basis_b_store as store

UTC = dt.timezone.utc
H = R.H_MS


# ------------------------------------------------------------------------------------------------------- pure rule

def test_spot_name_handles_multiplier_prefixes():
    assert R.spot_name("1000PEPEUSDT") == ("PEPEUSDT", 1e3)
    assert R.spot_name("1MBABYDOGEUSDT") == ("BABYDOGEUSDT", 1e6)
    assert R.spot_name("1000000MOGUSDT") == ("MOGUSDT", 1e6)
    assert R.spot_name("SOLUSDT") == ("SOLUSDT", 1.0)
    assert R.spot_name("1INCHUSDT") == ("1INCHUSDT", 1.0)


def test_eligible_drops_stables_and_missing_spot():
    assert R.eligible("SOLUSDT", {"SOLUSDT"}) == ("SOLUSDT", 1.0)
    assert R.eligible("USDCUSDT", {"USDCUSDT"}) is None
    assert R.eligible("BTCDOMUSDT", {"BTCDOMUSDT"}) is None
    assert R.eligible("XYZUSDT", set()) is None
    assert R.eligible("SOLUSDC", {"SOLUSDC"}) is None


def test_rank_universe_uses_previous_30_days_and_age():
    day = 100 * R.DAY_MS
    listings = [R.Listing("AUSDT", "AUSDT", 1.0, 0), R.Listing("BUSDT", "BUSDT", 1.0, 0),
                R.Listing("YOUNGUSDT", "YOUNGUSDT", 1.0, day - 30 * R.DAY_MS),
                R.Listing("GONEUSDT", "GONEUSDT", 1.0, 0)]
    qv = {"AUSDT": {day - k * R.DAY_MS: 10.0 for k in range(1, 31)},
          "BUSDT": {day - k * R.DAY_MS: 20.0 for k in range(1, 31)},
          "YOUNGUSDT": {day - k * R.DAY_MS: 99.0 for k in range(1, 31)},
          "GONEUSDT": {day - k * R.DAY_MS: 50.0 for k in range(2, 31)}}     # no bar on D-1
    qv["AUSDT"][day] = 1e9                                                   # day D itself is not used
    ranked = [(li.perp, r) for li, r in R.rank_universe(day, listings, qv)]
    assert ranked == [("BUSDT", 0), ("AUSDT", 1)]


def _b(values, start=0):
    return {start + k * H: v for k, v in enumerate(values)}


def test_reference_is_median_of_previous_168_and_needs_120():
    b = _b([0.001 * (k % 3) for k in range(169)])
    assert R.reference(b, 168 * H) == pytest.approx(0.001)
    sparse = _b([0.0] * 119 + [None] * 49 + [0.0])
    assert R.reference(sparse, 168 * H) is None


def test_event_and_exit_rules():
    b = _b([0.0] * 168 + [-0.015])
    bh, m, d = R.deviation(b, 168 * H)
    assert (bh, m) == (-0.015, 0.0) and R.is_event(d)
    assert not R.is_event(-0.0099)
    e = 169 * H
    b[e] = -0.010                                   # not yet half way back
    assert R.exit_due(b, e, m, d, e) is None
    b[e + H] = -0.007                               # >= d/2 = -0.0075: exit at the next open
    assert R.exit_due(b, e, m, d, e + H) == (e + 2 * H, "half")
    stuck = dict(b)
    for k in range(24):
        stuck[e + k * H] = -0.012
    assert R.exit_due(stuck, e, m, d, e + 22 * H) is None
    assert R.exit_due(stuck, e, m, d, e + 23 * H) == (e + 24 * H, "24h")


def test_invalid_bars_are_none():
    bars_ok = [R.Bar(0, 10, 10, 50)]
    assert R.basis_series(bars_ok, [R.Bar(0, 10, 10, 19)], 1.0, 1e-5, 1e-5) == {0: None}
    assert R.basis_series(bars_ok, [R.Bar(0, 10, 10, 50)], 1.0, 6e-4, 1e-5) == {0: None}
    assert R.basis_series(bars_ok, [R.Bar(0, 0.01, 0.01, 50)], 1000.0, 1e-5, 1e-5)[0] == pytest.approx(0.0)


def test_book_vwap_and_net():
    assert R.book_vwap([(10.0, 50.0), (11.0, 100.0)], 610.0) == pytest.approx((610.0 / 60.0, 1.0))
    p, share = R.book_vwap([(10.0, 1.0)], 100.0)
    assert p == 10.0 and share == pytest.approx(0.1)
    n = R.net(100, 101, 100, 100, funding=-0.002, hours=8760 / 100, cash_y=0.0, borrow_y=0.4, spread_cost=0.002)
    assert n["price"] == pytest.approx(0.01) and n["fund"] == pytest.approx(0.002)
    assert n["net"] == pytest.approx(0.01 + 0.002 - 0.003 - 0.002 - 0.004)


def test_funding_window_is_entry_exclusive_exit_inclusive():
    stamps = [(8 * H + 3, 0.001), (16 * H - 2, -0.004), (24 * H, 0.5)]
    assert R.funding_paid(stamps, 8 * H, 16 * H) == pytest.approx(-0.004)


def test_pooled_t_matches_plain_t_when_joined():
    xs = [1.0, 2.0, 3.0, 4.0]
    n0, m0 = 3, 2.0
    sd0 = 1.0
    t = R.pooled_t(n0, m0, sd0, xs)
    sample = [1.0, 2.0, 3.0] + xs                  # mean 2, sd 1 for the first three
    mean = sum(sample) / len(sample)
    sd = math.sqrt(sum((x - mean) ** 2 for x in sample) / (len(sample) - 1))
    assert t == pytest.approx(mean / (sd / math.sqrt(len(sample))))


# ------------------------------------------------------------------------------------------------- tick, fake API

T0 = dt.datetime(2026, 11, 10, 12, 0, 20, tzinfo=UTC)
NOW_MS = int(T0.timestamp() * 1000) // H * H


class FakeBinance(runner.Binance):
    def __init__(self, secret=True):
        super().__init__("k", "s" if secret else None)
        self.perp_close = {}                        # hour -> close override for AAA
        self.now_ms = NOW_MS
        self.inventory_qty = 1e6

    def perp_info(self):
        mk = lambda s: {"symbol": s, "contractType": "PERPETUAL", "quoteAsset": "USDT", "status": "TRADING",
                        "onboardDate": 0, "filters": [{"filterType": "PRICE_FILTER", "tickSize": "0.0001"}]}
        return {"symbols": [mk("AAAUSDT"), mk("BTCUSDT")]}

    def spot_info(self):
        mk = lambda s: {"symbol": s, "status": "TRADING", "isMarginTradingAllowed": True,
                        "filters": [{"filterType": "PRICE_FILTER", "tickSize": "0.0001"}]}
        return {"symbols": [mk("AAAUSDT"), mk("BTCUSDT")]}

    def _rows(self, sym, interval, limit, perp):
        if interval == "1d":
            day = self.now_ms // R.DAY_MS * R.DAY_MS
            qv = 1e9 if sym.startswith("BTC") else 1e7
            return [[day - k * R.DAY_MS, 1, 1, 1, 1, 1, 0, qv, 1000] for k in range(limit - 1, -1, -1)]
        rows = []
        for k in range(limit - 1, -1, -1):
            t = self.now_ms - k * H
            c = self.perp_close.get(t, 10.0) if perp and sym == "AAAUSDT" else 10.0
            rows.append([t, 10.0, c, c, c, 1, t + H - 1, 1, 100])
        return rows

    def perp_klines(self, sym, interval, limit):
        return self._rows(sym, interval, limit, True)

    def spot_klines(self, sym, interval, limit):
        return self._rows(sym, interval, limit, False)

    def perp_depth(self, sym):
        return {"bids": [["9.99", "1000"]], "asks": [["10.01", "1000"]]}

    def spot_depth(self, sym):
        return {"bids": [["9.99", "1000"]], "asks": [["10.01", "1000"]]}

    def funding(self, sym, start_ms, end_ms):
        return [{"fundingTime": start_ms - 1 + H, "fundingRate": "-0.003"}]

    def margin_assets(self):
        return [{"assetName": "AAA", "isBorrowable": True}]

    def inventory(self):
        return {"assets": {"AAA": str(self.inventory_qty)}}

    def next_rates(self, assets):
        return [{"asset": a, "nextHourlyInterestRate": "0.00002"} for a in assets]

    def max_borrowable(self, asset):
        return {"amount": "0"}


@pytest.fixture
def testdb(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTFX_TEST_DB", str(tmp_path / "b.db"))
    monkeypatch.setenv("BASIS_B_CASH_RATE", "0")
    return tmp_path


def test_tick_opens_then_exits_a_paper_trade(testdb):
    api = FakeBinance()
    api.perp_close[NOW_MS - H] = 9.8                # perp 2 % under spot at the close of the last hour
    out = runner.tick(api, T0, log=lambda *_: None)
    assert out == {"coins": 1, "signals": 1, "exits": 0}
    (t,) = store.load_trades("open")
    assert t["symbol"] == "AAAUSDT" and t["entry_ms"] == NOW_MS and t["fillable"] == 1
    assert t["d_bp"] == pytest.approx(math.log(0.98) * 1e4)
    assert t["rate_hourly_in"] == pytest.approx(0.00002) and t["borrowable"] == 1
    assert runner.tick(api, T0 + dt.timedelta(minutes=5), log=lambda *_: None) == {"skipped": 1}

    api.now_ms = NOW_MS + H                         # the entry bar closed back at par: exit at this open
    out = runner.tick(api, T0 + dt.timedelta(hours=1), log=lambda *_: None)
    assert out["exits"] == 1 and out["signals"] == 0
    (c,) = store.load_trades("closed")
    assert c["exit_ms"] == NOW_MS + H and c["exit_reason"] == "half"
    assert c["funding"] == pytest.approx(-0.003)
    hs = 4 * R.half_spread(c["rank"])
    assert c["net_registered"] == pytest.approx(0.003 - R.FEES - hs - 0.4 / 8760)
    rate_y = 0.00002 * 8760
    expected_book = (9.99 / 10.01 - 1) - (10.01 / 9.99 - 1) + 0.003 - R.FEES - rate_y / 8760
    assert c["net_book"] == pytest.approx(expected_book)


def test_no_secret_records_unknown_borrow(testdb):
    api = FakeBinance(secret=False)
    api.perp_close[NOW_MS - H] = 9.8
    runner.tick(api, T0, log=lambda *_: None)
    (t,) = store.load_trades("open")
    assert t["fillable"] is None and t["inventory"] is None and "BINANCE_API_SECRET" in t["borrow_note"]


def test_thin_inventory_is_not_fillable(testdb):
    api = FakeBinance()
    api.inventory_qty = 5.0                         # 1000 USDT needs ~100 coins
    api.perp_close[NOW_MS - H] = 9.8
    runner.tick(api, T0, log=lambda *_: None)
    assert store.load_trades("open")[0]["fillable"] == 0


def test_fillable_falls_back_to_max_borrowable():
    assert runner.fillable(False, 1e9, 1.0) == 0
    assert runner.fillable(True, None, 100.0, 0.0) is None
    assert runner.fillable(True, None, 100.0, 150.0) == 1
    assert runner.fillable(True, None, 100.0, 50.0) == 0
    assert runner.fillable(None, 10.0, 100.0, 500.0) == 0


def test_empty_inventory_is_unknown_not_unfillable(testdb):
    api = FakeBinance()
    api.inventory = lambda: {"assets": {}, "updateTime": 0}
    api.perp_close[NOW_MS - H] = 9.8
    runner.tick(api, T0, log=lambda *_: None)
    (t,) = store.load_trades("open")
    assert t["fillable"] is None and "maxBorrowable 0" in t["borrow_note"]


def test_account_that_can_borrow_nothing_reads_unknown(testdb):
    api = FakeBinance()
    api.margin_assets = lambda: [{"assetName": "AAA", "isBorrowable": False}, {"assetName": "USDT", "isBorrowable": False}]
    api.inventory = lambda: {"assets": {}, "updateTime": 0}
    api.perp_close[NOW_MS - H] = 9.8
    runner.tick(api, T0, log=lambda *_: None)
    (t,) = store.load_trades("open")
    assert t["fillable"] is None and t["borrowable"] is None and "không vay được coin nào" in t["borrow_note"]


def test_one_unborrowable_asset_is_not_fillable(testdb):
    api = FakeBinance()
    api.margin_assets = lambda: [{"assetName": "AAA", "isBorrowable": False}, {"assetName": "USDT", "isBorrowable": True}]
    api.perp_close[NOW_MS - H] = 9.8
    runner.tick(api, T0, log=lambda *_: None)
    assert store.load_trades("open")[0]["fillable"] == 0


def test_signed_request_never_puts_secret_in_url():
    seen = []

    class Resp:
        def __init__(self):
            self.body = b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self.body

    def opener(req, timeout):
        seen.append((req.full_url, dict(req.header_items())))
        return Resp()

    api = runner.Binance("KEY123", "SECRET456", opener=opener)
    api.inventory()
    url, headers = seen[0]
    assert "SECRET456" not in url and "signature=" in url and "timestamp=" in url
    assert headers.get("X-mbx-apikey") == "KEY123"


# ---------------------------------------------------------------------------------------------------------- status

def _closed(v, fillable=1):
    return {"status": "closed", "fillable": fillable, "net_book": v, "net_registered": v, "entry_ms": 0,
            "exit_ms": H, "symbol": "X", "d_bp": -150.0, "rate_hourly_in": None, "inventory_usd": None}


def test_status_reads_stops_at_40_signals():
    assert st.evaluate([])["verdict"] == "NO_DATA"
    assert st.evaluate([_closed(-0.01)] * 39)["verdict"] == "CONTINUE"
    assert st.evaluate([_closed(-0.01)] * 40)["verdict"] == "STOP"
    many_unfillable = [_closed(0.02)] * 27 + [_closed(0.02, fillable=0)] * 13
    r = st.evaluate(many_unfillable)
    assert r["verdict"] == "STOP" and "không vay được" in r["verdict_reason"]


def test_status_promote_check_needs_measured_borrow():
    good = [_closed(0.02)] * 40
    assert st.evaluate(good)["verdict"] == "PROMOTE_CHECK"
    assert st.evaluate(good[:-1] + [_closed(0.02, fillable=None)])["verdict"] == "CONTINUE"


def test_status_not_fillable_counts_zero():
    r = st.evaluate([_closed(0.02), _closed(0.05, fillable=0)])
    assert r["cum_net_bp"] == pytest.approx(200.0) and r["mean_net_bp"] == pytest.approx(100.0)


def test_status_function_on_empty_db(testdb):
    s = st.status()
    assert s["available"] is False and s["verdict"] == "NO_DATA" and s["signals"] == 0
