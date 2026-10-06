# Prompt mẫu: research thêm thuật toán

Copy khối dưới đây làm prompt cho phiên mới. Sửa phần "Đang chạy trên VPS" khi có thêm thuật toán đạt hoặc được deploy.

Trước khi dùng, nên tải dữ liệu mới để có holdout sạch (đoạn 2025-01..2026-09 đã bị dùng nhiều lần; cache cũ dừng
ở 2026-09-24/28). Không truyền mã thì `pull_cache.sh` chỉ tải 15 mã, nên ghi rõ các mã cần:

```bash
research/tools/pull_cache.sh USDJPY EURJPY ...
research/.venv/bin/python -m research.m1
```

```text
Research thêm thuật toán giao dịch trên dữ liệu hiện có. Research đến khi tìm được thuật toán hợp lý bậc live (xem dưới) thì thôi.

KHÔNG BAO GIỜ DỪNG trước khi có một ứng viên bậc live đạt holdout:
- Kết quả âm ở một vòng KHÔNG phải điểm dừng. Xong một vòng thì ghi kết quả (xem "Sau mỗi vòng") rồi mở ngay vòng
  tiếp theo với hướng mới, trong cùng lượt, không chờ tôi trả lời.
- Không kết thúc lượt bằng một báo cáo "không tìm thấy", một kết luận kiểu "đã hết hướng", hay một câu hỏi xin ý
  kiến. Hướng nào cần tôi quyết (dữ liệu mới, mã mới, VPS...) thì ghi vào báo cáo vòng đó rồi làm tiếp các hướng
  khác không cần quyết.
- Hết ý thì mở rộng: đọc thêm tài liệu, đổi mã / khung thời gian / cơ chế / cách ghép tín hiệu, dùng kỷ Dukascopy,
  xem lại các hiệu ứng "có thật nhưng nhỏ hơn phí" xem có cách thực thi nào khác.
- Ứng viên demo cũng không phải điểm dừng.
- Nếu ngữ cảnh bị tóm tắt hoặc sang phiên mới: đọc mục mới nhất của research/JOURNAL.md và báo cáo vòng gần nhất
  rồi làm tiếp vòng sau.

Dữ liệu (research/data/, git-ignore):
- 26 mã IC, M1 trong data/m1/*.npz, 2016 đến nay (năng lượng từ 2018).
- 6 mã IC mới ở vòng 7: ES35, F40, IT40, STOXX50, US2000, USDCNH (M1 bid). Cache của DOGEUSD rỗng.
- Dukascopy 2004-2015 trong data/duka/: M1 bid/ask của USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD; H1 của 11 mã.

Ràng buộc cố định (chỉ những điều này):
- Lot không phụ thuộc vốn; thuật toán được tăng giảm lot quanh một lot/rủi ro mặc định.
- Mỗi lệnh giữ tối đa 5 ngày.
- Một bot giữ tối đa 3 lệnh cùng lúc.
Mọi thứ khác tôi không nói đều được tự đổi: mã, khung thời gian, cách vào/thoát lệnh, engine, số mã mỗi bot...

Đọc trước để không test lại (22 vòng đã chạy, chỉ C3 đạt bậc live; vòng mới nhất ở đầu JOURNAL):
- research/JOURNAL.md (toàn bộ) và research/README.md
- research/results/portfolio/swing_lab_v2_2026-09-27.md ("What was tried"), prereg_swing_v2.md
- research/results/portfolio/flow_search_2026-09-27.md, flow_search_round4_2026-09-27.md
- research/results/portfolio/round6_commodity_flows_2026-10-04.md (bảng power của holdout, lỗi phí kim loại)
- research/results/portfolio/round7_new_data_2026-10-05.md (kỷ Dukascopy, mã mới, premia nhiều tuần)
- research/results/portfolio/round8_inter_symbol_2026-10-05.md (lead-lag, spillover, pairs; mục "Pitfalls")
- research/results/portfolio/round9_capital_100k_2026-10-05.md (vốn $100k, giới hạn nới; macro fair value, COT,
  mua S&P 500 sau sụt giảm/VIX > 30, carry theo swap ròng, bán quyền chọn S&P 500, C3 ở quỹ prop; mục "Process")
- research/results/portfolio/round10_new_directions_2026-10-06.md và thư mục round10_new_directions/ (mốc giá châu Á,
  sự kiện ngân hàng trung ương gộp, ghép tín hiệu FX có cổng phí, pinning quyền chọn; ngưỡng edge tối thiểu theo mã
  và thời gian giữ lệnh; mục "Pitfalls" về test ngày lễ)
- research/results/portfolio/round11_multiday_cross_section_index_scan_2026-10-06.md (drift 1-5 ngày sau sự kiện,
  cross-section 1-5 ngày, quét toàn bộ khung 15/60 phút của chỉ số)
- research/results/portfolio/round12_flows_execution_2026-10-06.md và thư mục round12_flows_execution/ (hedge cuối
  tháng ở fix WM/R, cách thực thi khác cho hiệu ứng nhỏ hơn phí và phí hoà vốn của từng cái, điều kiện làm dòng lệnh
  lớn lên, tài liệu 2018-26; 3 ứng viên đã đăng ký và mở holdout; mục "Pitfalls"; BRIEF.md là mẫu brief cho các
  nhánh song song)
- research/results/portfolio/round13_structural_2026-10-06.md và thư mục round13_structural/ (quét ổn định lấy kỷ
  Dukascopy 2004-15 làm đoạn khám phá, lịch cấu trúc: thuế / thanh toán trái phiếu Mỹ / index extension / cuối năm tài
  chính, luật ngày biến động lớn của vàng áp cho dầu và chỉ số)
- research/results/portfolio/round14_books_2026-10-06.md (ghép các hiệu ứng giờ ổn định thành một book; điều kiện
  làm E1 lớn lên)
- research/results/portfolio/round15_short_windows_2026-10-06.md (cửa sổ 1-10 phút quanh 32 mốc fix / đấu giá /
  mở-đóng cửa; mốc giờ ECB dịch năm 2015)
- research/results/portfolio/round16_income_flows_2026-10-06.md và round16_income_flows/STREAM_X.md (bảng ~45 hiệu
  ứng có thật ở mid kèm sd, phí, tỉ lệ suy giảm; power theo từng cấu trúc phí; giá trị của từng quyết định)
- research/results/portfolio/round17_microstructure_2026-10-06.md (dòng lệnh suy từ giá chào IC; momentum ngày biến
  động lớn ở chỉ số châu Âu)
- research/results/portfolio/round18_decay_dom_2026-10-06.md (xu hướng theo năm của 49 hiệu ứng; cách tìm ra luật dự
  báo được holdout; quét ngày lịch trong tháng)
- research/results/portfolio/round19_declared_2026-10-06.md (chỉ giả thuyết khai báo trước: cơ chế E1 ở CAD/AUD/NZD/
  GBP/CHF/CNH với lịch sử giờ fix chính thức; tài liệu lượt hai 34 bài)
- research/results/portfolio/round20_declared2_2026-10-06.md (USD giảm ngày FOMC: bền qua 3 kỷ nhưng 8 lần/năm; đấu
  giá tất toán đáo hạn chỉ số châu Âu / HK)
- research/results/portfolio/round21_fed_events_2026-10-06.md (luật USD ngày FOMC áp cho biên bản, điều trần,
  Jackson Hole, refunding: không có)
- research/results/portfolio/round22_residual_2026-10-06.md và round22_residual/TRIAGE_R.md (mọi ý tưởng còn mở của
  vòng 3-21, đã phân loại: cần tôi quyết / đã test / hậu kiểm / dưới phí) và báo cáo các vòng sau nếu có (xem JOURNAL)

Những họ đã cạn, đừng quét lại kiểu cũ (chỉ làm lại nếu cách dựng khác hẳn và nói rõ khác ở đâu):
- quét theo giờ / lịch không điều kiện: 90k ô lịch x khung (vòng 3), 48k ô quanh 19 mốc fix/mở cửa (vòng 4),
  15.9k ô 15/60 phút của chỉ số (vòng 11);
- lead-lag, spillover, pairs, PCA, currency strength (vòng 8); momentum / reversal / carry / TSMOM / Donchian 1 ngày
  đến 12 tháng, đơn mã và cross-section (vòng 2, 7, 11);
- sự kiện: ngân hàng trung ương, tin vĩ mô Mỹ và ngoài Mỹ, đấu giá trái phiếu, EIA/API, trước/sau quyết định, drift
  1-5 ngày (vòng 3, 4, 6, 10, 11); ngày lễ (vòng 10, nhớ placebo);
- dữ liệu ngoài: COT, funding/order flow Binance, GEX/DIX, VIX, lợi suất, 42 chuỗi FRED (vòng 4, 9);
- thực thi khác cho các hiệu ứng nhỏ hơn phí (chọn phút/giây theo spread, lệnh limit bị động, gộp nhiều dòng lệnh vào
  một lệnh, lot theo dự báo, mã sinh đôi rẻ hơn) và điều kiện theo cỡ dòng lệnh (vòng 12): SGE, Sydney (sau mở),
  fix ECB cần phí khứ hồi dưới cả commission 0.6 bp mới đạt live; limit bị động khớp đúng những ngày giá chạy ngược;
- quét ổn định 270k ô giờ/lịch FX và vàng từ 2004 (vòng 13): hiệu ứng ổn định có thật nhưng là hiệu ứng giờ trong
  ngày 1-2 bp, co lại còn 1/5 so với 2004-15, phần lớn dưới phí; lịch do luật / thanh toán / quy tắc chỉ số đặt ra
  (thuế Mỹ, thanh toán coupon/bill, index extension, cuối năm tài chính) không làm FX, vàng, US30 nhúc nhích ở 1 ngày;
  dòng lệnh ETF đòn bẩy ngày biến động lớn chỉ thấy ở vàng, ở chỉ số là đợt sập 3-4/2020;
- ghép hiệu ứng giờ ổn định thành book và lọc E1 theo điều kiện (vòng 14): các chân gần như độc lập, 9 chân sẽ đạt
  live nếu giữ cỡ IS, nhưng 5/9 chân mất > 80 % net ở VAL; bộ lọc nhân E1 lên 1.5-1.7 lần nhưng giảm số lệnh nên
  power vẫn ~2. Đừng làm lại hai hướng này trên 11 mã hiện có;
- cửa sổ 1-10 phút quanh các mốc (vòng 15, 110k ô): có thật ở giá mid, vượt xa ngẫu nhiên, nhưng 0.3-2.7 bp so với
  phí khứ hồi 1-7 bp; chọn phút trên 2004-15 tệ hơn ngẫu nhiên vì mốc giờ thể chế dịch. Bạc/vàng giảm vào phiên đấu
  giá LBMA (12:00 / 15:00 London) ổn định 9/9 năm nhưng bằng hoặc dưới phí ở IC;
- dòng tiền chuyển đổi thu nhập xuyên biên giới (cổ tức, coupon, đáo hạn; vòng 16): vài bp trong khối 1-5 ngày sd
  60-450 bp, không có gì;
- dòng lệnh suy từ thay đổi giá chào (tick rule / OFI chỉ có giá, cache IC không có khối lượng; vòng 17): dự báo đảo
  chiều theo chính lợi suất, phần độc lập chỉ 0.01-0.06 bp mỗi z; momentum trong ngày ở ngày biến động lớn của chỉ số
  châu Âu: 1-2 bp so với phí ~3.7 bp; họ "dòng lệnh tỉ lệ với biến động ngày" chỉ đúng cho vàng ở settlement COMEX;
- ngày lịch trong tháng (1-31, n ngày cuối, quy ước ngày trả tiền) x khung giờ (vòng 18, 632k ô): nhiễu như ngày làm
  việc; cấu trúc ổn định của FX là theo giờ trong ngày, không theo ngày;
- đồng nội tệ yếu vào fix của chính nó (vòng 19): không đúng ở CAD/AUD/NZD/GBP/CHF; chỉ đúng nơi fix ràng buộc dòng
  lệnh (ECB cho EUR = E1, CFETS 16:30 cho CNY: có thật nhưng dưới phí, Tokyo TTM cho JPY = C3). Tài liệu lượt hai (vòng
  12 K + 19 T, ~64 bài): các hiệu ứng có chiều trong bài hoặc đã chết sau khi công bố hoặc dưới phí;
- carry ngày ngân hàng trung ương (vòng 20): chỉ chân USD ngày FOMC còn sống (net IS t 1.90, VAL 2.40, gộp 2004-24 t
  3.25) nhưng 8 lần/năm nên không qua ngưỡng; đấu giá tất toán đáo hạn chỉ số (Mỹ, Nhật, châu Âu, HK): đã cạn;
  phần bù chỉ có ở chính quyết định FOMC, không nhân lên được bằng các sự kiện Fed khác (vòng 21).

Kết luận chung của các vòng 3-9: các dòng lệnh có thật ngoài gotobi chỉ 0.02-3 bp, cỡ spread + commission của IC;
premia nhiều tuần thua phí qua đêm (financing markup) của IC; thông tin giữa các mã được định giá trong phút đầu;
hiệu ứng hiếm (vài chục lần/năm) không đủ power cho holdout 21 tháng. Vòng 9 cho thấy vốn lớn và giới hạn nới (giữ
nhiều tuần, nhiều lệnh, lot theo vốn) không mở ra edge mới: macro fair value, COT và carry ròng đều âm hoặc t ở mức
ngẫu nhiên; bán quyền chọn chỉ số (VRP) có phần bù thật nhưng chỉ là beta, không có alpha từ 2015. Vòng 10: với 1
lệnh/ngày, bậc live cần edge gộp ~1.4 bp mỗi 15 phút ở EURUSD/USDJPY, ~2.6 bp ở US30, ~2.7 bp ở vàng; ở FX sàn phí
là commission 0.6 bp, phút spread = 0 không cứu được vì edge nằm ở phút sôi động. Vòng 11: ở 1-5 ngày phí không còn
là vấn đề nhưng không có tín hiệu (drift sau sự kiện tắt từ 2015, cross-section không dự báo được).
Vòng 12: ba ứng viên đạt số bậc demo ở IS/VAL, cả ba suy giảm theo thời gian (IS > VAL > HOLD): hedge cuối tháng ở
fix WM/R (+6.8 → +1.7 → -0.2 bp/lệnh, loại), AUDUSD trước 10:00 Sydney ngoài giờ rollover (loại, dip còn 1/3), vàng
theo chiều ngày vào settlement COMEX ngày biến động lớn (+3.5 → +2.1 → +1.7 bp, t holdout 0.37: còn là ứng viên demo
yếu). Mọi dòng lệnh từng qua IS/VAL trừ gotobi đều yếu đi ở 2025-26. Vòng 13: chọn hiệu ứng ổn định từ 2004
cũng không tránh được co lại; ứng viên E1 (bán EURUSD 11:00-13:00 London mỗi ngày) giữ được cỡ IS/VAL nhưng holdout
chỉ +0.64 bp, t 0.99, và bằng 0 khi cả hai lệnh trễ 1 phút: demo yếu.
Bảng giá trị quyết định (vòng 16, STREAM_X): ở phí IC không hiệu ứng nào đã biết đạt power live; bỏ commission FX
hoặc venue phí thấp đưa 2-3 hiệu ứng (Sydney V, slot trước fix ECB) lên mức live nếu chúng thôi suy giảm (Sydney giữ
0.31 cỡ VAL ở holdout, cần ~0.7). Cách rẻ nhất để định giá quyết định đó: Dukascopy AUD/NZD (và XAU/XAG) M1 2004-15,
rồi dữ liệu sau 2026-09-24.
Sau vòng 22: danh sách ý tưởng không cần tôi quyết đã cạn (TRIAGE_R). Phiên mới nên bắt đầu từ quyết định của tôi
(xem "Hướng cần tôi quyết"); nếu tôi chưa quyết gì mà vẫn yêu cầu chạy tiếp, chỉ mở hướng thật sự mới về cơ chế, khai
báo trước toàn bộ, không quét lại.
Hệ quả để chọn hướng (cập nhật sau vòng 15): bậc live cần edge net khoảng gấp đôi E1 với 1 lệnh/ngày; ghép book,
lọc điều kiện và cửa sổ ngắn đều không tới được (vòng 14-15). Sau 15 vòng, thứ chặn là phí của IC (commission 0.6 bp
FX/kim loại, spread chỉ số và kim loại ở các phút mốc), không phải thiếu hiệu ứng: hàng trăm ô có thật ở giá mid. Hướng
còn lại trên dữ liệu hiện có phải là cơ chế mới về loại (không phải dòng lệnh theo giờ / lịch đã quét), ví dụ dòng
tiền chuyển đổi thu nhập xuyên biên giới có ngày và chiều biết trước (cổ tức, coupon, đáo hạn) hoặc hiệu ứng nhiều
ngày nơi phí chỉ là phần nhỏ của sd; còn lại là các quyết định ở mục dưới.
Lập luận gốc: một hiệu ứng đủ power bậc live, nếu giữ nguyên độ lớn, sẽ cho t net ở IS (6 năm) khoảng
3 x sqrt(6 / 1.73) = 5.6, nên các lần quét không điều kiện đã phải thấy nó. Hướng còn lại là những gì chưa vòng nào
đặt điều kiện: dòng lệnh có chiều và độ lớn đoán trước được từ dữ liệu công khai (như gotobi), điều kiện làm một
dòng lệnh có thật lớn lên >= 3 lần, cách thực thi khác cho hiệu ứng nhỏ hơn phí, hoặc cơ chế mới từ tài liệu.
Hướng mới phải giải thích vì sao nó thoát được những giới hạn này, và tính trước power của nó theo bảng frontier.

Bài học vòng 18 về holdout: luật có chiều khai báo trước (cơ chế, tài liệu, hoặc chọn trên 2004-15) giữ 65-103 % cỡ
VAL ở holdout (C3, vàng ngày lớn, E1); luật chọn sau khi đã nhìn VAL chỉ giữ 19-31 % (J5c, I, M1). Vì vậy: chỉ đăng ký
luật có chiều và tham số cố định trước khi nhìn VAL; nếu đã nhìn VAL, tính t holdout kỳ vọng với khoảng 1/4 cỡ VAL.
Trước khi mở holdout: tính power và t holdout kỳ vọng theo cỡ hiệu ứng ở VAL, không theo IS; hiệu ứng ở VAL đã nhỏ
hơn hẳn IS thì coi như đang suy giảm và nói rõ trong đăng ký. Holdout 2025-26 đã mở thêm 3 lần ở vòng 12, nên chỉ mở
cho ứng viên có t holdout kỳ vọng đáng kể.

Hướng cần tôi quyết (ghi lại, đừng tự làm): kéo thêm mã IC (cross FX, EM, softs, cổ phiếu CFD), dữ liệu sau
2026-09-24 (Dukascopy hoặc cache IC; là holdout sạch duy nhất còn lại), một cấu trúc phí không có sàn commission
0.6 bp, Dukascopy M1 2004-15 cho thêm mã (GBPUSD, AUDUSD, NZDUSD, USDCAD, AUDJPY, XAU, XAG; chỉ số US30/US500),
dữ liệu ngoài trả phí (OI/gamma Deribit, AUM quỹ ETF đòn bẩy, premium SGE), chạy demo cho các ứng viên DEMO, và có
cho phép tính net IS của chỉ số theo phí hiện tại hay không (là đổi ngưỡng, chưa áp dụng). Dữ liệu quyền chọn FX công khai của DTCC chỉ tải được từ 2024-12 (trước đó nằm ở Deep
Archive), tức là trùng holdout.

Đang chạy trên VPS (đã có cBot, backtest cTrader và deploy; preset ở app/cbot_presets.py):
- C3 Gotobi JPY basket (cBot/GotobiBot.cs), thuật toán duy nhất đang chạy: USDJPY, EURJPY, GBPJPY, mỗi cặp một
  container, chart m15. Vào lệnh theo lịch gotobi quanh fix Tokyo, stop 3 x ATR20(H1), bỏ các ngày gotobi không có
  fix (ngày lễ Nhật, 31/12). Đạt holdout 2025-26 (R +0.042, t 2.9) và kỷ Dukascopy 2004-2015 (R +0.038, t 4.8).
- Ứng viên DEMO chờ tôi quyết (chưa có cBot, có luật dừng / lên live trong file đăng ký; đừng tối ưu lại):
  vàng theo chiều ngày vào settlement COMEX ngày biến động top 10 %
  (round12_flows_execution/PREREG_L_gold_settlement_bigday.md); bán EURUSD 11:00-13:00 London mỗi ngày
  (round13_structural/PREREG_M_eurusd_midday.md).
- C1 Crypto Donchian H4 đã trượt holdout và bị gỡ khỏi VPS ngày 2026-10-03. Đừng tối ưu lại C1 hay test
  Donchian/breakout xu hướng trên mã khác (đã âm ở crypto, chỉ số, kim loại, năng lượng, FX).
Muốn thuật toán MỚI, khác cơ chế với C3 (không phải lịch gotobi/fix JPY), ít tương quan với lợi nhuận ngày của C3:
báo tương quan đó trong báo cáo (trades_C3_gotobi_jpy_basket.csv trong research/results/portfolio/, git-ignore;
nếu thiếu thì chạy lại từ engine).
Dùng lại engine research/swing/swing.py và mô hình swap research/swing/rates.py. Lưu ý engine tính phí kim loại
(XAU/XAG/XPT) theo giá 2026, nên trước 2025 phí bị cao hơn thực tế 0.5-1.7 bp (chưa sửa, xem báo cáo vòng 6).
Ở vòng 9, FRED, Yahoo và trang IC không truy cập được từ máy này; nguồn thay thế (US Treasury, BIS, EIA, CBOE) có
trong báo cáo vòng 9. Lãi suất FRED đã tải sẵn nằm ở research/data/rates/.

"Hợp lý" có hai bậc. Chung cho cả hai:
- Có cơ sở kinh tế (dòng lệnh, thanh toán, phần bù rủi ro...), không chỉ là mẫu hình kỹ thuật.
- Chọn tham số trên 2016-2021 (IS), kiểm định trên 2022-2024 (VAL). Chiều lệnh cố định trước khi xem dữ liệu.
- Net > 0 ở IS và VAL; vẫn dương khi spread x1.5 và khi vào trễ 1 phút. t tính cluster theo ngày.
- Viết pre-registration (cấu hình + ngưỡng đạt + hash code từ `python -m research.tools.prereg_hashes`) TRƯỚC khi
  xem holdout; mỗi ứng viên chỉ xem holdout một lần.

Bậc LIVE (đạt như C3; ngưỡng các vòng 3-9):
- t >= 2.5 ở IS, >= 1.5 ở VAL; >= 2/3 số năm dương; thắng >= 95 % lệnh vào ngẫu nhiên.
- Chỉ mở holdout khi power = Sharpe mỗi lệnh (net) x sqrt(số lệnh dự kiến trong holdout) >= 3, và phải đạt holdout.

Bậc DEMO (ứng viên thật nhưng holdout không đủ power để kết luận, ví dụ hiệu ứng hiếm vài chục lần/năm):
- t >= 2.0 ở IS, net > 0 ở VAL; thắng >= 90 % lệnh vào ngẫu nhiên; không cần power >= 3.
- Vẫn mở holdout một lần sau pre-registration; net < 0 ở holdout thì loại.
- Pre-registration ghi thêm: số lệnh demo dự kiến mỗi năm, luật dừng (cắt khi R tích luỹ sau N lệnh demo dưới ngưỡng
  X, chọn trước) và luật lên live (holdout + demo gộp lại đạt t >= 2.5).
- Chỉ chạy trên tài khoản demo, rủi ro nhỏ cố định. Demo còn đo được spread và trượt giá thật ở phút vào lệnh.
- Tìm được ứng viên demo KHÔNG phải điểm dừng: ghi lại rồi tìm tiếp ứng viên bậc live.
Lưu ý về holdout: đoạn 2025-01..2026-09 đã bị dùng làm holdout cho nhiều chiến lược (C1, C3, C4, M1 và lab cũ đã
xoá), nên không còn sạch hoàn toàn. Kỷ Dukascopy 2004-2015 đã dùng cho C3, M1, vài screen FX ở vòng 7-8 và làm
đoạn thiết kế ở vòng 9. Nếu có dữ liệu mới sau 2026-09-24 thì dùng làm holdout; nếu không, nói rõ giới hạn này trong
báo cáo. Cắt dữ liệu holdout ngay khi load (ts < 2025-01-01) để không vô tình nhìn thấy.

Không hạ ngưỡng để có kết quả; kiên trì nghĩa là mở rộng hướng tìm, không phải nới tiêu chí. Bậc demo không phải
ngưỡng live hạ xuống: ứng viên demo không được lên live trước khi đạt luật lên live đã đăng ký.
Cập nhật tiến độ ngắn gọn khi tìm thấy hoặc loại một hướng.

Bẫy hay gặp (chi tiết ở mục "Pitfalls" của vòng 8, 10, 12, 13): mốc giờ thể chế cũng dịch (ECB-fix V lùi 15 phút
cuối 2015); kết quả ngày biến động lớn phải báo cả khi bỏ 3-4/2020; lệnh ngẫu nhiên đối chứng cho lệnh giữ nhiều giờ
phải vào sau tín hiệu (nếu không sẽ chứa luôn cú chạy dùng để chọn ngày); giờ ghi trong brief / đăng ký phải lấy từ
`date -u`, không ước lượng; ngày lễ phải cluster theo khối ngày và có placebo
nước khác; lệnh vào ngẫu nhiên cho luật có chiều phụ thuộc dữ liệu phải tính lại chiều tại thời điểm ngẫu nhiên; giờ
rollover của IC (17:00-18:00 New York) làm phí theo mùa ở các mốc giờ châu Á; nhãn phút đầu nến / cuối nến; kiểm cả hai
lệnh trễ 1 phút cho luật momentum vào một mốc giá.

Cách chạy một vòng (đã dùng từ vòng 10): viết BRIEF.md cho vòng (copy round12_flows_execution/BRIEF.md, sửa phần
hướng), chạy 3-4 nhánh song song bằng subagent, mỗi nhánh ghi giả thuyết kèm giờ UTC vào HYPOTHESES_<nhánh>.md
TRƯỚC khi tính, viết STREAM_<nhánh>.md, và PREREG_DRAFT_* nếu đạt. Panel phút dùng chung (26 mã, 2016-2024, không có
holdout) dựng lại từ data/m1 nếu scratchpad cũ đã mất. Máy 10 lõi / 16 GB: tối đa 2 tiến trình nặng mỗi nhánh.

Sau mỗi vòng (rồi mở vòng tiếp theo ngay, không dừng):
- Viết báo cáo vòng vào research/results/portfolio/ (luật chi tiết, số liệu từng giai đoạn/năm, những gì đã thử và
  loại). Nêu rõ mỗi ứng viên đạt bậc nào. Ứng viên demo kèm luật dừng / lên live; không tự viết cBot hay deploy.
- Thêm một mục vào research/JOURNAL.md; cập nhật research/README.md nếu liên quan.
- Cập nhật chính file research/PROMPT.md này cho khớp hiện trạng: số vòng, danh sách đọc trước, họ đã cạn, kết luận
  chung, hướng cần tôi quyết, và những gì giúp vòng sau tìm tốt hơn.
- Chạy test (`research/.venv/bin/python -m pytest research/tests`). Không commit.
- Báo tiến độ ngắn gọn cho tôi rồi làm tiếp.

Chỉ dừng khi một ứng viên bậc live đã đạt holdout đã đăng ký: khi đó viết báo cáo cuối như trên.
```
