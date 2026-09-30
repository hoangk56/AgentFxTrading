# GotobiBot: chi phí làm mờ (lệnh mồi + SL broker hẹp) — backtest 30/09/2026

**Câu hỏi.** Người dùng không muốn broker đọc được chiến thuật Gotobi. Quy ước được đưa ra để backtest trước khi
đổi code thật:

- Lệnh mồi gấp đôi lệnh thật, vào những ngày thường (không phải gotobi), cùng khung giờ với lệnh thật. Một nửa lệnh
  mồi bằng lot của lệnh thật, một nửa lot 0.01. Stop ảo 0.5 × ATR20(H1) do bot tự đóng, nên phần lớn lệnh mồi thua nhỏ.
- SL gửi lên broker ngẫu nhiên và không rộng hơn stop thật (3 × ATR20 H1). Như vậy nếu bot hoặc VPS chết, mỗi lệnh
  lỗ tối đa 1R.
- Giờ vào long nhiễu ±60 phút quanh 18:00 UTC. Giờ fix 00:55 giữ nguyên.

**Cách chạy.** Dùng cTrader CLI backtest trên VPS, tick IC Markets (tài khoản demo 10115236), khung m15, từ
01/01/2024 đến 25/09/2026 (32,7 tháng). Risk $200 mỗi lệnh thật (như live), `--commission-auto`, MaxSpread 3 pip
(GBPJPY 4 pip), SkipDates lấy theo preset. Code là `cBot/GotobiBot.cs` trong working tree ngày 30/09 (chưa
commit), build tạm trên VPS. Các run:

| run | tham số |
|---|---|
| base | `--VirtualStop=false --LongEntryJitterMinutes=0 --DecoyLegProbability=0`, tức bot như đang chạy live |
| new80 | mặc định mới: SL broker 0.8–1.0 × stop, lệnh mồi p = 0.8, một nửa lot 0.01 |
| new60 | như new80 nhưng `--EmergencyStopMin=0.6` |
| small | phương án người dùng chọn sau đó: như new80 nhưng toàn bộ lệnh mồi lot 0.01 (`DecoySmallShare` = 1, nay là mặc định) |

Script chạy và script tổng hợp (`run_camo_bt.sh`, `summarize_camo.py`) nằm ngoài repo. Report JSON đã lưu ở
`/tmp/camo_bt/reports/` trên VPS. R = net / $200.

## Kết quả theo cặp

| cặp · run | lệnh broker thấy | win broker thấy | net tổng | lệnh thật: net (R/lệnh) | mồi cỡ thật: n, net | mồi lot nhỏ: n, net | max DD |
|---|---|---|---|---|---|---|---|
| USDJPY base | 386 | 53,4 % | $3.677 | $3.677 (+0,048) | – | – | $1.025 |
| USDJPY new80 | 1.185 | 38,5 % | $810 | $3.249 (+0,042) | 388, −$2.403 | 411, −$36 | $1.510 |
| USDJPY new60 | 1.185 | 38,3 % | $464 | $2.903 (+0,038) | 388, −$2.403 | 411, −$36 | $1.622 |
| EURJPY base | 385 | 60,0 % | $4.792 | $4.792 (+0,062) | – | – | $631 |
| EURJPY new80 | 1.157 | 38,9 % | $1.466 | $4.710 (+0,061) | 383, −$3.120 | 389, −$123 | $1.358 |
| EURJPY new60 | 1.157 | 38,8 % | $1.130 | $4.374 (+0,057) | 383, −$3.120 | 389, −$123 | $1.391 |
| GBPJPY base | 383 | 53,8 % | $3.269 | $3.269 (+0,043) | – | – | $748 |
| GBPJPY new80 | 1.182 | 38,4 % | −$285 | $3.091 (+0,040) | 358, −$3.285 | 441, −$92 | $1.420 |
| GBPJPY new60 | 1.182 | 38,4 % | −$323 | $3.054 (+0,040) | 358, −$3.285 | 441, −$92 | $1.411 |
| USDJPY small | 1.185 | 38,5 % | $3.093 | $3.176 (+0,041) | – | 799, −$83 | $905 |
| EURJPY small | 1.157 | 38,9 % | $4.594 | $4.767 (+0,062) | – | 772, −$173 | $753 |
| GBPJPY small | 1.182 | 38,4 % | $2.839 | $3.021 (+0,039) | – | 799, −$183 | $922 |

