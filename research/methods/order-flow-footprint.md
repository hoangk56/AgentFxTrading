# Phương pháp: setup order flow / footprint (dùng chung mọi thị trường)

Viết 2026-11-03. Nguồn: Trader Dale, *Order Flow Trading Setups* (2021, 161 trang, bản PDF owner gửi). Tài liệu này
chép lại **logic** của sách thành định nghĩa đo được, để một vòng research ở bất kỳ thị trường nào (crypto perp,
VN30F, futures CME, cổ phiếu) khai báo trước và kiểm mà không phải đọc lại sách. Chưa có vòng nào kiểm nhóm này.

**Độ tin của nguồn: thấp.** Sách không có một con số thống kê nào (mọi lệnh "hypothetical", ví dụ chọn lọc, không có
tỉ lệ thắng, số mẫu hay phí) và phần lớn là quảng cáo phần mềm NinjaTrader của tác giả. Giá trị của nó ở chỗ khác: tác
giả đã **cố định sẵn gần hết tham số** (khung 30 phút, chênh 300 %, ≥ 3 tầng, chỉ lần chạm đầu, ≥ 2 nến rời hẳn, cắt lỗ
10-20 % biên độ ngày). Dùng đúng các số đó thì khai báo trước được mà không phải dò tham số.

## 1. Dữ liệu cần

| Bậc | Có gì | Setup chạy được | Ví dụ |
|---|---|---|---|
| A | từng lệnh khớp: giá, khối lượng, **bên chủ động** (taker mua / bán) | tất cả | Binance aggTrades (`isBuyerMaker` = true là bên bán chủ động, ghi vào cột bid), DNSE `get_trades` VN30F (có side, từ 2026-03-25), CME (trả phí) |
| B | lệnh khớp có khối lượng, không có bên | #1, #2, Volume Profile, chốt lời / cắt lỗ theo khối lượng | FX spot của vài nhà cung cấp, nến có volume |
| C | chỉ báo giá (tick quote), không có khối lượng khớp | không setup nào; số tick chỉ là proxy yếu cho #1, #2 | tick cache IC / cTrader của repo 105 |

Thiếu bên chủ động thì đừng suy bằng tick rule rồi gọi là footprint: vòng 17 đã thử dòng lệnh suy từ báo giá IC, ra
khoảng 1/20 phí.

## 2. Dựng footprint

Mọi định nghĩa dưới đây tính trên **nến đã đóng**. Mức giá chỉ được dùng sau khi nến tạo ra nó đóng (tránh look-ahead).

- **Nến:** 30 phút (khung chính của sách), 5 phút (vào / ra lệnh), 1 phút (delta cộng dồn). Mốc nến theo UTC, ghi rõ.
- **Ô giá:** gom theo bước giá `k × tick size`. Sách không nói k. Khai báo trước một quy tắc (ví dụ k sao cho một nến
  30 phút trung vị có 15-30 ô) và giữ cố định cả kỳ; nếu sàn đổi tick size thì ghi ngày đổi.
- **bid_vol(p), ask_vol(p):** khối lượng khớp tại ô p do bên bán chủ động / bên mua chủ động.
- **Delta nến** = Σ ask_vol − Σ bid_vol.
- **Delta cộng dồn (CVD):** cộng delta từ đầu phiên. Thị trường 24/7 thì đặt lại lúc 00:00 UTC (khai báo). VN30F: bỏ
  lệnh khớp ATO / ATC (không có bên chủ động).
- **POC / HVN của nến:** ô có tổng bid + ask lớn nhất trong nến.
- **Imbalance (so chéo, như sách):**
  - mua chủ động tại p khi `ask_vol(p) ≥ 3 × bid_vol(p − 1 ô)`;
  - bán chủ động tại p khi `bid_vol(p) ≥ 3 × ask_vol(p + 1 ô)`.
  - Hình minh hoạ của sách (trang 35): bid 13 so với ask 2 ở ô trên, bid 61 so với ask 14 là imbalance; ask 7 so với
    bid 0 ở ô dưới **không** được đánh dấu. Vậy bên đối diện bằng 0 thì không tính (hoặc phần mềm có sàn khối lượng
    không nói ra). **Tự thêm, phải khai báo:** bên đối diện > 0, và ô bên lớn ≥ một sàn (ví dụ trung vị khối lượng ô của
    N nến trước).
- **Stacked imbalance:** ≥ 3 ô liền nhau cùng loại imbalance trong một nến. Vùng = từ ô thấp nhất tới ô cao nhất.
- **Unfinished business (failed auction):** ở đỉnh nến, `bid_vol(high) > 0`; ở đáy nến, `ask_vol(low) > 0` (cả hai bên
  còn khớp ở cực trị). Đỉnh / đáy "xong" là khi bên kia bằng 0.
