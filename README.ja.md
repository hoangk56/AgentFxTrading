# 🤖 AgentFxTrading - cBot 自動売買システム

<div align="center">

**cTrader cBot + FastAPI レポートサーバー + マルチアカウント Web ダッシュボード**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*これは短い README の翻訳です。`docs/` の詳細なリファレンスは英語のみです。*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*マルチアカウント監視画面：市場セッション、口座 KPI、保有ポジション、取引テレメトリ。*

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
1 つ使います。bot は自身のルールで取引し、ポジションとテレメトリを **FastAPI サーバー**（Python）に報告します。
サーバーはそれを **PostgreSQL**（ローカルでは SQLite にフォールバック）に保存し、監視・bot 管理・バックテスト用の
**Web ダッシュボード**を提供します。

現在 2 つの cBot があります：

| cBot | 戦略 |
| :--- | :--- |
| `cBot/GotobiBot.cs` | USDJPY / EURJPY / GBPJPY の五十日（ゴトウビ）東京仲値トレード |
| `cBot/CryptoDonchianBot.cs` | BTCUSD / ETHUSD の H4 ドンチャン・ブレイクアウト（フォワードテスト） |

各 bot の内容は [docs/strategies.md](docs/strategies.md) を参照してください。

---

## 🚀 主な機能

- **ヘッドレス bot**：`ctrader-console` の Docker コンテナを、ダッシュボードの **Setup Instances** 画面から作成。
- **ダッシュボードからの指示**：Bots タブでポジションの決済、bot の一時停止 / 再開、全ポジション決済と停止。
- **ウォッチドッグ**：ログインで止まった、または足の処理が止まったコンテナを再起動。
- **リーダーボード**：任意の期間で、USD 損益またはロット中立の指標で bot を順位付け。
- **バックテストページ**：インストール済み bot の cTrader バックテストをコンテナで実行し、レポートをグラフ表示。
- **デモ / リアルの分離**：デモ口座とリアル口座でダッシュボードとデータを分離。

---

## 📊 ダッシュボード

| 📈 ライブ概要＆市場セッション | 🏆 パフォーマンスリーダーボード |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *KPI、保有ポジション、最近の取引* | *総合ランキング、勝率、Tier S/A/B/C バッジ* |

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
としてのサーバー（`127.0.0.1:8000` で待ち受け）をインストールし、2 つの cBot `.algo` パッケージをビルドして、
データベースの日次バックアップを有効にします。**SSH のパスワードログインは無効化される**ため、root セッションを
閉じる前に別のターミナルで鍵によるログインを確認してください。詳細・オプション・アップグレード：
[docs/deployment.md](docs/deployment.md)。

その後トンネル経由でダッシュボードを開き（`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`）、
**Docker Bot Management → Setup Instances** で cTrader 口座を追加します。

### 方法 2：ローカル / 手動

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # 任意：DATABASE_URL、DASHBOARD_ACCOUNTS
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
   **[docs/docker-instances.md](docs/docker-instances.md)** に `docker run` コマンドとして書かれています（5 セル）。
   例：USDJPY の Gotobi：

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

プリセット本体は唯一の情報源である [`app/cbot_presets.py`](app/cbot_presets.py) にあり、README では繰り返しません。
インストーラーで構築した VPS では `-v /root:/root` を `-v /home/forge/ctrader:/root` に置き換えてください。

---

## ⚙️ 設定

サーバーの設定はすべて `.env` から読み込まれます。[`.env.example`](.env.example) から始めてください。ローカル実行では
設定は不要です。すべての変数、`DASHBOARD_ACCOUNTS` の形式、データベースの選択、プリセットに含まれない cBot
パラメーターは [docs/configuration.md](docs/configuration.md) にあります。

---

## 📚 ドキュメント

| ドキュメント | 内容 |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | 構成要素、リクエストの流れ、API グループ、プロジェクト構成 |
| [docs/strategies.md](docs/strategies.md) | 各 cBot の動作とルールの所在 |
| [docs/configuration.md](docs/configuration.md) | `.env` の変数、cBot パラメーター |
| [docs/deployment.md](docs/deployment.md) | VPS インストーラー、手動セットアップ、cBot ビルド、サービス、バックアップ、テスト |
| [docs/docker-instances.md](docs/docker-instances.md) | プリセットの `docker run` コマンド全 5 件 |
| `http://127.0.0.1:8000/docs` | FastAPI が自動生成する対話型 API リファレンス（`/redoc` も） |
| [research/README.md](research/README.md) | オフラインの戦略研究とその結論 |

---

## 🔬 研究の現状

この README はパフォーマンスの数値を掲載しません。[`research/`](research/README.md) のオフライン研究では、
2026-09-27 時点で、検証した戦略のうち事前登録したホールドアウトを通過したのは JPY ペアの五十日トレード
（`GotobiBot`）だけです。`CryptoDonchianBot` はホールドアウトで不合格となり、フォワードテストとしてのみ稼働して
います。どちらの bot も実験的なものとして扱い、まずデモ口座で動かしてください。

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
