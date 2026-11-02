"""Push capture + paper entry for A2-D5L through Upbit's official Telegram channel @upbit_news, on a Telegram USER
account over MTProto (Telethon). The user approved the account route on 2026-11-02 after the keyless t.me/s poller
(tg_capture.py) showed a 17.7 s preview lag on its first sample.

What it measures (the registered promotion gate of PREREG_A2_D5L: notice seen <= 3 s after N on >= 80 % of live
KRW-listing notices):
- every new channel post: Telegram time (whole seconds), local receive time (agentFx is NTP-synced), the lag;
- for a KRW-listing post: the Binance USDT-M perp of each listed coin (also 1000x / 1000000x contracts), its age
  (onboardDate <= N - 7 d, as the rule), and the public bookTicker of the alt perp and BTCUSDT at receive time and
  again at max(N + 5 s, receive time) = the paper entry (long alt at the ask, short BTC at the bid).
It sends NO order and reads nothing from Upbit (Upbit blocks this IP; the exit at the KRW open L and the registered
net are graded later from public data by A2's fwd_a2.py on another host).

Files in the working directory (never in git): push.env (TG_API_ID, TG_API_HASH; chmod 600), push.session (the
account's login; chmod 600), push_log.csv, push_paper.csv, push_heartbeat.log, login_state.json while logging in.

Usage:
  python -I tg_push.py login-start <phone, e.g. +84...>   send the login code to the account's Telegram app
  python -I tg_push.py login-finish <code> [2FA password] finish the login, join @upbit_news
  python -I tg_push.py run [until, e.g. 2027-01-01T00:00Z] listen (cron restarts it under flock)
  python -I tg_push.py report                             lag stats and paper entries"""
import asyncio, csv, datetime as dt, json, os, re, statistics, sys, time, urllib.request

CH = "upbit_news"
SESSION = "push"
UA = "agentfx-a2-push/1"
FAPI = "https://fapi.binance.com"
LOG_FIELDS = ["msg_id", "post_utc", "recv_utc", "recv_minus_post_s", "krw_listing", "tickers", "text"]
PAPER_FIELDS = ["msg_id", "coin", "perp", "post_utc", "recv_utc", "perp_age_d", "eligible", "detect_utc",
                "detect_alt_bid", "detect_alt_ask", "detect_btc_bid", "detect_btc_ask", "entry_utc", "entry_alt_ask",
                "entry_btc_bid", "entry_alt_spread_bp", "note"]
HERE = os.getcwd()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def env():
    vals = {}
    for line in open(os.path.join(HERE, "push.env")):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return int(vals["TG_API_ID"]), vals["TG_API_HASH"]


