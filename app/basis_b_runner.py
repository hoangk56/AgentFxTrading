"""Basis B demo runner: one paper trade per signal of the registered rule (app/basis_b.py), with the real Binance book
and margin-borrow data logged at entry. No order is ever sent. docs/basis-b-demo.md has the terms.

    python -m app.basis_b_runner tick       # hourly (cron at :00, :05, :10; a finished hour is not redone)
    python -m app.basis_b_runner check      # connectivity: public endpoints, then the signed margin endpoints
    python -m app.basis_b_runner status     # the stop / promotion status printed as JSON

Environment: BINANCE_API_KEY and BINANCE_API_SECRET (HMAC; read-only permission is enough, the runner only reads).
Without the secret the trades are still recorded, with the borrow fields unknown. BASIS_B_NOTIONAL (USDT per leg,
default 1000) sizes the book walk; BASIS_B_CASH_RATE (default 0.0388, Fed funds 2026-10-01) is the cash charge.
The key and secret are read from the environment only and never logged.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from app import basis_b as R
from app import basis_b_store as store

SPOT = "https://api.binance.com"
FAPI = "https://fapi.binance.com"
UA = "agentfx-basis-b/1"
PAUSE_S = 0.12
BOOK_LIMIT = 20
KLINES = 200                       # 168-hour reference + the signal hour + slack; limit < 500 = weight 2


class BinanceError(Exception):
    pass


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _iso(t: dt.datetime) -> str:
    return t.replace(microsecond=0).isoformat()


class Binance:
    """Minimal REST client. Public calls need nothing; `signed` calls need key + secret; `keyed` calls the key."""

    def __init__(self, key: Optional[str] = None, secret: Optional[str] = None, opener: Callable = None):
        self.key = key or None
        self.secret = secret or None
        self._open = opener or urllib.request.urlopen
        self._last = 0.0

    @property
    def has_secret(self) -> bool:
        return bool(self.key and self.secret)

    def _get(self, base: str, path: str, params: Optional[Dict[str, Any]] = None, auth: str = "") -> Any:
        params = dict(params or {})
        headers = {"User-Agent": UA}
        if auth:
            if not self.key or (auth == "signed" and not self.secret):
                raise BinanceError("no API key/secret")
            headers["X-MBX-APIKEY"] = self.key
        if auth == "signed":
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 10000
            q = urllib.parse.urlencode(params)
            q += "&signature=" + hmac.new(self.secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        else:
            q = urllib.parse.urlencode(params)
        url = base + path + ("?" + q if q else "")
        for attempt in range(3):
            wait = PAUSE_S - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                with self._open(urllib.request.Request(url, headers=headers), timeout=20) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")[:300]
                if e.code in (418, 429):
                    raise BinanceError(f"{path}: HTTP {e.code} rate limit, stopping: {body}")
                if e.code >= 500 and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise BinanceError(f"{path}: HTTP {e.code}: {body}")
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise BinanceError(f"{path}: {e}")
        raise BinanceError(f"{path}: retries exhausted")

    # public
    def perp_info(self):
        return self._get(FAPI, "/fapi/v1/exchangeInfo")

    def spot_info(self):
        return self._get(SPOT, "/api/v3/exchangeInfo", {"permissions": "SPOT"})

    def perp_klines(self, sym, interval, limit):
        return self._get(FAPI, "/fapi/v1/klines", {"symbol": sym, "interval": interval, "limit": limit})

    def spot_klines(self, sym, interval, limit):
        return self._get(SPOT, "/api/v3/klines", {"symbol": sym, "interval": interval, "limit": limit})

    def perp_depth(self, sym):
        return self._get(FAPI, "/fapi/v1/depth", {"symbol": sym, "limit": BOOK_LIMIT})

    def spot_depth(self, sym):
        return self._get(SPOT, "/api/v3/depth", {"symbol": sym, "limit": BOOK_LIMIT})

    def funding(self, sym, start_ms, end_ms):
        return self._get(FAPI, "/fapi/v1/fundingRate", {"symbol": sym, "startTime": start_ms, "endTime": end_ms,
                                                         "limit": 100})

    # key / signed (margin)
    def margin_assets(self):
        return self._get(SPOT, "/sapi/v1/margin/allAssets", auth="key")

    def inventory(self):
        return self._get(SPOT, "/sapi/v1/margin/available-inventory", {"type": "MARGIN"}, auth="signed")

    def next_rates(self, assets: Sequence[str]):
        return self._get(SPOT, "/sapi/v1/margin/next-hourly-interest-rate",
                         {"assets": ",".join(assets), "isIsolated": "FALSE"}, auth="signed")

    def max_borrowable(self, asset: str):
        return self._get(SPOT, "/sapi/v1/margin/maxBorrowable", {"asset": asset}, auth="signed")


# ---------------------------------------------------------------------------------------------------------- parsing

def bars(rows) -> List[R.Bar]:
    return [R.Bar(int(r[0]), float(r[1]), float(r[4]), int(r[8])) for r in rows]


def levels(side) -> List[Tuple[float, float]]:
    return [(float(p), float(q)) for p, q in side]


def tick_sizes(info) -> Dict[str, float]:
    out = {}
    for s in info.get("symbols", []):
        for f in s.get("filters", []):
            if f.get("filterType") == "PRICE_FILTER":
                out[s["symbol"]] = float(f["tickSize"])
    return out


def cash_rate() -> float:
    return float(os.environ.get("BASIS_B_CASH_RATE", "0.0388"))


def notional() -> float:
    return float(os.environ.get("BASIS_B_NOTIONAL", "1000"))


# ---------------------------------------------------------------------------------------------------------- universe

def build_universe(api: Binance, day_ms: int, perp_info, spot_info, log=print) -> List[Dict[str, Any]]:
    spot_trading = {s["symbol"] for s in spot_info.get("symbols", []) if s.get("status") == "TRADING"}
    listings = []
    for s in perp_info.get("symbols", []):
        if s.get("contractType") != "PERPETUAL" or s.get("quoteAsset") != "USDT" or s.get("status") != "TRADING":
            continue
        el = R.eligible(s["symbol"], spot_trading)
        if el:
            listings.append(R.Listing(s["symbol"], el[0], el[1], int(s.get("onboardDate", 0))))
    qv: Dict[str, Dict[int, float]] = {}
    for li in listings:
        rows = api.perp_klines(li.perp, "1d", R.VOLUME_DAYS + 2)
        qv[li.perp] = {int(r[0]): float(r[7]) for r in rows if int(r[0]) < day_ms}
    ranked = R.rank_universe(day_ms, listings, qv)
    rows = [{"symbol": li.perp, "spot": li.spot, "factor": li.factor, "rank": rank} for li, rank in ranked]
    store.save_universe(day_ms, rows)
    log(f"universe {dt.datetime.fromtimestamp(day_ms / 1000, dt.timezone.utc).date()}: {len(rows)} of "
        f"{len(listings)} eligible perps")
    return rows


def universe_for(api: Binance, day_ms: int, perp_info, spot_info, log=print) -> List[Dict[str, Any]]:
    rows = store.load_universe(day_ms)
    return rows if rows else build_universe(api, day_ms, perp_info, spot_info, log)


# ------------------------------------------------------------------------------------------------------------ borrow

class Borrow:
    """Margin borrow facts for one run, each fetched at most once; failures become a note, never an exception."""

    def __init__(self, api: Binance, spot_info):
        self.api = api
        self.notes: List[str] = []
        self.margin_pair = {s["symbol"]: bool(s.get("isMarginTradingAllowed")) for s in spot_info.get("symbols", [])}
        self._assets = None
        self._inventory = None

    def _try(self, label, fn):
        try:
            return fn()
        except BinanceError as e:
            self.notes.append(f"{label}: {e}")
            return None

    def borrowable(self, spot: str, asset: str) -> Optional[bool]:
        """False when the pair has no cross margin or the asset is not borrowable; None when unknown. If the key's
        account can borrow no asset at all (seen 2026-11-01: all 494 false), that is the account's state, not the
        coin's, so it reads as unknown with a note instead of counting every signal as not fillable."""
        if self.api.key and self._assets is None:
            rows = self._try("allAssets", self.api.margin_assets) or []
            self._assets = {r.get("assetName"): bool(r.get("isBorrowable")) for r in rows}
            if self._assets and not any(self._assets.values()):
                self.notes.append("tài khoản không vay được coin nào (isBorrowable false cho mọi coin): trạng thái "
                                  "tài khoản, không tính là không vay được")
                self._assets = {}
        if not self.margin_pair.get(spot, False):
            return False
        if self._assets and asset in self._assets:
            return self._assets[asset]
        return None

    def inventory(self, asset: str) -> Optional[float]:
        if not self.api.has_secret:
            return None
        if self._inventory is None:
            r = self._try("available-inventory", self.api.inventory) or {}
            self._inventory = {k: float(v) for k, v in (r.get("assets") or {}).items()}
        return self._inventory.get(asset) if self._inventory else None

    def rate(self, asset: str) -> Optional[float]:
        if not self.api.has_secret:
            return None
        r = self._try("next-hourly-interest-rate", lambda: self.api.next_rates([asset])) or []
        for x in r:
            if x.get("asset") == asset:
                return float(x.get("nextHourlyInterestRate"))
        return None

    def max_borrowable(self, asset: str) -> Optional[float]:
        if not self.api.has_secret:
            return None
        r = self._try("maxBorrowable", lambda: self.api.max_borrowable(asset)) or {}
        return float(r["amount"]) if "amount" in r else None


