# GotobiBot, lãi kép rủi ro = số dư/3, nạp lại về $1,000 (2026-10-09)

Câu hỏi của user: vốn đầu $1,000, mỗi lệnh rủi ro = số dư / 3, số dư dưới $1,000 thì nạp cho đủ $1,000, thống kê
từng năm từ 2020.

## Cách làm

- Backtest cTrader CLI mới trên VPS (`~/gotobi-cmp/`). Dùng đúng `cBot/GotobiBot.algo` đang chạy prod (PR #13,
  sha1 `0332227e`), tick IC, `--commission-auto`, 3 cặp USDJPY/EURJPY/GBPJPY, mỗi cặp một job mỗi năm, từ
  01/01/2020 đến 08/10/2026. Camouflage để mặc định (stop broker 0.8-1.0x, entry jitter, decoy 0.01 lot). `--SkipDates`
  gồm 32 ngày gotobi rơi vào lễ Nhật / ngân hàng 2020-2026 (`tools/gotobi_holidays.no_fix_days`) cộng 25/12/2026.
  Rủi ro cố định $1,000/leg, `MaxLotsPerTrade=1000` để lot không bị cắt, balance $1,000,000.
- Kết quả: 2,686 leg thật trên 457 ngày gotobi, R/leg **+0.061** (net, sau commission + swap). 6,022 decoy tổng
  −$805, giữ nguyên không scale.
- Mô phỏng offline (`~/gotobi-cmp/sim.py`): đầu mỗi ngày gotobi, tức lúc leg long đầu tiên vào lệnh, nếu số dư
  < $1,000 thì nạp cho đủ $1,000. Sau đó mọi leg của ngày đó (3 long + 3 short) rủi ro = số dư/3. Lot =
  lot gốc × risk/$1,000, làm tròn xuống 0.01. PnL scale theo lot. Nếu số dư về ≤ 0 thì coi là stop-out: số dư = 0,
  các leg còn lại trong ngày bị huỷ.
- Hai biến thể. **Không cap** là đúng nguyên văn câu hỏi. **Cap 5 lot** là thứ bot hiện tại thực sự làm, vì
  `MaxLotsPerTrade` mặc định là 5.

## Edge theo năm (rủi ro cố định)

| năm | leg | ngày | R/leg | win % | ngày tệ nhất (R, cộng 6 leg) | số ngày lỗ ≥ 3R |
|---|---|---|---|---|---|---|
| 2020 | 392 | 66 | +0.046 | 57 | −2.20 | 0 |
| 2021 | 399 | 68 | +0.073 | 60 | −1.89 | 0 |
| 2022 | 395 | 67 | +0.071 | 58 | −3.71 | 2 |
| 2023 | 409 | 69 | +0.036 | 58 | −5.20 | 3 |
| 2024 | 393 | 67 | +0.058 | 56 | −3.72 | 2 |
| 2025 | 386 | 67 | +0.064 | 57 | −2.97 | 0 |
| 2026 | 312 | 53 | +0.079 | 57 | −3.07 | 1 |

Ở mức rủi ro số dư/3 mỗi leg, một ngày lỗ ≥ 3R xoá sạch tài khoản. 3 cặp JPY tương quan 0.67-0.83 nên 3 long thường
thua cùng lúc.

## Liên tục 2020 → 10/2026, số dư/3, KHÔNG cap lot

| năm | đầu năm $ | nạp $ (lần) | lãi/lỗ $ | cuối năm $ | maxDD | lot lớn nhất | cháy |
|---|---|---|---|---|---|---|---|
| 2020 | 1,000 | 537 (3) | +170 | 1,707 | 99 % | 367 | 0 |
| 2021 | 1,707 | 0 | +355,007 | 356,714 | 75 % | 518 | 0 |
| 2022 | 356,714 | 2,676 (4) | −357,408 | 25,814 | 100 % | 1,514 | 2 |
| 2023 | 25,814 | 3,833 (7) | −30,245 | 3,099 | 100 % | 34 | 3 |
| 2024 | 3,099 | 3,975 (8) | +33,823 | 43,314 | 100 % | 45 | 2 |
| 2025 | 43,314 | 730 (3) | −28,109 | 15,935 | 100 % | 497 | 0 |
| 2026 | 15,935 | 1,243 (2) | +2,588 | 21,263 | 100 % | 127 | 1 |

