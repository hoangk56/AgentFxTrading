# 🤖 AgentFxTrading - Hệ Thống Giao Dịch Tự Động Bằng cBot

<div align="center">

**cBot cTrader + máy chủ nhận báo cáo FastAPI + dashboard web đa tài khoản**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/stargazers)
[![Forks](https://img.shields.io/github/forks/kienphan/AgentFxTrading?style=social)](https://github.com/kienphan/AgentFxTrading/network/members)
[![Issues](https://img.shields.io/github/issues/kienphan/AgentFxTrading)](https://github.com/kienphan/AgentFxTrading/issues)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kaz126)

[🇬🇧 English](README.md) | [🇻🇳 Tiếng Việt](README.vi.md) | [🇨🇳 中文](README.zh.md) | [🇵🇹 Português](README.pt.md) | [🇯🇵 日本語](README.ja.md) | [🇷🇺 Русский](README.ru.md)

*Đây là bản dịch của README ngắn; tài liệu tham chiếu chi tiết trong `docs/` chỉ có bằng tiếng Anh.*

<br/>

<img src="docs/screenshots/overview.png" alt="AgentFxTrading Web Dashboard Overview" width="95%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);" />

*Màn hình giám sát đa tài khoản: phiên giao dịch, KPI tài khoản, vị thế đang mở và telemetry lệnh.*

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
là một container Docker. Các bot giao dịch theo luật của riêng chúng và báo cáo vị thế, telemetry về **máy chủ
FastAPI** (Python); máy chủ lưu vào **PostgreSQL** (SQLite làm dự phòng khi chạy local) và phục vụ **dashboard web**
để giám sát, quản lý bot và backtest.

Hiện có hai cBot:

| cBot | Chiến lược |
| :--- | :--- |
| `cBot/GotobiBot.cs` | Giao dịch Gotobi quanh giờ fix Tokyo trên USDJPY / EURJPY / GBPJPY |
| `cBot/CryptoDonchianBot.cs` | Breakout Donchian H4 trên BTCUSD / ETHUSD (forward test) |

Xem [docs/strategies.md](docs/strategies.md) để biết từng bot làm gì.

---

## 🚀 Tính Năng Chính

- **Bot headless**: container Docker `ctrader-console`, tạo từ màn hình **Setup Instances** trên dashboard.
- **Lệnh từ dashboard**: đóng một vị thế, tạm dừng / chạy lại bot, hoặc đóng hết vị thế rồi dừng bot, ngay trong tab Bots.
- **Watchdog**: khởi động lại container bị kẹt ở bước đăng nhập hoặc ngừng xử lý nến.
- **Bảng xếp hạng**: xếp hạng bot theo P&L USD hoặc trung hoà khối lượng, trong khoảng thời gian bất kỳ.
- **Sổ cái (Ledger)**: số dư kỳ vọng so với số dư broker của từng tài khoản; ghi nạp/rút và xem khoản lệch.
- **Trang Backtest**: chạy backtest cTrader cho một bot đã cài trong container và vẽ biểu đồ báo cáo.
- **Tách biệt Demo / Real**: dashboard và dữ liệu riêng cho tài khoản demo và tài khoản thật.

---

## 📊 Dashboard

| 📈 Tổng Quan & Phiên Giao Dịch | 🏆 Bảng Xếp Hạng Hiệu Suất |
| :---: | :---: |
| [![Overview Dashboard](docs/screenshots/overview.png)](docs/screenshots/overview.png) | [![Quant Leaderboard](docs/screenshots/leaderboard.png)](docs/screenshots/leaderboard.png) |
| *Chỉ số KPI, vị thế đang mở và lệnh gần đây* | *Xếp hạng tổng hợp, tỷ lệ thắng và huy hiệu Tier S/A/B/C* |

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
`agentfx` (lắng nghe `127.0.0.1:8000`), build hai gói `.algo` của cBot và bật backup cơ sở dữ liệu hằng ngày.
**Đăng nhập SSH bằng mật khẩu bị tắt**, nên hãy kiểm tra key từ một terminal khác trước khi đóng phiên root. Chi tiết,
tuỳ chọn và cách nâng cấp: [docs/deployment.md](docs/deployment.md).

Sau đó mở dashboard qua tunnel (`ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP`) và thêm tài khoản cTrader ở
**Docker Bot Management → Setup Instances**.

### Cách 2: chạy local / cài thủ công

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # tuỳ chọn: DATABASE_URL
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
   **[docs/docker-instances.md](docs/docker-instances.md)** (5 ô). Một ví dụ, Gotobi trên USDJPY:

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

Bản thân các preset nằm trong [`app/cbot_presets.py`](app/cbot_presets.py), nguồn sự thật duy nhất; README không chép
lại. Trên VPS cài bằng script, thay `-v /root:/root` bằng `-v /home/forge/ctrader:/root`.

---

## ⚙️ Cấu Hình

Mọi thiết lập của máy chủ lấy từ `.env` — bắt đầu từ [`.env.example`](.env.example); chạy local không cần biến nào.
Toàn bộ biến môi trường, cách chọn cơ sở dữ liệu và các tham số cBot không thuộc
preset được mô tả trong [docs/configuration.md](docs/configuration.md).

---

## 📚 Tài Liệu

| Tài liệu | Nội dung |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Thành phần, luồng request, nhóm API, cấu trúc dự án |
| [docs/strategies.md](docs/strategies.md) | Từng cBot làm gì và luật của nó nằm ở đâu |
| [docs/configuration.md](docs/configuration.md) | Biến `.env`, tham số cBot |
| [docs/deployment.md](docs/deployment.md) | Script cài VPS, cài thủ công, build cBot, service, backup, test |
| [docs/docker-instances.md](docs/docker-instances.md) | Toàn bộ 5 lệnh `docker run` theo preset |
| `http://127.0.0.1:8000/docs` | Tham chiếu API tương tác do FastAPI tự sinh (cả `/redoc`) |
| [research/README.md](research/README.md) | Nghiên cứu chiến lược offline và kết luận |

---

## 🔬 Tình Trạng Nghiên Cứu

README này không công bố số liệu hiệu suất nào. Nghiên cứu offline trong [`research/`](research/README.md) cho thấy,
tính đến 2026-09-27, giao dịch Gotobi trên các cặp JPY (`GotobiBot`) là chiến lược duy nhất được kiểm tra đã vượt
holdout đăng ký trước; `CryptoDonchianBot` trượt holdout và chỉ chạy forward test. Hãy coi cả hai bot là thử nghiệm
và chạy trên tài khoản demo trước.

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
