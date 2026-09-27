# 🤖 AgentFxTrading - Sistema de Trading Automatizado com IA

<div align="center">

**cBots do cTrader + servidor de decisão FastAPI + painel web multi-conta**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Esta é uma tradução do README curto; a documentação de referência detalhada em `docs/` existe apenas em inglês.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Monitor multi-conta: killzones das sessões, KPIs da conta, posições abertas e telemetria de operações.*

</div>

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Principais Recursos](#-principais-recursos)
- [Painel](#-painel)
- [Início Rápido](#-início-rápido)
- [Executando os cBots](#-executando-os-cbots)
- [Configuração](#-configuração)
- [Documentação](#-documentação)
- [Situação da Pesquisa](#-situação-da-pesquisa)
- [Apoio & Corretora](#-apoio--corretora)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Visão Geral

O AgentFxTrading executa estratégias de trading como **cBots do cTrader** (C#), um contêiner Docker por combinação de
estratégia × símbolo × conta. Os bots com filtro de IA enviam um retrato do mercado a um **servidor FastAPI**
(Python), que aplica filtros determinísticos e verificações de risco da carteira e, quando o setup se qualifica, pede
a decisão a um **LLM**. Todos os bots reportam posições e telemetria ao servidor, que as guarda no **PostgreSQL**
(SQLite como alternativa local) e serve um **painel web** para monitoramento, gestão de bots e backtests.

Hoje há cinco cBots:

| cBot | Estratégia | Decisão |
| :--- | :--- | :--- |
| `cBot/AiAgentBot.cs` | TMS (Trend Momentum Signal) + rompimento da faixa de abertura (ORB) | Filtro de IA |
| `cBot/AsianRangeJudasSweepBot.cs` | Asian Range Judas Sweep (varredura de liquidez estilo ICT) | Filtro de IA |
| `cBot/FlowRsiBot.cs` | FlowRSI: RSI rápido/lento aninhados + filtros SMC | Filtro de IA |
| `cBot/GotobiBot.cs` | Operação Gotobi em torno do fixing de Tóquio em USDJPY / EURJPY / GBPJPY | Por regras |
| `cBot/CryptoDonchianBot.cs` | Rompimento de Donchian H4 em BTCUSD / ETHUSD (forward test) | Por regras |

Veja [docs/strategies.md](docs/strategies.md) para o que cada bot faz.

---

## 🚀 Principais Recursos

- **Vários LLMs**: Qwen (DashScope), OpenAI, Anthropic Claude, Google Gemini, DeepSeek ou qualquer endpoint compatível com OpenAI.
- **Filtros de custo**: o servidor responde `HOLD` sem chamar o LLM quando nenhum setup se qualifica.
- **Risco da carteira**: verificações de entrada no nível da carteira mais limites de perda diária por conta, estratégia e contêiner, editáveis no painel.
- **Bots headless**: contêineres Docker `ctrader-console`, criados pela tela **Setup Instances** do painel.
- **Watchdog**: reinicia contêineres travados no login ou que pararam de enviar dados.
- **Página de backtest**: roda backtests do cTrader de um bot instalado em contêineres e mostra o relatório em gráficos.
- **Escudo de notícias**: calendário de alto impacto da ForexFactory com avaliação por IA.
- **Isolamento Demo / Real**: painéis e dados separados para contas demo e reais.

---

## 📊 Painel

| 📈 Visão Geral ao Vivo & Sessões | 🧠 Estratégia de IA & Feed de Decisões |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![AI Strategy Feed](docs/screenshots/ai-thinking.png)](docs/screenshots/ai-thinking.png) |
| *KPIs, posições abertas, operações recentes e killzones* | *Raciocínio multi-timeframe, confiança do LLM e orientação de SL/TP* |

| 🏆 Ranking de Desempenho | 📰 Notícias Vermelhas da ForexFactory & Avaliação por IA |
| :---: | :---: |
| [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) | [![News Assessment](docs/screenshots/news-assessment.png)](docs/screenshots/news-assessment.png) |
| *Ranking composto, taxas de acerto e selos Tier S/A/B/C* | *Calendário de alto impacto, impacto por moeda e avaliação macro* |

Abra `http://127.0.0.1:8000/demo/dashboard` para contas demo, `http://127.0.0.1:8000/real/dashboard` para contas
reais, ou `http://127.0.0.1:8000/` para voltar ao último modo usado.

---

## ⚡ Início Rápido

### Opção 1: instalação em VPS com um comando (Ubuntu 22.04 / 24.04 / 26.04)

Numa VPS nova, como root:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

O script pede a chave pública SSH do usuário `forge` e depois instala o PostgreSQL 17, o Docker, o servidor como o
serviço systemd `agentfx` (escutando em `127.0.0.1:8000`), compila os cinco pacotes `.algo` dos cBots e ativa um
backup diário do banco de dados. **O login SSH por senha é desativado**, então confirme que a chave funciona a partir
de outro terminal antes de fechar a sessão root. Detalhes, opções e atualizações: [docs/deployment.md](docs/deployment.md).

Depois abra o painel por um túnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`), coloque a sua chave de LLM em
`/home/forge/AgentFxTrading/.env` e execute `sudo systemctl restart agentfx`.

### Opção 2: local / manual

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # depois defina LLM_PROVIDER e a chave de API correspondente
python app/server.py        # serve em http://127.0.0.1:8000
```

Se `DATABASE_URL` não apontar para um PostgreSQL acessível, o servidor usa o arquivo SQLite `portfolio.db`.

---

## 🤖 Executando os cBots

1. **Compile os pacotes `.algo`** — o instalador faz isso; para compilar manualmente veja
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots). Também é possível colar um arquivo
   `cBot/*.cs` no cTrader Desktop (**Automate → New cBot → Build**) e anexá-lo a um gráfico.
2. **Crie instâncias** — no painel, **Docker Bot Management → Setup Instances**: escolha ou adicione uma conta cTrader,
   marque as células símbolo × estratégia e clique em **Create instances**.
3. **Ou execute manualmente** — cada preset está escrito como um comando `docker run` em
   **[docs/docker-instances.md](docs/docker-instances.md)** (50 células). Um exemplo, XAUUSD TMS+ORB na sessão de
   Nova York:

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

Os presets em si ficam em [`app/cbot_presets.py`](app/cbot_presets.py), a única fonte da verdade; o README não os
repete. Numa VPS configurada pelo instalador, troque `-v /root:/root` por `-v /home/forge/ctrader:/root`.

---

## ⚙️ Configuração

Todas as configurações do servidor vêm do `.env` — comece por [`.env.example`](.env.example). O mínimo é
`LLM_PROVIDER` e a chave de API desse provedor. Todas as variáveis, o formato de `DASHBOARD_ACCOUNTS`, a escolha do
banco de dados, os limites de risco e os parâmetros dos cBots que não fazem parte dos presets estão descritos em
[docs/configuration.md](docs/configuration.md).

---

## 📚 Documentação

| Documento | Conteúdo |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Componentes, fluxo das requisições, grupos de API, estrutura do projeto |
| [docs/strategies.md](docs/strategies.md) | O que cada cBot faz e onde ficam as suas regras |
| [docs/configuration.md](docs/configuration.md) | Variáveis do `.env`, limites de risco, parâmetros dos cBots |
| [docs/deployment.md](docs/deployment.md) | Instalador de VPS, instalação manual, compilação dos cBots, serviço, backups, testes |
| [docs/docker-instances.md](docs/docker-instances.md) | Os 50 comandos `docker run` dos presets |
| `http://127.0.0.1:8000/docs` | Referência interativa da API gerada pelo FastAPI (também `/redoc`) |
| [research/README.md](research/README.md) | Pesquisa offline de estratégias e as suas conclusões |

---

## 🔬 Situação da Pesquisa

Este README não publica números de desempenho. A pesquisa offline em [`research/`](research/README.md) concluiu que,
em 2026-09-27, nenhuma das estratégias testadas — incluindo os bots TMS+ORB, Judas Sweep e FlowRSI em produção —
mostra uma vantagem que sobreviva à correção para testes múltiplos e aos anos fora da amostra. A única exceção até
agora é a operação Gotobi nos pares de JPY (`GotobiBot`), que passou no seu holdout pré-registrado; o
`CryptoDonchianBot` falhou no holdout e roda apenas como forward test. Trate todos os bots como experimentais e rode-os
primeiro numa conta demo.

> ⚠️ **Aviso**: operar produtos alavancados envolve alto risco de perda. Este software é fornecido para pesquisa e
> educação, sem garantia de resultados.

---

## ☕ Apoio & Corretora

- ☕ **Buy Me a Coffee**: apoie o desenvolvimento, os testes de modelos e a manutenção em [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126).

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **Corretora cTrader recomendada**: **[Abrir uma conta IC Markets cTrader](https://ic.com/?camp=95400)** (link de parceiro).

---

## 🤝 Contribuindo

Contribuições são bem-vindas: dê uma estrela ao repositório, reporte bugs ou sugira recursos em
[Issues](https://github.com/kienphan/AgentFxTrading/issues), converse em
[Discussions](https://github.com/kienphan/AgentFxTrading/discussions) ou abra um pull request focado, com testes.
As convenções de agentes e de código estão em [AGENTS.md](AGENTS.md). Contato: senior1206@gmail.com.

---

## 📄 Licença

Este projeto é licenciado sob a Licença MIT.

---

## 📈 Histórico de Estrelas

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
