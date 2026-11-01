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
- Vòng 30 thêm 6 mã FX: tick IC 2016-2024 của USDCNH, USDMXN, USDSGD, EURNOK, USDNOK, EURSEK trong data/<mã>/t1
  (2025-26 = holdout và forward chỉ nằm trong cache backtest trên VPS, chưa tải về); Dukascopy M1 2004-15 của 6 mã đó
  trong data/duka/m1_r30/ (ask sớm là rác, USDMXN từ 2007, USDCNH từ 2012).
- Dukascopy 2004-2015 trong data/duka/: M1 bid/ask của USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD; H1 của 11 mã.
  Vòng 24 thêm data/duka/m1c/ (npz gọn): AUDUSD, NZDUSD (Chủ nhật-thứ Sáu), XAUUSD, XAGUSD (thứ Hai-thứ Sáu),
  GBPUSD, USDCAD (chỉ thứ Tư); kim loại 2004-09 chỉ có bid. Bạc Dukascopy trước 2008 thưa, không tin được.

Ràng buộc: từ 2026-10-31 tôi bỏ hết ("lần này không có ràng buộc gì cả"): không còn giới hạn giữ 5 ngày, 3 lệnh
mỗi bot, lot không theo vốn, và không bắt buộc IC / cTrader (sàn khác như Binance được). Ngưỡng thống kê LIVE / DEMO
bên dưới giữ nguyên. Luật nào chiếm vốn (chân spot, lệnh trả đủ tiền) phải chấm theo lợi suất VƯỢT lãi suất cash
(Fed funds, research/data/rates/DFF.csv) trên vốn đã dùng (bài học vòng 58).

Đọc trước để không test lại (63 vòng đã chạy, chỉ C3 đạt bậc live; vòng mới nhất ở đầu JOURNAL; tạm dừng sau vòng 29
theo yêu cầu của tôi, rồi ngày 2026-10-18 tôi duyệt quyết định 1, 2, 4: luật vàng chạy demo, vòng 30 trên 6 mã FX mới,
chạy lại log forward; ngày 2026-10-27 tôi cho research tiếp và cho tìm các nguồn khác (vòng 31 trở đi: dữ liệu công
khai không phải giá); hiện trạng ở cuối báo cáo vòng mới nhất):
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
  vòng 3-21, đã phân loại: cần tôi quyết / đã test / hậu kiểm / dưới phí)
- research/results/portfolio/round23_recent_2026-10-15.md và thư mục round23_recent/ (tài liệu 2025-26: bản đồ 40 bài
  ở STREAM_N.md, cách tìm qua Crossref theo ISSN / DOI prefix và arXiv; dòng tiền sell-side 2023-26 ở STREAM_P.md)
- research/results/portfolio/round24_relaxed_2026-10-15.md và thư mục round24_relaxed/ (điều kiện nới: bậc RELAXED,
  luật kỷ mới cho cơ chế từ 2024, Dukascopy 2004-15 cho AUD/NZD/XAU/XAG; STREAM_C.md chấm lại 60 hiệu ứng cũ kèm phí
  cần để đạt live; F3 đạt holdout, FOMC trượt)
- research/results/portfolio/round25_surprises_2026-10-17.md và thư mục round25_surprises/ (consensus công bố từ lịch
  ForexFactory 2007-24 và cách sửa giờ của nó ở STREAM_B.md; tổng điều tra tài liệu 2000-17 và kinh nghiệm tiếng Nhật /
  Trung / Hàn / Đức ở STREAM_C.md; STREAM_A.md định giá từng quyết định đang chờ tôi, kèm giả thuyết khai báo sẵn trong
  HYPOTHESES_A.md)
- research/results/portfolio/round26_tick_events_2026-10-17.md và thư mục round26_tick_events/ (mô hình khớp lệnh ở
  mức tick: độ trễ, stop phía server, limit chỉ khớp khi giá đi xuyên qua; straddle khi ra tin, cú nhảy ngoài lịch tin;
  danh sách phút giờ cố định có cú nhảy ở STREAM_J.md)
- research/results/portfolio/round27_levels_opens_2026-10-17.md và thư mục round27_levels_opens/ (vàng phá mốc tròn với
  lệnh stop chờ: chỉ mốc $50 / $100 có hiệu ứng, bậc DEMO, PREREG_DRAFT_G_gold_round50_cascade.md; chiều cú nhảy lúc sàn
  mở: có thông tin ở mid, không có gì sau phí)
- research/results/portfolio/round28_round_levels_2026-10-17.md và thư mục round28_round_levels/ (luật mốc tròn của vàng
  áp cho mốc lớn của 21 mã khác, gộp book: không có gì ngoài vàng; hiệu chỉnh khớp stop giữa dữ liệu phút và tick ở
  STREAM_R1.md)
- research/results/portfolio/round27_levels_opens/PREREG_G_gold_round50_cascade.md (holdout đã đăng ký của luật vàng
  mốc $50: qua bậc DEMO; lịch tin USD chính thức 2024-26 trong prereg_code/usd_high_2024_2026.csv, dùng lại được)
- research/results/portfolio/round29_fades_opens_2026-10-18.md và thư mục round29_fades_opens/ (fade mốc tròn nhỏ ở
  ES35 / F40 / IT40 / STOXX50 / US2000, chiều vài giây đầu ở giờ mở cửa ASX / TSE / A-share / HKEX / phiên đêm SGE:
  không có gì; sửa lỗi "đảo chiều" của vòng 28; mục "State at the pause" liệt kê thuật toán đang chạy, ứng viên, log
  forward và các quyết định chờ tôi theo thứ tự giá trị)
- research/results/portfolio/gold_level_cbot_2026-10-18.md (luật vàng mốc $50 thành cBot GoldLevelBot: backtest cTrader
  trên holdout trùng 228/228 lệnh của engine; stop bảo vệ $100; lịch tin USD chính thức kéo dài tới 2027 trong
  cBot/seeds/usd_high_calendar.csv, hiệu lực tới 2026-12-11; chạy demo từ 2026-10-18)
- research/results/portfolio/round30_fix_flows_2026-10-18.md và thư mục round30_fix_flows/ (6 mã FX mới: dòng tiền NOK
  của Norges Bank, fix Banxico của USDMXN, VWAP ABS của USDSGD, đóng cửa CFETS của USDCNH ở spread thật: không có gì;
  cách kéo tick IC qua backtest cTrader trên VPS)
- research/results/portfolio/round31_new_sources_2026-10-27.md và thư mục round31_new_sources/ (bảng dòng tiền / vị thế
  công khai của Nhật: TFX Click 365, MoF, JPX; tổng điều tra ~1.550 chiến lược của cộng đồng thực chiến ở STREAM_P.md;
  dòng tiền on-chain, vị thế Bitfinex / Binance, thanh lý; lượng vàng ETF nắm giữ, dự báo nhiệt độ NOAA cho khí;
  BRIEF.md là mẫu brief cho nguồn mới, kèm luật mạng)
- research/results/portfolio/round32_liquidity_vol_attention_2026-10-27.md và thư mục của nó (TGA / RRP / H.4.1, vol
  ngầm định CBOE của từng tài sản, Wikipedia pageviews / Hacker News; bản nháp HN "recession" không đăng ký)
- research/results/portfolio/round33_cross_venue_2026-10-27.md và thư mục round33_cross_venue/ (premium Coinbase /
  kimchi, premium SGE miễn phí, chiều giao hàng Au(T+D), tiền gửi SNB)
- research/results/portfolio/round34_china_etf_options_2026-10-28.md và thư mục của nó (xếp hạng thành viên SHFE kèm
  tách khách hàng môi giới / thành viên khác = "COT" ngày của Trung Quốc; liều tái cân bằng ETF đòn bẩy từ lịch sử
  ProShares; 16.5 triệu lệnh quyền chọn BTC Deribit; fade đáo hạn thứ Sáu 08:00 chỉ đúng ở VAL)
- research/results/portfolio/round35_options_volume_asia_positioning_2026-10-28.md (put/call CBOE theo lớp nối liền
  2006-24 qua JSON thống kê ngày; vị thế tổ chức TAIFEX 2018-24 qua FinMind, dòng tiền TWSE 2004-24)
- research/results/portfolio/round36_asia_liquidity_household_cash_2026-10-28.md (giao dịch currency board HKMA, HIBOR /
  SHIBOR, RRR; tiền Kho bạc Mỹ trả hộ gia đình từ DTS; mục "State after round 36 (pause)")
