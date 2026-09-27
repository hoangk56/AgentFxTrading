# 🐳 Docker Instance Catalog — all 50 presets

Every instance AgentFxTrading ships: **15 symbols × 3 strategies = 45 `docker run` commands**, plus the Gotobi Fix bot on
its three JPY pairs and the Crypto Donchian bot on BTCUSD and ETHUSD = **50**, written out in full.

This file is the long form of the dashboard's **Docker Bot Management → Setup Instances** grid. Ticking a cell there
runs exactly the command printed here. Both come from [`app/cbot_presets.py`](../app/cbot_presets.py), which is the
single source of truth for strategy flags — `tests/test_cbot_presets.py` fails the build if this file and that module
drift apart.

> **Prerequisites live in [deployment.md](deployment.md).** Install the server, write the cTID password file and build
> the five `.algo` packages first: [Building the cBots](deployment.md#building-the-cbots) and
> [Running bots](deployment.md#running-bots). Come back here once
> `cBot/AiAgentBot.algo`, `cBot/AsianRangeJudasSweepBot.algo`, `cBot/FlowRsiBot.algo`, `cBot/GotobiBot.algo` and
> `cBot/CryptoDonchianBot.algo` exist.

---

## 📋 Contents

- [Adapting a block](#-adapting-a-block)
- [Container naming](#-container-naming)
- [The 50-cell grid](#-the-50-cell-grid)
- [TMS + ORB — `AiAgentBot.algo`](#-tms--orb--aiagentbotalgo)
- [Asian Range Judas Sweep — `AsianRangeJudasSweepBot.algo`](#-asian-range-judas-sweep--asianrangejudassweepbotalgo)
- [FlowRSI — `FlowRsiBot.algo`](#-flowrsi--flowrsibotalgo)
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

- **`--RiskPerTradePercent`** (TMS+ORB) / **`--riskFactor`** (Judas) / **`--RiskPercentage`** + **`--MaxRiskPerTradeMoney`**
  (FlowRSI) — the presets are sized for a demo balance. Cut them to `0.1`–`0.2` on real capital. **`--RiskPerTradeMoney`**
  (Gotobi Fix, Crypto Donchian) is dollars per trade, not a percentage: set it to what one trade may lose on that
  account (Crypto Donchian scales it 0.5x-2x by breakout strength).
- **`--network host`** assumes the API server runs on the same machine as the container. On a split setup, drop it and
  point `--ApiUrl` / `--DashboardServerUrl` at the server's reachable address instead.

---

## 🏷️ Container naming

The dashboard names containers `cbot-<account slug>-<symbol>-<session>[-<strategy>]`, and the blocks below follow the
same scheme with `demo` as the slug:

| Strategy | Pattern | Example |
| :--- | :--- | :--- |
| TMS + ORB | `cbot-<slug>-<symbol>-<session>` | `cbot-demo-xauusd-newyork` |
| Judas Sweep | `cbot-<slug>-<symbol>-KZ-london-ny-judas` | `cbot-demo-xauusd-KZ-london-ny-judas` |
| FlowRSI | `cbot-<slug>-<symbol>-all-flowrsi` | `cbot-demo-xauusd-all-flowrsi` |
| Gotobi Fix | `cbot-<slug>-<symbol>-fix-gotobi` | `cbot-demo-usdjpy-fix-gotobi` |
| Crypto Donchian | `cbot-<slug>-<symbol>-h4-donchian` | `cbot-demo-btcusd-h4-donchian` |

The name doubles as `--BotId`, so `docker ps` tells you the account, symbol, session and strategy of every bot without
opening its flags — and the dashboard can match a running container back to its config row.

---

## 🗺️ The 50-cell grid

`period` · session for each cell. ✅ = a block the READMEs spelled out verbatim; 🧮 = derived from the nearest block,
scaled by pip size (indices `0.1`, XAU / BTC / ETH / JPY `0.01`, forex `0.0001`); 🔬 = validated by the research, only
on the JPY pairs; 🧪 = research C1, forward test only (failed its 2025-26 holdout), only on BTCUSD and ETHUSD.

| Symbol | TMS + ORB | Judas Sweep | FlowRSI | Gotobi Fix | Crypto Donchian |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **XAUUSD** | ✅ `m15` · New York | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **EURUSD** | ✅ `m15` · London | ✅ `m15` · London + NY killzones | ✅ `m15` · All sessions | – | – |
| **GBPUSD** | ✅ `m15` · London | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **USDJPY** | ✅ `m15` · Tokyo | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | 🔬 `m15` · Tokyo fix | – |
| **GBPJPY** | ✅ `m15` · London | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | 🔬 `m15` · Tokyo fix | – |
| **EURJPY** | ✅ `m15` · London | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | 🔬 `m15` · Tokyo fix | – |
| **USDCAD** | ✅ `m15` · New York | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **AUDUSD** | ✅ `m15` · Tokyo | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **AUDJPY** | ✅ `m15` · Tokyo | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **US30** | ✅ `m15` · New York | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **USTEC** | ✅ `m5` · New York | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **DE40** | ✅ `m15` · London | 🧮 `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **UK100** | ✅ `m15` · London | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | – |
| **BTCUSD** | 🧮 `m15` · New York | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | 🧪 `h1` · H4 breakout |
| **ETHUSD** | 🧮 `m15` · New York | ✅ `m15` · London + NY killzones | 🧮 `m15` · All sessions | – | 🧪 `h1` · H4 breakout |

---

## 📈 TMS + ORB — `AiAgentBot.algo`

Trend Momentum Signal plus an Opening Range Breakout, gated by the AI server. One bot per symbol per
session; ATR drives every stop, target and trail.

### XAUUSD — TMS+ORB

`m15` · New York

Documented block — the flags the README shipped, plus the gold pip floors the cBot used to hard-code: the giveback lock arms at `150` pips ($1.50) and an AI break-even needs `300` pips ($3) of profit.

```bash
docker run -d \
  --name cbot-demo-xauusd-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=XAUUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-xauusd-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --OrbStartHour=13 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=200.0 \
  --MinOrWidthPips=400.0 \
  --OrbBufferPips=50.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --GivebackArmMinPips=150.0 \
  --MinAdjustBeProfitPips=300.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=10 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### EURUSD — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-eurusd-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurusd-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=17 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=3.0 \
  --MinOrWidthPips=6.0 \
  --OrbBufferPips=1.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=5 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### GBPUSD — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-gbpusd-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpusd-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=17 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=4.5 \
  --MinOrWidthPips=10.0 \
  --OrbBufferPips=1.5 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=10 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### USDJPY — TMS+ORB

`m15` · Tokyo

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-usdjpy-tokyo \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdjpy-tokyo" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="tokyo" \
  --OrbStartHour=0 \
  --SessionEndHour=9 \
  --SessionDstRule="None" \
  --MinDecisiveBreakoutPips=4.0 \
  --MinOrWidthPips=8.0 \
  --OrbBufferPips=1.5 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=3 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### GBPJPY — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-gbpjpy-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpjpy-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=17 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=6.0 \
  --MinOrWidthPips=15.0 \
  --OrbBufferPips=2.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=5 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### EURJPY — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-eurjpy-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurjpy-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=17 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=5.0 \
  --MinOrWidthPips=12.0 \
  --OrbBufferPips=1.5 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=5 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### USDCAD — TMS+ORB

`m15` · New York

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-usdcad-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDCAD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdcad-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="newyork" \
  --OrbStartHour=13 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=4.0 \
  --MinOrWidthPips=10.0 \
  --OrbBufferPips=1.5 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=4 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### AUDUSD — TMS+ORB

`m15` · Tokyo

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-audusd-tokyo \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audusd-tokyo" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="tokyo" \
  --OrbStartHour=0 \
  --SessionEndHour=9 \
  --SessionDstRule="None" \
  --MinDecisiveBreakoutPips=3.0 \
  --MinOrWidthPips=8.0 \
  --OrbBufferPips=1.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=3 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### AUDJPY — TMS+ORB

`m15` · Tokyo

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-audjpy-tokyo \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audjpy-tokyo" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="tokyo" \
  --OrbStartHour=0 \
  --SessionEndHour=9 \
  --SessionDstRule="None" \
  --MinDecisiveBreakoutPips=4.0 \
  --MinOrWidthPips=10.0 \
  --OrbBufferPips=1.5 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=4 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### US30 — TMS+ORB

`m15` · New York

Documented block — the flags the README shipped, plus the index exit profile the cBot used to hard-code: Tier 2 at `2.5` ATR or `1200` pips, then a `0.9` ATR trail and at most `35%` giveback of the peak; the giveback lock arms at `1000` pips; an AI break-even needs `50` pips of profit.

*On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-us30-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=US30 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-us30-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="newyork_index" \
  --OrbStartHour=14 \
  --OrbStartMinute=30 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=30.0 \
  --MinOrWidthPips=80.0 \
  --OrbBufferPips=15.0 \
  --BreakevenTriggerAtr=1.6 \
  --BreakevenOffsetAtr=0.2 \
  --TrailTriggerAtr=2.2 \
  --TrailDistanceAtr=1.3 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --Tier2TriggerAtr=2.5 \
  --Tier2TrailDistanceAtr=0.9 \
  --Tier2GivebackMfeRatio=0.35 \
  --MinAdjustBeProfitPips=50.0 \
  --Tier2TriggerPips=1200.0 \
  --GivebackArmMinPips=1000.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=30 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### USTEC / NAS100 — TMS+ORB

`m5` · New York

Documented block — the flags the README shipped, plus the index exit profile the cBot used to hard-code: Tier 2 at `2.5` ATR or `600` pips, then a `0.9` ATR trail and at most `35%` giveback of the peak; the giveback lock arms at `600` pips; an AI break-even needs `50` pips of profit.

*Broker alias: some brokers name this symbol `NAS100`.*

```bash
docker run -d \
  --name cbot-demo-ustec-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USTEC \
  --period=m5 \
  --full-access \
  --BotId="cbot-demo-ustec-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="newyork_index" \
  --OrbStartHour=14 \
  --OrbStartMinute=30 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=25.0 \
  --MinOrWidthPips=70.0 \
  --OrbBufferPips=12.0 \
  --BreakevenTriggerAtr=1.6 \
  --BreakevenOffsetAtr=0.2 \
  --TrailTriggerAtr=2.2 \
  --TrailDistanceAtr=1.3 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --Tier2TriggerAtr=2.5 \
  --Tier2TrailDistanceAtr=0.9 \
  --Tier2GivebackMfeRatio=0.35 \
  --MinAdjustBeProfitPips=50.0 \
  --Tier2TriggerPips=600.0 \
  --GivebackArmMinPips=600.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=25 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### DE40 / GER40 — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, plus the index exit profile the cBot used to hard-code: Tier 2 at `2.5` ATR or `400` pips, then a `0.9` ATR trail and at most `35%` giveback of the peak; the giveback lock arms at `500` pips; an AI break-even needs `50` pips of profit.

*Broker alias: some brokers name this symbol `GER40`.*

```bash
docker run -d \
  --name cbot-demo-de40-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=DE40 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-de40-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=16 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=20.0 \
  --MinOrWidthPips=60.0 \
  --OrbBufferPips=10.0 \
  --BreakevenTriggerAtr=1.6 \
  --BreakevenOffsetAtr=0.2 \
  --TrailTriggerAtr=2.2 \
  --TrailDistanceAtr=1.3 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --Tier2TriggerAtr=2.5 \
  --Tier2TrailDistanceAtr=0.9 \
  --Tier2GivebackMfeRatio=0.35 \
  --MinAdjustBeProfitPips=50.0 \
  --Tier2TriggerPips=400.0 \
  --GivebackArmMinPips=500.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=25 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### UK100 / GB100 — TMS+ORB

`m15` · London

Documented block — the flags the README shipped, plus the index exit profile the cBot used to hard-code: Tier 2 at `2.5` ATR or `400` pips, then a `0.9` ATR trail and at most `35%` giveback of the peak; the giveback lock arms at `400` pips; an AI break-even needs `50` pips of profit. `MaxGivebackAtr` is `1.0`, not the README's `0.6`: the cBot raised every index to `1.0`, so `0.6` never applied.

*Broker alias: some brokers name this symbol `GB100`. On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-uk100-london \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=UK100 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-uk100-london" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="london" \
  --OrbStartHour=8 \
  --SessionEndHour=16 \
  --SessionDstRule="Europe" \
  --MinDecisiveBreakoutPips=25.0 \
  --MinOrWidthPips=120.0 \
  --OrbBufferPips=15.0 \
  --BreakevenTriggerAtr=1.6 \
  --BreakevenOffsetAtr=0.2 \
  --TrailTriggerAtr=2.2 \
  --TrailDistanceAtr=1.3 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=1.5 \
  --MaxSlAtr=4.5 \
  --MinTpAtr=2.0 \
  --MaxTpAtr=8.0 \
  --MaxGivebackAtr=1.0 \
  --Tier2TriggerAtr=2.5 \
  --Tier2TrailDistanceAtr=0.9 \
  --Tier2GivebackMfeRatio=0.35 \
  --MinAdjustBeProfitPips=50.0 \
  --Tier2TriggerPips=400.0 \
  --GivebackArmMinPips=400.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=1.5 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### BTCUSD — TMS+ORB

`m15` · New York

Derived from **XAUUSD TMS+ORB** ×50 (dollar volatility): `$100 / $200 / $25` breakout / OR width / buffer. An AI break-even needs `6000` pips ($60) of profit.

```bash
docker run -d \
  --name cbot-demo-btcusd-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=BTCUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-btcusd-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="newyork" \
  --OrbStartHour=13 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=10000.0 \
  --MinOrWidthPips=20000.0 \
  --OrbBufferPips=2500.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --MinAdjustBeProfitPips=6000.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=10 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

### ETHUSD — TMS+ORB

`m15` · New York

Derived from **XAUUSD TMS+ORB** ×4: `$8 / $16 / $2` breakout / OR width / buffer. An AI break-even needs `600` pips ($6) of profit.

```bash
docker run -d \
  --name cbot-demo-ethusd-newyork \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AiAgentBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=ETHUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-ethusd-newyork" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --TmsTimeFrame="Hour" \
  --EmaPeriod=5 \
  --SessionName="newyork" \
  --OrbStartHour=13 \
  --SessionEndHour=21 \
  --SessionDstRule="US" \
  --MinDecisiveBreakoutPips=800.0 \
  --MinOrWidthPips=1600.0 \
  --OrbBufferPips=200.0 \
  --BreakevenTriggerAtr=1.2 \
  --BreakevenOffsetAtr=0.1 \
  --TrailTriggerAtr=2.0 \
  --TrailDistanceAtr=1.0 \
  --PartialCloseRatio=0.5 \
  --MinSlAtr=0.8 \
  --MaxSlAtr=3.0 \
  --MinTpAtr=1.0 \
  --MaxTpAtr=6.0 \
  --MaxGivebackAtr=1.0 \
  --MinAdjustBeProfitPips=600.0 \
  --EnablePostTpGate=true \
  --PostTpPullbackAtr=0.5 \
  --BounceTradeEnabled=true \
  --BounceDistanceThreshold=10 \
  --RiskPerTradePercent=0.2 \
  --TrendTpDisabled=true
```

---

## 🏹 Asian Range Judas Sweep — `AsianRangeJudasSweepBot.algo`

ICT Smart Money Concepts: build the Asian range (00:00–06:00 UTC), wait for the London or New York killzone to
sweep it, then trade the reversal. All 15 cells run `m15` with `--UseAiGateMode=true`.

`breakEvenTrigger` is deliberately not shipped: `breakEvenMode` defaults to `Risk_Reward_Ratio` and the bot reads
that pip value only in its `Fixed_Pips` branch, so the per-symbol numbers the README listed never did anything —
`breakEvenRrTrigger` is what gates the move. Break-even stays on via `--enableBreakEvenPrice=true`.

### XAUUSD — Judas Sweep

`m15` · London + NY killzones

Documented block — the README flags, minus `breakEvenTrigger`, with the sweep buffer raised 30 → 500 pips ($5.00) to match the auto-scale the bot itself wants for gold.

```bash
docker run -d \
  --name cbot-demo-xauusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=XAUUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-xauusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-xauusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=200.0 \
  --maxAsianRangePips=8000.0 \
  --sweepBufferPips=500.0 \
  --AiSlMinFloorPips=200.0 \
  --stoplossPip=200.0 \
  --takeprofitPip=450.0 \
  --enableBreakEvenPrice=true
```

### EURUSD — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-eurusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-eurusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=15.0 \
  --maxAsianRangePips=45.0 \
  --sweepBufferPips=3.5 \
  --AiSlMinFloorPips=15.0 \
  --stoplossPip=15.0 \
  --takeprofitPip=35.0 \
  --enableBreakEvenPrice=true
```

### GBPUSD — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-gbpusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-gbpusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=15.0 \
  --maxAsianRangePips=45.0 \
  --sweepBufferPips=3.5 \
  --AiSlMinFloorPips=15.0 \
  --stoplossPip=15.0 \
  --takeprofitPip=35.0 \
  --enableBreakEvenPrice=true
```

### USDJPY — Judas Sweep

`m15` · London + NY killzones

Derived — reuses the **EURUSD / GBPUSD** major block unchanged.

```bash
docker run -d \
  --name cbot-demo-usdjpy-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdjpy-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-usdjpy-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=15.0 \
  --maxAsianRangePips=45.0 \
  --sweepBufferPips=3.5 \
  --AiSlMinFloorPips=15.0 \
  --stoplossPip=15.0 \
  --takeprofitPip=35.0 \
  --enableBreakEvenPrice=true
```

### GBPJPY — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-gbpjpy-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpjpy-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-gbpjpy-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=25.0 \
  --maxAsianRangePips=70.0 \
  --sweepBufferPips=5.0 \
  --AiSlMinFloorPips=25.0 \
  --stoplossPip=25.0 \
  --takeprofitPip=50.0 \
  --enableBreakEvenPrice=true
```

### EURJPY — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-eurjpy-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurjpy-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-eurjpy-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=25.0 \
  --maxAsianRangePips=70.0 \
  --sweepBufferPips=5.0 \
  --AiSlMinFloorPips=25.0 \
  --stoplossPip=25.0 \
  --takeprofitPip=50.0 \
  --enableBreakEvenPrice=true
```

### USDCAD — Judas Sweep

`m15` · London + NY killzones

Derived — reuses the **EURUSD / GBPUSD** major block unchanged.

```bash
docker run -d \
  --name cbot-demo-usdcad-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDCAD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdcad-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-usdcad-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=15.0 \
  --maxAsianRangePips=45.0 \
  --sweepBufferPips=3.5 \
  --AiSlMinFloorPips=15.0 \
  --stoplossPip=15.0 \
  --takeprofitPip=35.0 \
  --enableBreakEvenPrice=true
```

### AUDUSD — Judas Sweep

`m15` · London + NY killzones

Derived — reuses the **EURUSD / GBPUSD** major block unchanged.

```bash
docker run -d \
  --name cbot-demo-audusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-audusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=15.0 \
  --maxAsianRangePips=45.0 \
  --sweepBufferPips=3.5 \
  --AiSlMinFloorPips=15.0 \
  --stoplossPip=15.0 \
  --takeprofitPip=35.0 \
  --enableBreakEvenPrice=true
```

### AUDJPY — Judas Sweep

`m15` · London + NY killzones

Derived — reuses the **GBPJPY / EURJPY** cross block unchanged.

```bash
docker run -d \
  --name cbot-demo-audjpy-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audjpy-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-audjpy-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=25.0 \
  --maxAsianRangePips=70.0 \
  --sweepBufferPips=5.0 \
  --AiSlMinFloorPips=25.0 \
  --stoplossPip=25.0 \
  --takeprofitPip=50.0 \
  --enableBreakEvenPrice=true
```

### US30 — Judas Sweep

`m15` · London + NY killzones

Derived from **UK100 Judas** ×5 by daily range (60 / 400 index points).

*On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-us30-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=US30 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-us30-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-us30-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=600.0 \
  --maxAsianRangePips=4000.0 \
  --sweepBufferPips=150.0 \
  --AiSlMinFloorPips=750.0 \
  --stoplossPip=750.0 \
  --takeprofitPip=1750.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

### USTEC / NAS100 — Judas Sweep

`m15` · London + NY killzones

Derived from **UK100 Judas** ×4 by daily range (50 / 300 index points).

*Broker alias: some brokers name this symbol `NAS100`.*

```bash
docker run -d \
  --name cbot-demo-ustec-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USTEC \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-ustec-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-ustec-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=500.0 \
  --maxAsianRangePips=3000.0 \
  --sweepBufferPips=120.0 \
  --AiSlMinFloorPips=600.0 \
  --stoplossPip=600.0 \
  --takeprofitPip=1400.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

### DE40 / GER40 — Judas Sweep

`m15` · London + NY killzones

Derived from **UK100 Judas** ×3 by daily range (35 / 250 index points).

*Broker alias: some brokers name this symbol `GER40`.*

```bash
docker run -d \
  --name cbot-demo-de40-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=DE40 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-de40-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-de40-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=350.0 \
  --maxAsianRangePips=2500.0 \
  --sweepBufferPips=90.0 \
  --AiSlMinFloorPips=450.0 \
  --stoplossPip=450.0 \
  --takeprofitPip=1000.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

### UK100 / GB100 — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

*Broker alias: some brokers name this symbol `GB100`. On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-uk100-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=UK100 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-uk100-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-uk100-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=120.0 \
  --maxAsianRangePips=800.0 \
  --sweepBufferPips=30.0 \
  --AiSlMinFloorPips=150.0 \
  --stoplossPip=150.0 \
  --takeprofitPip=350.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

### BTCUSD — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-btcusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=BTCUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-btcusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-btcusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=10000.0 \
  --maxAsianRangePips=400000.0 \
  --sweepBufferPips=1500.0 \
  --AiSlMinFloorPips=20000.0 \
  --stoplossPip=25000.0 \
  --takeprofitPip=60000.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

### ETHUSD — Judas Sweep

`m15` · London + NY killzones

Documented block — the flags the README shipped, minus `breakEvenTrigger`.

```bash
docker run -d \
  --name cbot-demo-ethusd-KZ-london-ny-judas \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/AsianRangeJudasSweepBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=ETHUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-ethusd-KZ-london-ny-judas" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --label="cbot-demo-ethusd-KZ-london-ny-judas" \
  --DashboardServerUrl="http://127.0.0.1:8000" \
  --UseDirectAiApi=false \
  --UseAiGateMode=true \
  --minAsianRangePips=800.0 \
  --maxAsianRangePips=35000.0 \
  --sweepBufferPips=150.0 \
  --AiSlMinFloorPips=1500.0 \
  --stoplossPip=2000.0 \
  --takeprofitPip=5000.0 \
  --enableBreakEvenPrice=true \
  --riskFactor=0.2
```

---

## 🌊 FlowRSI — `FlowRsiBot.algo`

Nested fast/slow RSI with SMC structure, fair-value-gap detection and a premium/discount filter. The RSI and
risk flags never change per symbol — only the four pip-sized filters do.

### XAUUSD — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; the four pip filters are resized for gold (`$0.5 / $0.5 / $8 / $0.2`), and the SL floor is `$15` (`MinSlFloorPips=1500`) with `$10` of profit before break-even (`MinBreakEvenPips=1000`).

```bash
docker run -d \
  --name cbot-demo-xauusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=XAUUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-xauusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=50.0 \
  --MaxSpreadPips=50.0 \
  --TrailingStopDistancePips=800.0 \
  --BreakEvenExtraPips=20.0 \
  --MinSlFloorPips=1500.0 \
  --MinBreakEvenPips=1000.0
```

### EURUSD — FlowRSI

`m15` · All sessions

Documented block — the flags the README shipped, unchanged.

```bash
docker run -d \
  --name cbot-demo-eurusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true
```

### GBPUSD — FlowRSI

`m15` · All sessions

Derived — RSI, SMC and risk flags are symbol-agnostic, so this is the **EURUSD FlowRSI** block unchanged; the cBot's own pip defaults apply (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-gbpusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true
```

### USDJPY — FlowRSI

`m15` · All sessions

Derived — the **EURUSD FlowRSI** block plus the JPY floors: `MinSlFloorPips=18` and `MinBreakEvenPips=15` (the cBot applied these to every JPY pair on its own before they became flags). The other pip filters keep the cBot's defaults (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-usdjpy-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdjpy-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --MinSlFloorPips=18.0 \
  --MinBreakEvenPips=15.0
```

### GBPJPY — FlowRSI

`m15` · All sessions

Derived — the **EURUSD FlowRSI** block plus the JPY floors: `MinSlFloorPips=18` and `MinBreakEvenPips=15` (the cBot applied these to every JPY pair on its own before they became flags). The other pip filters keep the cBot's defaults (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-gbpjpy-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=GBPJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-gbpjpy-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --MinSlFloorPips=18.0 \
  --MinBreakEvenPips=15.0
```

### EURJPY — FlowRSI

`m15` · All sessions

Derived — the **EURUSD FlowRSI** block plus the JPY floors: `MinSlFloorPips=18` and `MinBreakEvenPips=15` (the cBot applied these to every JPY pair on its own before they became flags). The other pip filters keep the cBot's defaults (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-eurjpy-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=EURJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-eurjpy-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --MinSlFloorPips=18.0 \
  --MinBreakEvenPips=15.0
```

### USDCAD — FlowRSI

`m15` · All sessions

Derived — RSI, SMC and risk flags are symbol-agnostic, so this is the **EURUSD FlowRSI** block unchanged; the cBot's own pip defaults apply (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-usdcad-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USDCAD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-usdcad-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true
```

### AUDUSD — FlowRSI

`m15` · All sessions

Derived — RSI, SMC and risk flags are symbol-agnostic, so this is the **EURUSD FlowRSI** block unchanged; the cBot's own pip defaults apply (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-audusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true
```

### AUDJPY — FlowRSI

`m15` · All sessions

Derived — the **EURUSD FlowRSI** block plus the JPY floors: `MinSlFloorPips=18` and `MinBreakEvenPips=15` (the cBot applied these to every JPY pair on its own before they became flags). The other pip filters keep the cBot's defaults (`FvgMinPips=2`, `MaxSpreadPips=30`, `TrailingStopDistancePips=25`, `BreakEvenExtraPips=0.5`).

```bash
docker run -d \
  --name cbot-demo-audjpy-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=AUDJPY \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-audjpy-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --MinSlFloorPips=18.0 \
  --MinBreakEvenPips=15.0
```

### US30 — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for a 0.1-pip index (`10 / 6 / 35 / 1` points).

*On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-us30-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=US30 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-us30-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=100.0 \
  --MaxSpreadPips=60.0 \
  --TrailingStopDistancePips=350.0 \
  --BreakEvenExtraPips=10.0
```

### USTEC — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for a 0.1-pip index (`8 / 5 / 35 / 1` points).

*Broker alias: some brokers name this symbol `NAS100`.*

```bash
docker run -d \
  --name cbot-demo-ustec-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=USTEC \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-ustec-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=80.0 \
  --MaxSpreadPips=50.0 \
  --TrailingStopDistancePips=350.0 \
  --BreakEvenExtraPips=10.0
```

### DE40 — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for a 0.1-pip index (`5 / 4 / 35 / 1` points).

*Broker alias: some brokers name this symbol `GER40`.*

```bash
docker run -d \
  --name cbot-demo-de40-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=DE40 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-de40-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=50.0 \
  --MaxSpreadPips=40.0 \
  --TrailingStopDistancePips=350.0 \
  --BreakEvenExtraPips=10.0
```

### UK100 — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for a 0.1-pip index (`3 / 3 / 35 / 0.5` points).

*Broker alias: some brokers name this symbol `GB100`. On cTrader 1 pip = 0.1 index point.*

```bash
docker run -d \
  --name cbot-demo-uk100-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=UK100 \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-uk100-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=30.0 \
  --MaxSpreadPips=30.0 \
  --TrailingStopDistancePips=350.0 \
  --BreakEvenExtraPips=5.0
```

### BTCUSD — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for crypto (`$50 / $50 / $300 / $10`).

```bash
docker run -d \
  --name cbot-demo-btcusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=BTCUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-btcusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=5000.0 \
  --MaxSpreadPips=5000.0 \
  --TrailingStopDistancePips=30000.0 \
  --BreakEvenExtraPips=1000.0
```

### ETHUSD — FlowRSI

`m15` · All sessions

Derived from **EURUSD FlowRSI**; pip filters resized for crypto (`$3 / $5 / $20 / $1`).

```bash
docker run -d \
  --name cbot-demo-ethusd-all-flowrsi \
  --restart unless-stopped \
  --network host \
  -v $(pwd):/workspace \
  -v /root:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /workspace/cBot/FlowRsiBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_pwd \
  --account=YOUR_ACCOUNT_ID \
  --symbol=ETHUSD \
  --period=m15 \
  --full-access \
  --BotId="cbot-demo-ethusd-all-flowrsi" \
  --ApiUrl="http://127.0.0.1:8000/trade" \
  --AccountLabel="demo" \
  --FastRsiPeriod=7 \
  --SlowRsiPeriod=14 \
  --EnableSmcFilter=true \
  --EnableFvgDetection=true \
  --EnablePremiumDiscountFilter=true \
  --RiskPercentage=0.5 \
  --MaxRiskPerTradeMoney=50.0 \
  --TargetRiskReward=1.5 \
  --UseAiGateMode=true \
  --FvgMinPips=300.0 \
  --MaxSpreadPips=500.0 \
  --TrailingStopDistancePips=2000.0 \
  --BreakEvenExtraPips=100.0
```

---

## 🗾 Gotobi Fix — `GotobiBot.algo`

The research's validated algorithm (C3 in
[`research/results/portfolio/swing_lab_v2_2026-09-27.md`](../research/results/portfolio/swing_lab_v2_2026-09-27.md)):
on gotobi days (the 5th, 10th, 15th, 20th, 25th and the month's last day, a weekend one moved to the Friday before)
it buys at 18:00 UTC the evening before, closes at the 09:55 Tokyo fix (00:55 UTC), sells at the fix and closes at
11:55 Tokyo (02:55 UTC). No AI gate, no `/trade` calls: it reports its trades, sends telemetry and obeys the
dashboard's pause and close commands like the other bots. It only exists for the three JPY pairs the research
validated.

Every trade risks `--RiskPerTradeMoney` (dollars, never a share of equity) at a stop of 3 x ATR20(H1), so the lot
follows volatility around that default. The schedule, the stop and the one-position-at-a-time rule are the cBot's
defaults and are the same on every pair; a cell only sets the risk and the entry spread cap. Server-side daily loss
limits are enforced on `/trade` and so do not gate this bot: its own exposure is one position of one default risk,
two legs a day, eight gotobi days a month. Japanese public holidays have no Tokyo fix; list them in
`--SkipDates="yyyy-MM-dd,..."` to sit them out. The default skips 2026-12-25 (a Friday gotobi day while the broker
is closed for Christmas). A `--SkipDates` value replaces that default, so include 2026-12-25 in it.

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
  --RiskPerTradeMoney=50.0 \
  --MaxSpreadPips=3.0
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
  --RiskPerTradeMoney=50.0 \
  --MaxSpreadPips=3.0
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
  --RiskPerTradeMoney=50.0 \
  --MaxSpreadPips=4.0
```

## 🪙 Crypto Donchian — `CryptoDonchianBot.algo`

Research candidate C1 in
[`research/results/portfolio/swing_lab_v2_2026-09-27.md`](../research/results/portfolio/swing_lab_v2_2026-09-27.md):
on an H4 close above the prior 55-bar high it buys (below the prior 55-bar low it sells); every qualifying bar is an
entry, so a breakout that keeps going stacks up to 3 positions. A position leaves on an H4 close below the prior
20-bar low (shorts: above the 20-bar high), at its stop of 3 x ATR20(H4) from the fill, or after 5 days. Like Gotobi
Fix it has no AI gate and no `/trade` calls, and obeys the dashboard's pause and close commands. The H4 bars are
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

1. **`--name` and `--BotId`** — swap the `demo` slug (`cbot-live-xauusd-newyork`). Container names are unique per host.
2. **`--account`** — the live account number.
3. **`--AccountLabel`** — `live` (or `live-main`), so trades are tagged and routed to `/real/dashboard`.
4. **`--pwd-file`** — a dedicated password file if the live account sits under a different cTID.

Then register both accounts in `.env` so the dashboard renders a tab for each:

```bash
DASHBOARD_ACCOUNTS=demo-10101649|10101649|demo|Demo Account;live-88888888|88888888|live|Live Main
```

And lower the risk flags on the live side — see [Adapting a block](#-adapting-a-block).

> 💡 **Prefer clicking?** The dashboard's **Docker Bot Management → Setup Instances** screen does all of this for you:
> pick (or create) a cTrader account, tick the symbol × strategy cells you want, and press **Create instances**. It
> generates exactly the commands above, saves them as bot configs and starts the containers. The cTID password is
> written to `$CTRADER_HOME/ctrader_data/ctid_<slug>_pwd` (mode 0600) and never stored in the database.
