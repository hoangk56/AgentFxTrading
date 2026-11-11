"""A2-D5L executor: long the Binance USDT-M perp / short BTCUSDT 5 s after an Upbit KRW-listing notice, close both at
the Upbit KRW open. Rule: research/results/portfolio/round65_retail_venues/A2/PREREG_A2_D5L.md. Docs: docs/a2-live.md.

The notice comes from the Telegram capture (`tg_pull.py`, round 74 TG2), which appends every @upbit_news post to
`pull_log.csv` in A2_CAPTURE_DIR within ~1.5 s of its post time. This process tails that file and never touches
Telegram, so the capture test keeps running unchanged.

Dry run unless A2_LIVE=1: the same path runs end to end and the fills are taken at the book (ask for a buy, bid for a
sell), so the dry-run log is what the live run would have done. Live needs A2_BINANCE_KEY / A2_BINANCE_SECRET (a
futures-only key, no withdrawals, IP-restricted) on an account in one-way mode that nothing else trades.

Usage:
    python -m app.a2_live run          # the loop (cron + flock keeps one running)
    python -m app.a2_live check        # config, key, position mode, balance; sends no order
    python -m app.a2_live status       # open events and the closed trades
    python -m app.a2_live close-all    # flatten every open event now
"""
import csv
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

log = logging.getLogger("a2_live")

FAPI = "https://fapi.binance.com"
UPBIT = "https://api.upbit.com"
UA = "agentfx-a2-live/1"
BTC = "BTCUSDT"
ENTRY_DELAY_S = 5.0     # registered: each leg's first trade >= N + 5 s
PRICE_LEAD_S = 0.3      # read the book this long before N + 5 s, so the order itself goes out on time
MIN_PERP_AGE_D = 7.0    # registered: the perp traded >= 7 days before N
FEE_BP = 20.0           # registered cost: four taker fills
POLL_FILE_S = 0.2
PERPS_EVERY_S = 300     # background exchangeInfo refresh; the cache is used up to 600 s old
POLL_UPBIT_S = 2.0
CLOSE_RETRY_S = 30.0
TRADE_FIELDS = ["msg_id", "coin", "perp", "mode", "notional", "post_utc", "detect_utc", "entry_utc", "alt_qty",
                "alt_entry", "alt_ask_before", "btc_qty", "btc_entry", "btc_bid_before", "krw_open_utc", "exit_utc",
                "alt_exit", "btc_exit", "exit_reason", "net_bp", "note"]


# ------------------------------------------------------------------------------------------------------------ config
@dataclass
class Config:
    live: bool = False
    key: Optional[str] = None
    secret: Optional[str] = None
    notional: float = 0.0           # USDT per leg at full size
    phasein_trades: int = 10
    phasein_fraction: float = 0.25
    leverage: int = 3
    max_open: int = 3
    max_entry_delay_s: float = 10.0
    max_hold_h: float = 6.0
    capture_dir: str = "/home/forge/tg_capture_a2"
    state_dir: str = "data/a2_live"

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Config":
        g = lambda k, d: (env.get(k) or "").strip() or d          # noqa: E731
        return cls(live=g("A2_LIVE", "0") == "1", key=g("A2_BINANCE_KEY", None), secret=g("A2_BINANCE_SECRET", None),
                   notional=float(g("A2_NOTIONAL_USDT", "0")), phasein_trades=int(g("A2_PHASEIN_TRADES", "10")),
                   phasein_fraction=float(g("A2_PHASEIN_FRACTION", "0.25")), leverage=int(g("A2_LEVERAGE", "3")),
                   max_open=int(g("A2_MAX_OPEN", "3")), max_entry_delay_s=float(g("A2_MAX_ENTRY_DELAY_S", "10")),
                   max_hold_h=float(g("A2_MAX_HOLD_H", "6")),
                   capture_dir=g("A2_CAPTURE_DIR", "/home/forge/tg_capture_a2"),
                   state_dir=g("A2_STATE_DIR", "data/a2_live"))

    def problems(self) -> List[str]:
        """Why a live run must not start ([] = fine). A dry run needs none of these."""
        out = []
        if self.live:
            if not (self.key and self.secret):
                out.append("A2_LIVE=1 needs A2_BINANCE_KEY and A2_BINANCE_SECRET")
            if self.notional <= 0:
                out.append("A2_LIVE=1 needs A2_NOTIONAL_USDT > 0")
        if not 1 <= self.leverage <= 20:
            out.append("A2_LEVERAGE must be 1..20")
        return out


