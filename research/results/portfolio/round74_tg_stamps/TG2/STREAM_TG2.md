# STREAM_TG2: a <= 3 s capture route for @upbit_news (A2-D5L promotion gate)

Written 2026-11-02 15:05 UTC (`date -u`). Engineering and latency only: no P&L, no orders. Pre-registration:
HYPOTHESES_TG2.md (14:23 UTC). The stream was called back early (40 min of keyless data), so the keyless results are
indicative and the Mac poller keeps running.

## Answer first
- **No route is proven to pass yet.**
- **Clock skew is ruled out.**
  - agentFx: chrony synced, 11 µs fast of NTP.
  - Mac: sntp offset -0.2 / +0.6 ms.
  - The 11-58 s lags are real.
- **Keyless t.me forms are all late.** I sampled a busy channel (whale_alert_io) because @upbit_news is quiet at this
  hour. On one post, each form first showed it:
  - top page: 4-29 s after the post time;
  - `?after=`: 10-33 s;
  - per-post `?embed=1`: 39-63 s (slowest).
  - This matches agentFx's 1.5 s top-page poller (7 posts: median +22.5 s, p90 +50.6 s).
  - The preview is built from a lagging cache or replica, so no keyless form looks able to reach <= 3 s.
  - Still open: whether a URL never requested before is fresher. The `bcyc` form (`?before=` cycling) tests this; it
    is running now.
- **Best candidate: active MTProto pull** (`TG2/code/tg_pull.py`, user deploys it; steps below). Why passive push is
  late is documented:
  - core.telegram.org/api/updates: "the API may stop sending updates (or send fewer updates) for some
    channels/supergroups, thus clients (user accounts only) should also additionally invoke
    updates.getChannelDifference periodically for channels ... the user is currently viewing". It also says to
    re-poll after the server's `timeout` (default 1 s) and to short-poll at most 10 channels.
  - TDLib openChat: "in supergroups and channels all updates are received only for opened chats".
  - tg_push only listens passively, so it gets the posts late. tg_pull does the "opened chat" short-poll itself.
  - Expected if the server is fresh: U(0, 2 s) + RTT + up to 1 s of stamp rounding, i.e. about 80-95 % <= 3 s. Not
    measured yet.

## Delay per route (seen - post time, s; post stamps are whole seconds)
| route | where | posts | delay | <= 3 s |
|---|---|---|---|---|
| t.me/s top, 1.5 s poll | agentFx | 7 upbit | median 22.5, p90 50.6, min 14.6 | 0 / 7 |
| Telethon passive push | agentFx | 2 upbit | 58.4, 11.0 | 0 / 2 |
| t.me/s top | Mac | 1 whale | (4, 29.3] | 0 / 1 |
| t.me/s `?after=<id>` | Mac | 1 whale | (10, 33.2] | 0 / 1 |
| `t.me/<ch>/<id>?embed=1` | Mac | 1 whale | (39, 63.3] | 0 / 1 |
| `?before=` cycling (bcyc) | Mac | running | - | - |
| MTProto getChannelDifference, 2 s | agentFx (user step) | not deployed | - | - |

How to read the delay column: (a, b] means the post was not on the route's previous request (a s after the post time)
and was on the next one (b s after). One probe each of `?after=`, `?before=`, `/s/<ch>/<id>` and the embed form
returned 200 with `cache-control: no-store`, so the HTTP headers do not reveal the cache.

## Still running on the Mac
- `run_mac.sh` (pid 65966) runs `tg2_poll.py` (pid 65969) in two phases:
  - phase 1, until 2026-11-02 17:30Z: whale_alert_io top / bcyc / after, plus upbit bcyc / top;
  - phase 2, until 2026-11-03 12:00Z: upbit_news bcyc / top / after, one request every >= 4 s.
- All requests go through the shared `.last_req` lock, with the `Python-urllib/3` UA. The poller stops by itself on
  403 / 429 / 418 / 503. So far: 470 requests, all 200.
- Logs: `research/data/telegram_hist/tg2/{requests.log,firstseen.csv,poll1.out,poll2.out}`.
- Read: `python3 -I TG2/code/tg2_poll.py report [capture.csv copied from agentFx]`.
- Stop: `pkill -f run_mac.sh; pkill -f "tg2_poll.py run"`.

## Code and tests
- `TG2/code/tg_pull.py`: active fetcher.
  - Fetches with `diff` (GetChannelDifference with pts), `ids` (channels.GetMessages for the next id) or `alt`.
  - Period: 2 s by default, never < 1 s.
  - FloodWait: sleeps, doubles the period and logs it. A FloodWait over 300 s, or an auth / AUTH_KEY error, writes
    STOP_PULL and stops.
  - Requires a hard end time.
  - Connects with `receive_updates=False`, so it does not take tg_push's update stream.
- `research/tests/test_tg_pull.py`: 10 tests pass (pure parts and the poll loop on fakes).
- An end-to-end run against a fake client passed. The fake used Telethon 1.45.0 (venv-push's version) with real
  Telethon types.
- `TG2/code/tg2_poll.py`, `run_mac.sh`: keyless poller.

## User steps (agentFx; I ran nothing there except read-only commands)
Exact commands are in `TG2/USER_STEPS_TG2.md`. In short:
1. `scp` tg_pull.py into `/home/forge/tg_capture_a2/`.
2. Copy the session with the sqlite backup API into `pull.session`, then `chmod 600 pull.session`.
3. Start it: `setsid nohup venv-push/bin/python -I tg_pull.py run 2026-11-09T00:00Z 2 diff >> pull_run.log 2>&1 < /dev/null &`.
4. Read: `tg_pull.py report` and `tail pull_heartbeat.log`.
5. Stop: `touch STOP_PULL`, or `pkill -f "tg_pull.py run"`.

**Risk:** the copy shares push.session's auth key. Telegram revokes a key it sees from two IPs at once; both copies run
on one host, so this is not expected. If it does happen, tg_push needs a new login. The alternative is a second login
for tg_pull (not prepared).