def fillable(borrowable: Optional[bool], inventory: Optional[float], qty: Optional[float],
             max_borrowable: Optional[float] = None) -> Optional[int]:
    """1 / 0 / None (unknown). Not borrowable is final; otherwise the system inventory must cover the quantity. When
    the inventory is not reported (it comes back empty for an account without margin assets), the account's
    maxBorrowable decides if it is positive; 0 there only means the account has no collateral, so it stays unknown."""
    if borrowable is False:
        return 0
    if qty is None:
        return None
    if inventory is not None:
        return 1 if inventory >= qty else 0
    if max_borrowable is not None and max_borrowable > 0:
        return 1 if max_borrowable >= qty else 0
    return None


# --------------------------------------------------------------------------------------------------------------- tick

def _series(api: Binance, coin: Dict[str, Any], ticks_p, ticks_s):
    fp = bars(api.perp_klines(coin["symbol"], "1h", KLINES))
    sp = bars(api.spot_klines(coin["spot"], "1h", KLINES))
    tp = ticks_p.get(coin["symbol"], float("inf")) / fp[-1].close if fp and fp[-1].close > 0 else float("inf")
    ts = ticks_s.get(coin["spot"], float("inf")) / sp[-1].close if sp and sp[-1].close > 0 else float("inf")
    b = R.basis_series(fp, sp, coin["factor"], tp, ts)
    return b, {x.open_ms: x for x in fp}, {x.open_ms: x for x in sp}