- research/results/portfolio/round37_forced_flows_2026-10-29.md và thư mục round37_forced_flows/ (ký quỹ / biên độ SHFE
  và SGE từ file tham số ngày 2013-24, funding crypto theo mức trả ở mốc 00/08/16 UTC, lệnh stop qua đỉnh / đáy kỷ lục
  và cực trị tuần / tháng / quý / năm, dòng tiền Stock Connect; mục "Pitfalls" về nguồn)
- research/results/portfolio/round38_short_volume_storms_2026-10-29.md và thư mục của nó (khối lượng bán khống FINRA
  Reg SHO hằng ngày 2009-24 và số chứng chỉ quỹ ETF SSGA / iShares; bão Đại Tây Dương qua dự báo chính thức ATCF; mục
  "Pitfalls" về file FINRA, file issuer có dòng 2025-26)
- research/results/portfolio/round39_rolls_positioning_2026-10-29.md và thư mục của nó (lịch roll GSCI / BCOM / USO cho
  dầu / khí, cách IC dựng giá XTI / XBR; khảo sát nguồn sentiment broker miễn phí, COT small-trader, dòng tiền JPX theo
  loại nhà đầu tư)
- research/results/portfolio/round40_news_leverage_2026-10-30.md và thư mục của nó (GDELT 1.0 daily events 2013-24 và
  giờ công bố; vay ký quỹ / bán khống SSE + SZSE 2010-24 qua Eastmoney; bản đăng ký HK50 bật tăng đã trượt holdout)
- research/results/portfolio/round41_supply_cycles_2026-10-30.md và thư mục của nó (lịch và kết quả đấu giá trái phiếu
  Mỹ / JGB / Bund 2004-24 kèm cách đọc file MoF / Finanzagentur; chỉ mục SEC EDGAR 2015-24 cho phát hành cổ phiếu)
- research/results/portfolio/round42_megacap_boj_ops_2026-10-30.md và thư mục của nó (giờ công bố lợi nhuận của top-40 mã
  Mỹ từ EDGAR submissions JSON + trọng số từ 13F Vanguard; file nghiệp vụ mua JGB của BoJ 2013-24)
- research/results/portfolio/round43_mood_ratings_2026-10-30.md và thư mục của nó (thời tiết NOAA ISD qua bucket AWS công
  khai cho 11 thành phố có sàn, kết quả bóng đá quốc tế, xếp hạng tín nhiệm quốc gia; mục "Pitfalls" về robots.txt)
- research/results/portfolio/round44_insiders_tff_2026-10-30.md và thư mục của nó (bộ dữ liệu giao dịch nội bộ SEC 2014-24;
  CFTC TFF qua mirror Hugging Face; cftc.gov chặn ClaudeBot trong robots.txt)
- research/results/portfolio/round45_combined_jpx_short_2026-10-30.md và thư mục của nó (mô hình ridge gộp các đặc trưng
  không phải giá của vòng 37-44; tỉ lệ bán khống hằng ngày TSE qua stock-marketdata.com, báo cáo vị thế bán khống lớn qua karauri.net)
- research/results/portfolio/round46_rebalancing_bond_leg_2026-10-30.md và thư mục của nó (lợi suất ngày Treasury / MoF JGB /
  Bundesbank 2004-24 và cách đọc file; tín hiệu tái cân bằng 60/40 của Harvey-Mazzoleni-Melone 2025 dựng đủ hai chân)
- research/results/portfolio/round47_buyback_capacity_2026-10-30.md và thư mục của nó (XBRL company-concept mua lại cổ phiếu
  và giờ 8-K item 2.02 của top-200 mã Mỹ 2014-24; ghép tên 13F Vanguard với CIK)
- research/results/portfolio/round48_btc_network_2026-10-30.md và thư mục của nó (chuỗi block BTC của Coin Metrics community,
  mốc điều chỉnh độ khó của mempool.space, mempool 15 phút của blockchain.com; giá BTC 2012-17 làm PRE)
- research/results/portfolio/round49_cb_speech_tone_2026-10-30.md và thư mục của nó (JSON bài phát biểu Fed có giờ đăng,
  CSV bài phát biểu ECB, lịch FOMC 2009-24; từ điển diều hâu / bồ câu)
- research/results/portfolio/round50_fund_flows_2026-10-30.md và thư mục của nó (Fed H.6 quỹ thị trường tiền tệ và ngày công
  bố; ici.org chặn bot)
- research/results/portfolio/round51_gold_auction_volume_2026-10-30.md (khối lượng / số vòng đấu giá LBMA cần tài khoản IBA)
- research/results/portfolio/round52_lit_census_2026-10-30.md và CENSUS_Z.md (rà 48.633 tiêu đề Crossref + 797 arXiv 2018-24
  đối chiếu với 51 vòng: chỉ còn USDT mint -> BTC vài phút là mở)
- research/results/portfolio/round53_usdt_mints_2026-10-30.md và thư mục của nó (mint USDT Omni + Tron 2017-24; hướng mở cuối
  của bản rà vòng 52 cũng trượt)
- research/results/portfolio/round54_single_stocks_2026-10-30.md và thư mục của nó (tôi duyệt hướng CFD cổ phiếu MT5 ngày
  2026-10-30: dữ liệu ngày Dukascopy 263 mã Mỹ 2016-24, mô hình phí IC MT5, stocklib; DATA_D.md cách tải và bẫy)
- research/results/portfolio/round55_insider_intraday_2026-10-30.md và thư mục của nó (M1 Dukascopy cổ phiếu ngày có sự kiện,
  spread 09:30-10:30 theo phút; commission $0.02 / cổ phiếu của IC ~12 bp khứ hồi là chi phí trói buộc)
- research/results/portfolio/round56_stock_cross_section_2026-10-30.md và thư mục của nó (cross-section ngày của ~200 mã lớn,
  bẫy ngày bắt đầu của book giữ nhiều ngày)
- research/results/portfolio/round57_earnings_gaps_2026-10-30.md và thư mục của nó (gap lớn sau công bố lợi nhuận; datafeed
  Dukascopy bóp tốc độ sau khi tải nhiều trong ngày, quy tắc cắt mẫu theo ngày ngẫu nhiên)
- research/results/portfolio/round58_unconstrained_carry_2026-10-31.md và thư mục của nó (bỏ ràng buộc: carry funding
  long spot / short perp USDT-M Binance; dữ liệu research/data/binance/ = 891 perp kể cả đã huỷ niêm yết, funding + spot
  384 mã, code/carry.py; A3 qua ngưỡng đã đăng ký nhưng HOLD chỉ bằng lãi suất cash)
  và báo cáo các vòng sau nếu có (xem JOURNAL)

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
  phần bù chỉ có ở chính quyết định FOMC, không nhân lên được bằng các sự kiện Fed khác (vòng 21);
- tài liệu mới 2025-01..2026-10 (vòng 23 N, 23.9k bản ghi, 40 bài có chiều + cửa sổ): fade gap mở lại 17:00 NY có
  thật ở mid mọi cặp mọi năm nhưng dưới phí 3-5 bp (spread giờ rollover), đảo chiều bất đối xứng trong ngày, BTC quanh
  ngày lễ NYSE, pre-market US500: không có. Vàng quanh Giáng sinh chỉ là mùa vụ cuối năm (1/1, EURUSD, bạc cùng chiều);
- dòng tiền sell-side 2023-26 (vòng 23 P): vol-control, tái cân bằng theo ngưỡng (chân cổ phiếu), CTA đổi tín hiệu
  21/63/252 ngày, buyback blackout, tuần sau đáo hạn quyền chọn, quỹ hưu trí cuối quý: không thấy ở lợi suất 1-5 ngày
  của chỉ số; dòng tiền có ngưỡng công bố trước và thực hiện tuỳ ý trong nhiều giờ thì đã bị chạy trước;
- cơ chế chỉ có từ 2024 (vòng 24 A, kỷ mới): ETF BTC/ETH spot vào NAV 15-16 ET (kể cả ký theo dòng tiền cùng ngày:
  không có chiều), NISA mới (USDJPY/EURJPY vào fix sau ngày đặt lệnh), US T+1, "BTC dump 10 giờ": đều trượt ở
  DISCOVERY; ETH ở IC phí 23-26 bp;