# -------------------------------------------------------------------------------------------------------------- http
class HttpError(Exception):
    def __init__(self, code: int, body: str, path: str = ""):
        super().__init__(f"{path} HTTP {code}: {body[:200]}")
        self.code, self.body = code, body

    def binance_code(self) -> Optional[int]:
        try:
            return int(json.loads(self.body).get("code"))
        except (ValueError, TypeError, AttributeError):
            return None


def http_json(method: str, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 5.0,
              opener: Callable = urllib.request.urlopen) -> Any:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, **(headers or {})})
    try:
        with opener(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.read().decode(errors="replace"), urllib.parse.urlsplit(url).path) from None


class Futures:
    """Binance USDT-M REST: public reads and the few signed calls the executor needs. Never logs the key."""

    def __init__(self, key: Optional[str] = None, secret: Optional[str] = None, http: Callable = http_json):
        self.key, self.secret, self.http = key, secret, http

    def public(self, path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Any:
        q = urllib.parse.urlencode(params or {})
        return self.http("GET", f"{FAPI}{path}" + (f"?{q}" if q else ""), timeout=timeout)

    def signed(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not (self.key and self.secret):
            raise HttpError(0, "no API key/secret", path)
        p = dict(params or {}, timestamp=int(time.time() * 1000), recvWindow=5000)
        q = urllib.parse.urlencode(p)
        q += "&signature=" + hmac.new(self.secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        return self.http(method, f"{FAPI}{path}?{q}", headers={"X-MBX-APIKEY": self.key})

    def exchange_info(self) -> Dict[str, Any]:
        return self.public("/fapi/v1/exchangeInfo", timeout=15)

    def book(self, symbol: str) -> Tuple[float, float]:
        b = self.public("/fapi/v1/ticker/bookTicker", {"symbol": symbol})
        return float(b["bidPrice"]), float(b["askPrice"])

    def dual_side(self) -> bool:
        return bool(self.signed("GET", "/fapi/v1/positionSide/dual").get("dualSidePosition"))

    def balance(self) -> Dict[str, Any]:
        return self.signed("GET", "/fapi/v3/account")

    def set_leverage(self, symbol: str, leverage: int) -> Any:
        return self.signed("POST", "/fapi/v1/leverage", {"symbol": symbol, "leverage": leverage})

    def set_cross(self, symbol: str) -> None:
        try:
            self.signed("POST", "/fapi/v1/marginType", {"symbol": symbol, "marginType": "CROSSED"})
        except HttpError as e:
            if e.binance_code() != -4046:          # -4046: already cross
                raise

    def order(self, symbol: str, side: str, qty: str, reduce_only: bool = False) -> Dict[str, Any]:
        p = {"symbol": symbol, "side": side, "type": "MARKET", "quantity": qty, "newOrderRespType": "RESULT"}
        if reduce_only:
            p["reduceOnly"] = "true"
        return self.signed("POST", "/fapi/v1/order", p)


class Upbit:
    """The KRW open: Upbit's first 1m candle of KRW-<coin> (the research's L). Before the market opens the quotation
    API answers 404 "Code not found" or an empty list."""

    def __init__(self, http: Callable = http_json):
        self.http = http

    def first_candle(self, coin: str) -> Optional[str]:
        try:
            r = self.http("GET", f"{UPBIT}/v1/candles/minutes/1?market=KRW-{coin}&count=1", timeout=5)
        except HttpError as e:
            if e.code in (400, 404):
                return None
            raise
        return r[0].get("candle_date_time_utc") if r else None


# ------------------------------------------------------------------------------------------------------- the notice
def krw_listing(t: str) -> bool:
    # Same test as tg_pull.krw_listing (round 74 TG2), which the capture test uses.
    return (t.startswith("[거래]") and ("KRW" in t or "원화" in t) and "종료" not in t and "유의" not in t
            and any(k in t for k in ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")))


def krw_tickers(t: str) -> List[str]:
    """Same as tg_pull.krw_tickers: a coin followed by its own market list without KRW is left out."""
    out: List[str] = []
    for m in re.finditer(r"\(([A-Z0-9]{1,15})\)(\(([^)]*)\))?", t):
        markets = m.group(3)
        if markets is not None and "마켓" in markets and "KRW" not in markets:
            continue
        if m.group(1) not in ("KRW", "BTC", "USDT") and m.group(1) not in out:
            out.append(m.group(1))
    return out


def read_posts(path: str) -> List[Tuple[int, float, str]]:
    """(msg id, post epoch, text) of the KRW-listing posts in pull_log.csv, one per id."""
    if not os.path.exists(path):
        return []
    out, seen = [], set()
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                mid = int(r["msg_id"])
            except (KeyError, TypeError, ValueError):
                continue
            if mid in seen or not krw_listing(r.get("text") or ""):
                continue
            seen.add(mid)
            out.append((mid, dt.datetime.fromisoformat(r["post_utc"]).timestamp(), r["text"]))
    return out


# ----------------------------------------------------------------------------------------------------------- sizing
def lot_filters(info: Dict[str, Any]) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
    """(step, min qty, max qty, min notional) for a MARKET order."""
    f = {x["filterType"]: x for x in info.get("filters", [])}
    lot = f.get("MARKET_LOT_SIZE") or f["LOT_SIZE"]
    return (Decimal(lot["stepSize"]), Decimal(lot["minQty"]), Decimal(lot["maxQty"]),
            Decimal(f.get("MIN_NOTIONAL", {}).get("notional", "0")))


def leg_qty(notional: float, price: float, info: Dict[str, Any]) -> Decimal:
    """Quantity for `notional` USDT, floored to the step and capped at the market max; 0 when below the minimums."""
    step, mn, mx, min_notional = lot_filters(info)
    q = (Decimal(str(notional)) / Decimal(str(price)) / step).to_integral_value(ROUND_DOWN) * step
    q = min(q, (mx / step).to_integral_value(ROUND_DOWN) * step)
    if q < mn or q * Decimal(str(price)) < min_notional:
        return Decimal(0)
    return q


def qty_str(q: Decimal) -> str:
    return format(q.normalize(), "f")


def net_bp(alt_in: float, alt_out: float, btc_in: float, btc_out: float) -> float:
    """Registered arithmetic: long alt minus short BTC at equal notional, less 20 bp."""
    return ((alt_out / alt_in - 1) - (btc_out / btc_in - 1)) * 1e4 - FEE_BP


def iso(t: Optional[float]) -> str:
    return "" if t is None else dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


# ------------------------------------------------------------------------------------------------------------ store
class Store:
    """state.json (processed post ids, open events) and trades.csv (one row per closed or skipped event)."""

    def __init__(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        self.folder = folder
        self.state_path = os.path.join(folder, "state.json")
        self.trades_path = os.path.join(folder, "trades.csv")
        self.lock = threading.RLock()
        self.state = (json.load(open(self.state_path)) if os.path.exists(self.state_path)
                      else {"seen": [], "open": {}})

    def save(self) -> None:
        with self.lock:
            tmp = self.state_path + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(self.state, fh, indent=1)
            os.replace(tmp, self.state_path)

    def seen(self) -> set:
        return set(self.state["seen"])

    def mark_seen(self, ids) -> None:
        with self.lock:
            self.state["seen"] = sorted(set(self.state["seen"]) | set(ids))
            self.save()

    def open_events(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return {k: dict(v) for k, v in self.state["open"].items()}

    def put_open(self, key: str, ev: Dict[str, Any]) -> None:
        with self.lock:
            self.state["open"][key] = ev
            self.save()

    def drop_open(self, key: str) -> None:
        with self.lock:
            self.state["open"].pop(key, None)
            self.save()

    def append_trade(self, row: Dict[str, Any]) -> None:
        with self.lock:
            new = not os.path.exists(self.trades_path)
            with open(self.trades_path, "a", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=TRADE_FIELDS, extrasaction="ignore")
                if new:
                    w.writeheader()
                w.writerow({k: row.get(k, "") for k in TRADE_FIELDS})

    def trades(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.trades_path):
            return []
        with open(self.trades_path, newline="") as fh:
            return list(csv.DictReader(fh))

    def live_entries(self) -> int:
        n = sum(1 for r in self.trades() if r["mode"] == "live" and r["alt_entry"])
        return n + sum(1 for e in self.open_events().values() if e.get("mode") == "live")

    def stopped(self) -> bool:
        return os.path.exists(os.path.join(self.folder, "STOP_A2"))


# --------------------------------------------------------------------------------------------------------- executor
class Skip(Exception):
    pass


class Executor:
    def __init__(self, cfg: Config, fut: Futures, upbit: Upbit, store: Store, now: Callable[[], float] = time.time,
                 sleep: Callable[[float], None] = time.sleep, notify: Callable[[str], Any] = lambda text: None):
        self.cfg, self.fut, self.upbit, self.store = cfg, fut, upbit, store
        self.now, self.sleep, self.notify = now, sleep, notify
        self.mode = "live" if cfg.live else "dry"
        self._perps: Dict[str, Dict[str, Any]] = {}
        self._perps_at = 0.0
        self._prepared: set = set()

    # ---- market data
    def perps(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        if force or self.now() - self._perps_at > 600:
            info = self.fut.exchange_info()
            self._perps = {s["symbol"]: s for s in info["symbols"] if s.get("contractType") == "PERPETUAL"
                           and s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING"}
            self._perps_at = self.now()
        return self._perps

    def find_perp(self, coin: str) -> Optional[Dict[str, Any]]:
        for force in (False, True):
            p = self.perps(force)
            for sym in (f"{coin}USDT", f"1000{coin}USDT", f"1000000{coin}USDT"):
                if sym in p:
                    return p[sym]
        return None

    # ---- orders
    def _order(self, symbol: str, side: str, qty: Decimal, reduce_only: bool = False) -> Tuple[float, Decimal]:
        """(average price, filled qty). Dry run fills the whole qty at the book."""
        if not self.cfg.live:
            bid, ask = self.fut.book(symbol)
            return (ask if side == "BUY" else bid), qty
        r = self.fut.order(symbol, side, qty_str(qty), reduce_only)
        filled = Decimal(str(r.get("executedQty", "0")))
        if filled <= 0:
            raise HttpError(0, f"order not filled: status {r.get('status')}", "/fapi/v1/order")
        return float(r["avgPrice"]), filled

    def _prepare(self, symbol: str) -> None:
        if not self.cfg.live or symbol in self._prepared:
            return
        self.fut.set_cross(symbol)
        self.fut.set_leverage(symbol, self.cfg.leverage)
        self._prepared.add(symbol)

    def _both(self, fns: List[Callable[[], Any]]) -> List[Any]:
        """Run the calls at once; each result is the value or the exception."""
        out: List[Any] = [None] * len(fns)

        def go(i, fn):
            try:
                out[i] = fn()
            except Exception as e:      # noqa: BLE001 - the caller handles each leg's failure
                out[i] = e
        ts = [threading.Thread(target=go, args=(i, fn)) for i, fn in enumerate(fns)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        return out

    def notional(self) -> float:
        full = self.cfg.notional if self.cfg.notional > 0 else 1000.0     # dry run without a size: 1,000 USDT
        if self.cfg.live and self.store.live_entries() < self.cfg.phasein_trades:
            return full * self.cfg.phasein_fraction
        return full

    # ---- one listed coin
    def handle(self, msg_id: int, coin: str, post_t: float) -> Optional[Dict[str, Any]]:
        """Enter one event, or record why not. Returns the open event (the exit is watched by the caller)."""
        row: Dict[str, Any] = {"msg_id": msg_id, "coin": coin, "mode": self.mode, "post_utc": iso(post_t),
                               "detect_utc": iso(self.now())}
        try:
            if self.store.stopped():
                raise Skip("STOP_A2 present")
            p = self.find_perp(coin)
            if p is None:
                raise Skip("no Binance USDT-M perp")
            perp = row["perp"] = p["symbol"]
            age = (post_t - p["onboardDate"] / 1000) / 86400
            if age < MIN_PERP_AGE_D:
                raise Skip(f"perp {age:.1f} d old < {MIN_PERP_AGE_D:.0f} d")
            if len(self.store.open_events()) >= self.cfg.max_open:
                raise Skip(f"{self.cfg.max_open} events already open")
            notional = row["notional"] = round(self.notional(), 2)
            for r in self._both([lambda: self._prepare(perp), lambda: self._prepare(BTC)]):
                if isinstance(r, Exception):
                    raise Skip(f"leverage / margin setup failed: {r}")
            wait = post_t + ENTRY_DELAY_S - PRICE_LEAD_S - self.now()
            if wait > 0:
                self.sleep(wait)
            if self.now() > post_t + self.cfg.max_entry_delay_s:
                raise Skip(f"late: {self.now() - post_t:.1f} s after the notice")
            (ab, aa), (bb, ba) = self._both([lambda: self.fut.book(perp), lambda: self.fut.book(BTC)])
            row.update(alt_ask_before=aa, btc_bid_before=bb)
            q_alt, q_btc = leg_qty(notional, aa, p), leg_qty(notional, bb, self.perps()[BTC])
            if q_alt <= 0 or q_btc <= 0:
                raise Skip(f"size below the market minimum at {notional} USDT")
            wait = post_t + ENTRY_DELAY_S - self.now()
            if wait > 0:
                self.sleep(wait)
            row["entry_utc"] = iso(self.now())
            alt, btc = self._both([lambda: self._order(perp, "BUY", q_alt), lambda: self._order(BTC, "SELL", q_btc)])
            if isinstance(alt, Exception) or isinstance(btc, Exception):
                self._unwind(perp, alt, btc)
                raise Skip(f"entry failed: alt {alt if isinstance(alt, Exception) else 'ok'}, "
                           f"btc {btc if isinstance(btc, Exception) else 'ok'}")
        except Skip as e:
            row["exit_reason"], row["note"] = "skipped", str(e)
            self.store.append_trade(row)
            log.info("A2 %s %s skipped: %s", msg_id, coin, e)
            if row.get("perp"):
                self.notify(f"A2 [{self.mode}] bỏ qua {coin} ({row['perp']}): {e}")
            return None
        ev = dict(row, alt_entry=alt[0], alt_qty=qty_str(alt[1]), btc_entry=btc[0], btc_qty=qty_str(btc[1]),
                  opened_at=self.now())
        self.store.put_open(f"{msg_id}:{coin}", ev)
        log.info("A2 %s %s entered %s: long %s @ %s, short BTC %s @ %s", msg_id, coin, self.mode, ev["alt_qty"],
                 alt[0], ev["btc_qty"], btc[0])
        self.notify(f"A2 [{self.mode}] vào {coin}: long {ev['alt_qty']} {perp} @ {alt[0]}, short {ev['btc_qty']} "
                    f"BTC @ {btc[0]} ({notional} USDT/chân), {self.now() - post_t:.1f} s sau tin")
        return ev

    def _unwind(self, perp: str, alt: Any, btc: Any) -> None:
        """One leg filled and the other did not: close the filled one at once."""
        for sym, side, res in ((perp, "SELL", alt), (BTC, "BUY", btc)):
            if not isinstance(res, Exception):
                try:
                    self._order(sym, side, res[1], reduce_only=True)
                except Exception as e:       # noqa: BLE001
                    log.error("A2 unwind of %s failed, close it by hand: %s", sym, e)

    # ---- exit
    def watch_exit(self, key: str) -> None:
        """Poll Upbit until the KRW market opens (or the max hold), then close both legs; retries until closed."""
        ev = self.store.open_events()[key]
        deadline = ev["opened_at"] + self.cfg.max_hold_h * 3600
        reason, krw_open = "max hold", ""
        while self.now() < deadline:
            if key not in self.store.open_events():
                return                                   # closed elsewhere (close-all)
            try:
                c = self.upbit.first_candle(ev["coin"])
            except Exception as e:                       # noqa: BLE001 - keep polling
                log.warning("A2 Upbit poll %s: %s", ev["coin"], e)
                c = None
            if c:
                reason, krw_open = "krw open", c
                break
            self.sleep(POLL_UPBIT_S)
        self.close(key, reason, krw_open)

    def close(self, key: str, reason: str, krw_open: str = "") -> Dict[str, Any]:
        ev = self.store.open_events().get(key)
        if ev is None:
            return {}
        legs = {"alt": (ev["perp"], "SELL", Decimal(ev["alt_qty"])), "btc": (BTC, "BUY", Decimal(ev["btc_qty"]))}
        done: Dict[str, float] = {}
        tries = 0
        while len(done) < 2:
            todo = [k for k in legs if k not in done]
            res = self._both([lambda k=k: self._order(*legs[k], reduce_only=True) for k in todo])
            for k, r in zip(todo, res):
                if not isinstance(r, Exception):
                    done[k] = r[0]
                elif isinstance(r, HttpError) and r.binance_code() == -2022:     # nothing left to reduce
                    done[k] = float("nan")
            if len(done) < 2:
                tries += 1
                log.error("A2 close %s failed (try %d): %s", key, tries, [str(r) for r in res if isinstance(r, Exception)])
                self.sleep(CLOSE_RETRY_S)
        ev.update(exit_utc=iso(self.now()), krw_open_utc=krw_open, exit_reason=reason, alt_exit=done["alt"],
                  btc_exit=done["btc"])
        if all(x == x for x in (done["alt"], done["btc"])):      # not NaN
            ev["net_bp"] = round(net_bp(ev["alt_entry"], done["alt"], ev["btc_entry"], done["btc"]), 1)
        self.store.append_trade(ev)
        self.store.drop_open(key)
        log.info("A2 %s closed (%s): net %s bp", key, reason, ev.get("net_bp"))
        self.notify(f"A2 [{ev['mode']}] đóng {ev['coin']} ({reason}): net {ev.get('net_bp', '?')} bp")
        return ev


# -------------------------------------------------------------------------------------------------------------- loop
def run(cfg: Config, ex: Executor, until: Optional[float] = None) -> int:
    pull_log = os.path.join(cfg.capture_dir, "pull_log.csv")
    store = ex.store
    if not store.state["seen"]:                          # first start: never trade posts that came before it
        store.mark_seen(m for m, _, _ in read_posts(pull_log))
    for key in store.open_events():                      # resume exits after a restart
        threading.Thread(target=ex.watch_exit, args=(key,), daemon=True).start()
    ex.perps(force=True)                                 # exchangeInfo takes seconds: never load it at a notice

    def keep_perps():
        while True:
            time.sleep(PERPS_EVERY_S)
            try:
                ex.perps(force=True)
            except Exception as e:                       # noqa: BLE001 - the cached list stays in use
                log.warning("A2 exchangeInfo refresh: %s", e)
    threading.Thread(target=keep_perps, daemon=True).start()
    log.info("A2 executor started (%s), %d open", ex.mode, len(store.open_events()))
    while until is None or time.time() < until:
        seen = store.seen()
        new = [(m, t, x) for m, t, x in read_posts(pull_log) if m not in seen]
        if new:
            store.mark_seen(m for m, _, _ in new)
        for msg_id, post_t, text in new:
            for coin in krw_tickers(text):
                def one(m=msg_id, c=coin, t=post_t):
                    ev = ex.handle(m, c, t)
                    if ev is not None:
                        ex.watch_exit(f"{m}:{c}")
                threading.Thread(target=one, daemon=True).start()
        time.sleep(POLL_FILE_S)
    return 0


def check(cfg: Config, fut: Futures) -> int:
    print(f"mode {'LIVE' if cfg.live else 'dry run'}; notional {cfg.notional} USDT/leg; leverage {cfg.leverage}; "
          f"max open {cfg.max_open}; phase-in {cfg.phasein_trades} trades x {cfg.phasein_fraction}")
    print(f"capture {cfg.capture_dir}/pull_log.csv: {'found' if os.path.exists(os.path.join(cfg.capture_dir, 'pull_log.csv')) else 'MISSING'}")
    print(f"key: {'set' if cfg.key else 'missing'}; secret: {'set' if cfg.secret else 'missing'}")
    for p in cfg.problems():
        print("problem:", p)
    if cfg.key and cfg.secret:
        try:
            print("one-way mode:", "no (hedge mode: switch it off)" if fut.dual_side() else "yes")
            acc = fut.balance()
            print(f"available balance {acc.get('availableBalance')} USDT, wallet {acc.get('totalWalletBalance')}")
        except HttpError as e:
            print("signed call failed:", e)
            if e.binance_code() == -2015:
                print("hint: the key needs Enable Futures and the IP restriction 204.168.144.232 (Binance enables futures only on IP-restricted keys)")
            return 1
    print("upbit candles:", "ok" if Upbit().first_candle("BTC") else "no answer")
    return 0 if not cfg.problems() else 1


def status(store: Store) -> int:
    for k, e in store.open_events().items():
        print("open", k, e["mode"], e["perp"], "since", e["entry_utc"])
    for r in store.trades():
        print(r["post_utc"], r["coin"], r["mode"], r["exit_reason"], r["net_bp"] or "-", r["note"])
    return 0


def main(argv: List[str]) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = Config.from_env()
    fut = Futures(cfg.key, cfg.secret)
    store = Store(cfg.state_dir)
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "check":
        return check(cfg, fut)
    if cmd == "status":
        return status(store)
    from app.alerts import notify, setup_alerts
    setup_alerts()
    ex = Executor(cfg, fut, Upbit(), store, notify=notify)
    if cmd == "close-all":
        for key in store.open_events():
            ex.close(key, "close-all")
        return 0
    if cmd == "run":
        if cfg.problems():
            for p in cfg.problems():
                log.error("A2 executor not started: %s", p)
            return 2
        if cfg.live:
            try:
                hedge = fut.dual_side()
            except HttpError as e:     # -2015: wrong key, IP not whitelisted, or futures not enabled on the key
                log.error("A2 executor not started: Binance refused the key (%s); run `python -m app.a2_live check`", e)
                return 2
            if hedge:
                log.error("A2 executor not started: the futures account is in hedge mode; switch to one-way")
                return 2
        return run(cfg, ex)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
