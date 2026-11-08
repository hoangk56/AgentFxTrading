"""Active MTProto fetcher for Upbit's official Telegram channel @upbit_news (round 74 TG2, A2-D5L capture test).

Why: the passive push logger (tg_push.py, Telethon `events.NewMessage`) got posts 11-58 s after their post time.
Telegram documents that it "may stop sending updates (or send fewer updates) for some channels/supergroups", and that
user clients should "additionally invoke updates.getChannelDifference periodically for channels ... the user is
currently viewing" (core.telegram.org/api/updates); TDLib: "in supergroups and channels all updates are received only
for opened chats" (td_api::openChat). This script does that short-poll itself and logs when each new post is first
returned, so the delay is (poll phase + RTT) instead of Telegram's passive schedule.

- Method `diff` (default): updates.getChannelDifference(pts) every PERIOD s; new_messages are the new posts. The
  server's suggested `timeout` is logged (not obeyed below PERIOD: the measurement needs the fast poll).
- Method `ids`: channels.getMessages([last_id + 1, last_id + 2]); a post exists when the result is not MessageEmpty.
- Method `alt`: alternate diff / ids each tick (each method then sampled every 2 x PERIOD s).
- Period: default 2 s, never < 1 s. FloodWait n s -> sleep n s, double the period (cap 60 s), log; FloodWait > 300 s
  -> stop. Auth errors (401 family, AUTH_KEY_DUPLICATED) -> write STOP_PULL and stop. Hard end time (required).
- The client connects with receive_updates=False (invokeWithoutUpdates), so it does not take the account's update
  stream away from tg_push.py when it runs on a copy of the same session.
- Read only on Telegram: no message is sent, nothing is joined. No order.
- Paper entry (added 2026-11-08, same as tg_push.py): for a KRW-listing post, outside the poll loop, the Binance
  USDT-M perp of each listed coin (also 1000x / 1000000x), its age (eligible when onboardDate <= N - 7 d), and the
  public bookTicker of the alt perp and BTCUSDT at receive time and at max(N + 5 s, now) = the paper entry (long alt
  at the ask, short BTC at the bid). Public market data only; the exit and the net are graded later by fwd_a2.py.

Files (working directory, never in git): pull.session (a COPY of push.session; chmod 600), push.env (read for
TG_API_ID / TG_API_HASH, never printed), pull_log.csv (one row per post per method), pull_paper.csv (one row per
listed coin), pull_heartbeat.log (every 10 min: calls, errors, RTT, server timeout, period), pull_state.json (pts,
last id), STOP_PULL (stop marker).
Usage:
  venv-push/bin/python -I tg_pull.py run <until, e.g. 2026-11-09T00:00Z> [period_s=2] [method=diff]
  venv-push/bin/python -I tg_pull.py report"""
import asyncio, csv, datetime as dt, json, os, re, statistics, sys, time, urllib.request

CH = "upbit_news"
UA = "agentfx-a2-pull/1"
FAPI = "https://fapi.binance.com"
PERPS_EVERY = 300
PAPER_FIELDS = ["msg_id", "coin", "perp", "post_utc", "recv_utc", "perp_age_d", "eligible", "detect_utc",
                "detect_alt_bid", "detect_alt_ask", "detect_btc_bid", "detect_btc_ask", "entry_utc", "entry_alt_ask",
                "entry_btc_bid", "entry_alt_spread_bp", "note"]
SESSION = "pull"
PERIOD = 2.0
MIN_PERIOD = 1.0
MAX_PERIOD = 60.0
FLOOD_STOP = 300
MAX_STREAK = 30
HB_EVERY = 600
LOG_FIELDS = ["msg_id", "post_utc", "recv_utc", "recv_minus_post_s", "method", "rtt_s", "period_s", "krw_listing",
              "text"]
HERE = os.getcwd()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def parse_until(s):
    """'2026-11-09T00:00Z' -> epoch s (UTC). Required: a run without an end time is refused."""
    if not s:
        raise ValueError("end time required, e.g. 2026-11-09T00:00Z")
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("end time must be UTC (end with Z)")
    return t.timestamp()


def clamp_period(p):
    return min(MAX_PERIOD, max(MIN_PERIOD, float(p)))


def after_flood(period, seconds):
    """(new period, stop?) after a FloodWait of `seconds`."""
    return clamp_period(period * 2), seconds > FLOOD_STOP