- lịch sử dài 2004-15 (vòng 24 B): V mở phiên Sydney chỉ xuất hiện từ ~2011 (PRE net âm), các mốc fix LBMA vàng/bạc,
  COMEX mở, phiên vàng Trung Quốc: dưới phí; mùa vụ cuối năm vàng + USD (15/12 đến cuối tháng 12) chỉ là chuỗi
  2016-23, PRE t 0.69, VAL t 0.04; vàng tháng 9 + 11 (Baur) đảo chiều sau 2010; vàng tháng 1, Santa Claus, USD hồi
  tháng 1: không có;
- chấm lại 60 hiệu ứng cũ theo bậc RELAXED (vòng 24 C): chỉ còn cửa sổ ECB EURUSD (F1-F5, F20) và USD ngày FOMC; ghép
  book không có power holdout (~0.7) vì các chân đã biết holdout yếu. USD ngày FOMC đã trượt holdout (vòng 24);
- phần bất ngờ đoán trước được của tin vĩ mô theo consensus công bố (vòng 25 B, 144 ô): neo vào số kỳ trước (Campbell &
  Sharpe), chỉ báo sớm so với consensus cũ (ADP, khảo sát Fed vùng, CPI các nước -> HICP, CPI Tokyo, claims, PMI
  flash), nowcast Cleveland Fed / GDPNow: consensus đoán được nhưng FX đã định giá trước giờ ra tin, gộp lại <= ~1 bp so
  với phí khứ hồi 0.8-1.9 bp ở phút ra tin;
- tài liệu 2000-17 và kinh nghiệm thực chiến không phải tiếng Anh (vòng 25 C: 13.7k bản ghi, 39 họ, 27 họ đã test):
  thứ Hai sau thứ Sáu giảm, phá mốc tròn ở chỉ số, ngày giao dịch đầu / cuối tháng ở Tokyo: không có. Mốc $10 của vàng
  là rào cản thật ở mọi kỷ từ 2004 (đi tiếp sau khi phá) nhưng net chỉ bằng nửa phí IC; lát giờ COMEX là chọn sau khi
  nhìn, power 1.68 ở cỡ VAL;
- thực thi theo tick quanh thông tin (vòng 26): straddle stop OCO đặt 2 phút trước tin, limit bắt cú vọt, fade sau 1
  phút (630 ô): giá đi tiếp sau khi stop khớp +0.2-1.6 bp gross, dưới phí khứ hồi phút ra tin 1.1-3.0 bp (dầu 3.6-7.9,
  khí 25-57); cú nhảy vài giây ngoài lịch tin (7.8k ô): theo thì trượt, fade cú nhảy chỉ một mã có thật ở mid (+0.6-3.5
  bp) nhưng dưới phí 1.6-1.9 bp. Độ trễ 250 ms không phải ràng buộc, spread mới là ràng buộc;
- chiều cú nhảy vài giây đầu ở 8 mốc giờ sàn (mở cửa SHFE / SGE, fix CNY, mở cửa châu Âu, 07:00 NZ, imbalance 15:50 NY,
  settlement; vòng 27 V, 3.9k ô): có thông tin ở mid vượt ngẫu nhiên, nhưng net chỉ như ngẫu nhiên; mốc vàng $10 thường
  (vòng 27 G): không có cú dồn stop nhanh; bạc và bạch kim không có rào cản ở mốc tròn;
- mốc tròn lớn (cùng luật với vàng $50, khoảng cách {1, 5} x 10^k gần 3.4 % giá) ở FX, cặp JPY, chỉ số Mỹ / châu Âu /
  châu Á, dầu, BTC (vòng 28, 22 mã, book gộp IS t -6.55): không đi tiếp ở mã nào ngoài vàng. "Mốc nhỏ của chỉ số đảo
  chiều" mà vòng 28 ghi là sai đo: số mid của R2 tính từ giá khớp stop nên chứa trượt giá mô hình (vòng 29 F);
- fade sau khi phá mốc tròn nhỏ "tươi" ở 4 chỉ số châu Âu chưa dùng (ES35, F40, IT40, STOXX50) và US2000 (vòng 29 F):
  lỗ mọi mã, book IS t -4.96; giá chỉ về +0.7-1.2 bp sau 30 phút so với phí khứ hồi 3.9-4.8 bp; không phí thì power
  tối đa 1.46;
- chiều vài giây đầu ở giờ mở cửa ASX, TSE, A-share / HKEX sáng và chiều, phiên đêm SGE (vòng 29 O, 2.8k ô): có chiều ở
  mid (cụm 00:00 UTC) nhưng 0.4-1.5 bp so với phí 1.4-2 bp; net max t 2.01, p 0.63;
- fix EM và dòng tiền NOK trên 6 mã mới (vòng 30, giả thuyết khai báo từ vòng 25): USDMXN vào fix Banxico có ở PRE
  2007-15 (mid +2.28, t 2.87) nhưng đảo dấu từ 2016 (net IS -2.69, VAL -4.28); USDSGD vào VWAP ABS: không có; đóng cửa
  CFETS của USDCNH có thật ở mid (t 4.6) nhưng net ở spread IC +0.08 bp (cần phí khứ hồi <= 0.70 bp, IC 1.15); EURNOK theo
  chiều Norges Bank: IS +2.33 (t 1.65), VAL -4.99, độ dốc theo cỡ dòng tiền mất ở VAL; giá EURNOK của IC nhảy +2.3 bp
  vào phút 09:00 Oslo rồi về (lỗi giá chào, tính vào phí nếu vào lệnh ở phút đó);
- dữ liệu công khai không phải giá (vòng 31-33, 2026-10-27): bảng tuần MoF / JPX và OI TFX Click 365 của Nhật (OI cho
  biết phía của retail, volume dự báo độ lớn, không dự báo chiều); tổng điều tra chiến lược cộng đồng (mql5, QuantConnect,
  Quantpedia, GitHub, GogoJungle: phá đỉnh / đáy hôm trước của vàng đã suy giảm từ 2016, bình vị thế thứ Sáu sai chiều);
  dòng tiền sàn CoinMetrics (không point-in-time), vị thế Bitfinex, tỉ lệ long/short và OI Binance (đi tiếp, không đảo),
  thanh lý (đi tiếp); lượng nắm giữ GLD / IAU / SLV (= momentum 1 ngày), dự báo CPC cho khí (đã vào giá 24 giờ trước khi
  đăng); net liquidity / TGA / RRP / H.4.1 (Fed tăng tài sản lại ngược chiều, đuôi rút tiền chỉ dương ở VAL); VRP và cú
  sốc vol ngầm định từng tài sản, VVIX / SKEW (= đảo chiều 1 ngày), tương quan ngầm định; chú ý trên Wikipedia / HN (luật
  HN "recession" -> mua US500 3 ngày chỉ ở mức ngẫu nhiên của họ, random IS 0.879); premium Coinbase (chiều ổn định nhưng
  IS t 1.4-1.7, power <= 1.7), kimchi (sai chiều); premium SGE (độ dốc đổi dấu mỗi kỷ), chiều giao hàng Au(T+D); tiền gửi
  SNB (chỉ có ở kỷ sàn 2009-15);
- vòng 34 (2026-10-28): xếp hạng thành viên SHFE (top-20, ghế có tên, khách hàng vs thành viên khác) và kho SHFE / INE
  cho vàng, bạc, dầu, AUD (chiều không ổn định giữa các kỷ); liều tái cân bằng ETF đòn bẩy / ngược (ProShares 2006-24)
  cho chỉ số Mỹ, kim loại, năng lượng, VIX, JP225 (momentum vàng vào settlement không phải dòng ETF đòn bẩy; USTEC liều
  cao IS t 1.38 / VAL 2.78; bạc đảo ở VAL); dòng lệnh quyền chọn BTC Deribit (delta, put, risk reversal, VRP, block,
  gamma dealer) ở 4 giờ-5 ngày; fade đáo hạn thứ Sáu 08:00 UTC có ở VAL (+16.7 bp, t 3.24) nhưng IS t 0.80 vì phí 2017-21;
