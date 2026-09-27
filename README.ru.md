# 🤖 AgentFxTrading - Автоматическая торговая система на базе ИИ

<div align="center">

**cBot'ы cTrader + сервер решений на FastAPI + веб-панель для нескольких счетов**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Это перевод краткого README; подробная справочная документация в `docs/` есть только на английском.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Мониторинг нескольких счетов: киллзоны сессий, KPI счетов, открытые позиции и телеметрия сделок.*

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
комбинацию стратегия × инструмент × счёт. Боты с ИИ-фильтром отправляют снимок рынка на **сервер FastAPI** (Python),
который применяет детерминированные фильтры и проверки риска портфеля, а когда сетап подходит, запрашивает решение у
**LLM**. Все боты сообщают серверу о позициях и телеметрии; сервер хранит их в **PostgreSQL** (при локальном запуске —
SQLite как запасной вариант) и обслуживает **веб-панель** для мониторинга, управления ботами и бэктестов.

Сейчас есть пять cBot'ов:

| cBot | Стратегия | Решение |
| :--- | :--- | :--- |
| `cBot/AiAgentBot.cs` | TMS (Trend Momentum Signal) + пробой диапазона открытия (ORB) | Через ИИ-фильтр |
| `cBot/AsianRangeJudasSweepBot.cs` | Asian Range Judas Sweep (сбор ликвидности в стиле ICT) | Через ИИ-фильтр |
| `cBot/FlowRsiBot.cs` | FlowRSI: вложенные быстрый/медленный RSI + фильтры SMC | Через ИИ-фильтр |
| `cBot/GotobiBot.cs` | Сделка Gotobi вокруг токийского фиксинга на USDJPY / EURJPY / GBPJPY | По правилам |
| `cBot/CryptoDonchianBot.cs` | Пробой канала Дончиана на H4 по BTCUSD / ETHUSD (форвард-тест) | По правилам |

Что делает каждый бот, описано в [docs/strategies.md](docs/strategies.md).

---

## 🚀 Основные возможности

- **Несколько LLM**: Qwen (DashScope), OpenAI, Anthropic Claude, Google Gemini, DeepSeek или любой OpenAI-совместимый endpoint.
- **Фильтры затрат**: если подходящего сетапа нет, сервер отвечает `HOLD`, не вызывая LLM.
- **Риск портфеля**: проверки входа на уровне портфеля плюс дневные лимиты убытка по счёту, стратегии и контейнеру, настраиваемые в панели.
- **Боты без интерфейса**: Docker-контейнеры `ctrader-console`, создаваемые на экране **Setup Instances** панели.
- **Watchdog**: перезапускает контейнеры, застрявшие на входе в систему или переставшие присылать данные.
- **Страница бэктестов**: запускает бэктест cTrader установленного бота в контейнере и строит графики по отчёту.
- **Новостной щит**: календарь важных событий ForexFactory с оценкой от ИИ.
- **Разделение Demo / Real**: отдельные панели и данные для демо- и реальных счетов.

---

## 📊 Панель управления

| 📈 Обзор и рыночные сессии | 🧠 Стратегия ИИ и лента решений |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![AI Strategy Feed](docs/screenshots/ai-thinking.png)](docs/screenshots/ai-thinking.png) |
| *KPI, открытые позиции, последние сделки и киллзоны* | *Рассуждения по нескольким таймфреймам, уверенность LLM и уровни SL/TP* |

| 🏆 Рейтинг эффективности | 📰 Красные новости ForexFactory и оценка ИИ |
| :---: | :---: |
| [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) | [![News Assessment](docs/screenshots/news-assessment.png)](docs/screenshots/news-assessment.png) |
| *Сводный рейтинг, процент выигрышей и значки Tier S/A/B/C* | *Календарь важных событий, влияние на валюты и макрооценка* |

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
systemd-сервис `agentfx` (слушает `127.0.0.1:8000`), собирает пять пакетов `.algo` и включает ежедневный бэкап базы
данных. **Вход по SSH с паролем отключается**, поэтому перед закрытием сессии root проверьте вход по ключу из другого
терминала. Подробности, параметры и обновление: [docs/deployment.md](docs/deployment.md).

Затем откройте панель через туннель (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`), впишите ключ LLM в
`/home/forge/AgentFxTrading/.env` и выполните `sudo systemctl restart agentfx`.

### Вариант 2: локально / вручную

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # затем укажите LLM_PROVIDER и соответствующий API-ключ
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
   **[docs/docker-instances.md](docs/docker-instances.md)** (50 ячеек). Пример: XAUUSD TMS+ORB, нью-йоркская сессия:

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

Сами пресеты находятся в [`app/cbot_presets.py`](app/cbot_presets.py) — единственном источнике истины; README их не
повторяет. На VPS, установленном скриптом, замените `-v /root:/root` на `-v /home/forge/ctrader:/root`.

---

## ⚙️ Конфигурация

Все настройки сервера берутся из `.env` — начните с [`.env.example`](.env.example). Минимально нужны `LLM_PROVIDER` и
API-ключ этого провайдера. Все переменные, формат `DASHBOARD_ACCOUNTS`, выбор базы данных, лимиты риска и параметры
cBot'ов, не входящие в пресеты, описаны в [docs/configuration.md](docs/configuration.md).

---

## 📚 Документация

| Документ | Содержание |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Компоненты, поток запросов, группы API, структура проекта |
| [docs/strategies.md](docs/strategies.md) | Что делает каждый cBot и где находятся его правила |
| [docs/configuration.md](docs/configuration.md) | Переменные `.env`, лимиты риска, параметры cBot'ов |
| [docs/deployment.md](docs/deployment.md) | Установщик VPS, ручная установка, сборка cBot'ов, сервис, бэкапы, тесты |
| [docs/docker-instances.md](docs/docker-instances.md) | Все 50 команд `docker run` по пресетам |
| `http://127.0.0.1:8000/docs` | Интерактивный справочник API, генерируемый FastAPI (также `/redoc`) |
| [research/README.md](research/README.md) | Офлайн-исследование стратегий и его выводы |

---

## 🔬 Состояние исследований

Этот README не публикует никаких показателей доходности. Офлайн-исследование в [`research/`](research/README.md)
показало, что на 2026-09-27 ни одна из проверенных стратегий — включая работающих ботов TMS+ORB, Judas Sweep и FlowRSI —
не имеет преимущества, которое выдерживает поправку на множественные проверки и вневыборочные годы. Единственное
исключение на сегодня — сделка Gotobi на парах с JPY (`GotobiBot`), прошедшая заранее зарегистрированную отложенную
выборку (holdout); `CryptoDonchianBot` её не прошёл и работает только как форвард-тест. Считайте всех ботов
экспериментальными и сначала запускайте их на демо-счёте.

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
