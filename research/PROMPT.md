# Prompt mẫu: research thêm thuật toán

Copy khối dưới đây làm prompt cho phiên mới. Sửa phần "Đã có" khi có thêm thuật toán đạt.

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
- research/STRATEGIES.md
- research/results/portfolio/swing_lab_v2_2026-09-27.md
- research/results/portfolio/prereg_swing_v2.md
Đã có C3 (gotobi JPY basket, đạt). Muốn thuật toán MỚI, khác cơ chế, ít tương quan với C3.
Dùng lại engine research/swing/swing.py và mô hình swap research/swing/rates.py.

"Hợp lý" nghĩa là:
- Có cơ sở kinh tế (dòng lệnh, thanh toán, phần bù rủi ro...), không chỉ là mẫu hình kỹ thuật.
- Chọn tham số trên 2016-2021, kiểm định trên 2022-2024.
- Viết pre-registration (cấu hình + ngưỡng đạt + hash code từ `python -m research.tools.prereg_hashes`) TRƯỚC khi xem đoạn kiểm tra cuối; mỗi ứng viên chỉ xem một lần.
- Dương ở cả ba giai đoạn, t đủ lớn, đa số các năm dương, thắng lệnh vào ngẫu nhiên, vẫn dương khi spread x1.5.
Lưu ý: đoạn 2025-01..2026-09 đã bị dùng làm holdout cho nhiều chiến lược (C1, C3, C4 và lab cũ), nên không còn sạch hoàn toàn. Nếu có dữ liệu mới sau 2026-09-24 thì dùng làm holdout; nếu không, nói rõ giới hạn này trong báo cáo.

Không hạ ngưỡng để có kết quả; kiên trì nghĩa là mở rộng hướng tìm, không phải nới tiêu chí.
Cập nhật tiến độ ngắn gọn khi tìm thấy hoặc loại một hướng.

Kết thúc:
- Viết báo cáo vào research/results/portfolio/ (luật chi tiết, số liệu từng giai đoạn/năm, những gì đã thử và loại).
- Thêm một dòng vào research/JOURNAL.md; cập nhật research/README.md và lab/catalog.py nếu liên quan.
- Chạy test. Không commit.
```
