# 🤖 AgentFxTrading - Automated cBot Trading System

<div align="center">

**cTrader cBots + a FastAPI reporting server + a multi-account web dashboard**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Multi-account trading monitor: market sessions, account KPIs, open positions and trade telemetry.*

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
account. The bots trade on their own rules and report positions and telemetry to a **FastAPI server** (Python),
which stores them in **PostgreSQL** (SQLite as a local fallback) and serves a **web dashboard** for monitoring, bot
management and backtests.

Two cBots ship today:

| cBot | Strategy |
| :--- | :--- |
| `cBot/GotobiBot.cs` | Gotobi Tokyo-fix trade on USDJPY / EURJPY / GBPJPY |
| `cBot/CryptoDonchianBot.cs` | H4 Donchian breakout on BTCUSD / ETHUSD (forward test) |

See [docs/strategies.md](docs/strategies.md) for what each bot does.

---

## 🚀 Key Features

- **Headless bots**: `ctrader-console` Docker containers, created from the dashboard's **Setup Instances** screen.
- **Dashboard commands**: close a position, pause / resume a bot, or close its positions and stop it, from the Bots tab.
- **Watchdog**: restarts containers stuck at login or no longer handling bars.
- **Leaderboard**: ranks the bots by USD P&L or lot-neutral, over any period.
- **Ledger**: expected vs broker balance per account; record deposits and withdrawals, see any discrepancy.
- **Backtest page**: runs cTrader backtests of an installed bot in containers and charts the report.
- **Demo / Real isolation**: separate dashboards and data for demo and live accounts.

---

## 📊 Dashboard

| 📈 Live Overview & Market Sessions | 🏆 Quant Performance Leaderboard |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *KPI metrics, active positions and recent trades* | *Composite ranking, win rates and Tier S/A/B/C badges* |

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
`agentfx` systemd service (bound to `127.0.0.1:8000`), builds the two cBot `.algo` packages and enables a daily
database backup. **Password SSH login is disabled**, so check that your key works from a second terminal before
closing the root session. Details, overrides and upgrades: [docs/deployment.md](docs/deployment.md).

Then open the dashboard through a tunnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`) and add your cTrader
account on **Docker Bot Management → Setup Instances**.

### Option 2: local / manual

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # optional: DATABASE_URL
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
   **[docs/docker-instances.md](docs/docker-instances.md)** (5 cells). One example, Gotobi on USDJPY:

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

The presets themselves live in [`app/cbot_presets.py`](app/cbot_presets.py), the single source of truth; the
README does not repeat them. On a VPS set up by the installer, replace `-v /root:/root` with
`-v /home/forge/ctrader:/root`.

---

## ⚙️ Configuration

All server settings come from `.env` — start from [`.env.example`](.env.example); a local run needs none of them.
Every variable, database selection and the cBot parameters that are not presets are
described in [docs/configuration.md](docs/configuration.md).

---

## 📚 Documentation

| Document | Contents |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Components, request flow, API groups, project structure |
| [docs/strategies.md](docs/strategies.md) | What each cBot does and where its rules live |
| [docs/configuration.md](docs/configuration.md) | `.env` variables, cBot parameters |
| [docs/deployment.md](docs/deployment.md) | VPS installer, manual setup, building cBots, service, backups, tests |
| [docs/docker-instances.md](docs/docker-instances.md) | All 5 preset `docker run` commands |
| `http://127.0.0.1:8000/docs` | Interactive API reference generated by FastAPI (also `/redoc`) |
| [research/README.md](research/README.md) | Offline strategy research and its conclusions |

---

## 🔬 Research Status

This README publishes no performance figures. The offline research in [`research/`](research/README.md) found that,
as of 2026-09-27, the Gotobi JPY trade (`GotobiBot`) is the one strategy tested that passed its pre-registered
holdout; `CryptoDonchianBot` failed its holdout and runs as a forward test only. Treat both bots as experimental and
run them on a demo account first.

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
