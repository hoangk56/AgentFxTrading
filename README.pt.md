# 🤖 AgentFxTrading - Sistema de Trading Automatizado com cBots

<div align="center">

**cBots do cTrader + servidor de relatórios FastAPI + painel web multi-conta**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Esta é uma tradução do README curto; a documentação de referência detalhada em `docs/` existe apenas em inglês.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Monitor multi-conta: sessões de mercado, KPIs da conta, posições abertas e telemetria de operações.*

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

O AgentFxTrading executa estratégias de trading como **cBots do cTrader** (C#), um contêiner Docker por estratégia ×
símbolo × conta. Os bots operam pelas próprias regras e reportam posições e telemetria a um **servidor FastAPI**
(Python), que as guarda no **PostgreSQL** (SQLite como alternativa local) e serve um **painel web** para
monitoramento, gestão de bots e backtests.

Hoje há um cBot:

| cBot | Estratégia |
| :--- | :--- |
| `cBot/GotobiBot.cs` | Operação Gotobi no fixing de Tóquio em USDJPY / EURJPY / GBPJPY |

Veja [docs/strategies.md](docs/strategies.md) para o que o bot faz.

---

## 🚀 Principais Recursos

- **Bots headless**: contêineres Docker `ctrader-console`, criados na tela **Setup Instances** do painel.
- **Comandos pelo painel**: fechar uma posição, pausar / retomar um bot, ou fechar as posições dele e pará-lo, na aba Bots.
- **Watchdog**: reinicia contêineres travados no login ou que deixaram de processar barras.
- **Ranking**: classifica os bots por P&L em USD ou neutro em lotes, em qualquer período.
- **Livro-razão (Ledger)**: saldo esperado vs saldo da corretora por conta; registre depósitos e saques e veja a diferença.
- **Página de backtest**: roda backtests do cTrader de um bot instalado em contêineres e mostra o relatório em gráficos.
- **Isolamento Demo / Real**: painéis e dados separados para contas demo e reais.

---

## 📊 Painel

| 📈 Visão Geral ao Vivo & Sessões | 🏆 Ranking de Desempenho |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *KPIs, posições abertas e operações recentes* | *Ranking composto, taxas de acerto e selos Tier S/A/B/C* |

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
serviço systemd `agentfx` (escutando em `127.0.0.1:8000`), compila o pacote `.algo` do cBot e ativa um
backup diário do banco de dados. **O login SSH por senha é desativado**, então confirme que a chave funciona a partir
de outro terminal antes de fechar a sessão root. Detalhes, opções e atualizações: [docs/deployment.md](docs/deployment.md).

Depois abra o painel por um túnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`) e adicione a sua conta cTrader
em **Docker Bot Management → Setup Instances**.

### Opção 2: local / manual

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # opcional: DATABASE_URL
python app/server.py        # serve em http://127.0.0.1:8000
```

Se `DATABASE_URL` não apontar para um PostgreSQL acessível, o servidor usa o arquivo SQLite `portfolio.db`.

---

## 🤖 Executando os cBots

1. **Compile o pacote `.algo`** — o instalador faz isso; para compilar manualmente veja
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots). Também é possível colar um arquivo
   `cBot/*.cs` no cTrader Desktop (**Automate → New cBot → Build**) e anexá-lo a um gráfico.
2. **Crie instâncias** — no painel, **Docker Bot Management → Setup Instances**: escolha ou adicione uma conta cTrader,
   marque as células símbolo × estratégia e clique em **Create instances**.
3. **Ou execute manualmente** — cada preset está escrito como um comando `docker run` em
   **[docs/docker-instances.md](docs/docker-instances.md)** (5 células). Um exemplo, Gotobi em USDJPY:

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

Os presets em si ficam em [`app/cbot_presets.py`](app/cbot_presets.py), a única fonte da verdade; o README não os
repete. Numa VPS configurada pelo instalador, troque `-v /root:/root` por `-v /home/forge/ctrader:/root`.

---

## ⚙️ Configuração

Todas as configurações do servidor vêm do `.env` — comece por [`.env.example`](.env.example); uma execução local não
precisa de nenhuma. Todas as variáveis, a escolha do banco de dados e os parâmetros
dos cBots que não fazem parte dos presets estão descritos em [docs/configuration.md](docs/configuration.md).

---

## 📚 Documentação

| Documento | Conteúdo |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Componentes, fluxo das requisições, grupos de API, estrutura do projeto |
| [docs/strategies.md](docs/strategies.md) | O que cada cBot faz e onde ficam as suas regras |
| [docs/configuration.md](docs/configuration.md) | Variáveis do `.env`, parâmetros dos cBots |
| [docs/deployment.md](docs/deployment.md) | Instalador de VPS, instalação manual, compilação dos cBots, serviço, backups, testes |
| [docs/docker-instances.md](docs/docker-instances.md) | Todos os 5 comandos `docker run` dos presets |
| `http://127.0.0.1:8000/docs` | Referência interativa da API gerada pelo FastAPI (também `/redoc`) |
| [research/README.md](research/README.md) | Pesquisa offline de estratégias e as suas conclusões |

---

## 🔬 Situação da Pesquisa

Este README não publica números de desempenho. A pesquisa offline em [`research/`](research/README.md) concluiu que,
em 2026-09-27, a operação Gotobi nos pares de JPY (`GotobiBot`) é a única estratégia testada que passou no seu holdout
pré-registrado. Trate o bot como experimental e rode-o primeiro numa conta demo.

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
