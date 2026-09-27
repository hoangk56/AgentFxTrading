# 🤖 AgentFxTrading - Автоматическая торговая система на cBot'ах

<div align="center">

**cBot'ы cTrader + сервер отчётов на FastAPI + веб-панель для нескольких счетов**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Это перевод краткого README; подробная справочная документация в `docs/` есть только на английском.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Мониторинг нескольких счетов: рыночные сессии, KPI счетов, открытые позиции и телеметрия сделок.*

</div>

---

## 📋 Содержание

- [Обзор](#-обзор)
- [Основные возможности](#-основные-возможности)
- [Панель управления](#-панель-управления)
- [Быстрый старт](#-быстрый-старт)
- [Запуск cBot'ов](#-запуск-cbotов)
- [Конфигурация](#-конфигурация)
- [Документация](#-документация)
- [Состояние исследований](#-состояние-исследований)
- [Поддержка и брокер](#-поддержка-и-брокер)
- [Участие в проекте](#-участие-в-проекте)
- [Лицензия](#-лицензия)

---

## 🎯 Обзор

AgentFxTrading запускает торговые стратегии как **cBot'ы cTrader** (C#), по одному Docker-контейнеру на каждую
комбинацию стратегия × инструмент × счёт. Боты торгуют по своим правилам и сообщают о позициях и телеметрии
**серверу на FastAPI** (Python); сервер хранит их в **PostgreSQL** (при локальном запуске — в SQLite) и отдаёт
**веб-панель** для мониторинга, управления ботами и бэктестов.

Сейчас есть два cBot'а:

| cBot | Стратегия |
| :--- | :--- |
| `cBot/GotobiBot.cs` | Сделка Gotobi вокруг токийского фиксинга на USDJPY / EURJPY / GBPJPY |
| `cBot/CryptoDonchianBot.cs` | Пробой канала Дончиана H4 на BTCUSD / ETHUSD (форвард-тест) |

Что делает каждый бот, описано в [docs/strategies.md](docs/strategies.md).

---

## 🚀 Основные возможности

- **Боты без интерфейса**: Docker-контейнеры `ctrader-console`, создаются на экране **Setup Instances** панели.
- **Команды из панели**: закрыть позицию, приостановить / возобновить бота или закрыть его позиции и остановить — во вкладке Bots.
- **Watchdog**: перезапускает контейнеры, зависшие на входе или переставшие обрабатывать бары.
- **Рейтинг**: ранжирует ботов по P&L в USD или без учёта объёма лота за любой период.
- **Страница бэктестов**: запускает бэктесты cTrader установленного бота в контейнерах и строит графики отчёта.
- **Разделение демо / реал**: отдельные панели и данные для демо- и реальных счетов.

---

## 📊 Панель управления

| 📈 Обзор и рыночные сессии | 🏆 Рейтинг эффективности |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *KPI, открытые позиции и последние сделки* | *Сводный рейтинг, процент выигрышей и значки Tier S/A/B/C* |

Откройте `http://127.0.0.1:8000/demo/dashboard` для демо-счетов, `http://127.0.0.1:8000/real/dashboard` для реальных
счетов или `http://127.0.0.1:8000/`, чтобы вернуться в последний использованный режим.

---

## ⚡ Быстрый старт

### Вариант 1: установка на VPS одной командой (Ubuntu 22.04 / 24.04 / 26.04)

На новом VPS от имени root:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

Скрипт спрашивает публичный SSH-ключ пользователя `forge`, затем устанавливает PostgreSQL 17, Docker, сервер как
systemd-сервис `agentfx` (слушает `127.0.0.1:8000`), собирает два пакета `.algo` и включает ежедневный бэкап базы
данных. **Вход по SSH с паролем отключается**, поэтому перед закрытием сессии root проверьте вход по ключу из другого
терминала. Подробности, параметры и обновление: [docs/deployment.md](docs/deployment.md).

Затем откройте панель через туннель (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`) и добавьте счёт cTrader в
**Docker Bot Management → Setup Instances**.

### Вариант 2: локально / вручную

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # необязательно: DATABASE_URL, DASHBOARD_ACCOUNTS
python app/server.py        # работает на http://127.0.0.1:8000
```

Если `DATABASE_URL` не указывает на доступный PostgreSQL, сервер использует файл SQLite `portfolio.db`.

---

## 🤖 Запуск cBot'ов

1. **Соберите пакеты `.algo`** — установщик делает это сам; ручная сборка описана в
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots). Можно также вставить файл
   `cBot/*.cs` в cTrader Desktop (**Automate → New cBot → Build**) и запустить его на графике.
2. **Создайте инстансы** — в панели откройте **Docker Bot Management → Setup Instances**, выберите или добавьте счёт
   cTrader, отметьте ячейки инструмент × стратегия и нажмите **Create instances**.
3. **Или запустите вручную** — каждый пресет записан как команда `docker run` в
   **[docs/docker-instances.md](docs/docker-instances.md)** (5 ячеек). Пример: Gotobi на USDJPY:

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

Сами пресеты находятся в [`app/cbot_presets.py`](app/cbot_presets.py) — единственном источнике истины; README их не
повторяет. На VPS, установленном скриптом, замените `-v /root:/root` на `-v /home/forge/ctrader:/root`.

---

## ⚙️ Конфигурация

Все настройки сервера берутся из `.env` — начните с [`.env.example`](.env.example); для локального запуска ни одна
не обязательна. Все переменные, формат `DASHBOARD_ACCOUNTS`, выбор базы данных и параметры cBot'ов, не входящие в
пресеты, описаны в [docs/configuration.md](docs/configuration.md).

---

## 📚 Документация

| Документ | Содержание |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Компоненты, поток запросов, группы API, структура проекта |
| [docs/strategies.md](docs/strategies.md) | Что делает каждый cBot и где находятся его правила |
| [docs/configuration.md](docs/configuration.md) | Переменные `.env`, параметры cBot'ов |
| [docs/deployment.md](docs/deployment.md) | Установщик VPS, ручная установка, сборка cBot'ов, сервис, бэкапы, тесты |
| [docs/docker-instances.md](docs/docker-instances.md) | Все 5 команд `docker run` по пресетам |
| `http://127.0.0.1:8000/docs` | Интерактивный справочник API, генерируемый FastAPI (также `/redoc`) |
| [research/README.md](research/README.md) | Офлайн-исследование стратегий и его выводы |

---

## 🔬 Состояние исследований

Этот README не публикует показателей доходности. Офлайн-исследование в [`research/`](research/README.md) показало,
что на 2026-09-27 сделка Gotobi на парах с JPY (`GotobiBot`) — единственная из проверенных стратегий, прошедшая
заранее зарегистрированный holdout; `CryptoDonchianBot` holdout не прошёл и работает только как форвард-тест.
Считайте оба бота экспериментальными и сначала запускайте их на демо-счёте.

> ⚠️ **Отказ от ответственности**: торговля продуктами с кредитным плечом сопряжена с высоким риском убытков. Программа
> предоставляется для исследований и обучения, без гарантии результатов.

---

## ☕ Поддержка и брокер

- ☕ **Buy Me a Coffee**: поддержите разработку, тестирование моделей и сопровождение на [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126).

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **Рекомендуемый брокер cTrader**: **[Открыть счёт IC Markets cTrader](https://ic.com/?camp=95400)** (партнёрская ссылка).

---

## 🤝 Участие в проекте

Мы рады любому вкладу: поставьте звезду репозиторию, сообщайте об ошибках и предлагайте функции в
[Issues](https://github.com/kienphan/AgentFxTrading/issues), обсуждайте в
[Discussions](https://github.com/kienphan/AgentFxTrading/discussions) или присылайте небольшие pull request'ы с тестами.
Соглашения для агентов и кода — в [AGENTS.md](AGENTS.md). Контакт: senior1206@gmail.com.

---

## 📄 Лицензия

Проект распространяется по лицензии MIT.

---

## 📈 История звёзд

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
