# 🤖 AgentFxTrading - AI 自動売買システム

<div align="center">

**cTrader cBot + FastAPI 判断サーバー + マルチアカウント Web ダッシュボード**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*これは短い README の翻訳です。`docs/` の詳細なリファレンスは英語のみです。*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*マルチアカウント監視画面：セッションのキルゾーン、口座 KPI、保有ポジション、取引テレメトリ。*

</div>

---

## 📋 目次

- [概要](#-概要)
- [主な機能](#-主な機能)
- [ダッシュボード](#-ダッシュボード)
- [クイックスタート](#-クイックスタート)
- [cBot の実行](#-cbot-の実行)
- [設定](#-設定)
- [ドキュメント](#-ドキュメント)
- [研究の現状](#-研究の現状)
- [サポート＆ブローカー](#-サポートブローカー)
- [貢献](#-貢献)
- [ライセンス](#-ライセンス)

---

## 🎯 概要

AgentFxTrading は取引戦略を **cTrader cBot**（C#）として実行し、戦略 × 銘柄 × 口座ごとに Docker コンテナを
1 つ使います。AI ゲート付きの bot は市場スナップショットを **FastAPI サーバー**（Python）に送り、サーバーは
決定論的なゲートとポートフォリオのリスクチェックを適用したうえで、条件を満たすセットアップについて **LLM**
に判断を求めます。すべての bot はポジションとテレメトリをサーバーに報告し、サーバーはそれを
**PostgreSQL**（ローカルでは SQLite にフォールバック）に保存し、監視・bot 管理・バックテスト用の
**Web ダッシュボード**を提供します。

現在 5 つの cBot があります：

| cBot | 戦略 | 判断方式 |
| :--- | :--- | :--- |
| `cBot/AiAgentBot.cs` | TMS（Trend Momentum Signal）+ Opening Range Breakout | AI ゲート |
| `cBot/AsianRangeJudasSweepBot.cs` | Asian Range Judas Sweep（ICT 流の流動性スイープ） | AI ゲート |
| `cBot/FlowRsiBot.cs` | FlowRSI：速い/遅い RSI の入れ子 + SMC フィルター | AI ゲート |
| `cBot/GotobiBot.cs` | USDJPY / EURJPY / GBPJPY の五十日（ゴトウビ）東京仲値トレード | ルールベース |
| `cBot/CryptoDonchianBot.cs` | BTCUSD / ETHUSD の H4 ドンチャン・ブレイクアウト（フォワードテスト） | ルールベース |

各 bot の内容は [docs/strategies.md](docs/strategies.md) を参照してください。

---

## 🚀 主な機能

- **複数 LLM 対応**：Qwen（DashScope）、OpenAI、Anthropic Claude、Google Gemini、DeepSeek、または任意の OpenAI 互換エンドポイント。
- **コストゲート**：有効なセットアップがなければ、サーバーは LLM を呼ばずに `HOLD` を返します。
- **ポートフォリオリスク**：ポートフォリオ単位のエントリーチェックに加え、口座・戦略・コンテナごとの日次損失上限（ダッシュボードで編集可能）。
- **ヘッドレス bot**：`ctrader-console` の Docker コンテナを、ダッシュボードの **Setup Instances** 画面から作成。
- **ウォッチドッグ**：ログインで止まった、またはデータ送信が途絶えたコンテナを再起動。
- **バックテストページ**：インストール済み bot の cTrader バックテストをコンテナで実行し、レポートをグラフ表示。
- **ニュースシールド**：ForexFactory の重要指標カレンダーと AI による評価。
- **デモ / リアルの分離**：デモ口座とリアル口座でダッシュボードとデータを分離。

---

## 📊 ダッシュボード

| 📈 ライブ概要＆市場セッション | 🧠 AI 戦略＆判断フィード |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![AI Strategy Feed](docs/screenshots/ai-thinking.png)](docs/screenshots/ai-thinking.png) |
| *KPI、保有ポジション、最近の取引、キルゾーン* | *マルチタイムフレームの推論、LLM の確信度、SL/TP の目安* |

| 🏆 パフォーマンスリーダーボード | 📰 ForexFactory 重要ニュース＆ AI 評価 |
| :---: | :---: |
| [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) | [![News Assessment](docs/screenshots/news-assessment.png)](docs/screenshots/news-assessment.png) |
| *総合ランキング、勝率、Tier S/A/B/C バッジ* | *重要指標カレンダー、通貨への影響、マクロ評価* |

デモ口座は `http://127.0.0.1:8000/demo/dashboard`、リアル口座は `http://127.0.0.1:8000/real/dashboard`、
`http://127.0.0.1:8000/` は前回使ったモードに戻ります。

---

## ⚡ クイックスタート

### 方法 1：VPS へのワンライナーインストール（Ubuntu 22.04 / 24.04 / 26.04）

新しい VPS で root として：

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

スクリプトは `forge` ユーザーの SSH 公開鍵を尋ね、その後 PostgreSQL 17、Docker、systemd サービス `agentfx`
としてのサーバー（`127.0.0.1:8000` で待ち受け）をインストールし、5 つの cBot `.algo` パッケージをビルドして、
データベースの日次バックアップを有効にします。**SSH のパスワードログインは無効化される**ため、root セッションを
閉じる前に別のターミナルで鍵によるログインを確認してください。詳細・オプション・アップグレード：
[docs/deployment.md](docs/deployment.md)。

その後トンネル経由でダッシュボードを開き（`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`）、LLM キーを
`/home/forge/AgentFxTrading/.env` に書いて `sudo systemctl restart agentfx` を実行します。

### 方法 2：ローカル / 手動

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # LLM_PROVIDER と対応する API キーを設定
python app/server.py        # http://127.0.0.1:8000 で起動
```

`DATABASE_URL` が接続可能な PostgreSQL を指していない場合、サーバーは SQLite ファイル `portfolio.db` を使います。

---

## 🤖 cBot の実行

1. **`.algo` パッケージをビルド** — インストーラーが行います。手動ビルドは
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots) を参照。`cBot/*.cs` を
   cTrader Desktop に貼り付けて（**Automate → New cBot → Build**）チャートに適用することもできます。
2. **インスタンスを作成** — ダッシュボードの **Docker Bot Management → Setup Instances** で cTrader 口座を選択または
   追加し、銘柄 × 戦略のセルにチェックを入れて **Create instances** をクリック。
3. **または手動で実行** — すべてのプリセットは
   **[docs/docker-instances.md](docs/docker-instances.md)** に `docker run` コマンドとして書かれています（50 セル）。
   例：XAUUSD TMS+ORB、ニューヨークセッション：

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

プリセット本体は唯一の情報源である [`app/cbot_presets.py`](app/cbot_presets.py) にあり、README では繰り返しません。
インストーラーで構築した VPS では `-v /root:/root` を `-v /home/forge/ctrader:/root` に置き換えてください。

---

## ⚙️ 設定

サーバーの設定はすべて `.env` から読み込まれます。[`.env.example`](.env.example) から始めてください。最低限必要なのは
`LLM_PROVIDER` とそのプロバイダーの API キーです。すべての変数、`DASHBOARD_ACCOUNTS` の形式、データベースの選択、
リスク上限、プリセットに含まれない cBot パラメーターは [docs/configuration.md](docs/configuration.md) にあります。

---

## 📚 ドキュメント

| ドキュメント | 内容 |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | 構成要素、リクエストの流れ、API グループ、プロジェクト構成 |
| [docs/strategies.md](docs/strategies.md) | 各 cBot の動作とルールの所在 |
| [docs/configuration.md](docs/configuration.md) | `.env` 変数、リスク上限、cBot パラメーター |
| [docs/deployment.md](docs/deployment.md) | VPS インストーラー、手動セットアップ、cBot ビルド、サービス、バックアップ、テスト |
| [docs/docker-instances.md](docs/docker-instances.md) | プリセットの `docker run` コマンド全 50 件 |
| `http://127.0.0.1:8000/docs` | FastAPI が自動生成する対話型 API リファレンス（`/redoc` も） |
| [research/README.md](research/README.md) | オフラインの戦略研究とその結論 |

---

## 🔬 研究の現状

この README はパフォーマンスの数値を掲載しません。[`research/`](research/README.md) のオフライン研究では、
2026-09-27 時点で、検証したどの戦略も（稼働中の TMS+ORB、Judas Sweep、FlowRSI の bot を含む）多重検定の補正と
サンプル外の年を通過するエッジを示していません。これまでの唯一の例外は JPY ペアの五十日トレード（`GotobiBot`）で、
事前登録したホールドアウトを通過しました。`CryptoDonchianBot` はホールドアウトで不合格となり、フォワードテストとして
のみ稼働しています。すべての bot を実験的なものとして扱い、まずデモ口座で動かしてください。

> ⚠️ **免責事項**：レバレッジ商品の取引には大きな損失リスクがあります。本ソフトウェアは研究・教育目的で提供され、
> 結果を保証するものではありません。

---

## ☕ サポート＆ブローカー

- ☕ **Buy Me a Coffee**：開発、モデル検証、保守を [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126) で支援できます。

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **おすすめの cTrader ブローカー**：**[IC Markets cTrader 口座を開設](https://ic.com/?camp=95400)**（パートナーリンク）。

---

## 🤝 貢献

貢献を歓迎します：リポジトリへのスター、[Issues](https://github.com/kienphan/AgentFxTrading/issues) でのバグ報告や機能提案、
[Discussions](https://github.com/kienphan/AgentFxTrading/discussions) での議論、テスト付きの小さなプルリクエスト。
エージェントとコードの規約は [AGENTS.md](AGENTS.md) にあります。連絡先：senior1206@gmail.com。

---

## 📄 ライセンス

本プロジェクトは MIT ライセンスで提供されています。

---

## 📈 スター履歴

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
