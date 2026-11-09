# TG2 user steps: deploy the active MTProto fetcher (tg_pull.py) on agentFx

Written 2026-11-02 (round 74 TG2). TG2 ran nothing on agentFx (read-only rule); these are the steps for the user.
What it does: every 2 s it asks Telegram for @upbit_news's new posts (`updates.getChannelDifference`, read only) on a
copy of the account session that tg_push.py already uses, and logs post time / receive time per post. No message is
sent, no channel is joined, no order, no exchange call. Load: 0.5 requests/s to Telegram from one user account.

Tested on the Mac: 10 unit tests (`research/tests/test_tg_pull.py`, fake clock + Telethon-like fakes) and one end-to-end
run of `tg_pull.py run` against a fake Telethon 1.45.0 client (the version in venv-push) with real Telethon types:
new post logged, FloodWait doubled the period, AUTH_KEY_DUPLICATED wrote STOP_PULL and stopped. It has NOT talked to
Telegram yet.

## Risk to read first
- The copy shares the auth key with push.session. Telegram revokes a key used "under two different IP addresses
  simultaneously" (AUTH_KEY_DUPLICATED, Telethon's text). Both copies run on agentFx (one IP), which is the normal
  multi-connection case, so this is not expected; if it happens anyway, tg_pull stops by itself, but tg_push would also
  need a new login (`tg_push.py login-start` / `login-finish`). If that risk is not acceptable, log in a second session
  instead (same account, own key): copy tg_push.py's login-start/login-finish with SESSION = "pull" (not prepared).
- tg_pull connects with `receive_updates=False` (Telethon wraps every call in invokeWithoutUpdates), so Telegram keeps
  sending the account's push updates to tg_push's connection; the passive measurement is not disturbed.
- Polling at 2 s is faster than Telegram's own client guidance (re-poll an *opened* channel after the server's
  `timeout`, which tg_pull logs). A FloodWait doubles the period (logged); one > 300 s stops the script.

## 1. Copy the script (from the Mac)
```sh
scp /Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/TG2/code/tg_pull.py \
    agentFx:/home/forge/tg_capture_a2/tg_pull.py
```

## 2. Copy the session (on agentFx; sqlite backup = consistent copy while tg_push is running)
```sh
ssh agentFx
cd /home/forge/tg_capture_a2
venv-push/bin/python -I -c "import sqlite3; s=sqlite3.connect('push.session'); d=sqlite3.connect('pull.session'); s.backup(d); d.close(); s.close()"
chmod 600 pull.session
```

## 3. Start with a hard end time (7 days), detached from the ssh session
```sh
cd /home/forge/tg_capture_a2
setsid nohup venv-push/bin/python -I tg_pull.py run 2026-11-09T00:00Z 2 diff >> pull_run.log 2>&1 < /dev/null &
sleep 15; cat pull_heartbeat.log; cat pull_run.log
```
The heartbeat must show `start @upbit_news method diff period 2.0 pts ... last_id ...`. After 10 min it shows
`alive calls ~300 errors 0 rtt_median_s ... server_timeout [...]`.
Optional (survives a reboot, like tg_push): cron line
`* * * * * cd /home/forge/tg_capture_a2 && /usr/bin/flock -n /tmp/tg_pull_a2.lock venv-push/bin/python -I tg_pull.py run 2026-11-09T00:00Z 2 diff >> pull_run.log 2>&1 # tg-pull-a2 (round 74 TG2, ends 2026-11-09)`
(use either nohup or cron, not both: the cron flock does not see a nohup process).

## 4. Read (read only)
```sh
ssh agentFx 'cd /home/forge/tg_capture_a2 && venv-push/bin/python -I tg_pull.py report; tail -n 5 pull_heartbeat.log'
ssh agentFx 'cd /home/forge/tg_capture_a2 && venv-push/bin/python -I tg_push.py report; python3 -I tg_capture.py report'
```
Pass (HYPOTHESES_TG2): >= 80 % of new posts with receive - post <= 3 s over >= 5 posts (~1-2 days).

## 5. Stop
```sh
ssh agentFx 'cd /home/forge/tg_capture_a2 && touch STOP_PULL'   # stops within one period; also blocks restarts
ssh agentFx 'pkill -f "tg_pull.py run"'                         # immediate
```
To restart after a stop: `rm STOP_PULL`, then step 3. To remove: stop, then `rm pull.session pull_state.json`
(keep pull_log.csv).

## Optional second test (after >= 5 posts with `diff`)
`... tg_pull.py run <end> 1 alt` alternates getChannelDifference and channels.getMessages(next id) every 1 s (each
method every 2 s, 1 request/s): tells whether one method returns new posts sooner than the other.
