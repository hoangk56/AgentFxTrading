# Daily check 2026-09-24 (GMT+7), đến 21:41

> Chỉ đọc: không sửa code, DB hay VPS. Collector: `.claude/skills/daily-audit/scripts/collect_day.py today`.
> **Ghi đè bản chạy lúc 19:23 VN.** Bản này tính cả phần 19:23 → 21:41 VN (deploy PR #49, các lệnh đóng tay 19:36 và 19:58, lỗi `/portfolio/status`). Digest thu lúc 14:41 UTC. VPS HEAD và reflog kiểm lại lúc 14:49 UTC, không đổi.
>
> **Cập nhật sau phản hồi của user:** #2 là cố ý (tài khoản demo). #8: user xác nhận đã đóng tay 3 lệnh để restart container. #7 đã sửa và deploy lên VPS (PR #51, `09d12ef`, restart service 22:36 VN).
>
> Sau thời điểm thu thập (không audit): 82 US30 chạm SL −13,89 $, 83 USTEC AI Close −8,13 $, 84 EURJPY chạm SL −8,59 $, 85 XAUUSD +0,52 $. Không còn lệnh mở.

## 0. Phạm vi

| Mục | Giá trị |
|---|---|
| Cửa sổ | 2026-09-24 00:00–21:41 GMT+7 = 2026-09-23 17:00 → 2026-09-24 14:41 UTC |
| Code | VPS `5d7140f` · local `9b61a49` · origin/main `a500c82` (chỉ thêm skill daily-audit). Deploy trong ngày: `deef554` 00:37, `b220d1f` 01:25, `a8e6686` 01:35, `1f1f6a5` 12:36, `d3109cd` 13:31, `fd24478` 16:28, `7cf06d4` 17:51, `9b61a49` 18:08, `5d7140f` 19:42 VN. `.algo`: AiAgentBot/Judas 16:33, FlowRsiBot 19:44 VN |
| Lệnh | 41 đóng, 44 mở mới (+2 lệnh ngoài sổ, xem #1), 3 còn mở lúc 21:41 |
| P&L | DB: **−58,63 $** (41 lệnh đóng). Balance 1718,77 → 1646,61 = **−72,16 $** = −58,63 + (−13,53 của 2 lệnh ngoài sổ), khớp đến cent. Không có partial trên lệnh còn mở |
| Tài khoản | demo-10115236: balance 1646,61, equity 1636,98 (21:41 VN); **ledger (balance − Σpnl) = 1986,47** = 2000 − 13,53, không đổi so với lúc 19:23 |
| Test local | pytest `9b61a49` (checkout): 660 passed, 1 warning. pytest `5d7140f` (bản export `git archive`): 672 passed, 1 warning. `git status`: chỉ `.claude/` chưa track |

## 1. Tóm tắt

- **2 báo cáo mở lệnh bị rơi** (14:15 và 14:45 VN, không trùng restart): 2 lệnh chạy ngoài sổ, −13,53 $. Giải thích đúng khoản lệch ledger. Sau 19:23 không mất thêm báo cáo nào. SQL bù sổ ở §2.1.
- Hạn mức daily loss ở mức 10× (2000/1000/600/600/300) là **cố ý** vì đây là tài khoản demo (user xác nhận). Không còn là vấn đề.
- **Lot tối thiểu làm vượt % rủi ro, cả ở bot TMS**: lệnh đang mở #83 ustec-newyork chịu rủi ro 3,6× mức 0,2% cấu hình; #82 us30 FlowRSI 1,7×. AiAgentBot kẹp lên lot tối thiểu giống FlowRSI.
- **Mới, đã sửa và deploy (PR #51):** `/portfolio/status` luôn lỗi trên Postgres (`LIKE 'EUR%'` + tham số → psycopg2 `IndexError`) và trả 200 với dữ liệu rỗng. Chưa có caller nào trong hệ thống.
- 51, 70, 72 (19:36 VN) do user đóng tay trên cTrader để restart container; 3 FLAG FILL_FAR_FROM_LEVEL là nhiễu. Ghi chú nhỏ: FlowRSI dùng chung nhãn "Closed (Take Profit Early)" cho cả lệnh đóng ngoài bot, AI CLOSE_ALL và circuit breaker.
- Sổ sách còn lại khớp: 3 lệnh mở trong DB đều có telemetry live (tuổi ≤ 6 s). Không có ctrader_id trùng, không có lệnh ma. Backup 03:00 UTC OK. Watchdog không phải tự khởi động lại bot nào.

| # | Mức | Vấn đề | Bằng chứng chính | Code (`5d7140f`) | Trạng thái |
|---|---|---|---|---|---|
| 1 | P1 | 2 báo cáo open bị rơi, 2 lệnh ngoài sổ (−13,53 $) | `#675558107` 14:15:16 VN, `#675569508` 14:45:37 VN "Failed to report position open"; "Close position ignored" 15:13:48, 16:00:35 VN | `cBot/FlowRsiBot.cs:2978-3000`, `cBot/AiAgentBot.cs:1993`, `app/portfolio.py:376-381` | đã biết (2026-09-24-audit.md §2.3); không tái diễn sau 14:45 |
| 2 | — | Daily loss limit nâng 10× (2000/1000/600/600/300) | "Risk limits updated" 13:34:08–13:34:15 VN; vẫn hiệu lực lúc 21:41 | mặc định `app/risk_limits.py:22-26` (200/100/60/60/30) | **cố ý** (tài khoản demo, user xác nhận), không phải lỗi |
| 3 | P1 | Lot tối thiểu vượt % rủi ro, nay thấy cả ở AiAgentBot | #83 −11,90 $ tại SL = 0,72% (cấu hình 0,2%); #82 −13,88 $ = 0,84% (0,5%); id 62 de40-london lỗ −12,01 $ ≈ 3,5× | `cBot/AiAgentBot.cs:2357-2358`, `cBot/FlowRsiBot.cs:1789` | đã biết (audit §3.3, chỉ nêu FlowRSI); phần AiAgentBot mới |
| 4 | P1 | FlowRSI BUY chỉ số ngược xu hướng | 12 lệnh index BUY, 3 thắng, −58,73 $ (gồm lệnh ngoài sổ) | lock H1 không giới hạn tuổi | đã biết (audit §2.1, §9.4) |
| 5 | P2 | Cụm lệnh tương quan: 4 SELL JPY-cross trong nến 14:45 VN | id 64, 65, 66 + `#675569508`: −24,32 $ | không có giới hạn exposure | đã biết (audit §2.2) |
| 6 | P2 | VPS quá tải (hiện tại) | load 28,6/30,7/27,1 trên 8 vCPU (21:49 VN); CPU pressure `some avg60=50.95`; RAM available 902 MB | hạ tầng | tái phát (audit §3.4) |
| 7 | P3 | `/portfolio/status` luôn lỗi trên Postgres | ERROR 20:05:36 VN; `mogrify` tái hiện `IndexError` với `()` và `('demo-10115236',)` | `app/portfolio.py:627-648`, `app/db.py:34-83` | **mới**, đã sửa và deploy (PR #51, `09d12ef`, 22:36 VN) |
| 8 | P3 | Nhãn "Closed (Take Profit Early)" cho lệnh đóng ngoài bot, AI CLOSE_ALL và circuit breaker | 51, 70, 72 đóng 19:36:52–59 VN (FILL_FAR_FROM_LEVEL); lệnh dashboard 29fa1f67/ed8fba65/58af7491 hết hạn | `cBot/FlowRsiBot.cs:2899`, `:1545`, `:2191` | user đã xác nhận 3 lệnh là đóng tay để restart container; còn lại ghi chú về nhãn, tuỳ chọn |
| 9 | P3 | Snapshot `/trade` của FlowRSI vẫn đọc nến `Count − 1` | `563fca4` chỉ đổi `EvaluateStrategySignals` sang `ClosedBarIndex()` | `cBot/FlowRsiBot.cs:1211-1233` | **mới**, nghi ngờ ảnh hưởng nhỏ |
| 10 | P3 | `RestoreInitialSlDistances` không retry | 13:25:46–13:26:02 VN, 6 bot timeout | — | đã sửa trong ngày (`ea74949`, deploy 19:42 VN); sau restart 19:47–19:50 VN không còn lỗi |
| 11 | P3 | `Asset 'USD' not found` ở ustec-newyork | 13:25:06 VN, 1 lần, ngay sau reboot | `cBot/AiAgentBot.cs:598` | đã biết (bản 19:23), không tái diễn |

## 2. Chi tiết

### 1. Hai báo cáo mở lệnh bị rơi, hai lệnh chạy ngoài sổ

- **Bằng chứng:**

  | ctrader_id | Bot | Mở (VN) | Báo cáo open | Đóng (VN) | PnL bot báo |
  |---|---|---|---|---|---|
  | 675558107 | us30-all-flowrsi | 14:15:14 Buy 0.10 @ 51404.8, SL 51290.14, TP 51571.25 | 14:15:16 `[Portfolio Hub] Failed to report position open: An error occurred while sending the request.` | 15:13:48 | −11,62 |
  | 675569508 | eurjpy-london | 14:45:37 Sell 0.01, SL 28.6p, TP 38.1p | 14:45:37 `[Portfolio] Failed to report position open: …` | 16:00:35 | −1,91 |

  - −11,62 − 1,91 = −13,53 = 2000 − 1986,47. Ledger đứng yên ở 1986,47 từ 19:23 đến 21:41 VN.
  - Không trùng lần restart nào (00:38, 12:37, 13:20 reboot, 13:32, 16:31, 17:52, 18:09, 19:46 VN).
  - Cùng kiểu lỗi ở đường `/trade`: 12 dòng `[AI Agent Retry] … Unable to read data from the transport connection: Connection reset by peer` trong 7 bot FlowRSI; chỉ 1/12 gần một lần restart. Ví dụ eurjpy-all-flowrsi lúc 20:15:03 và 21:15:00 VN. Đường `/trade` được retry từ `734cdbb` cứu; đường báo cáo thì không.
- **Nguyên nhân:**
  - Bot gửi báo cáo kiểu fire-and-forget, không retry, chỉ log `ex.Message` (`FlowRsiBot.cs:2978-3000`, `AiAgentBot.cs:1993`).
  - Server bỏ báo cáo close khi không có dòng mang ctrader_id đó (`app/portfolio.py:376-381`).
  - **Nghi ngờ mạnh** về điều kiện kích hoạt: uvicorn chạy keep-alive mặc định 5 s, còn HttpClient .NET giữ socket nhàn rỗi lâu hơn. Xác nhận bằng cách log `ex.InnerException`, hoặc tăng `--timeout-keep-alive` rồi xem lỗi reset còn không.
- **Ảnh hưởng:** daily loss, leaderboard và dashboard thiếu 13,53 $. Trong lúc 2 lệnh mở, server không tính chúng vào rủi ro mở hay US-index alignment. Tần suất 2/46 lệnh mở.
- **Hướng sửa:** (1) server tạo dòng `closed` từ payload close khi gặp ctrader_id lạ; (2) bot retry có backoff với `HttpRequestException`, sau khi server idempotent theo `ctrader_id`; (3) uvicorn `--timeout-keep-alive 75`, hoặc `PooledConnectionIdleTimeout` < 5 s trong cBot.
- **SQL bù sổ cho user tự chạy.** Giá có `/* ~ */` là ước tính. Đối chiếu cTrader History theo 2 position id trước khi chạy:

  ```sql
  SELECT id, ctrader_id FROM positions WHERE ctrader_id IN (675558107, 675569508);  -- phải rỗng
  BEGIN;
  INSERT INTO positions (bot_id, symbol, side, volume, initial_volume, entry_price, sl_pips, tp_pips,
                         sl_price, tp_price, entry_time, exit_time, exit_price, pnl, status,
                         account_id, ctrader_id, close_reason)
  VALUES
  ('cbot-demo-demo-us30-all-flowrsi', 'US30', 'Buy', 0.1, 0.1, 51404.8, 1151.6, 1659.5,
   51290.13571, 51571.24643, '2026-09-24 07:15:14+00', '2026-09-24 08:13:48+00',
   51288.6 /* ~ */, -11.62, 'closed', 'demo-10115236', 675558107, 'StopLoss (recovered: open report lost)'),
  ('cbot-demo-demo-eurjpy-london', 'EURJPY', 'Sell', 0.01, 0.01, 180.191 /* ~ */, 28.6, 38.1,
   180.477 /* ~ */, 179.810 /* ~ */, '2026-09-24 07:45:37+00', '2026-09-24 09:00:35+00',
   180.494 /* ~ */, -1.91, 'closed', 'demo-10115236', 675569508, 'StopLoss (recovered: open report lost)');
  COMMIT;
  ```

### 2. Hạn mức daily loss nâng 10× (cố ý)

- 13:34:08–13:34:15 VN: 3 lần `PUT /api/risk-limits` qua nginx lưu **2000/1000/600/600/300**. Đến 21:41 VN không đổi.
- **User xác nhận là cố ý** vì đây là tài khoản demo. Các lần audit sau không báo mục này nữa, trừ khi chuyển sang tài khoản live.

### 3. Lot tối thiểu làm vượt % rủi ro, cả ở bot TMS

- **Bằng chứng:**

  | Lệnh | Bot | Lot | Khoảng SL | Lỗ tại SL | % balance | Cấu hình | Bội số |
  |---|---|---|---|---|---|---|---|
  | #83 (mở) | ustec-newyork | 0.1 | 1190,1p | −11,90 $ | 0,72% | 0,2% | 3,6× |
  | #82 (mở) | us30-all-flowrsi | 0.1 | 1387,6p | −13,88 $ | 0,84% | 0,5% | 1,7× |
  | id 62 (đã đóng) | de40-london | 0.1 | 1048,3p | −12,01 $ (chạm SL) | ≈0,7% | 0,2% | ≈3,5× |

  Log container: `14:30:08 Executing Market Order to Buy 0.1 USTEC (SL: 1190.1)` (ustec-newyork); `14:00:06 Executing Market Order to Buy 0.1 US30 (SL: 1387.6, TP: 2168.5)` (us30-all-flowrsi), giờ UTC. Cấu hình (`cbot_configs`): ustec-newyork và de40-london `RiskPerTradePercent=0.2`; us30-all-flowrsi `RiskPercentage=0.5`, `MaxRiskPerTradeMoney=50.0`.
- **Nguyên nhân:** `AiAgentBot.cs:2357-2358` tính volume theo % rồi nâng lên `VolumeInUnitsMin` (0.1 lot với chỉ số). Chặn duy nhất là mức $ tuyệt đối `MaxDollarRiskPerTrade` (`:2326-2345`), không so với % cấu hình. FlowRSI giống vậy (`FlowRsiBot.cs:1789`, audit §3.3).
- **Ảnh hưởng:** với bot TMS chỉ số, mỗi lệnh chịu rủi ro 2–3,6× mức cấu hình. Tính theo $ vẫn dưới 1% tài khoản.
- **Hướng sửa:** như §3.3: từ chối lệnh khi rủi ro ở lot tối thiểu > k × rủi ro mục tiêu (ví dụ k = 1,5), ở cả 2 bot.

### 4–5. FlowRSI BUY chỉ số và cụm JPY-cross (đã biết)

- Index BUY của FlowRSI đã đóng hôm nay: 42, 45, 47, 53, 55, 58, 59, 60 (đều SL), 71 (+16,32 TP), 72 (+0,18), 74 (+5,16), cộng `#675558107` (−11,62). Tổng **−58,73 $**, 3/12 thắng; 72 và 74 là lệnh đóng tay. Lúc 21:00 VN mở thêm #82 US30 BUY. Phân tích lock H1 cũ ở audit §9.4.
- Nến M15 14:45 VN: 4 lệnh SELL JPY-cross từ 2 chiến lược (id 64, 65, 66 + `#675569508`) chạm SL lúc 16:00–16:05 VN, tổng −24,32 $. Hướng sửa: giới hạn exposure theo đồng tiền, như phần còn thiếu của §2.2.

### 6. VPS quá tải (hiện tại, tái phát)

- **Bằng chứng:**
  - Load: 29,34/28,36/24,36 lúc 21:41 VN, và 28,62/30,69/27,10 lúc 21:49 VN, trên 8 vCPU.
  - `/proc/pressure/cpu some avg10=53.55 avg60=50.95`.
  - RAM: used 14,7/15,6 GB, available 902 MB, shared 4,6 GB; swap 3 MB.
  - 19:58:39–44 VN: 3 bot (btcusd, eurjpy, eurusd-all-flowrsi) gặp `[Dashboard] Command poll failed: TaskCanceledException … Timeout`, không trùng restart, đúng lúc user đóng tay 8 lệnh liền. Poll timeout 5 s nhưng không lệnh nào bị lỡ: cả 8 lệnh báo `done`.
- **Hướng sửa:** như audit §3.4: bật/tắt bot phiên theo lịch, gộp container.

### 7. `/portfolio/status` luôn lỗi trên Postgres (mới)

- **Bằng chứng:**
  - `20:05:36 [ERROR] app.portfolio: Failed to get portfolio status: tuple index out of range`, cùng giây với `GET /portfolio/status HTTP/1.1" 200 OK` từ 127.0.0.1 (journal 13:05:36 UTC). Đây là lần gọi duy nhất trong ngày.
  - Tái hiện read-only trên VPS: `cursor.mogrify(_adapt_query_for_pg("… symbol LIKE 'EUR%' … account_id = ?"), p)` ném `IndexError tuple index out of range` với cả `p = ()` và `p = ('demo-10115236',)`. `mogrify` chỉ định dạng câu lệnh ở client, không gửi gì lên DB.
- **Nguyên nhân:**
  - Query currency exposure (`app/portfolio.py:627-648`) có `LIKE 'EUR%'`… và luôn truyền `tuple(params)`, kể cả tuple rỗng.
  - `_adapt_query_for_pg` (`app/db.py:34-83`) chỉ đổi `?` thành `%s`, không nhân đôi `%` trong literal. Khi có tham số, psycopg2 đọc `%'` như một placeholder nên thiếu phần tử.
  - Hàm bắt exception và trả `open_positions: []`, `total_pnl: 0` với HTTP 200.
  - Test chạy trên SQLite nên không bắt được lỗi này.
- **Ảnh hưởng:** endpoint trả dữ liệu sai (rỗng) mà không báo lỗi. Hiện không có caller trong UI, cBot hay script (`git grep`), nên chưa ảnh hưởng giao dịch. Rủi ro là người hoặc agent dùng endpoint này sẽ thấy "0 lệnh mở, P&L 0".
- **Đã sửa, deploy 22:36 VN (PR #51, `09d12ef`):**
  - `app/db.py`: `_adapt_query_for_pg(sql, escape_percent=False)` nhân đôi `%` trong literal khi `escape_percent`. `PostgresCursorWrapper.execute` bật cờ này khi có tham số (`params is not None`). Không có tham số thì psycopg2 gửi câu lệnh nguyên văn, nên không nhân đôi.
  - Sửa ở tầng adapter nên áp dụng cho mọi query có `%` trong literal, không chỉ query này. Không query nào trong `app/` tự viết `%s` hay `%%`.
  - Test mới `tests/test_db_pg_percent_literal.py` (3 test): có tham số, tuple rỗng, không tham số. Trước khi sửa, 2 test đầu fail đúng lỗi định dạng.
  - pytest local: 663 passed.
  - Kiểm tra trên VPS, chỉ đọc, `db.py` đã sửa nạp trong bộ nhớ, không ghi file nào: `get_portfolio_status` thật chạy không lỗi với `account_id=None` và `'demo-10115236'`. Query CASE/LIKE qua psycopg2 thật trả `EUR 11, GBP 13, USD 9, XAU 6, OTHER 46` trên các lệnh đã đóng.
  - Sau deploy: pytest trên VPS 659 passed, 16 skipped. Service lên lại sau 9 s. `/portfolio/status` trả đúng 1 lệnh mở XAUUSD, `currency_exposure {"XAU": 1}`, không còn key `error`. 45 bot đều poll lại.

### 8. Nhãn "Closed (Take Profit Early)" gộp nhiều nguyên nhân (đã xác nhận nguồn đóng)

> **User xác nhận:** 51, 70, 72 là lệnh user đóng tay trên cTrader để restart container. Khớp với bằng chứng bên dưới. 3 FLAG FILL_FAR_FROM_LEVEL là nhiễu. Phần còn lại chỉ là ghi chú về nhãn, sửa hay không tuỳ user.

- **Bằng chứng:**
  - 19:35:19/29/39 VN: user bấm Close trên dashboard cho 51 (AUDJPY), 70 (ETHUSD), 72 (US30); journal có `POST /api/positions/{51,70,72}/close 200`. Ba bot này còn chạy `.algo` cũ, không poll, nên các lệnh 29fa1f67/ed8fba65/58af7491 không có dòng `done`.
  - 19:36:52–59 VN: cả 3 lệnh đóng. Log container chỉ có `[Portfolio Hub] Reported position closed`, không có dòng tự đóng nào của bot (`[AI Emergency Exit]`, `[Dashboard] close_position`, `Circuit Breaker`), và thời điểm không rơi vào ranh giới nến. **Nghi ngờ** user đã đóng trong app cTrader; xác nhận bằng cTrader History (nguồn đóng của #675464477, #675600708, #675619292).
  - DB ghi `close_reason = 'Closed (Take Profit Early)'` với exit xa TP (51: TP 111.432, exit 111.577; 70: TP 2615.56, exit 2641.8; 72: TP 51484.02, exit 51330.1). Đây là nguồn của 3 FLAG FILL_FAR_FROM_LEVEL.
  - 19:37–19:40 VN: `restart_when_flat` khởi động lại 3 bot, sau đó chúng poll bình thường (`polling=True`).
- **Nguyên nhân:** `FlowRsiBot.cs:2899`: khi `PositionCloseReason.Closed` và bot không ghi lý do, nhãn mặc định là "Closed (Take Profit Early)" hoặc "(Cut Loss Early)". Ngoài lệnh đóng tay trên cTrader, hai đường bot tự đóng cũng rơi vào nhánh này vì gọi `ClosePosition` trần: AI `CLOSE_ALL` (`:1545`) và circuit breaker (`:2191`). AiAgentBot thì ghi "AI Close: …".
- **Ảnh hưởng:** thống kê theo lý do đóng và leaderboard không phân biệt được AI chốt sớm, circuit breaker hay người đóng tay. 3 lệnh hôm nay (+19,08 $).
- **Hướng sửa:** dùng `CloseWithReason` ở `:1545` ("AI Close: <reason>") và `:2191` ("Circuit Breaker"); đổi nhãn mặc định thành "Closed outside the bot (cTrader)".

### 9. Snapshot `/trade` của FlowRSI vẫn đọc nến `Count − 1` (mới, nghi ngờ)

- **Bằng chứng:** `563fca4` chuyển `EvaluateStrategySignals` sang `ClosedBarIndex()`, vì trong `OnBarClosed` `Bars.LastBar` có khi là nến vừa mở, mới có một tick (14/15 bot lúc 17:45 UTC 23/09, theo commit). Nhưng `SendStateToAgentAsync` vẫn:
  - lấy `fast_rsi`, `slow_rsi`, ATR, swing high/low tại `Bars.ClosePrices.Count - 1` (`FlowRsiBot.cs:1228-1233`);
  - gửi danh sách bars bắt đầu từ `Bars.Count - 1` (`:1211-1226`).
- **Ảnh hưởng (nghi ngờ nhỏ):** tín hiệu cross/FVG/sweep và SL/TP vẫn lấy từ nến đã đóng. Chỉ các giá trị hiển thị cho LLM và gate server lệch một nến một tick. Nến đó có close gần bằng nến trước nên RSI lệch ít. Cách xác nhận: so `F=/S=` trong `[SNAPSHOT FLOW_RSI]` với RSI của nến đã đóng trong log bot ở những nến có Candidate.
- **Hướng sửa:** dùng `ClosedBarIndex()` cho `index` và bắt đầu vòng bars từ nến đã đóng.

## 3. Thống kê lệnh trong ngày

Theo chiến lược (lệnh đóng trong cửa sổ, DB; cộng lệnh ngoài sổ):

| Chiến lược | Đóng | Thắng | P&L DB ($) | Ngoài sổ ($) |
|---|---|---|---|---|
| FlowRSI | 33 | 15 (45%) | −37,51 | −11,62 (1 lệnh) |
| TMS (tokyo/london) | 6 | 1 | −23,62 | −1,91 (1 lệnh) |
| Judas | 2 | 1 | +2,50 | 0 |
| **Tổng** | 41 | 17 | **−58,63** | −13,53 |

Theo lý do đóng:

| Lý do | Số lệnh | P&L ($) |
|---|---|---|
| StopLoss (Initial Structural Reversal) | 12 | −120,24 |
| Stop Loss (TMS) | 3 | −17,86 |
| AI Close: Confirmed Reversal (TMS) | 2 | −6,57 |
| StopLoss (Initial Spike Sweep) | 1 | −6,18 |
| AI Close: underwater (Judas) | 1 | −2,43 |
| Session End (EOD flatten) | 1 | +0,81 |
| Manual close (dashboard) | 9 | +0,88 |
| Take Profit (Judas) | 1 | +4,93 |
| StopLoss (Break-Even Zero-Loss) | 4 | +16,02 |
| Closed (Take Profit Early), đóng ngoài bot, xem #8 | 3 | +19,08 |
| TakeProfit (Target Hit) | 4 | +52,93 |

Quyết định LLM so với lệnh vào:

| Chiến lược | LLM BUY/SELL (conf ≥ 75) | Lệnh vào |
|---|---|---|
| FlowRSI | 28 / 8 | 35 trong DB + 1 ngoài sổ = 36 |
| TMS | 6 / 2 | 7 trong DB + 1 ngoài sổ = 8 |
| Judas | 4 / 2 | 2; 4 BUY bị `[Judas Entry Guard]` chặn |

9 lần partial close trong ngày (agent log `Partial close recorded`). Cả 9 thuộc các lệnh đã đóng, nên đã nằm trong P&L DB.

Thao tác tay (agent log): 16:36 pause/resume eurusd-london; 17:02 Close & Stop audusd-tokyo (đóng 0 lệnh), Resume 17:03; 17:10 đóng 73; 19:35 đóng 51/70/72 (lệnh hết hạn, xem #8); 19:58:23–42 đóng 74–81, cả 8 lệnh báo `done`.

Lệnh còn mở lúc 21:41 VN (tổng `sl_pnl` −34,28 $, P&L live −9,79 $):

| id | Bot | Lệnh | SL / TP | Tuổi | P&L live | Tại SL |
|---|---|---|---|---|---|---|
| 82 | us30-all-flowrsi | BUY 0.1 @ 51342.0 | 51203.24 / 51558.85 | 0,7 h | −4,02 | −13,88 (RISK_OVER, #3) |
| 83 | ustec-newyork | BUY 0.1 @ 30333.5 | 30214.49 / không có (Trend Mode, trailing) | 0,2 h | −2,34 | −11,90 (RISK_OVER, #3) |
| 84 | eurjpy-all-flowrsi | SELL 0.07 @ 180.579 | 180.761 / 180.31 | 0,2 h | −3,43 | −8,50 |

## 4. Đã xem, không phải bug

| Hiện tượng | Kết luận |
|---|---|
| BOT_EXCEPTION eurjpy-all-flowrsi 19:45:13 VN | Dòng `Info | [AI Decision] Action: HOLD …`: regex collector bắt nhầm chữ trong lý do của LLM. Không phải exception |
| Watchdog "stale feeds" de40- và us30-KZ-london-ny-judas (hiện tại, 5485 s và 3685 s) | `bar_telemetry` cho thấy cả hai xử lý nến 14:45 UTC. Bot không gọi `/trade` vì gate cục bộ khoá cả hai phía (`Locked=Low->BUY_LOCKED,High->SELL_LOCKED`), hoặc `Judas Sweep Filter … rejected`. Run command không có tham số phiên, nên watchdog xét chúng theo bar heartbeat và không restart. Đúng thiết kế |
| 56 lần "Daily loss limit reached" từ 00:00 đến 06:00 VN | Hạn mức cũ −200 $ của ngày UTC 23/09 (−281,23 $). Guard chạy đúng |
| TRADE_OP_FAILED eurjpy-all-flowrsi 12:47:08 VN | Modify rơi đúng lúc chạm TP (lệnh 50 đóng cùng giây, +11,53). Race đã biết (audit §5) |
| 4 lần `[TMS CLOSE GUARD] CLOSE_ALL rejected`; 4 lần `[Judas Entry Guard]` | Guard làm đúng việc |
| 8 lần restart service (00:38, 12:37, 13:20 reboot, 13:32, 16:31, 17:52, 18:09, 19:46 VN) | Deploy hoặc reboot nâng cấp. Không báo cáo nào rơi vì restart; lần 19:46 có 8 lệnh FlowRSI mở (74–81), tất cả đóng và báo cáo bình thường lúc 19:58 |
| TickStream WebSocketException (187 + 128 + 23), `Command poll failed … Connection refused` (127) | 100% trùng các lần restart |
| News Filter 429, XML fallback, "Central Dashboard sync bypassed" | ForexFactory giới hạn tốc độ, hoặc server chậm sau reboot. Không trùng tin mạnh nào |
| DOCKER_LOG_CORRUPT (eurjpy-, usdjpy-all-flowrsi) | Khối NUL do hard reset lúc reboot 13:20 VN; collector đã bỏ qua |
| `PUT /api/risk-limits 400` 13:32:29 VN | Kiểm tra giá trị −5 khi deploy |
| DIRECTION_SKEW TMS (6 BUY / 1 SELL, +1 SELL ngoài sổ) | Mẫu nhỏ; BUY chủ yếu USDJPY, cùng hướng giá hôm nay |
| SAME_BAR_CLUSTER 14:45 VN | Gộp vào #5 |
| Backup, watchdog | Backup SUCCESS 03:00 UTC (12K). Watchdog chạy, không có lần auto-heal nào trong ngày |

Review commit trong cửa sổ, đọc code tại `5d7140f`:

| Commit | Nội dung | Kết luận |
|---|---|---|
| `734cdbb` | Tắt thinking của Qwen ở `/trade`; bar heartbeat cho watchdog; retry `/trade` một lần | OK. Chỉ retry khi `HttpRequestException` và bot chỉ hành động theo response nhận được, nên không nhân đôi lệnh. Bridge Error hôm nay chỉ có 8 dòng timeout lúc 13:25–13:26 sau reboot |
| `490f1a7`, `563fca4` | Heartbeat theo `Server.Time`; Judas/FlowRSI xét tín hiệu trên nến đã đóng | `ClosedBarIndex()` đúng cả khi `LastBar` là nến mới và khi có khoảng trống tick. Còn sót snapshot (#9) |
| `c84a845`, `1005f50`, `8e7f2ea`, `ba502b6`, `fc3944e` | TMS cross-lock, partial TP, runner | Đã review ở audit §9–§10 |
| `723f22c` | Daily loss 3 lớp | Đã review ở audit §11.2; hạn mức bị nâng (#2) |
| `24b666c`, `a44f9d9` | Đóng tay, pause, Close & Stop, cờ NOT POLLING | OK. Lệnh không được poll hết hạn sau 15 s và không giao lại. Close & Stop chỉ stop container khi mọi lệnh đã đóng. Pause chặn mọi đường vào lệnh ở cả 3 bot (`FlowRsiBot.cs:1755`, `AiAgentBot.cs:2411`, `AsianRangeJudasSweepBot.cs:788/809/1925/1939/4436/4636`). Đã chạy thật 17:02–19:58 VN |
| `ea74949` | Retry khôi phục khoảng SL mỗi 30 s; fallback chỉ đo SL còn ở phía lỗ | OK. Có cờ in-flight chống gọi chồng |
| `736b025` | Leaderboard; `db.py` đặt `TimeZone=UTC` cho phiên Postgres | OK |
| `57c0693`, `50e2083`, `21289cd` | UI leaderboard, escape XSS, hiển thị runner không TP | Đọc lướt, không thấy vấn đề |

## 5. Tái hiện

```bash
OUT=<scratchpad>/day_today.txt
ssh forge@204.168.144.232 'cd /home/forge/AgentFxTrading && .venv/bin/python - today' \
  < .claude/skills/daily-audit/scripts/collect_day.py > "$OUT" 2>&1
```

Follow-up chỉ đọc, pipe qua stdin với header read-only trong `reference.md`:

- Log container theo cửa sổ UTC: đọc `sudo -n cat $(docker inspect -f '{{.LogPath}}' <c>)`, parse JSON, lọc theo `time`:
  - audjpy/ethusd/us30-all-flowrsi, 12:34:30–12:41:00 (ai đóng 51/70/72);
  - us30-all-flowrsi 13:59:30–14:01:30 và ustec-newyork 14:29:30–14:31:30 (khối lượng lệnh);
  - eurjpy-all-flowrsi 12:45:05–12:45:20;
  - 15 container `*-all-flowrsi`, 12:23–14:45, lọc `AI Agent Retry|Failed to report|Bridge Error|RestoreInitialSl`.
- `docker logs --tail 12` và `docker inspect` StartedAt cho de40-, us30-, xauusd-KZ-london-ny-judas.
- Journal: `sudo -n journalctl -u agentfx.service --since '2026-09-24 13:05:20' --until '13:05:50'` và `12:35:00–12:37:30`; đếm `GET /portfolio/status` từ 2026-09-23 17:00.
- `curl -s http://127.0.0.1:8000/api/watchdog/status`; `tail -30 logs/restart_when_flat.log`; `grep -n -B3 -A25 'tuple index out of range' logs/agent_2026-09-24.log`.
- Tái hiện lỗi #7: `conn._conn.cursor().mogrify(_adapt_query_for_pg("SELECT CASE WHEN symbol LIKE 'EUR%' THEN 'EUR' END FROM positions WHERE account_id = ?"), ())`.
- SQL: `SELECT id, close_reason, exit_time, pnl, initial_volume, volume FROM positions WHERE id IN (51,70,72)`.
- Local: `git show 5d7140f:<path>` cho `app/portfolio.py`, `app/db.py`, `app/cbot_watchdog.py`, `cBot/*.cs`; `git archive 5d7140f | tar -x -C <scratchpad>/vps_tree && .venv/bin/pytest -q`.
