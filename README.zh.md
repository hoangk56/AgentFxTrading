# 🤖 AgentFxTrading - cBot 自动交易系统

<div align="center">

**cTrader cBot + FastAPI 报告服务器 + 多账户 Web 仪表盘**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*这是简短 README 的译文；`docs/` 中的详细参考文档仅提供英文版。*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*多账户交易监控：交易时段、账户 KPI、持仓和交易遥测。*

</div>

---

## 📋 目录

- [概述](#-概述)
- [主要功能](#-主要功能)
- [仪表盘](#-仪表盘)
- [快速开始](#-快速开始)
- [运行 cBot](#-运行-cbot)
- [配置](#-配置)
- [文档](#-文档)
- [研究现状](#-研究现状)
- [支持与经纪商](#-支持与经纪商)
- [贡献](#-贡献)
- [许可证](#-许可证)

---

## 🎯 概述

AgentFxTrading 以 **cTrader cBot**（C#）的形式运行交易策略，每个 策略 × 品种 × 账户 组合对应一个 Docker 容器。
bot 按各自的规则交易，并把持仓和遥测数据报告给 **FastAPI 服务器**（Python）；服务器将其存入 **PostgreSQL**
（本地运行时回退到 SQLite），并提供用于监控、bot 管理和回测的 **Web 仪表盘**。

目前有一个 cBot：

| cBot | 策略 |
| :--- | :--- |
| `cBot/GotobiBot.cs` | USDJPY / EURJPY / GBPJPY 的五十日（Gotobi）东京定盘交易 |

bot 的具体做法见 [docs/strategies.md](docs/strategies.md)。

---

## 🚀 主要功能

- **无界面 bot**：`ctrader-console` Docker 容器，可在仪表盘的 **Setup Instances** 页面创建。
- **仪表盘指令**：在 Bots 页中平掉某个持仓、暂停 / 恢复 bot，或平掉其全部持仓并停止它。
- **看门狗**：重启卡在登录阶段或不再处理 K 线的容器。
- **排行榜**：按美元盈亏或手数中性指标，对任意时段内的 bot 排名。
- **账本（Ledger）**：按账户对比预期余额与券商余额；记录入金/出金并查看差额。
- **回测页面**：在容器中对已安装的 bot 运行 cTrader 回测，并以图表展示报告。
- **模拟 / 实盘隔离**：模拟账户与实盘账户使用各自独立的仪表盘和数据。

---

## 📊 仪表盘

| 📈 实时概览与市场时段 | 🏆 绩效排行榜 |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *KPI 指标、当前持仓和近期交易* | *综合排名、胜率和 Tier S/A/B/C 徽章* |

模拟账户打开 `http://127.0.0.1:8000/demo/dashboard`，实盘账户打开 `http://127.0.0.1:8000/real/dashboard`，
或打开 `http://127.0.0.1:8000/` 回到上次使用的模式。

---

## ⚡ 快速开始

### 方式一：VPS 一键安装（Ubuntu 22.04 / 24.04 / 26.04）

在全新的 VPS 上以 root 身份运行：

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

脚本会询问 `forge` 用户的 SSH 公钥，然后安装 PostgreSQL 17、Docker、以 systemd 服务 `agentfx` 运行的服务器
（监听 `127.0.0.1:8000`），编译 cBot 的 `.algo` 包，并启用每日数据库备份。**SSH 密码登录会被禁用**，
因此在关闭 root 会话之前，请先在另一个终端确认密钥可以登录。详细说明、可选参数与升级方法：
[docs/deployment.md](docs/deployment.md)。

之后通过隧道打开仪表盘（`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`），并在
**Docker Bot Management → Setup Instances** 中添加你的 cTrader 账户。

### 方式二：本地 / 手动安装

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # 可选：DATABASE_URL
python app/server.py        # 运行于 http://127.0.0.1:8000
```

如果 `DATABASE_URL` 没有指向可连接的 PostgreSQL，服务器会使用 SQLite 文件 `portfolio.db`。

---

## 🤖 运行 cBot

1. **编译 `.algo` 包** — 安装脚本会完成这一步；手动编译请见
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots)。也可以把 `cBot/*.cs`
   粘贴到 cTrader Desktop（**Automate → New cBot → Build**）后加载到图表上。
2. **创建实例** — 在仪表盘的 **Docker Bot Management → Setup Instances** 中选择或添加 cTrader 账户，勾选
   品种 × 策略 单元格，然后点击 **Create instances**。
3. **或手动运行** — 所有预设都以 `docker run` 命令的形式写在
   **[docs/docker-instances.md](docs/docker-instances.md)** 中（5 个单元格）。示例：USDJPY 上的 Gotobi：

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

预设本身位于唯一的事实来源 [`app/cbot_presets.py`](app/cbot_presets.py)，README 不再重复。在用安装脚本部署的 VPS 上，
请把 `-v /root:/root` 替换为 `-v /home/forge/ctrader:/root`。

---

## ⚙️ 配置

服务器的所有设置都来自 `.env`，请从 [`.env.example`](.env.example) 开始；本地运行不需要设置任何变量。全部变量、
数据库选择以及不属于预设的 cBot 参数，见 [docs/configuration.md](docs/configuration.md)。

---

## 📚 文档

| 文档 | 内容 |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | 组件、请求流程、API 分组、项目结构 |
| [docs/strategies.md](docs/strategies.md) | 各 cBot 的做法及其规则所在位置 |
| [docs/configuration.md](docs/configuration.md) | `.env` 变量、cBot 参数 |
| [docs/deployment.md](docs/deployment.md) | VPS 安装脚本、手动安装、编译 cBot、服务、备份、测试 |
| [docs/docker-instances.md](docs/docker-instances.md) | 全部 5 条预设 `docker run` 命令 |
| `http://127.0.0.1:8000/docs` | FastAPI 自动生成的交互式 API 参考（另有 `/redoc`） |
| [research/README.md](research/README.md) | 离线策略研究及其结论 |

---

## 🔬 研究现状

本 README 不公布任何绩效数字。[`research/`](research/README.md) 中的离线研究发现，截至 2026-09-27，JPY 货币对上的
五十日交易（`GotobiBot`）是所测试策略中唯一通过预先登记的留出集检验的。请把该 bot 视为实验性质，并先在模拟账户上运行。

> ⚠️ **免责声明**：交易杠杆产品存在较高的亏损风险。本软件仅供研究和学习使用，不保证任何结果。

---

## ☕ 支持与经纪商

- ☕ **Buy Me a Coffee**：通过 [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126) 支持开发、模型测试和维护。

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **推荐的 cTrader 经纪商**：**[开设 IC Markets cTrader 账户](https://ic.com/?camp=95400)**（合作伙伴链接）。

---

## 🤝 贡献

欢迎贡献：为仓库点星、在 [Issues](https://github.com/kienphan/AgentFxTrading/issues) 报告缺陷或提出功能建议、
在 [Discussions](https://github.com/kienphan/AgentFxTrading/discussions) 参与讨论，或提交附带测试的小型 Pull Request。
Agent 与代码约定见 [AGENTS.md](AGENTS.md)。联系方式：senior1206@gmail.com。

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 📈 Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