- vòng 35-36 (2026-10-28): put/call CBOE theo lớp và khối lượng quyền chọn OCC toàn thị trường (dữ liệu miễn phí trộn
  mở / đóng, mua / bán nên dòng lệnh có thông tin bị pha loãng); vị thế tổ chức nước ngoài TAIFEX và dòng tiền TWSE (cùng
  chiều thị trường trong ngày, không dự báo hôm sau); giao dịch currency board HKMA, HIBOR / SHIBOR / CNH HIBOR, RRR
  (HIBOR là tín hiệu lãi suất Mỹ qua tỉ giá neo); tiền Kho bạc trả hộ gia đình (hoàn thuế, An sinh xã hội, EIP; theo
  lịch hay thực trả đều phẳng);
- đăng ký chung các luật chỉ mạnh ở VAL (2026-10-28): 4 luật chọn theo VAL t của vòng 32-36 (fade đáo hạn Deribit,
  USTEC liều ETF đòn bẩy, HN "recession", U3 tiền hộ gia đình) đều âm ở holdout (t -1.12 đến -0.25): luật trượt IS mà
  chỉ đẹp ở VAL không giữ được; đừng gom luật kiểu này để mở holdout nữa;
- vòng 37 (2026-10-29), dòng lệnh bị ép có ngày công bố: ký quỹ / biên độ SHFE và SGE (tăng trước lễ, tăng tuỳ ý, giảm
  sau lễ, OI khách hàng SHFE; ~4.7 lần/năm, không có tác động giá ở kỷ nào; CME không truy cập được); funding vĩnh cửu
  theo mức dự báo quanh mốc 00/08/16 UTC (BTC giảm vào mốc cỡ phần funding, có ở mid nhưng phí IC 2020-21 7-8 bp, từ
  2022 hết funding lớn); stop qua kỷ lục / cực trị nổi bật (ATH, 52 tuần, tuần / tháng / quý / năm trước, biên ngày ra
  tin, MA200) trên chỉ số, kim loại, BTC, FX: đi tiếp ở mid (tuần trước t 4.02) nhưng +1-7 bp so với phí 1-4 bp, power
  <= 2.3 kể cả không phí, kỷ lục vàng không thêm gì cho luật $50; dòng tiền Stock Connect (chỉ cùng chiều trong cùng khung,
  chiều bắc ngừng công bố từ 2024-08; ngày Connect đóng đi ngược giả thuyết);
- vòng 38 (2026-10-29): khối lượng bán khống FINRA hằng ngày của ETF chỉ số / quốc gia / hàng hoá và top-10 thành phần
  (mức, z, thay đổi, ETF trừ rổ, tỉ lệ short-exempt / Rule 201; 408 ô, không họ nào hơn null: đó là market maker hedge
  ngay lập tức); dòng tạo / huỷ chứng chỉ ETF (SPY, DIA, IWM, IVV, EWJ) theo chiều đảo chiều (dòng tiền chạy theo giá);
  bão Đại Tây Dương (mối đe doạ đầu tiên theo dự báo chính thức, hết đe doạ, điều chỉnh dự báo) và gián đoạn cung có
  ngày (Abqaiq, Colonial, Freeport) cho dầu / khí: 2-3 lần/năm, chiều đổi giữa các kỷ, sự cố vào giá ở phút đầu;
- vòng 39 (2026-10-29): lịch roll của chỉ số / ETF hàng hoá (GSCI, BCOM, USO / UNG) trên CFD năng lượng (áp lực chỉ nằm
  ở chênh lệch C2-C1 và đang co lại; XTI / XBR của IC nội suy giữa 2 hợp đồng, không có ngày roll; 12 cửa sổ/năm không
  tới DEMO); vị thế small-trader COT (mức, thay đổi, ngược large spec, cross-section FX) và dòng tiền JPX theo loại nhà
  đầu tư vào JP225 (theo tuần nên không thể LIVE, không ô nào giữ từ IS sang VAL); không có kho sentiment broker miễn
  phí nào tải được mà không cần tài khoản (Dukascopy SWFX, FXCM SSI, Myfxbook, IG, FXSSI, AAII, NAAIM);
- vòng 40 (2026-10-29/30): tin tức mã hoá máy GDELT (tone, Goldstein, độ chú ý, xung đột vùng sản xuất dầu, cặp quốc gia,
  biểu tình) từ sáng hôm sau: đã vào giá trước khi file công bố, tone tiếp diễn sai chiều; vay ký quỹ / bán khống Trung
  Quốc (cắt nợ, tăng đòn bẩy, bán khống tăng vọt) cho HK50, CNH, AUD, vàng, JP225: không tiếp diễn, chỉ số bật tăng;
  luật HK50 bật tăng (hậu kiểm, tôi duyệt đăng ký 2026-10-30) trượt holdout (net +19.0 bp, t 0.74), bỏ hẳn.
- vòng 41 (2026-10-30): nguồn cung trái phiếu chính phủ có lịch (Mỹ mọi kỳ hạn, JGB, Bund; nhượng giá trước đấu giá theo
  DV01, đảo chiều sau, tuần đấu giá dày, bất ngờ kết quả, phiên sáng / chiều ngày đấu giá) cho FX, vàng, chỉ số ở 15 phút-5
  ngày: đảo chiều sau đấu giá chỉ có ở mid 2004-15, kết quả vào giá trong 15 phút; phát hành cổ phiếu Mỹ gộp từ EDGAR
  (IPO, shelf, secondary, tender offer, lock-up, EFFECT, ngày thanh toán, theo tuần): chỉ là chỉ báo thị trường nóng.
- vòng 42 (2026-10-30): công bố lợi nhuận của các mã nặng nhất chỉ số Mỹ ở cấp chỉ số (đi tiếp / đảo chiều sau giờ, mở-
  đóng cửa, phần bù ngày công bố, drift trước công bố, vài phút sau acceptance): không có, đảo chiều tối là tính chất của
  phiên tối 2016-21; nghiệp vụ mua JGB của BoJ (offer-to-cover, cut-off, đổi lịch / khối lượng, bảo vệ YCC) cho USDJPY,
  EURJPY, JP225: thị trường không giao dịch theo kết quả nghiệp vụ.
- vòng 43 (2026-10-30): cú sốc tâm lý (nắng / mây buổi sáng, nhiệt độ, gió ở thành phố có sàn, khói mù Trung Quốc, đội
  tuyển quốc gia thua bóng đá) cho chỉ số và tiền tệ địa phương: đã mất từ sau các mẫu 1982-2004, gió lặng chỉ +1-2 bp ở
  mid, dưới phí; hạ / nâng hạng tín nhiệm quốc gia và lịch xét hạng EU: vài chục lần/năm, chiều đổi giữa các kỷ.
- vòng 44 (2026-10-30): giao dịch nội bộ gộp (Form 4: mua / bán ròng, sau khi giảm, theo cỡ, CEO / CFO, mua cụm) cho chỉ
  số Mỹ ở 1-5 ngày (hiệu ứng ở mức tháng, đổi dấu ở VAL); vị thế CFTC TFF (quỹ đòn bẩy, quản lý tài sản, dealer) ở 1-3 ngày.
- vòng 45 (2026-10-30): gộp toàn bộ đặc trưng không phải giá của vòng 37-44 vào một mô hình khai báo trước (ridge, vote theo
  chiều khai báo): tương quan dự báo ngoài mẫu ~0, bằng null xáo ngày, nên các hiệu ứng lẻ là nhiễu; tỉ lệ bán khống hằng
  ngày TSE (mức, phần dư, thay đổi, luật >= 45 %, qua đêm) và thay đổi báo cáo vị thế bán khống >= 0.5 % cho JP225 ở 1-3 ngày.
- vòng 46 (2026-10-30): áp lực tái cân bằng quỹ 60/40 (ngưỡng, cuối tháng, hồi quy của bài) dựng cả chân trái phiếu Mỹ /
  JGB / Bund, và cắt đòn bẩy risk-parity 2 tài sản, ở 1-3 ngày: độ dốc của bài có thật nhưng chỉ ở ngày hỗn loạn, luật theo
  chiều không kiếm được gì; chân trái phiếu không thêm gì.
- vòng 47 (2026-10-30): cửa sổ mua lại cổ phiếu đo theo từng công ty (đô la XBRL x ngày 8-K 2.02 thật) ở cấp chỉ số
  (mức, mở lại cửa sổ, tách trong mùa báo cáo) ở 1-5 ngày: 94 % là tuần trong quý (= lịch của vòng 23 P4); mùa báo cáo
  dương cả ở US2000 nên là hiệu ứng mùa của cả thị trường, không phải lực mua lại.
