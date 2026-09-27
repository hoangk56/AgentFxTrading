# 🤖 AgentFxTrading - AI-Powered Automated Trading System

<div align="center">

**cTrader cBots + a FastAPI decision server + a multi-account web dashboard**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Multi-account trading monitor: session killzones, account KPIs, open positions and trade telemetry.*

</div>

---

## 📋 Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Dashboard](#-dashboard)
- [Quick Start](#-quick-start)
- [Running the cBots](#-running-the-cbots)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Research Status](#-research-status)
- [Support & Broker](#-support--broker)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

AgentFxTrading runs trading strategies as **cTrader cBots** (C#), one Docker container per strategy × symbol ×
account. The AI-gated bots send a market snapshot to a **FastAPI server** (Python), which applies deterministic
gates and portfolio risk checks and, when a setup qualifies, asks an **LLM** for the decision. Every bot reports
positions and telemetry back to the server, which stores them in **PostgreSQL** (SQLite as a local fallback) and
serves a **web dashboard** for monitoring, bot management and backtests.

Five cBots ship today:

| cBot | Strategy | Decision |
| :--- | :--- | :--- |
| `cBot/AiAgentBot.cs` | TMS (Trend Momentum Signal) + Opening Range Breakout | AI-gated |
| `cBot/AsianRangeJudasSweepBot.cs` | Asian Range Judas Sweep (ICT liquidity sweep) | AI-gated |
| `cBot/FlowRsiBot.cs` | FlowRSI: nested fast/slow RSI + SMC filters | AI-gated |
| `cBot/GotobiBot.cs` | Gotobi Tokyo-fix trade on USDJPY / EURJPY / GBPJPY | Rule-based |
| `cBot/CryptoDonchianBot.cs` | H4 Donchian breakout on BTCUSD / ETHUSD (forward test) | Rule-based |

See [docs/strategies.md](docs/strategies.md) for what each bot does.

---

## 🚀 Key Features

- **Multi-LLM**: Qwen (DashScope), OpenAI, Anthropic Claude, Google Gemini, DeepSeek, or any OpenAI-compatible endpoint.
- **Cost gates**: the server answers `HOLD` without calling the LLM when no setup qualifies.
- **Portfolio risk**: portfolio-level entry checks plus daily loss limits per account, strategy and container, editable on the dashboard.
- **Headless bots**: `ctrader-console` Docker containers, created from the dashboard's **Setup Instances** screen.
- **Watchdog**: restarts containers stuck at login or no longer sending data.
- **Backtest page**: runs cTrader backtests of an installed bot in containers and charts the report.
- **News shield**: ForexFactory high-impact calendar with an AI assessment.
- **Demo / Real isolation**: separate dashboards and data for demo and live accounts.

---

## 📊 Dashboard

| 📈 Live Overview & Market Sessions | 🧠 AI Strategy & Decision Feed |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![AI Strategy Feed](docs/screenshots/ai-thinking.png)](docs/screenshots/ai-thinking.png) |
| *KPI metrics, active positions, recent trades and killzones* | *Multi-timeframe reasoning, LLM confidence and SL/TP guidance* |

| 🏆 Quant Performance Leaderboard | 📰 ForexFactory Red News & AI Assessment |
| :---: | :---: |
| [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) | [![News Assessment](docs/screenshots/news-assessment.png)](docs/screenshots/news-assessment.png) |
| *Composite ranking, win rates and Tier S/A/B/C badges* | *High-impact calendar, currency impact and macro assessment* |

Open `http://127.0.0.1:8000/demo/dashboard` for demo accounts, `http://127.0.0.1:8000/real/dashboard` for live
accounts, or `http://127.0.0.1:8000/` to return to the mode you used last.

---

## ⚡ Quick Start

### Option 1: one-line VPS install (Ubuntu 22.04 / 24.04 / 26.04)

On a fresh VPS, as root:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

It asks for the SSH public key of the `forge` user, then installs PostgreSQL 17, Docker, the server as the
`agentfx` systemd service (bound to `127.0.0.1:8000`), builds the five cBot `.algo` packages and enables a daily
database backup. **Password SSH login is disabled**, so check that your key works from a second terminal before
closing the root session. Details, overrides and upgrades: [docs/deployment.md](docs/deployment.md).

Then open the dashboard through a tunnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`), put your LLM key in
`/home/forge/AgentFxTrading/.env` and run `sudo systemctl restart agentfx`.

### Option 2: local / manual

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then set LLM_PROVIDER and the matching API key
python app/server.py        # serves http://127.0.0.1:8000
```

Without `DATABASE_URL` pointing at a reachable PostgreSQL, the server falls back to the SQLite file `portfolio.db`.

---

## 🤖 Running the cBots

1. **Build the `.algo` packages** — the installer does this; for a manual build see
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots). You can also paste a
   `cBot/*.cs` file into cTrader Desktop (**Automate → New cBot → Build**) and attach it to a chart.
2. **Create instances** — on the dashboard, **Docker Bot Management → Setup Instances**: pick or add a cTrader
   account, tick the symbol × strategy cells and click **Create instances**.
3. **Or run them by hand** — every preset is written out as a `docker run` command in
   **[docs/docker-instances.md](docs/docker-instances.md)** (50 cells). One example, XAUUSD TMS+ORB on the New York
   session:

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

The presets themselves live in [`app/cbot_presets.py`](app/cbot_presets.py), the single source of truth; the
README does not repeat them. On a VPS set up by the installer, replace `-v /root:/root` with
`-v /home/forge/ctrader:/root`.

---

## ⚙️ Configuration

All server settings come from `.env` — start from [`.env.example`](.env.example). The minimum is `LLM_PROVIDER`
and that provider's API key. Every variable, the `DASHBOARD_ACCOUNTS` format, database selection, risk limits and
the cBot parameters that are not presets are described in [docs/configuration.md](docs/configuration.md).

---

## 📚 Documentation

| Document | Contents |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Components, request flow, API groups, project structure |
| [docs/strategies.md](docs/strategies.md) | What each cBot does and where its rules live |
| [docs/configuration.md](docs/configuration.md) | `.env` variables, risk limits, cBot parameters |
| [docs/deployment.md](docs/deployment.md) | VPS installer, manual setup, building cBots, service, backups, tests |
| [docs/docker-instances.md](docs/docker-instances.md) | All 50 preset `docker run` commands |
| `http://127.0.0.1:8000/docs` | Interactive API reference generated by FastAPI (also `/redoc`) |
| [research/README.md](research/README.md) | Offline strategy research and its conclusions |

---

## 🔬 Research Status

This README publishes no performance figures. The offline research in [`research/`](research/README.md) found
that, as of 2026-09-27, none of the strategies tested — the live TMS+ORB, Judas Sweep and FlowRSI bots included —
shows an edge that survives multiple-testing correction and out-of-sample years. The one exception so far is the
Gotobi JPY trade (`GotobiBot`), which passed its pre-registered holdout; `CryptoDonchianBot` failed its holdout and
runs as a forward test only. Treat every bot as experimental and run it on a demo account first.

> ⚠️ **Disclaimer**: trading leveraged products carries a high risk of loss. This software is provided for
> research and education, with no guarantee of results.

---

## ☕ Support & Broker

- ☕ **Buy Me a Coffee**: support development, model testing and maintenance via [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126).

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **Recommended cTrader broker**: **[Open an IC Markets cTrader Account](https://ic.com/?camp=95400)** (partner link).

---

## 🤝 Contributing

Contributions are welcome: star the repo, report bugs or suggest features in
[Issues](https://github.com/kienphan/AgentFxTrading/issues), discuss in
[Discussions](https://github.com/kienphan/AgentFxTrading/discussions), or open a focused pull request with tests.
Agent and code conventions are in [AGENTS.md](AGENTS.md). Contact: senior1206@gmail.com.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
