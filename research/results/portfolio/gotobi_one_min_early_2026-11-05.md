# GotobiBot: gửi mọi lệnh sớm 1 phút, năm 2026 (2026-11-05)

**Câu hỏi.** Chủ tài khoản hỏi: bot còn trễ và trượt giá, vậy mở và đóng lệnh sớm 1 phút trong năm 2026 có tốt hơn không?
Phương án sớm: mở long sớm 1 phút, đóng long và mở short lúc 00:54, đóng short lúc 02:54 UTC.

**Cách làm.** [one_min_early.py](gotobi_one_min_early/one_min_early.py), output [one_min_early.out](gotobi_one_min_early/one_min_early.out);
[subminute.py](gotobi_one_min_early/subminute.py), output [subminute.out](gotobi_one_min_early/subminute.out). Câu hỏi hậu kiểm, không đăng ký
trước. Tick IC theo ngày gotobi 2020-10/2026 (cache backtest trên VPS), 10-30 và 11-05 lấy từ depth log; m1 IC 2016-09/2026 có stop
3 x ATR. Đơn vị pip (0.01 JPY) mỗi cặp-ngày, + = sớm lợi hơn. t_day gộp 3 cặp thành trung bình mỗi ngày.
Sớm 1 phút đổi cả đóng long và mở short theo cùng giá bid, nên chênh lệch ở fix tính hai lần.

## Kết quả: giữ giờ hiện tại

| dữ liệu | sớm 60 s − bot | t_day | ghi chú |
|---|---|---|---|
| 2026 tick, không stop, 54 ngày tới 10-30 | +2.05p | +1.3 | CI95 −0.94..+5.21, 31/54 ngày dương |
| 2026 m1, có stop, 49 ngày tới 09-24 | +1.12p | +0.6 | bỏ riêng 09-18: +0.09p |
| 2025 tick, không stop | −0.05p | −0.0 | |
| 2020-2026 m1, có stop | −0.65p | −1.4 | |
| 2016-2025 m1, có stop | −1.07p | −2.65 | 3/11 năm dương (2016-2026) |

- Số dương của 2026 không có ý nghĩa thống kê. Ngày 09-18 đóng góp +48.6p: giá nhảy khoảng +45p đúng phút 02:54-02:55 (chưa kiểm tin gì).
  Năm ngày cuối (09-25..10-30) đều dương +6..+11p, n quá nhỏ để kết luận.
- Sớm 60 s không bỏ được trễ và trượt: lệnh gửi lúc 00:54:00 vẫn trễ khoảng 0.2 s và vẫn trượt theo độ sâu sổ lệnh như lệnh lúc 00:55:00.

## Trễ và trượt thật

- Log live từ 10-26: lệnh gửi ở 00:55:00.03-.07, khớp ở khoảng 00:55:00.2-.25 (broker ~0.17 s).
- Trượt lệnh thật ở fix và 02:55, 2 ngày 10-30 + 11-05 (n = 14): trung bình +0.13p.
- Giá bid so với 00:55:00, mỗi chiều ở fix: +0.2 s ≈ 0; +0.5 s −0.15p; +2 s −0.5p; +10 s −0.9..−1.6p (2025-2026).
- 5/19 lệnh mở short gặp `TechnicalError` lần đầu, cả 5 đều ở giây 00:55:00, rồi thử lại sau 2 s (2 trong số đó là lệnh thật, 10-30).
  Chi phí kỳ vọng khoảng 0.5p x 26 % ≈ 0.1p mỗi short. So với lãi ~10p mỗi cặp-ngày của bot năm 2026, nhỏ.

## Sớm vài giây

Tick theo giây, mỗi chiều ở fix: 2020-2024 đỉnh giá nằm ở +0.5 s (+0.54p, t +4.0), sớm 1-3 s mất 0.20-0.28p (t −3..−5). 2025-2026 đỉnh này
không còn: −5..+0.2 s gần như phẳng, sau đó giảm. Không có mốc sớm nào dương ổn định qua cả hai giai đoạn, nên không đổi sang gửi sớm vài giây.

**Giới hạn.** Hậu kiểm một năm, tick 2026 không tính stop; giá lúc fix nhiễu vài pip trong một giây; ngày 10-09, 10-15, 10-23 thiếu dữ liệu tick,
11-05 chưa có giá 02:55 nên không vào phần tổng hợp.
