# 🐳 Docker Instance Catalog — all 5 presets

Every instance AgentFxTrading ships: the Gotobi Fix bot on its three JPY pairs and the ECB window bot's two rules on
EURUSD = **5 `docker run` commands**, written out in full.

This file is the long form of the dashboard's **Docker Bot Management → Setup Instances** grid. Ticking a cell there
runs exactly the command printed here. Both come from [`app/cbot_presets.py`](../app/cbot_presets.py), which is the
single source of truth for strategy flags — `tests/app/test_cbot_presets.py` fails the build if this file and that module
drift apart.

> **Prerequisites live in [deployment.md](deployment.md).** Install the server, write the cTID password file and build
> the `.algo` package first: [Building the cBots](deployment.md#building-the-cbots) and
> [Running bots](deployment.md#running-bots). Come back here once `cBot/GotobiBot.algo` and `cBot/EcbWindowBot.algo` exist.

---

## 📋 Contents

- [Adapting a block](#-adapting-a-block)
- [Container naming](#-container-naming)
- [The 5-cell grid](#-the-5-cell-grid)
- [Gotobi Fix — `GotobiBot.algo`](#-gotobi-fix--gotobibotalgo)
- [ECB Window — `EcbWindowBot.algo`](#-ecb-window--ecbwindowbotalgo)
- [Running demo and live side by side](#-running-demo-and-live-side-by-side)

---

## ✏️ Adapting a block

Every command below is written for a demo account. Five placeholders are yours to replace; the strategy flags
underneath them are the preset and should be copied as-is.

| Placeholder | Replace with |
| :--- | :--- |
| `--ctid=your_email@example.com` | The email of your cTID login. |
| `--account=YOUR_ACCOUNT_ID` | Your cTrader account number, e.g. `10101649`. |
| `--pwd-file=/root/ctrader_data/ctid_pwd` | Path to the `chmod 600` file holding that cTID's password. |
| `--AccountLabel="demo"` | `demo` or `live` — the cBot tags every trade with it and routes live data to `/real/dashboard`. |
| `--name` / `--BotId` `cbot-demo-…` | Swap the `demo` slug for your own account slug so a demo and a live bot on the same symbol never collide. |

Two flags are worth a second look before you go live:

- **`--RiskPerTradeMoney`** is dollars per trade, not a percentage: set it to what one trade may lose on that account.
  The presets are sized for a demo balance.
- **`--network host`** assumes the API server runs on the same machine as the container. On a split setup, drop it and
  point `--ApiUrl` at the server's reachable address instead.

---

## 🏷️ Container naming

The dashboard names containers `cbot-<account slug>-<symbol>-<session>[-<strategy>]`, and the blocks below follow the
same scheme with `demo` as the slug:

| Strategy | Pattern | Example |
| :--- | :--- | :--- |
| Gotobi Fix | `cbot-<slug>-<symbol>-fix-gotobi` | `cbot-demo-usdjpy-fix-gotobi` |
| ECB Window F3 | `cbot-<slug>-eurusd-ecb-f3` | `cbot-live-eurusd-ecb-f3` |
| ECB Window E1 | `cbot-<slug>-eurusd-ecb-e1` | `cbot-demo-eurusd-ecb-e1` |

The name doubles as `--BotId`, so `docker ps` tells you the account, symbol, session and strategy of every bot without
opening its flags — and the dashboard can match a running container back to its config row.

---

## 🗺️ The 5-cell grid

`period` · session for each cell. 🔬 = passed a pre-registered LIVE holdout (Gotobi on the JPY pairs); 🧪 = a candidate
the research runs to measure it (F3 passed its holdout only at the RELAXED tier, E1 is a weak DEMO candidate).

| Symbol | Gotobi Fix | ECB Window F3 | ECB Window E1 |
| :--- | :--- | :--- | :--- |
| **USDJPY** | 🔬 `m15` · Tokyo fix | – | – |
| **EURJPY** | 🔬 `m15` · Tokyo fix | – | – |
| **GBPJPY** | 🔬 `m15` · Tokyo fix | – | – |
| **EURUSD** | – | 🧪 `m15` · ECB fix window | 🧪 `m15` · ECB fix window |

---

## 🗾 Gotobi Fix — `GotobiBot.algo`

The research's validated algorithm (C3 in
[`research/results/portfolio/swing_lab_v2_2026-09-27.md`](../research/results/portfolio/swing_lab_v2_2026-09-27.md)):
on gotobi days (the 5th, 10th, 15th, 20th, 25th and the month's last day, a weekend one moved to the Friday before)
it buys at 18:00 UTC the evening before, closes at the 09:55 Tokyo fix (00:55 UTC), sells at the fix and closes at
11:55 Tokyo (02:55 UTC). It reports its trades, sends telemetry and obeys the dashboard's pause and close
commands. It only exists for the three JPY pairs the research
validated.

Every trade risks `--RiskPerTradeMoney` (dollars, never a share of equity) at a stop of 3 x ATR20(H1), so the lot
follows volatility around that default. The schedule, the stop and the one-position-at-a-time rule are the cBot's
defaults and are the same on every pair; a cell only sets the risk, the entry spread cap, the days to sit out and
`--EmergencyStopMin=1.0`. Its exposure is one position of one default risk, two legs a day, six gotobi days a month.

`--EmergencyStopMin=1.0` sends the broker the real stop. The cBot's default draws the broker stop at random between
0.8x and 1.0x of it to hide the strategy, which cost ~1.4 % of the real legs' net over 2020-2026
([`gotobi_broker_stop_jitter_2026-10-15.md`](../research/results/portfolio/gotobi_broker_stop_jitter_2026-10-15.md)).
The ±60 min long entry jitter and the decoy legs stay on.

Japanese public holidays and the 31/12 bank holiday have no Tokyo fix, and on the 45 such gotobi days of 2016-2026
the basket lost money
([`gotobi_jp_holidays_2026-09-29.md`](../research/results/portfolio/gotobi_jp_holidays_2026-09-29.md)). The presets
list the coming ones in `--SkipDates`, together with 2026-12-25 (a Friday gotobi day while the broker is closed for
Christmas): that one is the cBot's own default, and a `--SkipDates` value replaces it. The list runs to the end of
2027; `python -m research.tools.gotobi_holidays --upcoming 2028-01-01:2028-12-31` prints the next year's dates.

### USDJPY — Gotobi Fix

`m15` · Tokyo fix

The pair the flow is about: importers buy USD against yen at the fix.

```bash
docker run -d \
  --name cbot-demo-usdjpy-fix-gotobi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/GotobiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdjpy-fix-gotobi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --RiskPerTradeMoney=100.0 \
  --MaxSpreadPips=3.0 \
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31" \
  --EmergencyStopMin=1.0
```

### EURJPY — Gotobi Fix

`m15` · Tokyo fix

Same flow through the yen leg; the research found it on EURJPY too (holdout R +0.057).

```bash
docker run -d \
  --name cbot-demo-eurjpy-fix-gotobi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/GotobiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurjpy-fix-gotobi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --RiskPerTradeMoney=100.0 \
  --MaxSpreadPips=3.0 \
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31" \
  --EmergencyStopMin=1.0
```

### GBPJPY — Gotobi Fix

`m15` · Tokyo fix

Same flow; GBPJPY quotes wider, so its entry spread cap is 4 pips instead of 3.

```bash
docker run -d \
  --name cbot-demo-gbpjpy-fix-gotobi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/GotobiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpjpy-fix-gotobi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --RiskPerTradeMoney=100.0 \
  --MaxSpreadPips=4.0 \
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31" \
  --EmergencyStopMin=1.0
```

---

## 🇪🇺 ECB Window — `EcbWindowBot.algo`

Sells EURUSD at 11:00 London and buys it back at 13:00 London: EUR is sold into the 14:15 CET ECB reference rate. Two
rules share the cBot, and `--UsdTopOnly` picks one:

- **F3** (`--UsdTopOnly=true`): only on USD-TOP days, when USDJPY and USDCHF rose from 18:00 New York the previous
  weekday to 07:00 London by at least the 67th percentile of the previous 250 weekdays. Never on a Monday (no quote at
  18:00 New York on Friday). It passed its 2025-2026 holdout at the research's RELAXED tier only
  ([`PREREG_R24_relaxed_hold.md`](../research/results/portfolio/round24_relaxed/PREREG_R24_relaxed_hold.md)), so the
  preset trades the minimum lot: a measurement of real fills, not a sized bet.
- **E1** (`--UsdTopOnly=false`): every weekday, a weak DEMO candidate
  ([`PREREG_M_eurusd_midday.md`](../research/results/portfolio/round13_structural/PREREG_M_eurusd_midday.md)). It
  logs and reports the USD-TOP flag of each trade, so its USD-TOP days also score F3.

Both skip 24/12 to 1/1. The lot is fixed (`--Lots`), never read off the account. The rule has no stop; the broker
gets a far guard stop (`--EmergencyStopPips=100`, touched by 0.11 % of E1's trades over 2016-2026 and by no F3 result,
[`ecb_window_cbot_2026-10-16.md`](../research/results/portfolio/ecb_window_cbot_2026-10-16.md)) for a bot that dies
with a position open.

The selector needs mid prices, which bars do not carry: the bot records the live USDJPY/USDCHF bid and ask at 18:00
New York and 07:00 London in `/root/ctrader_data/<BotId>_usd_top_quotes.csv` and reads its history from that log and
from [`cBot/seeds/ecb_usd_top_seed.csv`](../cBot/seeds/ecb_usd_top_seed.csv)
(`python -m research.tools.ecb_usd_top_seed`). A minute neither holds falls back to the bid close of an M15 bar, and
the bot logs the quote source of every decision.

### EURUSD — ECB Window F3

`m15` · ECB fix window

```bash
docker run -d \
  --name cbot-demo-eurusd-ecb-f3 \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/EcbWindowBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurusd-ecb-f3" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --UsdTopOnly=true \
  --Lots=0.01 \
  --EmergencyStopPips=100.0
```

### EURUSD — ECB Window E1

`m15` · ECB fix window

```bash
docker run -d \
  --name cbot-demo-eurusd-ecb-e1 \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/EcbWindowBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurusd-ecb-e1" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --UsdTopOnly=false \
  --Lots=0.1 \
  --EmergencyStopPips=100.0
```

---

## 👯 Running demo and live side by side

Nothing stops the same symbol × strategy cell from running on two accounts — the presets are account-agnostic. Four
things must differ per account:

1. **`--name` and `--BotId`** — swap the `demo` slug (`cbot-live-usdjpy-fix-gotobi`). Container names are unique per host.
2. **`--account`** — the live account number.
3. **`--AccountLabel`** — `live` (or `live-main`), so trades are tagged and routed to `/real/dashboard`.
4. **`--pwd-file`** — a dedicated password file if the live account sits under a different cTID.

Then create both accounts on the dashboard (**Setup Instances → New account**) so its account selector lists
each one.

And lower the risk flags on the live side — see [Adapting a block](#-adapting-a-block).

> 💡 **Prefer clicking?** The dashboard's **Docker Bot Management → Setup Instances** screen does all of this for you:
> pick (or create) a cTrader account, tick the symbol × strategy cells you want, and press **Create instances**. It
> generates exactly the commands above, saves them as bot configs and starts the containers. The cTID password is
> written to `$CTRADER_HOME/ctrader_data/ctid_<slug>_pwd` (mode 0600) and never stored in the database.