def krw_listing(t):
    # Same test as tg_capture.krw_listing / tg_push.krw_listing (round 73).
    return int(t.startswith("[거래]") and ("KRW" in t or "원화" in t) and "종료" not in t and "유의" not in t
               and any(k in t for k in ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")))


def krw_tickers(t):
    """Same as tg_push.krw_tickers (copied: `python -I` does not put the script's folder on sys.path). A coin
    followed by its own market list without KRW is left out; without per-coin lists every ticker counts."""
    out = []
    for m in re.finditer(r"\(([A-Z0-9]{1,15})\)(\(([^)]*)\))?", t):
        markets = m.group(3)
        if markets is not None and "마켓" in markets and "KRW" not in markets:
            continue
        if m.group(1) not in ("KRW", "BTC", "USDT") and m.group(1) not in out:
            out.append(m.group(1))
    return out


def http_json(url, timeout=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class Perps:
    """USDT-M perpetuals from exchangeInfo. run_live refreshes it in the background, so a listing does not wait for
    a 10 s exchangeInfo call; a miss forces one refresh."""

    def __init__(self, fetch=None):
        self.fetch = fetch or (lambda: http_json(f"{FAPI}/fapi/v1/exchangeInfo", timeout=10))
        self.by_symbol, self.at = {}, 0.0

    def refresh(self, force=False):
        if not force and time.time() - self.at < 600:
            return
        self.by_symbol = {s["symbol"]: s for s in self.fetch()["symbols"]
                          if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT"
                          and s.get("status") == "TRADING"}
        self.at = time.time()

    def find(self, coin):
        for force in (False, True):
            self.refresh(force)
            for sym in (f"{coin}USDT", f"1000{coin}USDT", f"1000000{coin}USDT"):
                if sym in self.by_symbol:
                    return self.by_symbol[sym]
        return None


def book(sym):
    b = http_json(f"{FAPI}/fapi/v1/ticker/bookTicker?symbol={sym}")
    return float(b["bidPrice"]), float(b["askPrice"])


async def paper(msg_id, coin, post_t, recv_t, perps, hb, here=HERE, book=book):
    """One pull_paper.csv row per listed coin; never raises (errors go to the row's note and the heartbeat)."""
    r = dict(msg_id=msg_id, coin=coin, post_utc=iso(post_t), recv_utc=iso(recv_t), perp="", perp_age_d="",
             eligible=0, note="")
    try:
        p = await asyncio.to_thread(perps.find, coin)
        if p is None:
            r["note"] = "no Binance USDT-M perp"
            return
        sym = p["symbol"]
        r["perp"] = sym
        age = (post_t - p["onboardDate"] / 1000) / 86400
        r["perp_age_d"] = round(age, 2)
        r["eligible"] = int(age >= 7)
        (ab, aa), (bb, ba) = await asyncio.gather(asyncio.to_thread(book, sym), asyncio.to_thread(book, "BTCUSDT"))
        r.update(detect_utc=iso(time.time()), detect_alt_bid=ab, detect_alt_ask=aa, detect_btc_bid=bb,
                 detect_btc_ask=ba)
        wait = post_t + 5 - time.time()
        if wait > 0:
            await asyncio.sleep(wait)
        (ab, aa), (bb, ba) = await asyncio.gather(asyncio.to_thread(book, sym), asyncio.to_thread(book, "BTCUSDT"))
        r.update(entry_utc=iso(time.time()), entry_alt_ask=aa, entry_btc_bid=bb,
                 entry_alt_spread_bp=round((aa - ab) / ((aa + ab) / 2) * 1e4, 1))
    except Exception as e:
        r["note"] = f"{type(e).__name__}: {str(e)[:120]}"
        hb.write(f"{iso(time.time())} paper error {coin}: {r['note']}\n")
    finally:
        append(os.path.join(here, "pull_paper.csv"), PAPER_FIELDS, r)


def row(msg_id, post_t, recv_t, method, rtt, period, text):
    txt = " ".join((text or "").split())
    return dict(msg_id=msg_id, post_utc=iso(post_t), recv_utc=iso(recv_t), recv_minus_post_s=round(recv_t - post_t, 3),
                method=method, rtt_s=round(rtt, 3), period_s=period, krw_listing=krw_listing(txt), text=txt[:160])


def real_posts(messages):
    """Channel posts (not MessageEmpty / MessageService) as (id, post epoch, text)."""
    out = []
    for m in messages or []:
        if type(m).__name__ != "Message" or getattr(m, "date", None) is None:
            continue
        out.append((m.id, m.date.timestamp(), getattr(m, "message", "") or ""))
    return sorted(out)


def diff_result(r):
    """(kind, new pts or None, posts, server timeout or None) of an updates.getChannelDifference result."""
    kind = type(r).__name__
    timeout = getattr(r, "timeout", None)
    if kind == "ChannelDifferenceEmpty":
        return kind, r.pts, [], timeout
    if kind == "ChannelDifference":
        return kind, r.pts, real_posts(r.new_messages), timeout
    if kind == "ChannelDifferenceTooLong":
        # dialog.pts is the new state; messages are the latest ones
        return kind, getattr(getattr(r, "dialog", None), "pts", None), real_posts(r.messages), timeout
    raise ValueError(f"unexpected result {kind}")


class Seen:
    """First receipt per (method, msg id); posts at or below `floor` (known at start) are never logged."""

    def __init__(self, floor, done=()):
        self.floor = floor
        self.done = set(done)

    def new(self, method, msg_id):
        if msg_id <= self.floor or (method, msg_id) in self.done:
            return False
        self.done.add((method, msg_id))
        return True


def append(path, fields, r):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerow(r)


def quantiles(xs):
    xs = sorted(xs)
    q = lambda p: xs[min(len(xs) - 1, int(p * len(xs)))]
    return dict(n=len(xs), median=statistics.median(xs), p80=q(0.8), p90=q(0.9), max=xs[-1],
                le3=sum(x <= 3 for x in xs))


class Poller:
    """The loop without Telethon: `call(name, **kw)` is an async function returning Telethon-like objects or raising
    FloodWait(seconds) / AuthStop; `now` / `sleep` are injectable for tests."""

    def __init__(self, call, end, period=PERIOD, method="diff", here=HERE, now=time.time, sleep=asyncio.sleep,
                 on_post=None):
        if method not in ("diff", "ids", "alt"):
            raise ValueError(method)
        self.call, self.end, self.period, self.method = call, end, clamp_period(period), method
        # on_post(msg_id, post_t, recv_t, text): once per post id (first method that sees it); must not block
        self.on_post, self.posted = on_post, set()
        self.here, self.now, self.sleep = here, now, sleep
        self.state_path = os.path.join(here, "pull_state.json")
        self.log_path = os.path.join(here, "pull_log.csv")
        self.hb = open(os.path.join(here, "pull_heartbeat.log"), "a", buffering=1)
        self.calls = self.errors = 0
        self.rtts, self.timeouts = [], []

    def beat(self, msg):
        self.hb.write(f"{iso(self.now())} {msg}\n")

    def save(self, st):
        json.dump(st, open(self.state_path + ".tmp", "w"))
        os.replace(self.state_path + ".tmp", self.state_path)

    def log_posts(self, posts, method, t0, t1, seen, st):
        for mid, post_t, text in posts:
            if seen.new(method, mid):
                append(self.log_path, LOG_FIELDS, row(mid, post_t, t1, method, t1 - t0, self.period, text))
                if self.on_post is not None and mid not in self.posted:
                    self.posted.add(mid)
                    try:
                        self.on_post(mid, post_t, t1, text)
                    except Exception as e:  # the paper side must never stop the capture
                        self.beat(f"on_post error {type(e).__name__}: {str(e)[:100]}")
            st["last_id"] = max(st["last_id"], mid)

    async def start_state(self):
        st = json.load(open(self.state_path)) if os.path.exists(self.state_path) else {}
        full = await self.call("full")  # channels.getFullChannel: current pts
        last = await self.call("last")  # messages.getHistory(limit=1): newest id
        st = dict(pts=full, last_id=max(st.get("last_id", 0), last), floor=max(st.get("floor", 0), last))
        self.save(st)
        return st

    async def run(self):
        st = await self.start_state()
        done = set()
        if os.path.exists(self.log_path):
            done = {(r["method"], int(r["msg_id"])) for r in csv.DictReader(open(self.log_path))}
        seen = Seen(st["floor"], done)
        self.beat(f"start @{CH} method {self.method} period {self.period} pts {st['pts']} last_id {st['last_id']}")
        tick, nxt, last_hb, streak = 0, self.now(), self.now(), 0
        while self.now() < self.end:
            if os.path.exists(os.path.join(self.here, "STOP_PULL")):
                self.beat("STOP_PULL present, stopping")
                return "stop-file"
            d = nxt - self.now()
            if d > 0:
                await self.sleep(d)
            if self.now() >= self.end:
                break
            nxt = max(nxt + self.period, self.now())
            method = self.method if self.method != "alt" else ("diff", "ids")[tick % 2]
            tick += 1
            t0 = self.now()
            try:
                if method == "diff":
                    r = await self.call("diff", pts=st["pts"])
                    t1 = self.now()
                    kind, pts, posts, timeout = diff_result(r)
                    if pts is not None:
                        st["pts"] = pts
                    if timeout is not None:
                        self.timeouts.append(timeout)
                    if kind == "ChannelDifferenceTooLong":
                        self.beat("ChannelDifferenceTooLong; pts reset")
                else:
                    # own cursor, so that in `alt` mode ids finds each post by itself (not after diff found it)
                    cur = st.setdefault("ids_last", st["last_id"])
                    msgs = await self.call("ids", ids=[cur + 1, cur + 2])
                    t1 = self.now()
                    posts = real_posts(msgs)
                    # any existing id (service messages too) moves the cursor, so a non-post id cannot stall it
                    st["ids_last"] = max([cur] + [m.id for m in msgs if type(m).__name__ != "MessageEmpty"])
                self.calls += 1
                self.rtts.append(t1 - t0)
                self.log_posts(posts, method, t0, t1, seen, st)
                self.save(st)
                streak = 0
            except FloodWait as e:
                self.errors += 1
                self.period, stop = after_flood(self.period, e.seconds)
                self.beat(f"FloodWait {e.seconds} s on {method}; period now {self.period}")
                if stop:
                    self.beat(f"FloodWait {e.seconds} s > {FLOOD_STOP} s, stopping")
                    open(os.path.join(self.here, "STOP_PULL"), "w").write(f"{iso(self.now())} FloodWait {e.seconds}\n")
                    return "flood"
                await self.sleep(e.seconds)
                nxt = self.now()
            except AuthStop as e:
                self.beat(f"auth error {e}, stopping")
                open(os.path.join(self.here, "STOP_PULL"), "w").write(f"{iso(self.now())} auth error {e}\n")
                return "auth"
            except (Transient, OSError, ConnectionError, asyncio.TimeoutError) as e:
                self.errors += 1
                streak += 1
                self.beat(f"error {type(e).__name__}: {str(e)[:100]}")
                if streak >= MAX_STREAK:
                    self.beat(f"{streak} errors in a row, stopping")
                    return "errors"
                if "PERSISTENT_TIMESTAMP" in str(e):  # pts no longer valid on the server: refetch it
                    try:
                        st["pts"] = await self.call("full")
                    except Exception as e2:  # next tick retries
                        self.beat(f"pts refetch failed {type(e2).__name__}")
            if self.now() - last_hb >= HB_EVERY:
                med = statistics.median(self.rtts) if self.rtts else 0
                tmo = sorted(set(self.timeouts))
                self.beat(f"alive calls {self.calls} errors {self.errors} rtt_median_s {med:.3f} "
                          f"server_timeout {tmo[:3]} period {self.period} pts {st['pts']} last_id {st['last_id']}")
                self.calls = self.errors = 0
                self.rtts, self.timeouts = [], []
                last_hb = self.now()
        self.beat("end time reached")
        return "end"


class FloodWait(Exception):
    def __init__(self, seconds):
        super().__init__(f"FloodWait {seconds}")
        self.seconds = seconds


class AuthStop(Exception):
    pass


class Transient(Exception):
    """Any other RPC error (counted, retried next tick; MAX_STREAK in a row stops)."""


def env():
    vals = {}
    for line in open(os.path.join(HERE, "push.env")):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return int(vals["TG_API_ID"]), vals["TG_API_HASH"]


async def run_live(until, period=PERIOD, method="diff"):
    from telethon import TelegramClient, errors, functions, types
    end = parse_until(until)
    if time.time() >= end:
        print("past end time; not polling")
        return 0
    if os.path.exists(os.path.join(HERE, "STOP_PULL")):
        print("STOP_PULL present; not polling (delete it to restart)")
        return 0
    if not os.path.exists(os.path.join(HERE, SESSION + ".session")):
        print("pull.session missing: copy push.session to pull.session first")
        return 2
    os.chmod(os.path.join(HERE, SESSION + ".session"), 0o600)
    api_id, api_hash = env()
    c = TelegramClient(os.path.join(HERE, SESSION), api_id, api_hash, receive_updates=False,
                       device_model="agentfx-a2-pull", system_version="linux", app_version="1.0",
                       flood_sleep_threshold=0)  # FloodWait is raised to us, never slept inside Telethon
    await c.connect()
    if not await c.is_user_authorized():
        open(os.path.join(HERE, "STOP_PULL"), "w").write(f"{iso(time.time())} not authorized\n")
        print("session not authorized")
        await c.disconnect()
        return 2
    chan = await c.get_input_entity(CH)

    async def call(name, **kw):
        try:
            if name == "full":
                return (await c(functions.channels.GetFullChannelRequest(chan))).full_chat.pts
            if name == "last":
                h = await c(functions.messages.GetHistoryRequest(chan, 0, None, 0, 1, 0, 0, 0))
                return max([m.id for m in h.messages], default=0)
            if name == "diff":
                return await c(functions.updates.GetChannelDifferenceRequest(
                    chan, types.ChannelMessagesFilterEmpty(), kw["pts"], 100, force=False))
            if name == "ids":
                r = await c(functions.channels.GetMessagesRequest(chan, [types.InputMessageID(i) for i in kw["ids"]]))
                return r.messages
        except errors.FloodWaitError as e:
            raise FloodWait(e.seconds)
        except (errors.UnauthorizedError, errors.AuthKeyError) as e:  # 401 family, AUTH_KEY_DUPLICATED (406)
            raise AuthStop(type(e).__name__)
        except errors.RPCError as e:
            raise Transient(f"{type(e).__name__} {e}"[:160])
        raise ValueError(name)

    perps, tasks = Perps(), set()
    poller = Poller(call, end, float(period), method)

    def on_post(msg_id, post_t, recv_t, text):
        txt = " ".join((text or "").split())
        if not krw_listing(txt):
            return
        for coin in krw_tickers(txt):
            t = asyncio.create_task(paper(msg_id, coin, post_t, recv_t, perps, poller.hb))
            tasks.add(t)
            t.add_done_callback(tasks.discard)

    async def keep_perps():
        while True:
            try:
                await asyncio.to_thread(perps.refresh, True)
            except Exception as e:
                poller.hb.write(f"{iso(time.time())} exchangeInfo error {type(e).__name__}\n")
            await asyncio.sleep(PERPS_EVERY)

    poller.on_post = on_post
    kp = asyncio.create_task(keep_perps())
    try:
        res = await poller.run()
        if tasks:  # let a pending paper entry finish (it waits at most until N + 5 s)
            await asyncio.wait(set(tasks), timeout=30)
    finally:
        kp.cancel()
        await c.disconnect()
    print(res)
    return 0


def report():
    p = os.path.join(HERE, "pull_log.csv")
    rows = list(csv.DictReader(open(p))) if os.path.exists(p) else []
    if not rows:
        print("0 posts")
        return
    for m in sorted({r["method"] for r in rows}):
        q = quantiles([float(r["recv_minus_post_s"]) for r in rows if r["method"] == m])
        print(f"{m}: posts {q['n']}; receive - post time median {q['median']:.2f} s, p80 {q['p80']:.2f}, "
              f"p90 {q['p90']:.2f}, max {q['max']:.2f}; <= 3 s {q['le3']} / {q['n']} "
              f"(post time is whole seconds: true delay is 0-1 s less)")
    for r in rows[-12:]:
        print(" ", r["msg_id"], r["recv_utc"], f"{float(r['recv_minus_post_s']):+.2f} s", r["method"],
              "rtt", r["rtt_s"], r["krw_listing"], r["text"][:60])
    krw = [float(r["recv_minus_post_s"]) for r in rows if r["krw_listing"] == "1"]
    print(f"KRW listings {len(krw)}; <= 3 s: {sum(x <= 3 for x in krw)} / {len(krw)}")
    p = os.path.join(HERE, "pull_paper.csv")
    for r in (list(csv.DictReader(open(p))) if os.path.exists(p) else []):
        print("paper", r["post_utc"], r["coin"], r["perp"] or "-", "eligible", r["eligible"], "entry",
              r.get("entry_utc") or "-", "alt ask", r.get("entry_alt_ask") or "-", "spread bp",
              r.get("entry_alt_spread_bp") or "-", r["note"])


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "report":
        report()
        return 0
    if cmd == "run":
        if len(argv) < 3:
            print(__doc__)
            return 2
        return asyncio.run(run_live(argv[2], argv[3] if len(argv) > 3 else PERIOD,
                                    argv[4] if len(argv) > 4 else "diff"))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