- **Volume cluster:** ô (hoặc dải ô liền nhau) có tổng khối lượng ≥ c × trung vị khối lượng ô của cùng đoạn. Sách chỉ
  nói "đậm hơn hẳn xung quanh"; khai báo c (ví dụ 3).
- **Multiple node:** POC của ≥ 2 nến 30 phút liền nhau rơi vào cùng ô.
- **Trades filter:** lệnh khớp đơn lẻ có cỡ ≥ Q. Sách: Q = 25 lot cho 6E, ~300 cho ES. Quy tắc dùng chung: chọn Q trên
  đoạn khám phá sao cho trung bình 5-10 tín hiệu mỗi ngày, rồi giữ cố định. aggTrades của Binance đã gộp các lần khớp
  cùng một lệnh taker, nên gần với "một lệnh" hơn trade thô.

## 3. Khung chung của mọi setup (vùng → rời đi → chạm lại lần đầu)

1. **Tạo vùng:** một sự kiện footprint ở mục 4 cho ra vùng giá [lo, hi].
2. **Rời đi:** sau nến tạo vùng phải có **≥ 2 nến 30 phút trọn vẹn** nằm hoàn toàn trên hi (vùng hỗ trợ) hoặc hoàn
   toàn dưới lo (vùng kháng cự). Sách nói "1-2 nến": dùng 2 cho chặt, hoặc khai báo cả hai thành hai ô.
3. **Chạm lại lần đầu:** giá quay về chạm vùng. **Chỉ lấy lần chạm đầu**; lần sau bỏ (sách: xác suất phản ứng thấp hơn).
4. **Chiều lệnh:** chạm từ trên xuống thì long, từ dưới lên thì short. Màu ô (xanh / đỏ) không quyết định chiều.
5. **Vào lệnh:** limit ở mép vùng gần giá (sách: "đầu vùng" hoặc ô khối lượng lớn nhất). Limit chỉ tính là khớp khi
   giá **đi xuyên qua** mức đó, không phải chỉ chạm.
6. **Cắt lỗ:** một trong ba cách, khai báo trước:
   - cố định 10-20 % biên độ ngày trung bình (ATR ngày);
   - sau mép xa của vùng;
   - trong vùng khối lượng thấp nằm sau vùng.
   Cách 2, 3 cho ra cắt lỗ ngoài khoảng 10-20 % ATR thì bỏ lệnh hoặc quay về cách 1 (sách).
7. **Chốt lời:** ngay trước vùng khối lượng lớn kế tiếp theo chiều lệnh (cụm / POC nến 30 phút trước đó). Khai báo
   "ngay trước" là bao nhiêu ô. Nếu R:R < 1 thì bỏ lệnh, hoặc nhắm vùng thứ hai (hai ô riêng).
8. **Sách không nói, phải tự khai báo:** vùng hết hạn sau bao lâu nếu chưa bị chạm; thoát theo thời gian; hai vùng
   chồng nhau thì lấy cái nào; một lúc tối đa bao nhiêu lệnh.

## 4. Các setup chính

| Mã | Setup sách | Sự kiện tạo vùng | Bậc dữ liệu | Điều kiện thêm |
|---|---|---|---|---|
| OF1 | #1 Volume cluster trong trend | volume cluster trong một đoạn trend | B | trend phải định nghĩa (sách mơ hồ), ví dụ đoạn N nến có hiệu giá ≥ x × ATR và ≥ y % nến cùng chiều; long nếu trend lên |
| OF1R | #1 Volume cluster trong cú từ chối giá | volume cluster trong một cú từ chối: giá lao mạnh một chiều rồi đảo nhanh | B | định nghĩa cú từ chối (biên độ, tốc độ đảo); vào theo chiều đảo |
| OF2 | #2 Multiple node | ≥ 2 POC liền nhau cùng ô, nằm trước trend, trong trend hoặc trong cú từ chối | B | sách cho phép cả ba ngữ cảnh: khai báo ô riêng hay gộp |
| OF3 | #3 Trades filter | ô có lệnh đơn ≥ Q | A | chiều theo hướng chạm, không theo bên của lệnh lớn |
| OF4 | #4 Stacked imbalance | vùng stacked imbalance mua (hỗ trợ) / bán (kháng cự) | A | tốt nhất trong trend hoặc trước trend; một cú đi thẳng một chiều cũng được |
| OF5 | #5 Unfinished business | đỉnh / đáy "chưa xong" | A | sách không đánh riêng: dùng làm nam châm (mục 6) |

## 5. Tín hiệu xác nhận (chỉ dùng ở vùng hỗ trợ / kháng cự có sẵn, không đánh riêng)