- vòng 48 (2026-10-30): dữ liệu mạng Bitcoin (hashrate, hash ribbons, thợ đào đầu hàng, điều chỉnh độ khó, hashprice, tỉ
  lệ phí, nghẽn mempool) cho BTC / ETH ở 1-5 ngày: luật sự kiện quá hiếm, điều chỉnh độ khó đổi chiều giữa các kỷ.
- vòng 49 (2026-10-30): giọng điệu văn bản bài phát biểu Fed / ECB (từ điển, so với giọng thường của người nói, lọc
  blackout / ngày ra tin, chênh Fed - ECB) từ +5 phút đến 5 ngày: thị trường không giao dịch theo giọng điệu; drift Fed ở
  VAL chỉ là năm 2022, đừng đăng ký.
- vòng 50 (2026-10-30): tài sản quỹ thị trường tiền tệ (Fed H.6) cho chỉ số Mỹ, FX, vàng ở 1-3 ngày; dòng tiền quỹ ICI
  chưa test (ici.org chặn bot).
- vòng 53 (2026-10-30): từng lần mint / burn USDT (Omni, Tron) cho BTC / ETH ở 5-60 phút: mint đi sau giá tăng, hiệu ứng
  của Saggu 2022 không còn sau 2018.
- vòng 54 (2026-10-30, CFD cổ phiếu): bán khống sau blackout theo Hartzmark-Solomon (sai chiều ở mã lớn), drift sau công bố
  lợi nhuận mã lớn 1-5 ngày (dưới phí), cửa sổ mua lại theo từng công ty, lệnh mua nội bộ vào lúc mở / đóng cửa giữ 1-5 ngày
  (drift phiên đầu sau ngày nộp có thật ở mid cả IS lẫn VAL nhưng phí khớp lúc mở cửa ăn hết).
- vòng 55 (2026-10-30, CFD cổ phiếu): lệnh mua nội bộ vào trong phiên D+1 (09:35 / 09:45 / 10:00) giữ đến đóng cửa hoặc
  D+2: sau 09:45 chỉ còn +6 bp drift ở VAL, phí ~24 bp; con số CEO / CFO IS của vòng 54 là một lệnh giá penny. Họ lệnh mua
  nội bộ đóng hẳn ở mọi giờ vào, giữ 0-5 ngày.
- vòng 56 (2026-10-30, CFD cổ phiếu): cross-section ngắn hạn của ~200 mã lớn Mỹ: đảo chiều mã không có tin (Chan / DLS /
  Lehmann, phần dư beta SPY hoặc ETF ngành, cửa sổ 1 / 5 ngày, giữ 1-5 ngày, k 3-9, điều kiện vol cao theo Nagel) và đi theo
  mã có tin 8-K 2.02: đảo chiều có ở mid (+3 đến +22 bp) nhưng nằm trong benchmark ngẫu nhiên, phụ thuộc ngày bắt đầu, phí
  khớp đóng cửa ~20-24 bp; không ô nào có net VAL > 0.
- vòng 57 (2026-10-30, CFD cổ phiếu): gap lớn sau công bố lợi nhuận (>= 2 %) vào lệnh 09:45 / 10:00, đi tiếp hoặc fade, giữ
  đến đóng cửa hoặc 1-4 ngày: chân 09:45 -> đóng cửa bằng của mã ngẫu nhiên (không riêng gì lợi nhuận), fade âm mọi năm,
  gap > 8 % quá ít cho power HOLD. Hướng CFD cổ phiếu lớn của IC (vòng 54-57) cạn với dữ liệu miễn phí và giới hạn cố định.
- vòng 58 (2026-10-31, không ràng buộc): carry funding trung tính delta trên Binance (long spot, short perp USDT-M, giữ
  nhiều tuần), BTC + ETH (A3) và top-30 mã (A2): IS +27-29 %/năm, VAL +6-9 % (t_nw ~7), A3 qua holdout đã đăng ký (+1.91
  %/năm, t 5.62) nhưng vượt lãi suất cash trên vốn đã dùng chỉ +0.01 %/năm (t 0.02); A2 trượt. Từ 2025 carry spot-perp =
  lãi suất cash (thành phần lãi 0.01 %/8h của funding); đừng làm lại carry có chân spot. Còn mở: chênh funding perp-perp
  giữa các sàn (thành phần lãi triệt tiêu), vòng 59.
- vòng 59 (2026-10-31): chênh funding perp-perp Binance vs Bybit (dữ liệu research/data/bybit/, 252 mã): IS +10.5 %/năm
  (t 4.65), VAL -0.14 %; gross VAL +4.1 % bằng phí taker. Hyperliquid (từ 2023-05) chưa chạy vì giới hạn API, tối đa RELAXED.
- vòng 60 (2026-10-31): short perp mới niêm yết Binance, hedge BTC, giữ 30 ngày (374 lần niêm yết 2020-24): trung vị
  +18-21 %/lần nhưng trung bình t 1.11 / 1.30 vì squeeze tới -345 %; stop chọn sau khi nhìn chỉ cứu VAL. Đừng làm lại.
- vòng 61 (2026-10-31): nhân tố tuần trên top-40 perp Binance: momentum 28 ngày (IS t 2.37, VAL 1.28, HOLD 2.47), carry
  funding (3.41 / 1.29 / -0.72), X3 = 50/50 (4.32 / 1.51 / HOLD +1.14 %/tuần t 1.16): X3 là ứng viên DEMO đã qua holdout
  (round61_crypto_factors/PREREG_X3_crypto_mom_carry.md, có luật dừng / lên live). Book theo chiều nào cũng cần Sharpe
  năm >= ~2.2 mới đủ power LIVE trên holdout 21 tháng; nhân tố crypto chỉ ~1.
- vòng 59 B2 (2026-10-31): chênh funding Binance vs Hyperliquid (30 mã, research/data/hyperliquid/): kỷ khám phá
  2023-06..2024-12 +16.3 %/năm t 6.81, holdout đã đăng ký +0.74 % t 1.27: trượt; chênh funding giữa sàn bị arbitrage hết.
- vòng 62 (2026-10-31): mốc funding cực lớn của altcoin Binance: nhận funding qua mốc thua (giờ sau mốc ngược phía nhận);
  phía trả trong giờ sau mốc +85 / +50 bp ở nến 1h nhưng toàn bộ nằm trong vài giây đầu (vào T+1 phút: VAL âm). P2 (vào
  T+1 s, thoát T+60 s, aggTrades) VAL mẫu mới +31 bp t 4.87, IS +3 bp t 0.15. Tôi duyệt test kỷ mới cho P2
  (round62_funding_capture/PREREG_P2_post_stamp_1s.md): holdout -5.7 bp t -1.38, trượt, bỏ hẳn. Dữ liệu: research/data/binance/perp_1h, perp_1m_stamps,
  aggtrades_stamps (REST aggTrades chỉ 2 ngày gần nhất, dùng file ngày data.binance.vision).
