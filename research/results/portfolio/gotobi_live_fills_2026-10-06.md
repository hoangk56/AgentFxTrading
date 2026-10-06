# GotobiBot: lệnh live/demo so với tick IC và backtest cTrader — 06/10/2026

**Câu hỏi.** Research và backtest giả định lệnh khớp đúng giá tick tại thời điểm gửi, không trượt, không trễ. Lệnh
thật có như vậy không? Lợi thế của C3 chỉ khoảng 3.8 pip gross mỗi lệnh (backtest 2016–2026, 4,574 lệnh, xem
[gotobi_cbot_backtest_2026-09-27.md](gotobi_cbot_backtest_2026-09-27.md)), nên 1 pip trượt đã là một phần lớn.

**Dữ liệu.**
- Lệnh: `/api/dashboard/history` trên VPS, 56 lệnh đóng từ 29/09 đến 06/10 (live + demo). Lệnh thật là 2 ngày gotobi
  30/09 và 05/10, mỗi tài khoản 12 lệnh. Còn lại là lệnh mồi 0.01 lot. API chỉ có giờ đến từng giây. Log container
  (từ lần tạo lại 04/10) có mili-giây.
- Tick: cache backtest cTrader trên VPS (`agentfx-bt-cache`, server demo), lấp đến 05/10 bằng backtest job #391–#393
  (GotobiBot demo, 28/09–06/10, tham số của bot). Ngày 06/10 chưa có trong cache nên bỏ.
- Backtest so sánh: chính job #391–#393, cùng ngày và cùng cặp. Giờ vào long trong backtest được nhiễu ±60 phút
  (camouflage), live 29/09 vào đúng 18:00, nên lệnh long 30/09 khác giờ và chỉ là nhiễu, không phải chi phí.

Script nằm ngoài repo (scratchpad của phiên): `slip.py` (giá khớp so với bid/ask tick cuối cùng tại giây khớp) và
`bt_vs_live.py` (pip từng lệnh live/demo so với lệnh backtest cùng ngày).

## 1. Giá khớp so với tick tại giây khớp

Trượt dương là bất lợi (mua cao hơn ask, bán thấp hơn bid), tính bằng pip.

| tài khoản · loại | n | vào lệnh: trung bình / trung vị | thoát lệnh bằng market (không tính stop): n, trung bình |
|---|---|---|---|
| live · thật | 12 | −0.0 / 0.0 | 12, −0.55 |
| live · mồi | 14 | +0.39 / +0.05 | 6, +0.30 |
| demo · thật | 12 | −0.62 / 0.0 | 12, −1.66 |
| demo · mồi | 12 | +0.08 / +0.05 | 3, −2.13 |

Ở độ phân giải 1 giây không thấy trượt có hệ thống. Lệnh live 04/10 22:00 khớp đúng bằng giá tick của server demo,
nên feed giá live và demo là một. Giá quanh 00:55 nhảy vài pip trong một giây, nên từng con số riêng lẻ nhiễu ±3–6 pip.
Thoát bằng stop lúc 21:00 UTC (giờ rollover, spread 3–20 pip) trượt đến 15 pip, nhưng chỉ có ở lệnh mồi 0.01 lot.

## 2. Pip từng lệnh: live/demo so với backtest cùng ngày

| ngày gotobi · cặp · chiều | live pip | backtest pip | live − bt | demo − bt |
|---|---|---|---|---|
| 30/09 EURJPY long | +10.1 | +1.4 | +8.7 | +8.6 |
| 30/09 GBPJPY long | +6.3 | +12.5 | −6.2 | −6.3 |
| 30/09 USDJPY long | −15.3 | −16.7 | +1.4 | +0.5 |
| 30/09 EURJPY short | +70.3 | +71.5 | −1.2 | −1.0 |
| 30/09 GBPJPY short | +79.3 | +79.9 | −0.6 | −3.0 |
| 30/09 USDJPY short | +67.6 | +68.8 | −1.2 | −1.2 |
| 05/10 EURJPY long | −34.5 | −27.9 | −6.6 | +0.0 |
| 05/10 GBPJPY long | −22.1 | −22.0 | −0.1 | −0.8 |
| 05/10 USDJPY long | −12.2 | −10.9 | −1.3 | −0.2 |
| 05/10 EURJPY short | +70.7 | +70.8 | −0.1 | −0.7 |
| 05/10 GBPJPY short | +26.1 | +26.9 | −0.8 | −1.5 |
| 05/10 USDJPY short | −18.7 | −19.9 | +1.2 | −0.0 |
| **trung bình, 12 lệnh** | | | **−0.57** | **−0.47** |
| trung bình, 6 lệnh short | | | −0.45 | −1.23 |

