# 🐳 Docker Instance Catalog — all 5 presets

Every instance AgentFxTrading ships: the Gotobi Fix bot on its three JPY pairs and the Crypto Donchian bot on BTCUSD
and ETHUSD = **5 `docker run` commands**, written out in full.

This file is the long form of the dashboard's **Docker Bot Management → Setup Instances** grid. Ticking a cell there
runs exactly the command printed here. Both come from [`app/cbot_presets.py`](../app/cbot_presets.py), which is the
single source of truth for strategy flags — `tests/app/test_cbot_presets.py` fails the build if this file and that module
drift apart.

> **Prerequisites live in [deployment.md](deployment.md).** Install the server, write the cTID password file and build
> the two `.algo` packages first: [Building the cBots](deployment.md#building-the-cbots) and
> [Running bots](deployment.md#running-bots). Come back here once `cBot/GotobiBot.algo` and
> `cBot/CryptoDonchianBot.algo` exist.

---

## 📋 Contents

- [Adapting a block](#-adapting-a-block)
- [Container naming](#-container-naming)
- [The 5-cell grid](#-the-5-cell-grid)
- [Gotobi Fix — `GotobiBot.algo`](#-gotobi-fix--gotobibotalgo)
- [Crypto Donchian — `CryptoDonchianBot.algo`](#-crypto-donchian--cryptodonchianbotalgo)
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

- **`--RiskPerTradeMoney`** is dollars per trade, not a percentage: set it to what one trade may lose on that account
  (Crypto Donchian scales it 0.5x-2x by breakout strength). The presets are sized for a demo balance.
- **`--network host`** assumes the API server runs on the same machine as the container. On a split setup, drop it and
  point `--ApiUrl` at the server's reachable address instead.

---

## 🏷️ Container naming

The dashboard names containers `cbot-<account slug>-<symbol>-<session>[-<strategy>]`, and the blocks below follow the
same scheme with `demo` as the slug:

| Strategy | Pattern | Example |
| :--- | :--- | :--- |
| Gotobi Fix | `cbot-<slug>-<symbol>-fix-gotobi` | `cbot-demo-usdjpy-fix-gotobi` |
| Crypto Donchian | `cbot-<slug>-<symbol>-h4-donchian` | `cbot-demo-btcusd-h4-donchian` |

The name doubles as `--BotId`, so `docker ps` tells you the account, symbol, session and strategy of every bot without
opening its flags — and the dashboard can match a running container back to its config row.

---

## 🗺️ The 5-cell grid

`period` · session for each cell. 🔬 = validated by the research, only on the JPY pairs; 🧪 = research C1, forward
test only (failed its 2025-26 holdout), only on BTCUSD and ETHUSD.

| Symbol | Gotobi Fix | Crypto Donchian |
| :--- | :--- | :--- |
| **USDJPY** | 🔬 `m15` · Tokyo fix | – |
| **EURJPY** | 🔬 `m15` · Tokyo fix | – |
| **GBPJPY** | 🔬 `m15` · Tokyo fix | – |
| **BTCUSD** | – | 🧪 `h1` · H4 breakout |
| **ETHUSD** | – | 🧪 `h1` · H4 breakout |

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
defaults and are the same on every pair; a cell only sets the risk, the entry spread cap and the days to sit out. Its
exposure is one position of one default risk, two legs a day, six gotobi days a month.

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
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31"
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
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31"
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
  --SkipDates="2026-12-25,2026-12-31,2027-05-05,2027-09-20,2027-12-31"
```

## 🪙 Crypto Donchian — `CryptoDonchianBot.algo`

Research candidate C1 in
[`research/results/portfolio/swing_lab_v2_2026-09-27.md`](../research/results/portfolio/swing_lab_v2_2026-09-27.md):
on an H4 close above the prior 55-bar high it buys (below the prior 55-bar low it sells); every qualifying bar is an
entry, so a breakout that keeps going stacks up to 3 positions. A position leaves on an H4 close below the prior
20-bar low (shorts: above the 20-bar high), at its stop of 3 x ATR20(H4) from the fill, or after 5 days. Like Gotobi
Fix it obeys the dashboard's pause and close commands. The H4 bars are
UTC-aligned (00:00, 04:00, ... UTC) as in the research; the bot builds them from H1 bars, so its chart is `h1` — the
broker's own H4 bars start at 21:00/22:00 UTC and would give other channels.

**Forward test only.** The rule was strong in 2018-2021 (R +0.276) and 2022-2024 (R +0.227) but failed its
pre-registered 2025-2026 holdout (R -0.025: BTCUSD -0.151, ETHUSD +0.123), so run it small and on demo first.

Every trade risks `--RiskPerTradeMoney` (dollars, never a share of equity) x a multiplier of 0.5-2 from the breakout's
distance past the channel against the median of this symbol's earlier breakouts, so one bot risks at most 3 x 2 x
the default at once. The channels, the stop, the scaling and the spread cap (10 % of the stop distance, which needs no
pip size) are the cBot's defaults; a cell only sets the risk. `--KillSwitchTrades=100` stops new entries once the mean
R of the last 100 closed trades is below `--KillSwitchMinR` (default 0); it is off by default because on 2018-2026 it
would have stopped ETHUSD in January 2020 and missed the next $12,000
([`crypto_donchian_cbot_2026-09-27.md`](../research/results/portfolio/crypto_donchian_cbot_2026-09-27.md)).

### BTCUSD — Crypto Donchian

`h1` · H4 breakout

The weaker of the two at the holdout (R -0.151; net +$380 only thanks to the lot scaling).

```bash
docker run -d \
  --name cbot-demo-btcusd-h4-donchian \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/CryptoDonchianBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=BTCUSD \
  --period=h1 \
  --full-access \
  --BotId="cbot-demo-btcusd-h4-donchian" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --RiskPerTradeMoney=100.0
```

### ETHUSD — Crypto Donchian

`h1` · H4 breakout

Positive in every era, holdout included (R +0.123).

```bash
docker run -d \
  --name cbot-demo-ethusd-h4-donchian \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/CryptoDonchianBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=ETHUSD \
  --period=h1 \
  --full-access \
  --BotId="cbot-demo-ethusd-h4-donchian" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --RiskPerTradeMoney=100.0
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