Tổng nạp $13,994, cuối kỳ $21,263, **lãi ròng +$7,269**. Lot 500-1,500 trên một lệnh là phi thực tế (thanh khoản
lúc fix, slippage).

## Liên tục, số dư/3, cap 5 lot (bot hiện tại)

| năm | đầu năm $ | nạp $ (lần) | lãi/lỗ $ | cuối năm $ | maxDD | leg bị cap |
|---|---|---|---|---|---|---|
| 2020 | 1,000 | 537 (3) | +22,359 | 23,896 | 94 % | 261/392 |
| 2021 | 23,896 | 0 | +55,559 | 79,456 | 23 % | 399/399 |
| 2022 | 79,456 | 0 | +109,647 | 189,103 | 16 % | all |
| 2023 | 189,103 | 0 | +47,584 | 236,686 | 11 % | all |
| 2024 | 236,686 | 0 | +47,943 | 284,629 | 15 % | all |
| 2025 | 284,629 | 0 | +67,352 | 351,981 | 4 % | all |
| 2026 | 351,981 | 0 | +49,115 | 401,096 | 5 % | all |

Tổng nạp $1,537, cuối kỳ $401,096. Đây thực chất **không còn là "số dư/3"**: từ giữa 2020 mọi leg đều chạm cap
5 lot, nên rủi ro thực tế mỗi leg chỉ còn khoảng $1.5-3k (dưới 1 % số dư). Năm 2020 suýt cháy (số dư thấp nhất
$224, DD 94 %) rồi mới thoát.

## Mỗi năm chạy riêng, bắt đầu $1,000

| năm | cap 5: nạp $ (lần) / lãi ròng $ / maxDD / cháy | không cap: nạp $ (lần) / lãi ròng $ / maxDD / cháy |
|---|---|---|
| 2020 | 1,537 (3) / +22,359 / 94 % / 0 | 1,537 (3) / +170 / 99 % / 0 |
| 2021 | 1,261 (3) / +44,160 / 74 % / 0 | 1,261 (3) / +272,954 / 75 % / 0 |
| 2022 | 4,428 (5) / +58,330 / 100 % / 2 | 4,428 (5) / +21,386 / 100 % / 2 |
| 2023 | 3,323 (6) / +26,397 / 100 % / 2 | 5,156 (11) / −2,058 / 100 % / 3 |
| 2024 | 5,311 (11) / +22,410 / 100 % / 2 | 5,311 (11) / +38,003 / 100 % / 2 |
| 2025 | 1,789 (4) / +40,820 / 76 % / 0 | 2,924 (7) / +13,011 / 100 % / 0 |
| 2026 | 2,123 (4) / +37,266 / 93 % / 0 | 3,448 (6) / +17,815 / 100 % / 1 |

## So sánh và độ nhạy

- Số dư/9 mỗi leg (tức tổng số dư/3 chia cho 3 cặp), cap 5: nạp $84, không lần cháy nào, DD năm 2020 là 72 %, sau đó
  ≤ 34 %. Cuối kỳ $362,415.
- Edge giảm một nửa (−0.03R/leg), số dư/3: cap 5 → nạp $13,918, cuối kỳ $79,054. Không cap → nạp $23,792, cuối kỳ
  $6,872, **lỗ ròng −$16,920**.

## Giữ tài khoản ở $10,000 khi đã chạm (không cap lot, mỗi năm chạy riêng từ $1,000)