- Lệnh short (vào lúc fix 00:55, cùng giờ với backtest): 11/12 chênh ≤ 0, trung bình khoảng −0.5 pip (live) và −1.2 pip
  (demo). Cơ chế: backtest đóng long và mở short trên cùng một tick 00:55:00.000. Bot thật đóng long (đồng bộ, ~0.3 s)
  rồi mới gửi lệnh short (~0.2–0.5 s nữa), đúng lúc giá bắt đầu rơi sau fix. Demo 30/09 khớp short lúc 00:55:02–03
  và mất nhiều nhất (GBPJPY −3.0).
- Lệnh long 05/10 (thứ Hai) chờ spread ≤ 3 pip sau giờ mở cửa tuần. Live qua cổng spread muộn hơn demo 30–45 s, và
  EURJPY vào cao hơn 7 pip. Đây là trễ thời điểm, không phải trượt giá. Backtest có cùng cổng spread, nên về kỳ vọng
  không lệch, chỉ thêm nhiễu.
- Commission live = backtest: $6/lot round trip (live USDJPY 30/09 0.23 lot, gross $99.27, net $97.89; backtest
  0.24 lot $1.44).

## 3. Lỗi lệnh chỉ có ở live

| thời điểm (UTC) | bot | lỗi | hậu quả |
|---|---|---|---|
| 05/10 00:55:00.51 | live EURJPY | mở short: `TechnicalError` | thử lại sau 30 s, khớp 00:55:30 |
| 05/10 00:55:00.53 | live USDJPY | mở short: `TechnicalError` | thử lại sau 30 s, khớp 00:55:30 |
| 06/10 01:02:20.27 | live GBPJPY | đóng lệnh mồi: `TechnicalError` | thử lại ngay, đóng sau 0.2 s |

Lần 05/10, 30 s trễ tình cờ không tốn gì (EURJPY −0.1, USDJPY +1.2 so với backtest). Nhưng lệnh short được đặt ngay
sau fix, lúc giá đi nhanh nhất, nên chờ 30 s là đánh cược cỡ vài pip mỗi lần. Log demo không có lỗi nào. Log live
trước 04/10 đã mất khi container được tạo lại.

## Kết luận

- Mô phỏng → backtest cTrader → khớp lệnh thật: không có khoảng cách lớn. Vào lệnh khớp đúng giá tick, commission
  đúng như backtest, feed live và demo là một.
- Có một chi phí thật mà backtest không có: độ trễ ở lệnh short lúc fix, khoảng 0.5–1.2 pip mỗi lệnh short. Lấy
  ~2.9 pip net mỗi lệnh (3.8 gross trừ ~0.9 commission), con số này ăn khoảng 15–40 % lợi thế của lệnh short.
  Với n = 12 thì chưa có ý nghĩa thống kê (độ lệch chuẩn của chênh lệch ~2 pip, SE ~0.6), nhưng 11/12 lệnh cùng một
  chiều và cơ chế rõ ràng.
- Bản thân lợi thế thì chưa kiểm được bằng lệnh live. Backtest +0.29 R mỗi ngày gotobi, độ lệch chuẩn 1.47 R, nên cần
  khoảng 100 ngày gotobi (~1.4 năm) để t ≥ 2. Live 2 ngày: +1.48 R (30/09, $200) và −0.05 R (05/10, $400).

## Việc nên làm

Mục 1–3 đã sửa trong `cBot/GotobiBot.cs` ngày 06/10 (build trên VPS không lỗi, chưa deploy lên các bot). Xem
`docs/strategies.md`, phần "Orders at the fix".


1. Giảm trễ lệnh short lúc fix: gửi lệnh short trước hoặc song song với lệnh đóng long (`ExecuteMarketOrderAsync` /
   `ClosePositionAsync`), thay vì đóng xong mới mở. Tài khoản hedging cho phép giữ cả hai trong chưa đến một giây.
2. Khi lệnh ở fix lỗi `TechnicalError`: thử lại sau 1–2 s thay vì 30 s.
3. Ghi mili-giây và bid/ask lúc gửi lệnh vào log/report, để lần sau đo trượt chính xác thay vì ở độ phân giải giây.
4. Chạy lại phép đo này sau khoảng 10 ngày gotobi (~2 tháng) để thu hẹp sai số.
