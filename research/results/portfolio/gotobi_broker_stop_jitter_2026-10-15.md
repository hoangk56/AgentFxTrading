# GotobiBot: tách chi phí stop broker hẹp và nhiễu giờ vào long (2026-10-15)

**Câu hỏi.** Bài 30/09 ([gotobi_camouflage_2026-09-30.md](gotobi_camouflage_2026-09-30.md)) đo stop broker
0.8-1.0× và nhiễu giờ vào ±60 phút **gộp chung**: lãi lệnh thật −5.9 % (2024-01..2026-09, risk $200). Người dùng
giữ hoặc tăng risk live ($400), nên muốn biết riêng từng phần tốn bao nhiêu để bỏ phần đắt nhất.

**Cách chạy.** Giống hệt baseline của [gotobi_compound_third_2026-10-09.md](gotobi_compound_third_2026-10-09.md):
cTrader CLI trên VPS (`~/gotobi-stop/`), `GotobiBot.algo` đang chạy prod (sha1 `0332227e`), tick IC,
`--commission-auto`, USDJPY/EURJPY/GBPJPY, mỗi cặp một job mỗi năm, 01/01/2020 → 08/10/2026, risk $1,000/leg,
`MaxLotsPerTrade=1000`, `--SkipDates` = 32 ngày lễ Nhật / ngân hàng. R = net / $1,000. Các bộ:

| bộ | tham số |
|---|---|
| base | mặc định (stop broker 0.8-1.0×, nhiễu ±60 phút, decoy 0.01 lot); report của bài 10-09 |
| base2 | mặc định, chạy lại: đo nhiễu, vì stop broker bốc bằng `Random` không seed |
| stop10 | `--EmergencyStopMin=1.0` (stop broker = stop thật 3 × ATR20 H1) |
| stop10nojit | `--EmergencyStopMin=1.0 --LongEntryJitterMinutes=0` (long vào đúng 18:00 UTC) |

14 job EURJPY/GBPJPY đầu tiên bị "aborted by timeout" ở lệnh đầu (tải tick quy đổi, 4 job song song); chạy lại
2 job một lúc thì qua hết, 63/63 report. Script so sánh `~/gotobi-stop/compare.py` (ngoài repo): ghép leg thật
theo cặp × chiều × ngày gotobi, t của chênh lệch từng cặp leg.

## Từng bộ

| bộ | leg thật | net $ | R/leg (t) | leg đóng bởi stop | decoy net $ |
|---|---|---|---|---|---|
| base | 2,686 | 162,627 | +0.0605 (+8.3) | 68 | −805 |
| base2 | 2,686 | 162,919 | +0.0607 (+8.3) | 66 | −823 |
| stop10 | 2,686 | 165,037 | +0.0614 (+8.5) | 46 | −823 |
| stop10nojit | 2,686 | 154,358 | +0.0575 (+7.9) | 50 | −812 |

## Ghép cặp (cùng cặp, chiều, ngày)

| so sánh | chênh net $ | % | R/leg (t) | leg thay đổi | theo cặp |
|---|---|---|---|---|---|
| base2 − base (nhiễu) | +293 | +0.2 | +0.0001 (+0.2) | 60 | EUR +1,609 · GBP +291 · USD −1,607 |
| stop10 − base | +2,411 | +1.5 | +0.0009 (+1.2) | 62 | EUR +2,471 · GBP +362 · USD −423 |
| stop10 − base2 | +2,118 | +1.3 | +0.0008 (+1.1) | 58 | EUR +863 · GBP +71 · USD +1,184 |
| stop10nojit − stop10 | **−10,680** | **−6.5** | **−0.0040 (−2.3)** | 1,168 (chỉ long) | EUR −2,837 · GBP −1,558 · USD −6,285 |

Chênh do nhiễu được tách theo giờ vào thực tế của bộ stop10 so với 18:00 (leg long):

| giờ vào có nhiễu so với 18:00 | n | nhiễu − 18:00, R/leg (t) | $ |
|---|---|---|---|
| sớm hơn > 20 phút | 382 | **+0.0209 (+2.9)** | +7,977 |
| trong ±20 phút | 552 | +0.0048 (+1.2) | +2,671 |
| muộn hơn > 20 phút | 395 | +0.0001 (+0.0) | +31 |

144 leg long của bộ không nhiễu vào sau 19:00 (ngày gotobi thứ Hai: chờ thị trường mở 22:00 Chủ nhật), như nhau
ở mọi bộ.

## Kết luận

1. **Stop broker 0.8-1.0× → 1.0× chỉ đáng ~+1.4 %** (+$2.1-2.4k trên 6.8 năm ở $1,000, t 1.1-1.2, không có ý
   nghĩa thống kê; nhiễu giữa hai lần chạy giống nhau $293). Cùng chiều ở cả hai cặp so sánh. Ở risk $400:
   khoảng +$130/năm. Bài 30/09 (−5.9 %) không lặp lại trên 2020-2026: con số đó gộp cả nhiễu giờ vào, trên 33
   tháng, và mỗi run bốc stop lại.
2. **Nhiễu giờ vào không tốn mà có lợi**: bỏ nó (vào đúng 18:00) mất −6.5 % (t −2.3), toàn ở leg long. Phần lợi
   nằm ở những leg nhiễu ra **sớm** (17:00-17:40): +0.021R/leg (t 2.9); leg nhiễu muộn ≈ 0. Giữ nhiễu.
3. Gợi ý (chưa phải kết luận): long vào sớm hơn 18:00 có thể tốt hơn. Đây là phát hiện in-sample trên
   2020-2026, đã gồm HOLD của C3 và có 4 phép so sánh; muốn dùng phải kiểm tra trước trên giai đoạn chưa xem
   (2014-2019) rồi mới đổi giờ.