- vòng 63 (2026-10-31, điều phối nhiều subagent song song theo yêu cầu của tôi, round63_parallel/BRIEF.md): S cổ phiếu Mỹ qua
  đêm / trong phiên khớp đấu giá (không có; stooq cấm bot), V bán biến động Deribit có hedge (không có), C cross-section
  trong ngày perp (không có), D thông báo Binance (robots cấm /bapi/), M hiệu ứng cũ theo phí CME (không có), B hồi quy basis
  perp-spot: phía perp rẻ hơn spot >100 bp (long perp / short spot vay margin) là ứng viên DEMO đã qua holdout (+213.5 bp, t 14.4);
  vào trễ 5 phút trên nến 1m holdout vẫn +222.8 bp t 13.9 (BM); lên live chỉ còn phụ thuộc vay được coin để short spot: cần demo trên tài
  khoản Binance margin. 2026-11-01 tôi duyệt: bot demo giấy app/basis_b_runner.py (docs/basis-b-demo.md, không đặt lệnh) ghi tín hiệu,
  sổ lệnh, lượng coin vay được và lãi vay mỗi giờ; trạng thái dừng / nâng hạng ở màn Nghiên cứu (research/registry.yaml). Không có gì ở R (đấu giá trái phiếu), U (mở khoá token), O (metrics Binance), P (Polymarket), X (roll VIX),
  W (Kalshi thời tiết), A (A-share chạm trần), BX (hedge B bằng perp Bybit: spot mới là bên dịch chuyển), BY (B trên Bybit: nến 1h Bybit mở = đóng trước).
  Nguồn cần tôi duyệt trước khi dùng lại: defillama-datasets.llama.fi (U), OHLCVault (A). Ý tưởng còn lại: round63_parallel/I/IDEAS_I.md.

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
Sau vòng 22: danh sách ý tưởng không cần tôi quyết đã cạn (TRIAGE_R). Vòng 23 (tài liệu và dòng tiền mới nhất) cũng
không có ứng viên live. Vòng 24 (điều kiện nới, tôi cho phép) cũng không có live: nới ngưỡng không tạo ra cơ chế mới,
chỉ F3 (lọc của E1) qua được holdout ở bậc RELAXED, và đang yếu đi ở 2026. Vòng 25 (bậc gốc, không RELAXED): thông tin
công khai đã nằm trong giá trước khi bot kịp hành động, kể cả phần bất ngờ đoán trước được của tin vĩ mô; tài liệu cũ đã
map hết; và theo STREAM_A, không quyết định nào đang chờ có kỳ vọng ra ứng viên live (cao nhất 3-5 %). Vòng 26: thực thi
ở mức tick (straddle khi ra tin, fade / theo cú nhảy) không cứu được kênh thông tin; họ "thông tin công khai" đã đóng ở
mọi thời điểm (trước, trong, sau tin, và ngoài lịch tin). Vòng 27-28: cơ chế mới duy nhất có bằng chứng dương ở cả bốn
kỷ là cú dồn stop khi vàng phá mốc $50 "tươi" (qua holdout bậc DEMO 2026-10-18, power 1.40), chỉ có ở vàng. Vòng 29:
fade mốc tròn ở chỉ số và giờ mở cửa châu Á đều dưới phí. Đã tạm dừng sau vòng 29 theo yêu cầu của tôi. Vòng 30 (tôi
duyệt dữ liệu 6 mã FX mới): mọi giả thuyết khai báo trước đều trượt, fix Banxico đảo dấu sau 2015, dòng tiền NOK suy
giảm như mọi dòng tiền khác, đóng cửa CFETS dưới phí IC. Luật vàng mốc $50 đã chạy demo (2026-10-18). Vòng 31-33 (tôi
cho tìm nguồn khác, 2026-10-27): 12 nguồn công khai không phải giá, không có ứng viên; thông tin có thật trong vài nguồn
(OI retail Nhật, dự báo thời tiết, chen chúc retail trên Binance) nhưng hoặc đã vào giá trước khi công bố, hoặc chỉ dự
báo độ lớn, hoặc chỉ 0.03-0.1 sd mỗi lệnh. Phiên mới nên bắt
đầu từ quyết định của tôi (xem "Hướng cần tôi quyết" và mục "State after round 30" của báo cáo vòng 30); nếu tôi chưa
quyết gì mà vẫn yêu cầu chạy tiếp, chỉ mở hướng thật sự mới về cơ chế hoặc cách thực thi, khai báo trước toàn bộ,
không quét lại.
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
dữ liệu ngoài trả phí (OI/gamma Deribit, AUM quỹ ETF đòn bẩy; premium SGE hoá ra miễn phí và đã test ở vòng 33), chạy demo cho các ứng viên DEMO, và có
cho phép tính net IS của chỉ số theo phí hiện tại hay không (là đổi ngưỡng, chưa áp dụng). Dữ liệu quyền chọn FX công khai của DTCC chỉ tải được từ 2024-12 (trước đó nằm ở Deep
Archive), tức là trùng holdout. Thêm từ vòng 23: chạy demo 1 lệnh/năm cho vàng quanh Giáng sinh hay test một luật cuối
năm vàng / USD khai báo trước trên dữ liệu sau 2026-09-24; các cơ chế chỉ có từ 2024 (dòng tiền ETF BTC/ETH spot vào
NAV 16:00 ET, BTC vào khung benchmark NY, NISA mới bán yên đầu tháng, gamma 0DTE) cần luật kỷ mới hoặc dữ liệu mới; dữ
liệu trái phiếu (lợi suất 10 năm / T-note) cho chân trái phiếu của tái cân bằng; bài trả phí Ewald et al. 2025 (giờ
long/short trong ngày của Brent) và truy cập SSRN. Thêm từ vòng 24: chạy demo F3 (và E1) theo luật dừng / lên live
trong round24_relaxed/PREREG_DRAFT_C_ecb_window_variants.md (cần cBot). Dữ liệu sau 2026-09-24: tôi đã chọn tải
(Dukascopy); F3 / E1 có log forward đã đăng ký (round24_relaxed/PREREG_R24_forward.md, chạy lại
prereg_code/fwd_r24.py.txt với ngày mới hơn, nối kết quả bên dưới), lát đầu 25/09-14/10 quá ít lệnh. Từ 2026-10-16 cũng có log forward cho B3 (long EURJPY vào fix ngày NAV
NISA) và A1 (BTCUSD 15-16 NY theo dòng tiền ETF hôm trước), hai luật trượt DISCOVERY nhưng mạnh ở TEST
(round24_relaxed/PREREG_R24_forward_B3_A1.md; chạy lại fwd_b3a1.py.txt khi có capture Farside mới, mốc B3 n 30 /
A1 n 250, đạt khi FWD t >= 2.0); lát đầu B3 n 2 +10.9 bp, A1 n 12 -7.3 bp. Lát 2 của F3 / E1 (đến 16/10, vòng 25): F3
vẫn 2 lệnh, E1 16 lệnh net -2.27 bp. Lát 3 (đến 26/10, vòng 31): F3 3 lệnh net -3.47 bp, HOLD + FWD +1.86 (t 1.96);
E1 22 lệnh net -1.31. Lát 4 (đến 28/10, vòng 37): F3 5 lệnh net -5.03, HOLD + FWD +1.71 (t 1.82); E1 HOLD + FWD +0.51
(t 0.82). Chạy fwd_r24.py cần PYTHONPATH=. (clib gọi research.swing); Dukascopy hay rơi ngày EURUSD vì
lỗi kết nối: kiểm số ngày từng mã cả bid lẫn ask rồi tải lại vào thư mục mới. Thêm từ vòng 31-33 (giá trị = khả năng ra
ứng viên live, chi tiết trong báo cáo từng vòng): order / position book OANDA cần tài khoản (DEMO ~3-5 %, LIVE ~1 %),
vị thế retail ròng OANDA Japan / Gaitame / FFAJ (~1-2 %), dòng tiền crypto point-in-time và OI / thanh lý gộp sàn trả phí
(~1-2 %), Google Trends / SVI (LIVE ~1 %, DEMO ~5 %), CME CVOL, OI quyền chọn theo strike, giá GBTC trước 2024 (chỉ để
tham khảo), premium vàng Ấn Độ (đăng nhập WGC). Thêm từ vòng 34: OI / Greeks Deribit trả phí (~2 %); xếp hạng CFFEX cho HK50 (~1 %). Thêm từ vòng 35-36: dữ liệu
quyền chọn open-close / open-buy trả phí (~2-3 %), lịch sử TAIFEX 2008-18 hoặc tài khoản KRX (~1 %), thử lại API HKMA từ
mạng khác, quy mô OMO của PBoC (Wind / CEIC hoặc cho phép dùng pbc.gov.cn dù robots.txt cấm). Tạm dừng sau vòng 36 theo
yêu cầu của tôi (2026-10-28). Bản đăng ký chung (joint_prereg_2026-10/PREREG_JOINT.md, tôi duyệt đổi ngưỡng, bỏ L3 /
V1, U3 trên BTC) đã mở holdout một lần ngày 2026-10-28: fade đáo hạn Deribit, USTEC liều ETF đòn bẩy cao, HN "recession"
-> mua US500, U3 tiền hộ gia đình -> BTC đều trượt và đều âm ở holdout; bỏ hẳn, không log forward, không đăng ký lại
(premium Coinbase, L3, V1 không mở nhưng cũng không còn là hướng đi). Ngày 2026-10-29 tôi yêu cầu research tiếp đến khi
có bot live; vòng 37 không có ứng viên. Thêm từ vòng 37: lịch sử ký quỹ từng sản phẩm CME (DataMine / FOIA; LIVE ~1 %,
DEMO ~3 %), dòng tiền Stock Connect trong ngày trả phí (~1 % / 3 %), funding BitMEX 2016-19 trả phí (< 1 %).
Vòng 38 không có ứng viên. Thêm từ vòng 38: EIA API key cho sự cố nhà máy hạt nhân -> khí (DEMO ~2 %), danh sách Rule
201 / threshold của nasdaqtrader (tài khoản hoặc feed trả phí; DEMO ~2 %), shares outstanding hằng ngày trả phí của QQQ
/ USO / UNG, PDF shut-in BSEE (< 1 % mỗi cái).
Vòng 39 không có ứng viên. Thêm từ vòng 39: tài khoản demo JForex của Dukascopy để lấy lịch sử SWFX sentiment 30 phút
(DEMO ~3 %, LIVE ~1 %), SSI trả phí của FXCM (~3 % / 1 %), sàn có CFD / futures năng lượng theo từng hợp đồng để giao
dịch chênh lệch C2-C1 qua kỳ roll (DEMO ~1-2 %).
Vòng 40 không có ứng viên; ngày 2026-10-30 tôi duyệt đăng ký luật HK50 bật tăng sau ngày cắt nợ ký quỹ, đã mở holdout
một lần và trượt. Thêm từ vòng 40: lịch sử GDELT 2.0 15 phút (BigQuery cần tài khoản Google; < 1 %), sentiment tin tức
trả phí RavenPack / MarketPsych (~2 %), phân bố tỉ lệ ký quỹ và khối lượng thanh lý cưỡng bức Wind / iFinD (~2 %).
Vòng 41 không có ứng viên. Thêm từ vòng 41: when-issued yields trả phí, dữ liệu phát hành Dealogic / SDC, crawl từng
hồ sơ EDGAR (< 1 % / ~1 % mỗi cái); sàn không có commission FX 0.6 bp lại thêm một hiệu ứng (đảo chiều sau đấu giá, ~2 %).
Vòng 42 không có ứng viên. Thêm từ vòng 42: CFD cổ phiếu IC (MT5) để giao dịch chính mã nặng sau công bố (LIVE ~3-5 %,
DEMO ~25 %: vẫn là quyết định giá trị nhất), futures chỉ số sau giờ rẻ hơn (~3 %), tick JGB futures / OIS yên trả phí (~1 %).
Vòng 43 không có ứng viên. Thêm từ vòng 43: PM2.5 theo giờ trả phí / cần đăng ký, lịch sử xếp hạng XBRL 17g-7(b) của các
hãng, CFD chỉ số / trái phiếu EM (~1-2 % DEMO). Không dùng lại countryeconomy.com (robots.txt cấm ClaudeBot đích danh).
Vòng 44 không có ứng viên. Thêm từ vòng 44: CFD cổ phiếu (MT5) theo lệnh mua "cơ hội" của người nội bộ (LIVE ~2-3 %, DEMO
~10 %), họ hàng hoá "fade thay đổi tuần của managed money" khai báo mới (DEMO ~2 %). cftc.gov chặn ClaudeBot trong robots.txt:
không tải từ đó nữa (vòng 39 D đã tải trước khi biết), dùng mirror Hugging Face nếu cần.
Vòng 45 không có ứng viên. Thêm từ vòng 45: J-Quants (gói trả phí) / QUICK cho tách bán khống có / không giới hạn giá 2008-24
(DEMO ~1-2 %). Mô hình gộp cho thấy không sàn rẻ hơn nào cứu được các nguồn miễn phí của vòng 37-44 (power HOLD < 1 kể cả ở mid).
Vòng 46 không có ứng viên. Thêm từ vòng 46: sàn có futures / CFD trái phiếu (LIVE < 1 %), lịch sử ES1 / TY1 1997-2015 trả phí
(DEMO ~2 %). data-api.ecb.europa.eu chặn ClaudeBot trong robots.txt: không dùng.
Vòng 47 không có ứng viên. Thêm từ vòng 47: CFD cổ phiếu (MT5) cho các mã mua lại lớn trong cửa sổ mở vs blackout (LIVE ~2-3 %,
DEMO ~10 %); dòng lệnh mua lại trả phí của sell-side (< 1 % / ~2 %).
Vòng 48 không có ứng viên. Thêm từ vòng 48: dòng coin của thợ đào point-in-time trả phí (CryptoQuant / Glassnode; < 1 % / ~1 %).
Vòng 49 không có ứng viên. Thêm từ vòng 49: giờ tin wire trả phí cho bài phát biểu, futures trái phiếu trong ngày, điểm giọng
điệu LLM / FinBERT thiết kế chỉ trên 2010-21 (mỗi cái LIVE < 1 %, DEMO ~1-2 %).
Vòng 50 không có ứng viên. Thêm từ vòng 50: tôi tải tay file dòng tiền tuần của ICI bằng trình duyệt (LIVE < 1 %, DEMO ~1-2 %).
www.ici.org nằm sau bot-wall Akamai (403 cả robots.txt): không tải, không thử lại bằng UA trình duyệt.
Vòng 51 không test được. Thêm từ vòng 51: đăng ký tài khoản IBA (ice.com report 179) để có giá từng vòng và khối lượng từng
phiên đấu giá vàng LBMA từ ~2015 (LIVE < 5 %, DEMO ~5 %, chỉ tốn một lần đăng ký). prices.lbma.org.uk sau Cloudflare 403.
Vòng 52 (rà tài liệu 2018-24): không còn hướng miễn phí nào có khả năng ra live >= 2 %. Thêm từ vòng 52: token RPC archive
Ethereum để lấy giờ mint USDT / USDC (LIVE ~2.5 %, DEMO ~10 %). export.arxiv.org cấm mọi bot trong robots.txt; apilist.tronscanapi.com
cấm ClaudeBot.
Vòng 53 không có ứng viên; token Ethereum giảm giá trị còn LIVE < 0.5 %, DEMO ~1-2 %. Sau bản rà vòng 52 và vòng 53, không còn
hướng miễn phí nào không cần tôi quyết có khả năng ra live >= 1 %: vòng tiếp theo nên bắt đầu từ một quyết định trong mục này
(CFD cổ phiếu MT5 vẫn giá trị nhất).
Ngày 2026-10-30 tôi duyệt hướng CFD cổ phiếu IC MT5 (research, chưa mở tài khoản / bot). Vòng 54 không có ứng viên. Thêm từ
vòng 54: đăng nhập demo IC MT5 để đo spread thật 09:30-09:45 của CFD cổ phiếu Mỹ (quyết định mọi luật vào lệnh lúc mở cửa),
sàn cổ phiếu không thu commission theo cổ phiếu (DEMO ~3 %), cổ phiếu nhỏ (IC / Dukascopy không có; LIVE ~1 %).
Vòng 55 không có ứng viên; đăng nhập demo IC MT5 để đo spread mở cửa giảm giá trị (commission ~12 bp đã lớn hơn drift còn lại;
DEMO < 2 %). Luật cổ phiếu ở IC cần > ~20 bp mỗi lệnh khi khớp lúc đóng cửa hoặc giữa phiên.
Vòng 56 không có ứng viên. Sàn không thu commission theo cổ phiếu giảm còn DEMO < 1 % cho cross-section.
Vòng 57 không có ứng viên. Sau 4 vòng cổ phiếu (54-57), không còn hướng miễn phí nào không cần tôi quyết có khả năng ra
live >= 1 %: vòng tiếp theo nên bắt đầu từ một quyết định trong mục này.
web.archive.org đã gắn cờ IP máy này là bot sau 6 request (vòng 37 M): đừng dùng làm nguồn tải hàng loạt. Thêm từ vòng 25 (STREAM_A.md xếp hạng theo khả năng ra ứng viên live): đã làm ở vòng 30 phần kéo
tick IC + Dukascopy cho USDCNH, USDMXN, USDSGD, EURNOK, USDNOK, EURSEK (không ra ứng viên). Còn lại: có chấp nhận nền
tảng khác cTrader không (cổ phiếu CFD của IC chỉ có trên MT5), trước khi dựng engine cổ phiếu từ dữ liệu miễn phí
(Dukascopy US stock CFD 2017-24 + SEC EDGAR; luật bán sau khi hết blackout lợi nhuận, live ~3-5 %); có log forward luật
mốc $10 của vàng (STREAM_C.md) trên dữ liệu sau 2026-09-24 không (demo là tối đa). Luật vàng mốc $50 đã chạy demo từ
2026-10-18 (xem "Đang chạy trên VPS"). Việc định kỳ không cần tôi quyết: dựng lại lịch tin USD của bot vàng trước
2026-12-11 (gold_level_cbot/calendar/, rồi research.tools.usd_high_calendar_seed và deploy; quá hạn thì bot ngừng đặt
lệnh); chạy lại hai log forward khi có ngày mới (B3 / A1 cần capture Farside trên Internet Archive, ngày 18/10 bị 429
suốt). Không khuyến nghị: cross
FX, EM khác (PLN, CZK, HUF, ZAR, TRY, HKD), softs, đổi sàn chỉ để research, dữ liệu trả phí, tick IC cho chỉ số châu
Âu / châu Á (vòng 28-29: hiệu ứng mốc tròn và giờ mở cửa đều dưới phí). Luật cuối năm
tháng 12/2026 và V Sydney sau 2024 cần đăng ký riêng trước khi xem; hướng venue phí thấp (vòng 16) giờ giá trị thấp hơn vì V Sydney chỉ
có từ ~2011.

