# 🤖 AgentFxTrading - Hệ Thống Giao Dịch Tự Động Với AI

<div align="center">

**cBot cTrader + máy chủ ra quyết định FastAPI + dashboard web đa tài khoản**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Đây là bản dịch của README ngắn; tài liệu tham chiếu chi tiết trong `docs/` chỉ có bằng tiếng Anh.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Màn hình giám sát đa tài khoản: killzone phiên giao dịch, KPI tài khoản, vị thế đang mở và telemetry lệnh.*

</div>

---

## 📋 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Tính Năng Chính](#-tính-năng-chính)
- [Dashboard](#-dashboard)
- [Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
- [Chạy cBot](#-chạy-cbot)
- [Cấu Hình](#-cấu-hình)
- [Tài Liệu](#-tài-liệu)
- [Tình Trạng Nghiên Cứu](#-tình-trạng-nghiên-cứu)
- [Ủng Hộ & Sàn Giao Dịch](#-ủng-hộ--sàn-giao-dịch)
- [Đóng Góp](#-đóng-góp)
- [Giấy Phép](#-giấy-phép)

---

## 🎯 Tổng Quan

AgentFxTrading chạy các chiến lược giao dịch dưới dạng **cBot cTrader** (C#), mỗi tổ hợp chiến lược × mã × tài khoản
là một container Docker. Các bot có cổng AI gửi ảnh chụp thị trường tới **máy chủ FastAPI** (Python); máy chủ áp dụng
các cổng lọc cố định và kiểm tra rủi ro danh mục, và khi setup đạt yêu cầu thì hỏi **LLM** để ra quyết định. Mọi bot
đều báo cáo vị thế và telemetry về máy chủ; máy chủ lưu vào **PostgreSQL** (SQLite làm dự phòng khi chạy local) và
phục vụ **dashboard web** để giám sát, quản lý bot và backtest.

Hiện có năm cBot:

| cBot | Chiến lược | Quyết định |
| :--- | :--- | :--- |
| `cBot/AiAgentBot.cs` | TMS (Trend Momentum Signal) + Opening Range Breakout | Qua cổng AI |
| `cBot/AsianRangeJudasSweepBot.cs` | Asian Range Judas Sweep (quét thanh khoản kiểu ICT) | Qua cổng AI |
| `cBot/FlowRsiBot.cs` | FlowRSI: RSI nhanh/chậm lồng nhau + bộ lọc SMC | Qua cổng AI |
| `cBot/GotobiBot.cs` | Giao dịch Gotobi quanh giờ fix Tokyo trên USDJPY / EURJPY / GBPJPY | Theo luật |
| `cBot/CryptoDonchianBot.cs` | Breakout Donchian H4 trên BTCUSD / ETHUSD (forward test) | Theo luật |

Xem [docs/strategies.md](docs/strategies.md) để biết từng bot làm gì.

---

## 🚀 Tính Năng Chính

- **Nhiều LLM**: Qwen (DashScope), OpenAI, Anthropic Claude, Google Gemini, DeepSeek, hoặc endpoint tương thích OpenAI bất kỳ.
- **Cổng tiết kiệm chi phí**: máy chủ trả `HOLD` mà không gọi LLM khi không có setup hợp lệ.
- **Rủi ro danh mục**: kiểm tra lệnh vào ở cấp danh mục cùng giới hạn lỗ theo ngày cho tài khoản, chiến lược và container, chỉnh được trên dashboard.
- **Bot headless**: container Docker `ctrader-console`, tạo từ màn hình **Setup Instances** trên dashboard.
- **Watchdog**: khởi động lại container bị kẹt ở bước đăng nhập hoặc ngừng gửi dữ liệu.
- **Trang Backtest**: chạy backtest cTrader cho một bot đã cài trong container và vẽ biểu đồ báo cáo.
- **Lá chắn tin tức**: lịch tin quan trọng ForexFactory kèm đánh giá bằng AI.
- **Tách biệt Demo / Real**: dashboard và dữ liệu riêng cho tài khoản demo và tài khoản thật.

---

## 📊 Dashboard

| 📈 Tổng Quan & Phiên Giao Dịch | 🧠 Chiến Lược AI & Luồng Quyết Định |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![AI Strategy Feed](docs/screenshots/ai-thinking.png)](docs/screenshots/ai-thinking.png) |
| *Chỉ số KPI, vị thế đang mở, lệnh gần đây và killzone* | *Lập luận đa khung thời gian, độ tin cậy của LLM và gợi ý SL/TP* |

| 🏆 Bảng Xếp Hạng Hiệu Suất | 📰 Tin Đỏ ForexFactory & Đánh Giá AI |
| :---: | :---: |
| [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) | [![News Assessment](docs/screenshots/news-assessment.png)](docs/screenshots/news-assessment.png) |
| *Xếp hạng tổng hợp, tỷ lệ thắng và huy hiệu Tier S/A/B/C* | *Lịch tin quan trọng, mức ảnh hưởng theo đồng tiền và đánh giá vĩ mô* |

Mở `http://127.0.0.1:8000/demo/dashboard` cho tài khoản demo, `http://127.0.0.1:8000/real/dashboard` cho tài khoản
thật, hoặc `http://127.0.0.1:8000/` để quay lại chế độ dùng gần nhất.

---

## ⚡ Bắt Đầu Nhanh

### Cách 1: cài VPS bằng một lệnh (Ubuntu 22.04 / 24.04 / 26.04)

Trên VPS mới, với quyền root:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

Script hỏi SSH public key cho user `forge`, rồi cài PostgreSQL 17, Docker, máy chủ dưới dạng service systemd
`agentfx` (lắng nghe `127.0.0.1:8000`), build năm gói `.algo` của cBot và bật backup cơ sở dữ liệu hằng ngày.
**Đăng nhập SSH bằng mật khẩu bị tắt**, nên hãy kiểm tra key từ một terminal khác trước khi đóng phiên root. Chi tiết,
tuỳ chọn và cách nâng cấp: [docs/deployment.md](docs/deployment.md).

Sau đó mở dashboard qua tunnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`), điền LLM key vào
`/home/forge/AgentFxTrading/.env` và chạy `sudo systemctl restart agentfx`.

### Cách 2: chạy local / cài thủ công

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # rồi đặt LLM_PROVIDER và API key tương ứng
python app/server.py        # chạy tại http://127.0.0.1:8000
```

Nếu `DATABASE_URL` không trỏ tới một PostgreSQL kết nối được, máy chủ dùng file SQLite `portfolio.db`.

---

## 🤖 Chạy cBot

1. **Build các gói `.algo`** — script cài đặt đã làm việc này; muốn build thủ công xem
   [docs/deployment.md → Building the cBots](docs/deployment.md#building-the-cbots). Cũng có thể dán một file
   `cBot/*.cs` vào cTrader Desktop (**Automate → New cBot → Build**) rồi gắn vào chart.
2. **Tạo instance** — trên dashboard, **Docker Bot Management → Setup Instances**: chọn hoặc thêm tài khoản cTrader,
   tích các ô mã × chiến lược và bấm **Create instances**.
3. **Hoặc chạy tay** — mọi preset đều được viết thành lệnh `docker run` trong
   **[docs/docker-instances.md](docs/docker-instances.md)** (50 ô). Một ví dụ, XAUUSD TMS+ORB phiên New York:

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

Bản thân các preset nằm trong [`app/cbot_presets.py`](app/cbot_presets.py), nguồn sự thật duy nhất; README không chép
lại. Trên VPS cài bằng script, thay `-v /root:/root` bằng `-v /home/forge/ctrader:/root`.

---

## ⚙️ Cấu Hình

Mọi thiết lập của máy chủ lấy từ `.env` — bắt đầu từ [`.env.example`](.env.example). Tối thiểu cần `LLM_PROVIDER`
và API key của nhà cung cấp đó. Toàn bộ biến môi trường, định dạng `DASHBOARD_ACCOUNTS`, cách chọn cơ sở dữ liệu,
giới hạn rủi ro và các tham số cBot không thuộc preset được mô tả trong [docs/configuration.md](docs/configuration.md).

---

## 📚 Tài Liệu

| Tài liệu | Nội dung |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Thành phần, luồng request, nhóm API, cấu trúc dự án |
| [docs/strategies.md](docs/strategies.md) | Từng cBot làm gì và luật của nó nằm ở đâu |
| [docs/configuration.md](docs/configuration.md) | Biến `.env`, giới hạn rủi ro, tham số cBot |
| [docs/deployment.md](docs/deployment.md) | Script cài VPS, cài thủ công, build cBot, service, backup, test |
| [docs/docker-instances.md](docs/docker-instances.md) | Toàn bộ 50 lệnh `docker run` theo preset |
| `http://127.0.0.1:8000/docs` | Tham chiếu API tương tác do FastAPI tự sinh (cả `/redoc`) |
| [research/README.md](research/README.md) | Nghiên cứu chiến lược offline và kết luận |

---

## 🔬 Tình Trạng Nghiên Cứu

README này không công bố số liệu hiệu suất nào. Nghiên cứu offline trong [`research/`](research/README.md) cho thấy,
tính đến 2026-09-27, chưa chiến lược nào được kiểm tra — kể cả các bot TMS+ORB, Judas Sweep và FlowRSI đang chạy thật —
có lợi thế trụ được sau hiệu chỉnh kiểm định bội (multiple testing) và qua các năm ngoài mẫu. Ngoại lệ duy nhất đến
nay là giao dịch Gotobi trên các cặp JPY (`GotobiBot`), đã vượt holdout đăng ký trước; `CryptoDonchianBot` trượt
holdout và chỉ chạy forward test. Hãy coi mọi bot là thử nghiệm và chạy trên tài khoản demo trước.

> ⚠️ **Tuyên bố miễn trừ**: giao dịch sản phẩm đòn bẩy có rủi ro thua lỗ cao. Phần mềm này phục vụ nghiên cứu và học
> tập, không đảm bảo kết quả.

---

## ☕ Ủng Hộ & Sàn Giao Dịch

- ☕ **Buy Me a Coffee**: ủng hộ phát triển, thử nghiệm mô hình và bảo trì qua [buymeacoffee.com/kaz126](https://buymeacoffee.com/kaz126).

  [![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=kaz126&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/kaz126)

- 📈 **Sàn cTrader khuyên dùng**: **[Mở tài khoản IC Markets cTrader](https://ic.com/?camp=95400)** (link đối tác).

---

## 🤝 Đóng Góp

Mọi đóng góp đều được hoan nghênh: star repo, báo lỗi hoặc đề xuất tính năng tại
[Issues](https://github.com/kienphan/AgentFxTrading/issues), thảo luận tại
[Discussions](https://github.com/kienphan/AgentFxTrading/discussions), hoặc gửi pull request gọn, có kèm test.
Quy ước cho agent và code nằm trong [AGENTS.md](AGENTS.md). Liên hệ: senior1206@gmail.com.

---

## 📄 Giấy Phép

Dự án được phát hành theo giấy phép MIT.

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kienphan/AgentFxTrading&type=Date)](https://star-history.com/#kienphan/AgentFxTrading&Date)
