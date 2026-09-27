# Prompt mẫu: research thêm thuật toán

Copy khối dưới đây làm prompt cho phiên mới. Sửa phần "Đang chạy trên VPS" khi có thêm thuật toán đạt hoặc được deploy.

Trước khi dùng, nên tải dữ liệu mới để có holdout sạch (đoạn 2025-01..2026-09 đã bị dùng nhiều lần):

```bash
research/tools/pull_cache.sh
research/.venv/bin/python -m research.m1
```

```text
Research thêm thuật toán giao dịch trên dữ liệu hiện có (26 mã, research/data, 2016 đến nay). Research đến khi tìm được thuật toán hợp lý thì thôi: kết quả âm ở một vòng KHÔNG phải điểm dừng, hãy mở rộng hướng tìm.

Ràng buộc cố định (chỉ những điều này):
- Lot không phụ thuộc vốn; thuật toán được tăng giảm lot quanh một lot/rủi ro mặc định.
- Mỗi lệnh giữ tối đa 5 ngày.
- Một bot giữ tối đa 3 lệnh cùng lúc.
Mọi thứ khác tôi không nói đều được tự đổi: mã, khung thời gian, cách vào/thoát lệnh, engine, số mã mỗi bot...

Đọc trước để không test lại:
- research/JOURNAL.md
- research/results/portfolio/swing_lab_v2_2026-09-27.md
- research/results/portfolio/prereg_swing_v2.md
- research/results/portfolio/gotobi_cbot_backtest_2026-09-27.md
- research/results/portfolio/crypto_donchian_cbot_2026-09-27.md
- research/results/portfolio/crypto_donchian_weekend_2026-09-27.md

Đang chạy trên VPS (đã có cBot, backtest cTrader và deploy; preset ở app/cbot_presets.py):
- C3 Gotobi JPY basket (cBot/GotobiBot.cs): USDJPY, EURJPY, GBPJPY, mỗi cặp một container, chart m15. Đạt holdout
  (R +0.042, t 2.9). Vào lệnh theo lịch gotobi quanh fix Tokyo, stop 3 x ATR20(H1).
- C1 Crypto Donchian H4 (cBot/CryptoDonchianBot.cs): BTCUSD, ETHUSD, chart h1 (bot tự dựng nến H4 theo UTC).
  Phá kênh 55 nến H4, thoát khi thủng kênh 20, stop 3 x ATR20(H4), lot x0.5..2 theo độ mạnh breakout. TRƯỢT holdout
  (R -0.025), chỉ chạy forward test; giả thuyết do thị trường chuyển sang 24/7 đã bị loại. Đừng tối ưu lại C1 hay
  test Donchian/breakout xu hướng trên mã khác (đã âm ở chỉ số, kim loại, năng lượng, FX).
Muốn thuật toán MỚI, khác cơ chế với cả hai (không phải lịch gotobi/fix JPY, không phải breakout xu hướng crypto),
ít tương quan với lợi nhuận ngày của C3 và C1: báo tương quan đó trong báo cáo (trades_C3_gotobi_jpy_basket.csv,
trades_C1_crypto_donchian_h4.csv trong research/results/portfolio/, git-ignore; nếu thiếu thì chạy lại từ engine).
Dùng lại engine research/swing/swing.py và mô hình swap research/swing/rates.py.

"Hợp lý" nghĩa là:
- Có cơ sở kinh tế (dòng lệnh, thanh toán, phần bù rủi ro...), không chỉ là mẫu hình kỹ thuật.
- Chọn tham số trên 2016-2021, kiểm định trên 2022-2024.
- Viết pre-registration (cấu hình + ngưỡng đạt + hash code từ `python -m research.tools.prereg_hashes`) TRƯỚC khi xem đoạn kiểm tra cuối; mỗi ứng viên chỉ xem một lần.
- Dương ở cả ba giai đoạn, t đủ lớn, đa số các năm dương, thắng lệnh vào ngẫu nhiên, vẫn dương khi spread x1.5.
Lưu ý: đoạn 2025-01..2026-09 đã bị dùng làm holdout cho nhiều chiến lược (C1, C3, C4 và lab cũ đã xoá), nên không còn sạch hoàn toàn. Nếu có dữ liệu mới sau 2026-09-24 thì dùng làm holdout; nếu không, nói rõ giới hạn này trong báo cáo.

Không hạ ngưỡng để có kết quả; kiên trì nghĩa là mở rộng hướng tìm, không phải nới tiêu chí.
Cập nhật tiến độ ngắn gọn khi tìm thấy hoặc loại một hướng.

Kết thúc:
- Viết báo cáo vào research/results/portfolio/ (luật chi tiết, số liệu từng giai đoạn/năm, những gì đã thử và loại).
- Thêm một dòng vào research/JOURNAL.md; cập nhật research/README.md nếu liên quan.
- Chạy test. Không commit.
```