Điều kiện nới tôi đã cho phép ở vòng 24 (round24_relaxed/BRIEF.md), dùng lại được nếu tôi cho phép tiếp:
- Bậc RELAXED (chỉ demo, không bao giờ live nếu chưa đạt bậc LIVE hoặc luật lên live đã đăng ký): net t >= 1.5 ở kỷ
  thiết kế; net > 0 với t >= 1.0 ở kỷ kiểm; dương khi spread x1.5 và trễ 1 phút; thắng >= 80 % lệnh ngẫu nhiên;
  power theo cỡ ở kỷ kiểm >= 1.5; có cơ chế kinh tế. Được mở holdout một lần sau khi có PREREG_DRAFT.
- Cơ chế chỉ có từ 2023-24: DISCOVERY = từ khi có..2025-06-30, TEST = 2025-07-01..ngày mới nhất; mỗi luật xem TEST
  một lần.
- Được tải dữ liệu (Dukascopy, bảng dòng tiền công khai); luật mùa vụ / dòng tiền khai báo trước được giữ đến 20
  ngày giao dịch (tính swap).
- Không nới: chiều lệnh từ cơ chế / nguồn, khai báo trước số liệu, phí thực thi được, benchmark ngẫu nhiên theo số ô.

Đang chạy trên VPS (đã có cBot, backtest cTrader và deploy; preset ở app/cbot_presets.py):
- C3 Gotobi JPY basket (cBot/GotobiBot.cs), thuật toán duy nhất đang chạy: USDJPY, EURJPY, GBPJPY, mỗi cặp một
  container, chart m15. Vào lệnh theo lịch gotobi quanh fix Tokyo, stop 3 x ATR20(H1), bỏ các ngày gotobi không có
  fix (ngày lễ Nhật, 31/12). Đạt holdout 2025-26 (R +0.042, t 2.9) và kỷ Dukascopy 2004-2015 (R +0.038, t 4.8).