def _book(api: Binance, coin, n_usdt: float, buy_perp: bool):
    """(perp vwap, perp filled share, perp spread, spot vwap, spot filled share, spot spread) for entry (buy perp,
    sell spot) or exit (sell perp, buy spot)."""
    pb, sb = api.perp_depth(coin["symbol"]), api.spot_depth(coin["spot"])
    pbids, pasks = levels(pb.get("bids", [])), levels(pb.get("asks", []))
    sbids, sasks = levels(sb.get("bids", [])), levels(sb.get("asks", []))
    pv = R.book_vwap(pasks if buy_perp else pbids, n_usdt)
    sv = R.book_vwap(sbids if buy_perp else sasks, n_usdt)
    return (pv[0] if pv else None, pv[1] if pv else None, R.spread_bp(pbids, pasks),
            sv[0] if sv else None, sv[1] if sv else None, R.spread_bp(sbids, sasks))


def _close_trade(api: Binance, borrow: Borrow, t: Dict[str, Any], x_ms: int, reason: str, now_ms: int, perp_bars,
                 spot_bars, log) -> None:
    po, so = perp_bars.get(x_ms), spot_bars.get(x_ms)
    stamps = [(int(r["fundingTime"]), float(r["fundingRate"]))
              for r in api.funding(t["symbol"], t["entry_ms"] + 1, x_ms + R.H_MS // 2)]
    funding = R.funding_paid(stamps, t["entry_ms"], x_ms)
    hours = (x_ms - t["entry_ms"]) / R.H_MS
    fields: Dict[str, Any] = {"status": "closed", "exit_ms": x_ms, "exit_reason": reason, "exit_at": _iso(_now()),
                              "funding": funding,
                              "perp_open_out": po.open if po else None, "spot_open_out": so.open if so else None}
    if po and so and t["perp_open_in"] and t["spot_open_in"]:
        reg = R.net(t["perp_open_in"], po.open, t["spot_open_in"], so.open, funding, hours, cash_rate(),
                    spread_cost=4 * R.half_spread(t["rank"]))
        fields.update(net_registered=reg["net"], fund_part=reg["fund"], price_part=reg["price"])
    pv, _, _, sv, _, _ = _book(api, t, t["notional"], buy_perp=False)     # the book now, even if the exit is late
    if pv and sv and t["perp_vwap_in"] and t["spot_vwap_in"]:
        rates = t.get("rates") or []
        borrow_y = (sum(rates) / len(rates) * R.HOURS_PER_YEAR) if rates else R.BORROW_Y
        bk = R.net(t["perp_vwap_in"], pv, t["spot_vwap_in"], sv, funding, hours, cash_rate(), borrow_y)
        fields.update(perp_vwap_out=pv, spot_vwap_out=sv, net_book=bk["net"])
    if x_ms < now_ms:
        fields["exit_reason"] = f"{reason}, ghi muộn {(now_ms - x_ms) // R.H_MS} giờ"
    store.update_trade(t["id"], fields)
    log(f"exit {t['symbol']} {reason} hold {hours:.0f} h registered "
        f"{(fields.get('net_registered') or 0) * 1e4:+.1f} bp book {(fields.get('net_book') or 0) * 1e4:+.1f} bp")


def _open_trade(api: Binance, borrow: Borrow, coin, h_ms: int, dev, perp_bars, spot_bars, log) -> bool:
    e_ms = h_ms + R.H_MS
    po, so = perp_bars.get(e_ms), spot_bars.get(e_ms)
    if po is None or so is None:
        log(f"signal {coin['symbol']} skipped: no open bar at entry")
        return False
    n_usdt = notional()
    pv, pfill, psp, sv, sfill, ssp = _book(api, coin, n_usdt, buy_perp=True)
    asset = coin["spot"][:-4]
    can = borrow.borrowable(coin["spot"], asset)
    inv = borrow.inventory(asset)
    rate = borrow.rate(asset)
    mx = borrow.max_borrowable(asset)
    qty = n_usdt / sv if sv else None
    fl = fillable(can, inv, qty, mx)
    note = "; ".join(borrow.notes[-3:]) if borrow.notes else None
    if not api.has_secret:
        note = ("chưa có BINANCE_API_SECRET: chưa đo lượng vay được và lãi vay" + (f"; {note}" if note else ""))
    elif fl is None and can is not False:
        note = ("Binance không trả lượng coin cho vay và tài khoản có maxBorrowable 0"
                + (f"; {note}" if note else ""))
    b_h, m_h, d_h = dev
    store.insert_trade({
        "symbol": coin["symbol"], "spot": coin["spot"], "factor": coin["factor"], "rank": coin["rank"],
        "signal_ms": h_ms, "entry_ms": e_ms, "b_h": b_h, "m_h": m_h, "d_bp": d_h * 1e4,
        "perp_open_in": po.open, "spot_open_in": so.open, "perp_vwap_in": pv, "spot_vwap_in": sv,
        "perp_fill_in": pfill, "spot_fill_in": sfill, "perp_spread_bp_in": psp, "spot_spread_bp_in": ssp,
        "entry_at": _iso(_now()), "notional": n_usdt,
        "borrowable": None if can is None else int(can), "inventory": inv,
        "inventory_usd": inv * sv if inv is not None and sv else None, "rate_hourly_in": rate,
        "max_borrowable": mx, "fillable": fl, "borrow_note": note, "status": "open",
        "rates_json": json.dumps([rate] if rate is not None else []),
    })
    log(f"signal {coin['symbol']} d {d_h * 1e4:.0f} bp rank {coin['rank']} spreads {psp}/{ssp} bp "
        f"borrowable {can} inventory {inv} rate {rate} fillable {fl}")
    return True


def tick(api: Binance, now: Optional[dt.datetime] = None, log=print) -> Dict[str, int]:
    now = now or _now()
    now_ms = int(now.timestamp() * 1000) // R.H_MS * R.H_MS
    h_ms = now_ms - R.H_MS                                     # the bar that just closed
    store.init_schema()
    if not store.run_started(now_ms, _iso(now)):
        return {"skipped": 1}
    coins_n = signals = exits = 0
    try:
        perp_info, spot_info = api.perp_info(), api.spot_info()
        tp, ts = tick_sizes(perp_info), tick_sizes(spot_info)
        borrow = Borrow(api, spot_info)
        uni = universe_for(api, h_ms // R.DAY_MS * R.DAY_MS, perp_info, spot_info, log)
        tradable = {c["symbol"]: c for c in uni if c["symbol"] not in R.NOT_TRADED}
        open_trades = store.load_trades("open")
        coins = dict(tradable)
        for t in open_trades:
            coins.setdefault(t["symbol"], {"symbol": t["symbol"], "spot": t["spot"], "factor": t["factor"],
                                           "rank": t["rank"]})
        busy = set()
        for sym, coin in sorted(coins.items()):
            try:
                b, pbars, sbars = _series(api, coin, tp, ts)
            except BinanceError as e:
                log(f"{sym}: klines failed: {e}")
                busy.update(t["symbol"] for t in open_trades if t["symbol"] == sym)
                continue
            coins_n += 1
            for t in [t for t in open_trades if t["symbol"] == sym]:
                due = R.exit_due(b, t["entry_ms"], t["m_h"], t["d_bp"] / 1e4, h_ms)
                if due is None:
                    busy.add(sym)
                    rate = borrow.rate(t["spot"][:-4])
                    if rate is not None:
                        store.update_trade(t["id"], {"rates_json": json.dumps((t.get("rates") or []) + [rate])})
                    continue
                _close_trade(api, borrow, t, due[0], due[1], now_ms, pbars, sbars, log)
                exits += 1
            if sym in tradable and sym not in busy:
                dev = R.deviation(b, h_ms)
                if dev is not None and R.is_event(dev[2]):
                    if _open_trade(api, borrow, coin, h_ms, dev, pbars, sbars, log):
                        signals += 1
        today = now_ms // R.DAY_MS * R.DAY_MS
        if not store.load_universe(today):
            build_universe(api, today, perp_info, spot_info, log)
        store.run_finished(now_ms, _iso(_now()), coins_n, signals, exits, api.has_secret)
        log(f"{_iso(now)} tick done: {coins_n} coins, {signals} signals, {exits} exits")
    except Exception as e:                          # noqa: BLE001 - the error is stored and the next cron retries
        store.run_finished(now_ms, None, coins_n, signals, exits, api.has_secret, error=str(e)[:500])
        log(f"{_iso(now)} tick failed: {e}")
        raise
    return {"coins": coins_n, "signals": signals, "exits": exits}


def check(api: Binance, log=print) -> int:
    """Probe the endpoints the runner uses; prints what works without printing any credential."""
    ok = True
    for label, fn in (("perp klines", lambda: api.perp_klines("SOLUSDT", "1h", 2)),
                      ("spot depth", lambda: api.spot_depth("SOLUSDT"))):
        try:
            fn()
            log(f"{label}: ok")
        except BinanceError as e:
            ok = False
            log(f"{label}: {e}")
    log(f"API key: {'set' if api.key else 'missing'}; secret: {'set' if api.secret else 'missing'}")
    probes = [("margin allAssets (key)", lambda: len(api.margin_assets()))]
    if api.has_secret:
        probes += [("available-inventory", lambda: len((api.inventory() or {}).get("assets") or {})),
                   ("next-hourly-interest-rate SOL", lambda: api.next_rates(["SOL"])),
                   ("maxBorrowable SOL", lambda: api.max_borrowable("SOL"))]
    for label, fn in probes:
        if not api.key:
            break
        try:
            log(f"{label}: ok ({fn()})")
        except BinanceError as e:
            ok = False
            log(f"{label}: {e}")
    return 0 if ok else 1


def from_env() -> Binance:
    return Binance(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"))


def main(argv: List[str]) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    cmd = argv[1] if len(argv) > 1 else "tick"
    if cmd == "tick":
        time.sleep(float(os.environ.get("BASIS_B_START_DELAY", "3")))
        tick(from_env())
        return 0
    if cmd == "check":
        return check(from_env())
    if cmd == "status":
        from app.basis_b_status import status
        print(json.dumps(status(), indent=2, ensure_ascii=False, default=str))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