Quy tắc: số dư/3 mỗi leg, nạp về $1,000 khi số dư dưới $1,000. Ngày gotobi đầu tiên mà số dư đầu ngày ≥ $10,000
thì từ ngày đó trở đi, đầu mỗi ngày gotobi đưa số dư về đúng $10,000: lãi thì rút phần dư, lỗ thì nạp phần thiếu.
Rủi ro lúc đó cố định $3,333/leg, lot lớn nhất 12-32. "Tiền túi tối đa" là đỉnh của (tổng nạp − tổng rút), gồm cả
$1,000 ban đầu, tức số tiền tối đa thật sự phải bỏ ra trong năm. Lãi ròng = rút + số dư cuối − nạp.

| năm | chạm $10k | nạp $ (lần) | rút $ | cuối năm $ | **lãi ròng $** | tiền túi tối đa $ | cháy | ngày lỗ nặng nhất $ |
|---|---|---|---|---|---|---|---|---|
| 2020 | 08/05 | 60,462 (24) | 86,705 | 5,325 | **+31,568** | 1,537 | 0 | −7,328 |
| 2021 | 26/02 | 50,850 (22) | 117,713 | 11,696 | **+78,559** | 11,947 | 0 | −6,287 |
| 2022 | 15/07 | 29,264 (13) | 85,772 | 2,429 | **+58,937** | 8,287 | 2 | −8,682 |
| 2023 | 19/05 | 69,760 (24) | 89,495 | 17,366 | **+37,101** | 9,213 | 3 | −11,068 |
| 2024 | 14/06 | 54,267 (20) | 82,306 | 12,547 | **+40,586** | 20,568 | 2 | −11,310 |
| 2025 | 15/04 | 66,424 (25) | 108,284 | 18,988 | **+60,848** | 1,789 | 0 | −9,904 |
| 2026 (đến 08/10) | 25/05 | 33,722 (16) | 78,625 | 14,527 | **+59,431** | 4,591 | 1 | −10,214 |

Năm nào cũng chạm $10k, chậm nhất là 15/07 (2022), và năm nào cũng lãi ròng. Phần lớn tiền nạp là nạp lại từ tiền
đã rút. Con số cần nhìn là tiền túi tối đa: tới $20.6k năm 2024 và $11.9k năm 2021. Ở mức $3,333/leg, một ngày xấu mất
$6-11k, nhiều ngày cháy cả $10k (2-3 lần mỗi năm 2022-2024).

Chạy liên tục 2020 → 08/10/2026 theo cùng quy tắc: chạm $10k ngày 08/05/2020. Nạp $544,124, rút $1,065,265, cuối
kỳ $14,527, lãi ròng **+$535,669**, khoảng $63-98k/năm từ 2021. Tiền túi tối đa $1,537, vì lãi 2020 đủ trả các lần nạp
về sau.

Để so sánh, không cap và không giữ $10k (mỗi năm riêng): lãi ròng 2020 +$170, 2021 +$272,954, 2022 +$21,386, 2023
−$2,058, 2024 +$38,003, 2025 +$13,011, 2026 +$17,815. Số dư phình rồi xẹp theo may rủi, có lệnh lên tới 398 lot.

Mọi số đều là backtest với edge +0.061R/leg. Edge mà giảm một nửa thì lãi ở mức $3,333/leg cũng giảm khoảng một nửa,
còn tần suất cháy thì tăng.

## Kết luận

Số dư/3 mỗi leg lớn hơn mức Kelly của edge này nhiều lần (R/leg ≈ +0.06, 6 leg tương quan mỗi ngày). Không cap:
tài khoản cháy hoặc gần cháy gần như mỗi năm, kết quả phụ thuộc may rủi theo thứ tự ngày, và 7 năm chỉ lãi ròng
+$7k trên $14k tiền nạp. Con số đẹp của bản cap 5 lot đến từ việc cap biến nó thành rủi ro cố định nhỏ ngay khi số
dư vượt khoảng $5-15k, chứ không phải từ quy tắc /3. Mọi số ở đây là backtest. Edge live cần khoảng 100 ngày gotobi
mới kiểm được ([gotobi_live_fills_2026-10-06.md](gotobi_live_fills_2026-10-06.md)).
