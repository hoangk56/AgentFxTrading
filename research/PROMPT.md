# Prompt mẫu: research thêm thuật toán

Copy khối dưới đây làm prompt cho phiên mới. Sửa phần "Đang chạy trên VPS" khi có thêm thuật toán đạt hoặc được deploy.

Trước khi dùng, nên tải dữ liệu mới để có holdout sạch (đoạn 2025-01..2026-09 đã bị dùng nhiều lần; cache cũ dừng
ở 2026-09-24/28). Không truyền mã thì `pull_cache.sh` chỉ tải 15 mã, nên ghi rõ các mã cần:

```bash
research/tools/pull_cache.sh USDJPY EURJPY ...
research/.venv/bin/python -m research.m1
```

```text
Research thêm thuật toán giao dịch trên dữ liệu hiện có. Research đến khi tìm được thuật toán hợp lý thì thôi: kết quả âm ở một vòng KHÔNG phải điểm dừng, hãy mở rộng hướng tìm.

Dữ liệu (research/data/, git-ignore):
- 26 mã IC, M1 trong data/m1/*.npz, 2016 đến nay (năng lượng từ 2018).
- 6 mã IC mới ở vòng 7: ES35, F40, IT40, STOXX50, US2000, USDCNH (M1 bid). Cache của DOGEUSD rỗng.
- Dukascopy 2004-2015 trong data/duka/: M1 bid/ask của USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD; H1 của 11 mã.

Ràng buộc cố định (chỉ những điều này):
- Lot không phụ thuộc vốn; thuật toán được tăng giảm lot quanh một lot/rủi ro mặc định.
- Mỗi lệnh giữ tối đa 5 ngày.
- Một bot giữ tối đa 3 lệnh cùng lúc.
Mọi thứ khác tôi không nói đều được tự đổi: mã, khung thời gian, cách vào/thoát lệnh, engine, số mã mỗi bot...

Đọc trước để không test lại (8 vòng đã chạy, chỉ C3 đạt):
- research/JOURNAL.md (toàn bộ) và research/README.md
- research/results/portfolio/swing_lab_v2_2026-09-27.md ("What was tried"), prereg_swing_v2.md
- research/results/portfolio/flow_search_2026-09-27.md, flow_search_round4_2026-09-27.md
- research/results/portfolio/round6_commodity_flows_2026-10-04.md (bảng power của holdout, lỗi phí kim loại)
- research/results/portfolio/round7_new_data_2026-10-05.md (kỷ Dukascopy, mã mới, premia nhiều tuần)
- research/results/portfolio/round8_inter_symbol_2026-10-05.md (lead-lag, spillover, pairs; mục "Pitfalls")

Kết luận chung của các vòng 3-8: các dòng lệnh có thật ngoài gotobi chỉ 0.02-3 bp, cỡ spread + commission của IC;
premia nhiều tuần thua phí qua đêm (financing markup) của IC; thông tin giữa các mã được định giá trong phút đầu;
hiệu ứng hiếm (vài chục lần/năm) không đủ power cho holdout 21 tháng. Hướng mới phải giải thích vì sao nó thoát được
những giới hạn này.

Đang chạy trên VPS (đã có cBot, backtest cTrader và deploy; preset ở app/cbot_presets.py):
- C3 Gotobi JPY basket (cBot/GotobiBot.cs), thuật toán duy nhất đang chạy: USDJPY, EURJPY, GBPJPY, mỗi cặp một
  container, chart m15. Vào lệnh theo lịch gotobi quanh fix Tokyo, stop 3 x ATR20(H1), bỏ các ngày gotobi không có
  fix (ngày lễ Nhật, 31/12). Đạt holdout 2025-26 (R +0.042, t 2.9) và kỷ Dukascopy 2004-2015 (R +0.038, t 4.8).
- C1 Crypto Donchian H4 đã trượt holdout và bị gỡ khỏi VPS ngày 2026-10-03. Đừng tối ưu lại C1 hay test
  Donchian/breakout xu hướng trên mã khác (đã âm ở crypto, chỉ số, kim loại, năng lượng, FX).
Muốn thuật toán MỚI, khác cơ chế với C3 (không phải lịch gotobi/fix JPY), ít tương quan với lợi nhuận ngày của C3:
báo tương quan đó trong báo cáo (trades_C3_gotobi_jpy_basket.csv trong research/results/portfolio/, git-ignore;
nếu thiếu thì chạy lại từ engine).
Dùng lại engine research/swing/swing.py và mô hình swap research/swing/rates.py. Lưu ý engine tính phí kim loại
(XAU/XAG/XPT) theo giá 2026, nên trước 2025 phí bị cao hơn thực tế 0.5-1.7 bp (chưa sửa, xem báo cáo vòng 6).

"Hợp lý" nghĩa là:
- Có cơ sở kinh tế (dòng lệnh, thanh toán, phần bù rủi ro...), không chỉ là mẫu hình kỹ thuật.
- Chọn tham số trên 2016-2021 (IS), kiểm định trên 2022-2024 (VAL).
- Ngưỡng đạt như các vòng 3-8: net > 0 ở IS và VAL; t (cluster theo ngày) >= 2.5 ở IS, >= 1.5 ở VAL; >= 2/3 số năm
  dương; thắng >= 95 % lệnh vào ngẫu nhiên; vẫn dương khi spread x1.5 và khi vào trễ 1 phút.
- Chỉ đáng mở holdout khi power = Sharpe mỗi lệnh (net) x sqrt(số lệnh dự kiến trong holdout) >= 3.
- Viết pre-registration (cấu hình + ngưỡng đạt + hash code từ `python -m research.tools.prereg_hashes`) TRƯỚC khi xem đoạn kiểm tra cuối; mỗi ứng viên chỉ xem một lần.
- Dương ở cả ba giai đoạn, t đủ lớn, đa số các năm dương.
Lưu ý về holdout: đoạn 2025-01..2026-09 đã bị dùng làm holdout cho nhiều chiến lược (C1, C3, C4, M1 và lab cũ đã
xoá), nên không còn sạch hoàn toàn. Kỷ Dukascopy 2004-2015 đã dùng cho C3, M1 và vài screen FX ở vòng 7-8. Nếu có
dữ liệu mới sau 2026-09-24 thì dùng làm holdout; nếu không, nói rõ giới hạn này trong báo cáo. Cắt dữ liệu holdout
ngay khi load (ts < 2025-01-01) để không vô tình nhìn thấy.

Không hạ ngưỡng để có kết quả; kiên trì nghĩa là mở rộng hướng tìm, không phải nới tiêu chí.
Cập nhật tiến độ ngắn gọn khi tìm thấy hoặc loại một hướng.

Kết thúc:
- Viết báo cáo vào research/results/portfolio/ (luật chi tiết, số liệu từng giai đoạn/năm, những gì đã thử và loại).
- Thêm một mục vào research/JOURNAL.md; cập nhật research/README.md nếu liên quan.
- Chạy test (`research/.venv/bin/python -m pytest research/tests`). Không commit.
```