Vùng có sẵn lấy từ OF1-OF4 hoặc từ Volume Profile (mục 7). Xem trên nến 5 phút bid × ask, trong lúc giá đang ở vùng.

| Mã | Xác nhận | Định nghĩa đo được (khai báo ngưỡng) |
|---|---|---|
| C1 | Lệnh limit lớn | kháng cự: ask_vol một ô ≥ m × trung bình ô gần đây (người bán bị động); hỗ trợ: bid_vol tương tự. Có thể tích lại trong vài phút |
| C2 | Hấp thụ | trong vùng, **cả** bid_vol và ask_vol của một ô ≥ m × trung bình, giá không đi tiếp |
| C3 | Lệnh chủ động + delta | kháng cự: delta nến 5 phút âm, bid lớn hơn hẳn ask; hỗ trợ: ngược lại |
| C4 | Phân kỳ CVD | nến 1 phút: giá làm đỉnh cao hơn mà CVD làm đỉnh thấp hơn → short (đáy thì ngược lại). Định nghĩa đỉnh / đáy (fractal N nến) phải khai báo |

Sách cho là mạnh nhất: C1 hoặc C2 rồi tới C3 (người lớn vào bị động trước, đám đông đuổi theo sau).

## 6. Quản lý lệnh

- **Nam châm (OF5):** giá có xu hướng quay về đỉnh / đáy chưa xong. Sách dùng nó để: kéo dài chốt lời nếu giá đang đi
  về phía đó; không đặt cắt lỗ trước một nam châm; không long khi có nam châm ngay dưới giá vào, không short khi có nam
  châm ngay trên.
- **Kéo cắt lỗ (trailing):** chỉ kéo khi có imbalance cùng chiều lệnh trên nến 5 phút. Thoát khi xuất hiện một tín hiệu
  C1-C4 ngược chiều, nhất là trong vùng khối lượng lớn.

## 7. Volume Profile để tìm vùng hỗ trợ / kháng cự (khung 30 phút, tối đa 1 giờ)

| Mã | Setup | Vùng |
|---|---|---|
| VP1 | Tích luỹ | đoạn đi ngang / kênh hẹp rồi bật thành trend: POC của profile đoạn đi ngang là hỗ trợ (trend lên) / kháng cự |
| VP2 | Trend | profile của cả đoạn trend thường mỏng: cụm khối lượng nổi lên trong đó là vùng, đánh theo trend |
| VP3 | Từ chối | profile của cú từ chối: cụm khối lượng nặng nhất trong đó là vùng, đánh theo chiều từ chối (sách: khó nhất) |

Hình dạng profile ngày (D cân bằng, P sau trend lên, b sau trend xuống, mỏng = trend mạnh) chỉ để đọc bối cảnh, không
phải tín hiệu.

Vào lệnh ở vùng VP chỉ khi có một xác nhận C1-C4.

## 8. Cách kiểm (bắt buộc khi mở vòng)

1. **Kiểm rẻ trước: OF5 có thật là nam châm không.** Đo tỉ lệ giá quay lại cực trị "chưa xong" trong H nến, so với cực
   trị "đã xong" có cùng khoảng cách tới giá hiện tại và cùng biến động. Không khác thì bỏ mọi luật dùng nam châm.
2. **Đối chứng giả (bắt buộc):** chạy đúng khung mục 3 (rời đi ≥ 2 nến, chạm đầu, chiều theo hướng chạm) trên **mức giá
   ngẫu nhiên** hoặc mức không có sự kiện footprint. Lần chạm lại đầu tiên của *bất kỳ* mức nào cũng có thể có hiệu ứng;
   footprint chỉ có giá trị nếu nó hơn mức đối chứng.
3. **Thứ tự:** OF5 (thống kê) → OF2, OF1, OF4, OF3 đánh riêng → C1-C4 chỉ làm bộ lọc trên ô cơ bản đã qua → VP1-VP3.
   Đừng nhân mọi setup × mọi xác nhận × mọi tham số: số ô lớn thì ngưỡng t của bộ ngẫu nhiên cũng lớn.
4. **Phí:** chấm sau phí taker / maker thật của sàn, spread và trượt giá. Limit không khớp thì không có lệnh (không được
   giả định khớp). Mục tiêu kiểu sách khoảng 10-20 % ATR ngày, nên phí phải nhỏ hơn nhiều so với con số đó.
5. **Kỷ:** khám phá / VAL / HOLD theo quy ước của repo đang làm; HOLD chỉ mở một lần cho ứng viên đã đăng ký trước. Cổng
   LIVE / DEMO giữ nguyên, không nới.

