#!/bin/sh
# TG2 keyless poller on the Mac. Phase 1 (to 17:30Z): whale_alert_io (3-4 posts/h) measures preview freshness per
# form while @upbit_news is quiet. Phase 2 (to 2026-11-03T12:00Z): @upbit_news only.
cd "$(dirname "$0")"
O=/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist/tg2
python3 -I tg2_poll.py run 2026-11-02T17:30Z 3 whale_alert_io:top,whale_alert_io:bcyc,whale_alert_io:after,upbit_news:bcyc,whale_alert_io:top,whale_alert_io:bcyc,whale_alert_io:after,upbit_news:top >> $O/poll1.out 2>&1
[ -e $O/STOP ] && exit 0
python3 -I tg2_poll.py run 2026-11-03T12:00Z 4 upbit_news:bcyc,upbit_news:top,upbit_news:after >> $O/poll2.out 2>&1