- EcbWindowBot (cBot/EcbWindowBot.cs, deploy 2026-10-16, PR #16): F3 chạy live 0.01 lot (cbot-live-live-eurusd-ecb-f3),
  E1 chạy demo 0.1 lot (cbot-demo-demo-eurusd-ecb-e1, ghi cờ USD-TOP để chấm cả F3 trên demo). Chấm theo luật dừng /
  lên live trong round24_relaxed/PREREG_DRAFT_C_ecb_window_variants.md; đừng tối ưu lại. 3 bot Gotobi demo đã xoá 10-16.
- GoldLevelBot (cBot/GoldLevelBot.cs, deploy 2026-10-18, PR #18): luật vàng mốc $50 chạy demo 0.01 lot
  (cbot-demo-demo-xauusd-levels-gold50), stop bảo vệ $100 ngoài luật. Log từng lệnh kèm giá theo mô hình ở
  /home/forge/ctrader/ctrader_data/<BotId>_trades.csv trên VPS; chấm bằng `python -m research.tools.gold_demo_check`
  (luật dừng / lên live trong PREREG_G_gold_round50_cascade.md); đừng tối ưu lại. Lịch tin trong
  cBot/seeds/usd_high_calendar.csv hiệu lực tới 2026-12-11.
- Ứng viên DEMO chờ tôi quyết (có luật dừng / lên live trong file đăng ký; đừng tối ưu lại; E1 / F3 giờ đã chạy, xem trên):
  vàng theo chiều ngày vào settlement COMEX ngày biến động top 10 %
  (round12_flows_execution/PREREG_L_gold_settlement_bigday.md); bán EURUSD 11:00-13:00 London mỗi ngày
  (round13_structural/PREREG_M_eurusd_midday.md). Ứng viên bậc RELAXED đã đạt holdout (vòng 24): F3, bán EURUSD
  11:00-13:00 London chỉ ngày USD mạnh từ tối hôm trước (round24_relaxed/PREREG_R24_relaxed_hold.md: holdout +2.00
  bp/lệnh, t 2.16, ~65 lệnh/năm; năm 2026 -0.91; forward 25/09-14/10: 2 lệnh, -9.2 bp; holdout + forward t 1.89). USD giảm ngày FOMC đã trượt holdout (-34.6 bp, t -2.36): bỏ.
  Ứng viên DEMO mới đã qua holdout (2026-10-18), nay đang chạy demo: vàng đi tiếp sau khi phá mốc $50 "tươi", stop chờ ở mốc + nửa
  spread, thoát sau 30 phút (round27_levels_opens/PREREG_G_gold_round50_cascade.md, có luật dừng / lên live): IS +5.99
  bp (t 2.66), VAL +3.27 (t 1.81), 9/9 năm dương, PRE (đã sửa lỗi nhìn trước một nến ở vòng 28) +3.90 (t 2.50);
  holdout n 228, net +2.87 bp (t 1.43), x1.5 +2.71, +1 phút +1.81, 2025 +0.80, 2026 +5.43. Không lên live được vì
  power 1.40 (Sharpe/lệnh 0.093). Cơ chế không có ở mã nào khác (vòng 28) nên không gộp được book. Số lệnh holdout gấp
  đôi dự kiến vì giá vàng tăng gấp đôi (mốc cố định theo đô la dày hơn theo %); 5 lệnh lớn nhất chiếm 518 / 655 bp.
  Đừng tối ưu lại (mốc $100, chỉ chiều giảm, mốc theo % giá đều là chọn sau khi xem holdout).
  Bản nháp, không khuyến nghị: vàng long quanh Giáng sinh (round23_recent/PREREG_DRAFT_N_gold_christmas.md) và luật
  cuối năm vàng + USD (round24_relaxed/PREREG_DRAFT_B_turn_of_year.md), 1 lệnh/năm, PRE và VAL yếu.
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
lệnh trễ 1 phút cho luật momentum vào một mốc giá. Thêm từ vòng 25: spread IC gấp đôi trong phút cuối trước giờ ra tin
(vào lệnh sớm ít nhất 2 phút); lịch ForexFactory (Hugging Face Ehsanrs2/Forex_Factory_Calendar) mất giờ ở các dòng cùng
khung giờ (nằm ở 00:00 giờ Tehran) và nhãn +04:30 sai ở mùa hè 2023-24, nên lấy giờ từ lịch chính thức và kiểm bằng
đỉnh hoạt động ở phút ra tin; cột "Previous" là số đã sửa (nhìn trước), dùng số công bố lần đầu; Dukascopy có thể mất
nguyên ngày vì HTTP 503 khi server bận: kiểm từng ngày forward và tải lại vào thư mục mới trước khi chạy log đã đăng ký;
mỗi phiên chỉ có ~200 lượt web search dùng chung và OpenAlex miễn phí hết hạn mức trong ngày, nên chia ngân sách cho các
nhánh tài liệu; không bao giờ đưa email của tôi vào request (tham số mailto / contact).

Cách chạy một vòng (đã dùng từ vòng 10; từ vòng 63 tôi muốn phiên chính làm điều phối, giao nhiều giả thuyết cho subagent chạy song song, brief mẫu round63_parallel/BRIEF.md): viết BRIEF.md cho vòng (copy round12_flows_execution/BRIEF.md, sửa phần
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
