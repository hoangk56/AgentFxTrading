# GotobiBot: đóng leg sớm hơn giờ của bot, kiểm tra offline 2004-2026 (2026-10-15)

**Câu hỏi.** Giả thuyết người dùng đưa ra: đóng lệnh sớm hơn thì lợi hơn. Bot hiện đóng long ở fix 00:55 UTC và
đóng short lúc 02:55 UTC (11:55 Tokyo).

**Cách làm.** [gotobi_early_exit/early_exit.py](gotobi_early_exit/early_exit.py), output
[early_exit.out](gotobi_early_exit/early_exit.out). Đăng ký trước ngay trong docstring của script, trước khi chạy.
Giờ vào lệnh giữ nguyên, nên chênh lệch mỗi leg là
long: B − A = bid(T) − bid(00:55), short: B − A = ask(02:55) − ask(T). Bỏ qua stop. m1 Dukascopy 2004-2015, m1 IC
2016-2026, USDJPY/EURJPY/GBPJPY, bỏ ngày lễ Nhật như bot. Đơn vị pip (0.01 JPY); t_day = gộp 3 cặp thành trung bình
mỗi ngày (3 cặp JPY cùng ngày không độc lập).

**Tiêu chí đăng ký.** 4 ô chính: long đóng 00:45 và 00:50, short đóng 01:55 và 02:25. Một ô đạt khi trên 2004-2019:
B − A > 0, t_day ≥ 2.5 (Bonferroni cho 4 ô), cả 3 cặp > 0; và B − A > 0 trên 2020-2026.

## Kết quả: KHÔNG ĐẠT ở cả 4 ô, giữ giờ đóng hiện tại

| ô | 2004-2019 | t_day | 2020-2026 | năm > 0 (2004-2026) |
|---|---|---|---|---|
| long 00:45 | −1.11p | −3.75 | −0.74p | 6/23 |
| long 00:50 | −1.30p | −5.41 | −1.06p | 3/23 |
| short 01:55 | −1.17p | −1.47 | −0.64p | 7/23 |
| short 02:25 | −0.36p | −0.71 | +0.44p | 14/23 |

Để so sánh, leg của bot lãi trung bình: long +4.36p (2004-2019), +4.31p (2020-2026); short +2.54p, +3.96p.

- **Long: đóng sớm lỗ rõ ràng, và lỗ ở mọi giai đoạn.** Giá vẫn đi lên (JPY yếu đi) đến tận phút fix: đóng sớm
  1 phút (00:54) đã mất −0.42p (t_day −3.2 trên 2004-2019), đóng 00:25-00:50 mất 1.1-1.8p, khoảng 25-40 % lãi của
  leg long. Đây là bằng chứng ngược chiều với giả thuyết, không chỉ là "không có ưu thế".
- **Short: đóng sớm không lợi.** Mọi mốc từ 01:00 đến 02:50 đều âm trên 2004-2019; đóng 01:00 mất −2.5p ở cả hai
  giai đoạn. Trên 2020-2026 các mốc 02:10-02:50 hơi dương (02:50: +0.42p, t_day 2.1) nhưng đó là một ô mô tả trong
  9, và âm trên 2004-2019.

**Bổ sung sau kết quả: đóng sớm 5 / 10 / 15 phút** (người dùng hỏi lại; thêm ô mô tả short 02:45, không đổi tiêu chí):

| đóng sớm | long (2004-2019 / 2020-2026) | năm > 0 | short (2004-2019 / 2020-2026) | năm > 0 |
|---|---|---|---|---|
| 5 phút | −1.30p (t −5.4) / −1.06p (t −2.9) | 3/23 | −0.20p (t −1.4) / +0.42p (t +2.1) | 11/23 |
| 10 phút | −1.11p (t −3.7) / −0.74p (t −1.6) | 6/23 | +0.05p (t +0.3) / +0.53p (t +2.0) | 12/23 |
| 15 phút | −1.59p (t −4.5) / −0.81p (t −1.7) | 4/23 | −0.21p (t −0.6) / +0.11p (t +0.4) | 11/23 |

Long: lỗ ở cả ba mốc. Short: ≈ 0 trên 2004-2019, hơi dương trên 2020-2026 (+0.4-0.5p, chừng 10-15 % lãi leg
short) nhưng chỉ nửa số năm dương; cùng dạng gợi ý "chỉ có ở 2020-2026" như vào long sớm
([gotobi_early_long_2014-2019_2026-10-15.md](gotobi_early_long_2014-2019_2026-10-15.md)), không đủ để đổi.

**Giới hạn.** Bỏ qua stop (đóng sớm chỉ bớt thời gian giữ lệnh, nên chỉ đổi kết quả ở những ngày stop bị chạm trong
khoảng T → giờ đóng); giá m1 lúc fix nhiễu vài pip trong một giây; độ trễ khớp lệnh live
([gotobi_live_fills_2026-10-06.md](gotobi_live_fills_2026-10-06.md)) không đổi chiều của chênh lệch 1-2 pip này.