def krw_listing(t):
    # Same test as tg_capture.krw_listing (round 73), kept here so this file runs on its own.
    return int(t.startswith("[거래]") and ("KRW" in t or "원화" in t) and "종료" not in t and "유의" not in t
               and any(k in t for k in ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")))


def krw_tickers(t):
    """Tickers that get a KRW market. A title can list several coins, each with its own market list
    ("셀레스티아(TIA)(KRW, BTC, USDT 마켓), 아이오넷(IO)(BTC, USDT 마켓)"); a coin followed by a market list without KRW
    is left out. Without per-coin lists, every ticker of a KRW title counts."""
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
    """USDT-M perpetuals from exchangeInfo, refreshed at most every 10 min (and on a miss)."""

    def __init__(self):
        self.by_symbol, self.at = {}, 0.0

    def refresh(self, force=False):
        if not force and time.time() - self.at < 600:
            return
        info = http_json(f"{FAPI}/fapi/v1/exchangeInfo", timeout=10)
        self.by_symbol = {s["symbol"]: s for s in info["symbols"]
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


def append(path, fields, row):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerow(row)


async def paper(msg_id, coin, post_t, recv_t, perps, hb):
    row = dict(msg_id=msg_id, coin=coin, post_utc=iso(post_t), recv_utc=iso(recv_t), perp="", perp_age_d="",
               eligible=0, note="")
    try:
        p = await asyncio.to_thread(perps.find, coin)
        if p is None:
            row["note"] = "no Binance USDT-M perp"
            return
        sym = p["symbol"]
        row["perp"] = sym
        age = (post_t - p["onboardDate"] / 1000) / 86400
        row["perp_age_d"] = round(age, 2)
        row["eligible"] = int(age >= 7)
        (ab, aa), (bb, ba) = await asyncio.gather(asyncio.to_thread(book, sym), asyncio.to_thread(book, "BTCUSDT"))
        row.update(detect_utc=iso(time.time()), detect_alt_bid=ab, detect_alt_ask=aa, detect_btc_bid=bb,
                   detect_btc_ask=ba)
        wait = post_t + 5 - time.time()
        if wait > 0:
            await asyncio.sleep(wait)
        (ab, aa), (bb, ba) = await asyncio.gather(asyncio.to_thread(book, sym), asyncio.to_thread(book, "BTCUSDT"))
        row.update(entry_utc=iso(time.time()), entry_alt_ask=aa, entry_btc_bid=bb,
                   entry_alt_spread_bp=round((aa - ab) / ((aa + ab) / 2) * 1e4, 1))
    except Exception as e:
        row["note"] = f"{type(e).__name__}: {str(e)[:120]}"
        hb.write(f"{iso(time.time())} paper error {coin}: {row['note']}\n")
    finally:
        append(os.path.join(HERE, "push_paper.csv"), PAPER_FIELDS, row)


def client():
    from telethon import TelegramClient
    api_id, api_hash = env()
    return TelegramClient(os.path.join(HERE, SESSION), api_id, api_hash, device_model="agentfx-a2-push",
                          system_version="linux", app_version="1.0")


def private(path):
    if os.path.exists(path):
        os.chmod(path, 0o600)


async def login_start(phone):
    c = client()
    await c.connect()
    sent = await c.send_code_request(phone)
    json.dump({"phone": phone, "hash": sent.phone_code_hash}, open(os.path.join(HERE, "login_state.json"), "w"))
    private(os.path.join(HERE, "login_state.json"))
    private(os.path.join(HERE, SESSION + ".session"))
    await c.disconnect()
    print("code sent to the account's Telegram app; next: login-finish <code> [2FA password]")


async def login_finish(code, password=None):
    from telethon.errors import SessionPasswordNeededError
    from telethon.tl.functions.channels import JoinChannelRequest
    st = json.load(open(os.path.join(HERE, "login_state.json")))
    c = client()
    await c.connect()
    try:
        await c.sign_in(phone=st["phone"], code=code, phone_code_hash=st["hash"])
    except SessionPasswordNeededError:
        if not password:
            print("this account has 2FA: run login-finish <code> <password>")
            await c.disconnect()
            return 1
        await c.sign_in(password=password)
    me = await c.get_me()
    await c(JoinChannelRequest(CH))
    os.remove(os.path.join(HERE, "login_state.json"))
    private(os.path.join(HERE, SESSION + ".session"))
    print(f"logged in as user id {me.id}; joined @{CH}")
    await c.disconnect()
    return 0


async def run(until=None):
    from telethon import events
    end = dt.datetime.fromisoformat(until.replace("Z", "+00:00")).timestamp() if until else float("inf")
    if time.time() >= end:
        print("past end time; not listening")
        return
    if os.path.exists(os.path.join(HERE, "STOP_PUSH")):
        print("STOP_PUSH present; not listening")
        return
    hb = open(os.path.join(HERE, "push_heartbeat.log"), "a", buffering=1)
    perps = Perps()
    await asyncio.to_thread(perps.refresh, True)
    c = client()
    await c.connect()
    if not await c.is_user_authorized():
        hb.write(f"{iso(time.time())} not logged in; run login-start / login-finish\n")
        open(os.path.join(HERE, "STOP_PUSH"), "w").write("not logged in\n")
        await c.disconnect()
        return
    chan = await c.get_entity(CH)
    seen = {"n": 0}
    tasks = set()

    @c.on(events.NewMessage(chats=chan))
    async def on_new(ev):
        recv = time.time()
        m = ev.message
        post = m.date.timestamp()
        txt = " ".join((m.message or "").split())
        krw = krw_listing(txt)
        tick = krw_tickers(txt) if krw else []
        append(os.path.join(HERE, "push_log.csv"), LOG_FIELDS,
               dict(msg_id=m.id, post_utc=iso(post), recv_utc=iso(recv), recv_minus_post_s=round(recv - post, 3),
                    krw_listing=krw, tickers="/".join(tick), text=txt[:200]))
        seen["n"] += 1
        for coin in tick:
            t = asyncio.create_task(paper(m.id, coin, post, recv, perps, hb))
            tasks.add(t)
            t.add_done_callback(tasks.discard)

    hb.write(f"{iso(time.time())} start, listening to @{CH}\n")

    async def beat():
        while time.time() < end:
            await asyncio.sleep(min(600, max(1, end - time.time())))
            hb.write(f"{iso(time.time())} alive, connected {c.is_connected()}, posts {seen['n']}\n")
            seen["n"] = 0
            try:
                await asyncio.to_thread(perps.refresh)
            except Exception as e:
                hb.write(f"{iso(time.time())} exchangeInfo error {type(e).__name__}\n")
        await c.disconnect()

    b = asyncio.create_task(beat())
    await c.run_until_disconnected()
    b.cancel()
    hb.write(f"{iso(time.time())} disconnected\n")


def report():
    p = os.path.join(HERE, "push_log.csv")
    rows = list(csv.DictReader(open(p))) if os.path.exists(p) else []
    lag = sorted(float(r["recv_minus_post_s"]) for r in rows)
    if not lag:
        print("0 posts received")
    else:
        q = lambda x: lag[min(len(lag) - 1, int(x * len(lag)))]
        krw = [float(r["recv_minus_post_s"]) for r in rows if r["krw_listing"] == "1"]
        print(f"posts {len(lag)}; receive - post time: median {q(0.5):.2f} s, p80 {q(0.8):.2f}, p90 {q(0.9):.2f}, "
              f"max {lag[-1]:.2f} (post time is whole seconds: true delay is 0-1 s less)")
        print(f"KRW listings {len(krw)}; <= 2 s after the post: {sum(x <= 2 for x in krw)} / {len(krw)}")
        for r in rows[-10:]:
            print(" ", r["recv_utc"], f"{float(r['recv_minus_post_s']):+.2f} s", r["krw_listing"], r["text"][:70])
    p = os.path.join(HERE, "push_paper.csv")
    for r in (list(csv.DictReader(open(p))) if os.path.exists(p) else []):
        print("paper", r["post_utc"], r["coin"], r["perp"] or "-", "eligible", r["eligible"], "entry",
              r.get("entry_utc") or "-", "alt ask", r.get("entry_alt_ask") or "-", "spread bp",
              r.get("entry_alt_spread_bp") or "-", r["note"])


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "report":
        report()
        return 0
    if cmd == "login-start":
        asyncio.run(login_start(argv[2]))
        return 0
    if cmd == "login-finish":
        return asyncio.run(login_finish(argv[2], argv[3] if len(argv) > 3 else None))
    if cmd == "run":
        asyncio.run(run(argv[2] if len(argv) > 2 else None))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