**Bẫy:**
- POC, cụm, imbalance của một nến chỉ biết khi nến đóng. Vùng chỉ dùng được sau khi các nến "rời đi" đã đóng.
- Thứ tự chạm trong một nến: dùng nến 1 phút hoặc tick để biết chạm cắt lỗ hay chốt lời trước.
- Ô giá đổi khi đổi tick size; giá crypto tăng giảm gấp nhiều lần qua các năm nên bước ô theo % giá hoặc theo ATR ổn
  định hơn bước cố định.
- Trades filter trên dữ liệu không gộp lệnh (trade thô) sẽ bỏ sót lệnh lớn bị chia nhỏ (iceberg), như sách đã nói.
- VN30F: khớp ATO / ATC không có bên; tick lịch sử REST chỉ từ 2026-03-25, sổ lệnh từ 2026-07-10, nên power thấp.

## 9. Đã kiểm gần với hướng này (đừng làm lại)

| Ở đâu | Đã kiểm | Kết quả |
|---|---|---|
| 105 vòng 4 | tỉ lệ mua chủ động theo giờ trên Binance (z 30 ngày) dự báo BTC 1-4 giờ | t 0,8 / 0,7: không có |
| 105 vòng 17 | dòng lệnh suy từ báo giá IC (OFI theo giá, tick rule, mật độ báo giá), 7 mã, 1-60 phút | phần độc lập với giá ~0,01-0,06 bp mỗi z, ~1/20 phí |
| 105 vòng 63 nhánh O (H3) | chênh mua / bán chủ động theo giờ trên altcoin perp, 4 giờ | gần 0 |
| 105 vòng 27-28 | hỗ trợ / kháng cự ở mốc giá tròn, 22 mã | chỉ vàng mốc $50 / $100 (bậc DEMO) |
| 106 R30 BE | dòng lệnh theo cỡ lệnh trên VN30F (gần với trades filter) | trượt dev |
| **105 vòng 75** | **cả họ của sách trên perp Binance BTC / ETH / SOL 2020-24** (aggTrades): setup 1-5, xác nhận 1-4 tại POC / VAH / VAL ngày trước, lần chạm lại đầu, đối chứng mức ngẫu nhiên | **không có**: 44 ô đều lỗ sau phí ở IS và VAL; chạm lại mức ngẫu nhiên lỗ 3-6 bp, vùng footprint hơn ngẫu nhiên 1-5 bp trước phí (< một lượt phí); không có "nam châm" unfinished auction; xác nhận không thêm gì. `105.AgentFxTrading/research/results/portfolio/round75_order_flow_2026-11-03.md` |

Các phép trên đều hỏi "dòng lệnh có dự báo giá N phút tới không". Hướng của sách khác: **sự kiện footprint tại một mức
giá, rồi đánh lần chạm lại đầu tiên**. Vòng 75 đã kiểm phần đó trên crypto perp và không thấy lợi thế; thị trường khác chỉ đáng thử nếu phí gần 0 hoặc khung / độ phân giải ô khác hẳn (ô 3-7 bp làm 64-77 % đỉnh / đáy 30 phút thành "unfinished").

**Bẫy dữ liệu gặp ở vòng 75:** khoá gộp `phút * 1e5 + floor(1e4 ln p)` tràn khi giá > $22.026 (BTC); file aggTrades tháng có timestamp đi lùi (SOL 2023-11) và thiếu nguyên ngày (BTC 610 giờ 2020-24). Kiểm mỗi tháng: phút, ô nằm trong [low, high] của phút, khối lượng chủ động khớp nến 1 phút.

## 10. Mẫu khai báo một ô

```text
Mã ô:           OF4-30m-k?-first-touch
Thị trường:     <sàn, mã, khung, kỷ khám phá / VAL / HOLD>
Dữ liệu:        <bậc A/B, nguồn, cách gom ô (k, tick size theo ngày)>
Sự kiện vùng:   <định nghĩa mục 2-4, mọi ngưỡng ghi số>
Rời đi:         >= 2 nến 30 phút trọn vẹn ngoài vùng
Vào:            limit ở mép vùng, chỉ lần chạm đầu, khớp khi giá đi xuyên qua
Cắt lỗ:         <cách 1/2/3>, kẹp 10-20 % ATR ngày (N ngày)
Chốt lời:       <vùng khối lượng kế tiếp - x ô>, bỏ lệnh nếu R:R < 1
Hết hạn vùng:   <số nến>; thoát theo thời gian: <số nến>
Đối chứng:      cùng khung trên mức ngẫu nhiên (cùng phân phối khoảng cách / biến động)
Phí:            <taker/maker, spread, trượt>
Cổng:           <LIVE/DEMO của repo>
```