## Cả rổ (3 cặp)

| run | lệnh broker thấy | win broker thấy | net tổng | net/tháng | lệnh thật | mồi cỡ thật | mồi lot nhỏ | tổng max DD các cặp |
|---|---|---|---|---|---|---|---|---|
| base | 1.154 | 55,7 % | $11.738 | $359 | $11.738 | – | – | $2.403 |
| new80 | 3.524 | 38,6 % | $1.991 | $61 | $11.051 | −$8.808 (1.129 lệnh) | −$251 (1.241 lệnh) | $4.288 |
| new60 | 3.524 | 38,5 % | $1.271 | $39 | $10.330 | −$8.808 | −$251 | $4.424 |
| **small** | 3.524 | **38,6 %** | **$10.526** | **$321** | $10.964 | – | −$438 (2.370 lệnh) | $2.580 |

## Kết luận

1. **Lệnh mồi cỡ thật ăn gần hết edge.** Trung bình mỗi lệnh lỗ −$7,8 (−0,039R). Tính ra 1.129 lệnh lỗ −$8.808,
   tức 80 % lãi của lệnh thật, và tổng max DD gần như tăng gấp đôi. Research cho thấy cùng khung giờ vào ngày thường
   có R ≈ 0 trước phí (placebo trong `swing_lab_v2_2026-09-27.md`), nên khoản lỗ này là chi phí thuần: phí hai chiều
   trên lot lớn, spread, và trượt giá khi bot đóng stop 0,5 × ATR bằng lệnh market.
2. **Lệnh mồi lot nhỏ gần như miễn phí**: −$0,20 mỗi lệnh, −$251 cho 1.241 lệnh. Chúng vẫn kéo tỉ lệ thắng xuống,
   nhưng broker tách chúng ra được ngay theo khối lượng.
3. **SL broker hẹp hơn stop thật làm mất một phần lãi của lệnh thật**: −5,9 % ở mức 0,8–1,0× và −12,0 % ở mức
   0,6–1,0×. USDJPY chịu thiệt nhiều nhất (−12 % / −21 %).
4. **Tỉ lệ thắng broker thấy** giảm từ 55,7 % xuống 38,6 %, gần như không phụ thuộc mức SL.
5. **Phương án được chọn ("small")**: SL broker 0,8–1,0×, nhiễu giờ vào long, toàn bộ lệnh mồi lot 0,01. Tổng lãi
   $10.526, tức −10,3 % so với bản gốc (−$1.212 trong 32,8 tháng, khoảng −$37/tháng). Tỉ lệ thắng broker thấy
   38,6 %. Tổng max DD $2.580, tăng 7 %. Lãi lệnh thật ($10.964) lệch nhẹ so với new80 ($11.051) dù cùng tham số,
   vì mức SL broker được bốc ngẫu nhiên lại ở mỗi run. Nhược điểm vẫn còn: lệnh mồi 0,01 lot tách ra được theo
   khối lượng.

Các ước tính viết trước khi chạy "small" (ngoại suy từ chi phí mỗi lệnh, không phải backtest riêng). Ước tính cho
toàn lot nhỏ là ~$322/tháng, còn backtest cho $321:
- Toàn bộ lệnh mồi (2:1) đều lot nhỏ: net ≈ $11.051 − 2.370 × $0,20 ≈ $10.575 ($322/tháng), win broker thấy ≈ 38 %.
  Nhưng khối lượng làm lộ lệnh mồi.
- 1/4 lệnh mồi cỡ thật, 3/4 lot nhỏ: net ≈ $11.051 − 592 × $7,8 − 1.778 × $0,20 ≈ $6.070 ($186/tháng).
