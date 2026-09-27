# Báo cáo rà soát cBot — 2026-09-22

Phạm vi: `cBot/FlowRsiBot.cs`, `cBot/AiAgentBot.cs`, `cBot/AsianRangeJudasSweepBot.cs`.
Bằng chứng đối chiếu: log 45 container trên `forge@204.168.144.232`, journal `agentfx.service`, bảng `positions` (PostgreSQL `agentfx`).
Commit gốc khi rà soát: `55a4b60`.

---

## Thang đánh giá

**Mức độ quan trọng (Severity)**

| Mức | Nghĩa |
|---|---|
| **P0** | Gây mất tiền trực tiếp hoặc phá vỡ hạn mức rủi ro đã cấu hình. Sửa trước khi chạy live. |
| **P1** | Sai lệch logic giao dịch hoặc số liệu ra quyết định. Sửa sớm. |
| **P2** | Chỉ sai trong điều kiện cụ thể (restart, mất mạng, fallback). Sửa theo kế hoạch. |
| **P3** | Chất lượng mã / hiệu năng, không ảnh hưởng kết quả giao dịch trực tiếp. |

**Mức độ ảnh hưởng (Impact)** — đánh giá theo 3 chiều: *phạm vi* (bao nhiêu bot), *tần suất* (bao lâu xảy ra một lần), *hệ quả tiền*.

---

## Bảng tổng hợp

| ID | Vấn đề | File | Mức | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|---|
| **C-00** | SL/TP truyền giá tuyệt đối vào tham số pip | FlowRsiBot.cs:1250 | P0 | 15 bot, mọi lệnh | ✅ Đã sửa (PR #31) |
| **C-01** | AI gate fail-open: vẫn vào lệnh khi AI lỗi/cooldown | FlowRsiBot.cs:784, 968, 1007 | P0 | 15 bot, mỗi lần server chậm | ✅ Đã sửa |
| **C-02** | ADJUST có thể nới rộng SL vượt rủi ro ban đầu | AiAgentBot.cs:2020 | P0 | 15 bot TMS | ✅ Đã sửa |
| **C-03** | Partial close tại BE không báo cáo → DB sai P&L | FlowRsiBot.cs:1346, AiAgentBot.cs:1370 | P1 | Mọi lệnh thắng | ✅ Đã sửa |
| **C-04** | Cost Gate bỏ qua việc theo dõi TDI cross ngoài phiên | AiAgentBot.cs:527 | P1 | 15 bot TMS, mỗi phiên | ✅ Đã sửa |
| **C-05** | SL sai phía bị kẹp âm thầm thành ~3×spread | FlowRsiBot.cs:1248 + 1167 | P1 | 15 bot, khi AI đảo chiều | ✅ Đã sửa |
| **C-06** | OnStart tính tín hiệu trên nến chưa đóng rồi gọi AI | FlowRsiBot.cs:447 | P1 | Mỗi lần restart/deploy | ✅ Đã sửa |
| **C-07** | Asian range lệch 1 nến (dùng giờ của tick đóng nến) | AsianRangeJudasSweepBot.cs:562 | P1 | 15 bot Judas, hằng ngày | ✅ Đã sửa |
| **C-08** | Lệnh sniper staged bỏ qua sàn SL tối thiểu | AsianRangeJudasSweepBot.cs:4131 | P1 | 15 bot Judas, khi staging | ✅ Đã sửa |
| **C-09** | Đánh dấu BE + đóng một phần dù lệnh sửa SL thất bại | AiAgentBot.cs:1361 | P1 | 15 bot TMS, khi broker từ chối | ✅ Đã sửa |
| **C-10** | Sau restart, initialSlDist lấy nhầm SL đã dời về BE | FlowRsiBot.cs:1305 | P2 | Lệnh đang mở khi restart | ✅ Đã sửa |
| **C-11** | Kẹp volume tối thiểu bỏ qua MaxRiskPerTradeMoney | FlowRsiBot.cs:1290 | P2 | Tài khoản nhỏ, symbol lớn | ✅ Đã sửa |
| **C-12** | Fallback XML đọc giờ ET của ForexFactory như UTC | FlowRsiBot.cs:1890 | P2 | Khi hub + JSON cùng lỗi | ✅ Đã sửa |
| **C-13** | Báo cáo đóng lệnh dùng Bid/Ask hiện tại, không dùng ClosingPrice | AiAgentBot.cs:1643, FlowRsiBot.cs:2040 | P2 | Mọi lệnh đóng | ✅ Đã sửa |
| **C-14** | Fallback XML tải về rồi vứt bỏ, tắt news filter 6 tiếng | AsianRangeJudasSweepBot.cs:2090 | P2 | Khi JSON lỗi | ✅ Đã sửa |
| **C-15** | Gọi HTTP đồng bộ trên luồng giao dịch trong OnBarClosed | AsianRangeJudasSweepBot.cs:1883 | P3 | 15 bot Judas, khi hub chậm | ✅ Đã sửa |
| **X-01** | `close_position` bỏ qua `ctrader_id` | app/portfolio.py:147 | P2 | Khi MaxPositions > 1 | ✅ Đã sửa |
| **X-02** | Judas XAUUSD: sweep buffer 30 pip = $0.30 | app/cbot_presets.py:122 | P2 | 1 bot | ✅ Đã sửa |
| **X-03** | `breakEvenTrigger` bị bỏ qua vì bot chạy mode R:R | app/cbot_presets.py:70 | P3 | 15 bot Judas | ✅ Đã sửa (giữ mode R:R, bỏ param chết) |
| **X-04** | Dashboard 500: `'list object' has no attribute 'page'` | templates/ | P2 | 1 lần lúc 09:45 | ⏭️ Bỏ qua (quyết định 22/09) |
| **OPS-01** | 7 lệnh đang mở mang SL/TP sai từ trước khi vá | (vận hành) | P0 | 7 lệnh | ⏭️ Bỏ qua (quyết định 22/09) |

---

## C-00 — SL/TP truyền giá tuyệt đối vào tham số pip ✅ ĐÃ SỬA

**Vị trí**: `cBot/FlowRsiBot.cs:1250`
**Mức**: P0 · **Ảnh hưởng**: 15 bot `*-all-flowrsi`, mọi lệnh kể từ khi triển khai

**Cơ chế**
Overload `ExecuteMarketOrder(tradeType, symbol, volume, label, stopLossPips, takeProfitPips, comment)` nhận **khoảng cách tính bằng pip**, nhưng bot truyền vào **giá tuyệt đối** `slPrice`/`tpPrice`.

**Bằng chứng**
```
[Order Executed] Buy 0.05 lots EURUSD at 1.14515 | SL: 1.14319, TP: 1.14817   ← bot log
Executing Market Order to Buy 5000 EURUSD (SL: 1.1, TP: 1.1)                  ← broker nhận
```

| Symbol | Broker nhận | Kết quả thực tế | P&L |
|---|---|---|---|
| EURUSD/GBPUSD/USDCAD/AUDUSD | 0.7–1.4 pip | Spread quét SL/TP sau 6–80 giây | ±$0.2–1.7 |
| JPY pairs | 157–210 pip (dự định 18–27) | Không bao giờ chạm, chạy 3–4h tới trailing stop | +$16 / +$26 / +$38 |
| XAUUSD | 4332 pip = $43.32 (dự định $9.45) | Chạm SL đúng mức sai | **−$43.99** |
| BTCUSD | 85475 pip = $854 | Chạm TP ở +860 | +$8.91 |

**Cách sửa đã áp dụng** (commit `40b8b62`)
```csharp
double entryRefPrice = tradeType == TradeType.Buy ? Symbol.Ask : Symbol.Bid;
double slPips = Math.Abs(entryRefPrice - slPrice) / Symbol.PipSize;
double tpPips = Math.Abs(tpPrice - entryRefPrice) / Symbol.PipSize;
var result = ExecuteMarketOrder(tradeType, SymbolName, targetUnits, BotId, slPips, tpPips, BotId);
```
Test hồi quy: `tests/test_flow_rsi_order_units.py` (2 test, fail trên code cũ, pass sau fix).
Đã build `.algo` và restart 15 container lúc 10:35 UTC ngày 22/09/2026.

**Còn lại**: xác minh log lệnh mới có dạng `(SL: 19.6, TP: 30.2)` thay vì `(SL: 1.1, TP: 1.1)`:
```bash
ssh forge@204.168.144.232 'docker logs --since 30m cbot-demo-demo-eurusd-all-flowrsi 2>&1 | grep "Executing Market Order"'
```

---

## C-01 — AI gate fail-open: vẫn vào lệnh khi AI lỗi hoặc đang cooldown ✅ ĐÃ SỬA

**Vị trí**: `cBot/FlowRsiBot.cs:784`, `:968`, `:1007`
**Mức**: P0 · **Ảnh hưởng**: 15 bot · tần suất: mỗi khi server chậm/khởi động lại đúng lúc đóng nến · hệ quả: vào lệnh hoàn toàn không qua kiểm duyệt AI

**Cơ chế**
Ba đường dẫn đều rơi thẳng vào `ExecuteTechnicalOrder` khi AI không trả lời:
- `:784` — cooldown đang bật (sau 3 lần lỗi liên tiếp, treo 15 phút)
- `:968` — HTTP trả về non-2xx
- `:1007` — exception (timeout `HttpClient` 60 giây, mất kết nối)

Trong khi đó bot Judas — được nêu là "reference pattern" trong chính comment của FlowRsiBot — **fail closed**: `AsianRangeJudasSweepBot.cs:3282` và `:3305` chỉ gọi `HandleAiFailure` rồi `return`, không vào lệnh.

**Kịch bản hỏng**
15 bot `*-all-flowrsi` cùng POST `/trade` tại thời điểm đóng nến M15. Server nghẽn quá 60 giây (LLM chậm, hoặc `systemctl restart agentfx.service` rơi đúng lúc đóng nến) → mọi bot có candidate mở lệnh kỹ thuật thuần, không qua AI. Sau 3 lần như vậy, cooldown 15 phút bật lên nhưng `:784` vẫn tiếp tục vào lệnh — tức là **đúng lúc AI được coi là không tin cậy thì bot lại giao dịch nhiều nhất**, trong khi tham số hiển thị `AI Gate Mode = true`.

**Đề xuất sửa**
Bỏ cả 3 lời gọi `ExecuteTechnicalOrder` trong nhánh lỗi, chỉ log + `HandleAiFailure`. Nếu muốn giữ chế độ chạy không AI thì tách thành tham số riêng (ví dụ `AllowTechnicalFallbackOnAiFailure`, mặc định `false`) để hành vi là chủ ý chứ không phải mặc định ẩn.

**Cách sửa đã áp dụng**
Thêm tham số opt-in, mặc định **tắt** — gate fail closed trừ khi vận hành cố ý bật:
```csharp
[Parameter("Allow Technical Fallback On AI Failure", Group = "AI Agent Integration", DefaultValue = false)]
public bool AllowTechnicalFallbackOnAiFailure { get; set; }
```
Cả 3 nhánh (cooldown / HTTP non-2xx / exception) nay bọc `ExecuteTechnicalOrder` trong `if (AllowTechnicalFallbackOnAiFailure)`, nhánh `else` chỉ log `[AI Gate Fail-Closed] ... candidate skipped`. `HandleAiFailure` giữ nguyên ở nhánh HTTP + exception để cooldown 3-strike vẫn lên; **không** thêm vào nhánh cooldown (sẽ tự gia hạn vô tận).

Đường dẫn `!UseAiGateMode` (backtest / standalone) giữ nguyên — có test chốt lại để tránh sửa quá tay.

Test hồi quy: `tests/test_ai_gate_fail_closed.py` (9 test, 4 fail trên code cũ).

---

## C-02 — ADJUST có thể nới rộng SL vượt rủi ro ban đầu ✅ ĐÃ SỬA

**Vị trí**: `cBot/AiAgentBot.cs:2020`
**Mức**: P0 · **Ảnh hưởng**: 15 bot TMS/ORB · hệ quả: vô hiệu hoá toàn bộ guardrail rủi ro đã tính lúc vào lệnh

**Cơ chế**
Nhánh `ADJUST` chỉ kiểm tra hai điều kiện trước khi `pos.ModifyStopLossPrice(targetSL.Value)`:
1. Anti-Premature BE Guard (chặn dời SL về hoà vốn quá sớm)
2. `valid` — SL nằm đúng phía thị trường với buffer

**Không có one-way ratchet**: nếu AI trả về `new_sl_price` xa hơn SL hiện tại, lệnh sửa được thực thi. So sánh:
- `FlowRsiBot.cs:1127` — có ratchet ("Strict One-Way Profit Ratchet")
- `AsianRangeJudasSweepBot.cs:1606` — `SafeModifyPosition` có ratchet
- `app/server.py:1972` — `validate_judas_adjust_decision` chỉ chạy cho bot Judas (`if is_judas`), bot TMS không được lớp bảo vệ phía server này

**Kịch bản hỏng**
Bot TMS long US30, SL 0.7×ATR, dollar risk đúng `MaxDollarRiskPerTrade = $12`. LLM trả `ADJUST` với `new_sl_price` cách entry 2×ATR kèm lý do "cho lệnh thở". Sửa thành công → rủi ro thực tế ~3× hạn mức. Mọi tính toán volume/guardrail tại thời điểm vào lệnh trở nên vô nghĩa.

**Đề xuất sửa**
Thêm ratchet trước khi gọi `ModifyStopLossPrice`:
```csharp
if (pos.StopLoss.HasValue &&
    ((pos.TradeType == TradeType.Buy  && targetSL.Value < pos.StopLoss.Value) ||
     (pos.TradeType == TradeType.Sell && targetSL.Value > pos.StopLoss.Value)))
{
    if (ShowLogs) Print($"[ADJUST Ratchet] Bỏ qua SL nới rộng {targetSL.Value} (hiện tại {pos.StopLoss.Value}).");
    continue;
}
```
Cân nhắc thêm: mở rộng `validate_judas_adjust_decision` phía server cho cả bot TMS (phòng thủ nhiều lớp).

**Cách sửa đã áp dụng**
Ratchet đặt **sau** Anti-Premature BE Guard và **trước** `minBuffer` / `ModifyStopLossPrice`, dùng `continue` nên lệnh bị từ chối giữ nguyên SL cũ:
```csharp
if (pos.StopLoss.HasValue &&
    ((pos.TradeType == TradeType.Buy  && targetSL.Value < pos.StopLoss.Value) ||
     (pos.TradeType == TradeType.Sell && targetSL.Value > pos.StopLoss.Value)))
{
    if (ShowLogs) Print($"[ADJUST Ratchet] Rejected widening SL ...");
    continue;
}
```
Test hồi quy: `tests/test_tms_adjust_ratchet.py` (7 test, 6 fail trên code cũ). Test trích chính điều kiện C# rồi chạy qua 4 kịch bản buy/sell × nới/siết, nên bắt được cả trường hợp đảo dấu so sánh (đã kiểm chứng bằng mutation).

**Chưa làm**: phần "cân nhắc thêm" phía server (`validate_judas_adjust_decision` vẫn chỉ chạy `if is_judas`). Đây là lớp phòng thủ thứ hai, đổi hành vi server cho 15 bot — tách riêng.

---

## C-03 — Partial close tại break-even không được báo cáo → DB sai P&L

**Vị trí**: `cBot/FlowRsiBot.cs:1346` (`ClosePosition(pos, volToClose)`), `cBot/AiAgentBot.cs:1370` (`pos.ModifyVolume(remainingVolume)`)
**Mức**: P1 · **Ảnh hưởng**: mọi lệnh thắng có partial close · FlowRSI đóng 25%, AiAgentBot đóng 50%

**Cơ chế**
Sự kiện `Positions.Closed` **không** kích hoạt khi đóng một phần. Phần đóng tại BE không sinh báo cáo nào. Khi lệnh đóng hẳn, `ReportPositionClosed` gửi `pos.NetProfit` của **phần còn lại** và `pos.VolumeInUnits` cũng chỉ còn phần còn lại — nhưng dòng DB vẫn giữ volume ban đầu từ lúc mở.

**Bằng chứng thực tế** — GBPJPY `#674345493` ngày 22/09:
```
05:15:30  [Portfolio Hub] Reported position open: #674345493 Sell GBPJPY   (0.09 lot)
08:16:09  [Partial Close] #674345493 closed 0.02 lots at Break-Even.        ← không có báo cáo
08:41:55  [Portfolio Hub] Reported position closed: #674345493 PnL: 38.27   ← chỉ của 0.07 lot
```
DB (`positions` id=4): `volume = 0.09`, `pnl = 38.27`. Lãi của 0.02 lot đóng tại BE bị mất hoàn toàn khỏi thống kê.

**Hệ quả**
Với `PartialCloseRatio = 0.5` của AiAgentBot, dashboard lệch **một nửa chân BE** trên mọi lệnh thắng. Leaderboard, daily_stats, win-rate và mọi phân tích dựng trên bảng `positions` đều sai lệch có hệ thống theo hướng đánh giá thấp bot.

**Đề xuất sửa**
Gửi một báo cáo `action = "partial_close"` ngay sau khi partial close thành công (kèm `ctrader_id`, volume đã đóng, P&L thực hiện), và phía server cộng dồn vào P&L của lệnh gốc + trừ volume. Hoặc tối thiểu: cập nhật `volume` của dòng DB về phần còn lại và cộng lãi partial vào trường `pnl`.

---

## C-04 — Cost Gate bỏ qua việc theo dõi TDI cross ngoài phiên

**Vị trí**: `cBot/AiAgentBot.cs:527`
**Mức**: P1 · **Ảnh hưởng**: 15 bot TMS · tần suất: đầu mỗi phiên, hằng ngày

**Cơ chế**
```csharp
if (GetBotPositions().Length == 0 && (!session.is_trading_time || session.phase == "closed" || session.phase == "ending"))
{
    return;   // ← thoát TRƯỚC khi gọi GetTmsSignals(index)
}
```
`GetTmsSignals` (`:600`) là **nơi duy nhất** cập nhật `_lastCrossBar` và `_lastCrossDir` (`:633-634`). Các cross xảy ra trước giờ mở phiên không bao giờ được ghi nhận.

**Kịch bản hỏng**
Bot NY (phiên 13:00 UTC): TDI cross up lúc 12:45. Đến 13:00 phiên mở, `_lastCrossDir` vẫn là `-1` của hôm trước, `bars_since_cross` ≈ 70 → `withinWindow` sai → `long_entry` **không bao giờ** đúng trong những nến đầu phiên. Đồng thời snapshot gửi cho LLM ghi `bias = BEARISH`, `cross_direction = "down"` trong khi thị trường vừa có cross tăng mới — LLM ra quyết định trên dữ liệu sai.

**Đề xuất sửa**
Tách phần cập nhật chỉ báo/cross ra khỏi Cost Gate: luôn gọi `GetTmsSignals(index)` (rẻ, thuần tính toán), chỉ chặn phần **gửi HTTP** cho AI khi ngoài phiên.

---

## C-05 — SL sai phía bị kẹp âm thầm thành ~3×spread + 2 pip

**Vị trí**: `cBot/FlowRsiBot.cs:1248` (kẹp), `:1167` (thiếu kiểm tra hướng)
**Mức**: P1 · **Ảnh hưởng**: 15 bot · điều kiện: AI trả action ngược hướng candidate, hoặc `new_sl_price` sai phía

**Cơ chế**
1. `ExecuteDecision` tại `:1167` thực thi **mọi** BUY/SELL của AI, không đối chiếu với `candidate_action` kỹ thuật đã gửi đi.
2. `ExecuteTechnicalOrder` tính `slDistancePips` từ `slPrice` (có thể sai phía) → dùng con số này để **tính volume**.
3. Pre-flight tại `:1244-1248` phát hiện SL sai phía nhưng **kẹp** thành `Ask/Bid ± (3×spread + 2 pip)` thay vì từ chối lệnh.

Volume đã được tính theo khoảng cách SL cũ (rộng), còn SL thực tế lại rất hẹp.

**Kịch bản hỏng**
Candidate = BUY, `technicalSL` cách 20 pip **dưới** giá. LLM trả SELL với confidence 80%. `slDistancePips = 20p` → sizing theo 20p; pre-flight dời `slPrice` lên `Ask + ~5p` → lệnh SELL với stop 5 pip và TP 30 pip. Gần như chắc chắn bị quét.

**Trạng thái quan sát**: chưa thấy xảy ra trong log ngày 22/09 (kiểm tra bằng cách ghép `SNAPSHOT FLOW_RSI ... Candidate=` với `LLM DECISION ... Action:` — 4 cặp "ngược" ban đầu đều là do log của bot khác xen kẽ, không phải cùng một bot). Nhưng đường dẫn hoàn toàn không có rào chắn.

**Đề xuất sửa**
- Tại `:1167`: từ chối action ngược với `allowedDirection` khi `allowedDirection` là BUY/SELL cụ thể (giống `MANAGE_ONLY` đang làm).
- Tại `:1244`: khi SL sai phía, **từ chối lệnh** và log Security Alert, thay vì kẹp; hoặc nếu kẹp thì phải tính lại volume theo khoảng cách SL sau khi kẹp.

---

## C-06 — OnStart tính tín hiệu trên nến chưa đóng rồi gọi AI

**Vị trí**: `cBot/FlowRsiBot.cs:447`
**Mức**: P1 · **Ảnh hưởng**: mỗi lần restart/deploy, 15 bot cùng lúc

**Cơ chế**
`OnStart` gọi `EvaluateStrategySignals(hasOpenPos)`. Hàm này dùng `index = Bars.ClosePrices.Count - 1` — lúc khởi động đó là **nến đang hình thành**, không phải nến đã đóng. Toàn bộ RSI cross / FVG / liquidity sweep / candidate được tính trên dữ liệu dở dang rồi gửi thẳng cho AI; nếu đang cooldown hoặc AI lỗi thì rơi vào `ExecuteTechnicalOrder` (xem C-01).

**Kịch bản hỏng**
Deploy 15 container lúc 10:35 → 15 snapshot đồng loạt trên nến M15 mới được 5 phút. Một cross tạm thời trong nến (sẽ đảo lại khi nến đóng) có thể được LLM xác nhận và vào lệnh thật. Lặp lại mỗi lần restart.

**Đề xuất sửa**
Trong `OnStart`, chỉ gọi `EvaluateStrategySignals` khi đang có vị thế mở (để AI quản lý lệnh), hoặc dùng `index = Bars.Count - 2` (nến đã đóng gần nhất) cho snapshot khởi động. Cách sạch hơn: `OnStart` chỉ gửi snapshot dạng "boot/manage", không mang candidate entry.

---

## C-07 — Asian range bị lệch một nến (dùng giờ của tick đóng nến)

**Vị trí**: `cBot/AsianRangeJudasSweepBot.cs:562` gọi `TrackAsianSession(Server.Time)`, logic tại `:1044-1070`
**Mức**: P1 · **Ảnh hưởng**: 15 bot Judas · tần suất: hằng ngày

**Cơ chế**
`TrackAsianSession` lấy **giờ từ `Server.Time`** (thời điểm tick đóng nến) nhưng lấy **High/Low từ `Bars.LastBar`** (nến vừa đóng, tức là nến bắt đầu trước đó 15 phút). Với `asianEndHour = 6`:
- Nến 05:45–06:00 đóng lúc 06:00 → `hour = 6`, không thoả `hour < 6` → **bỏ sót** nến cuối phiên Á.
- Nến 23:45–00:00 đóng lúc 00:00 → `hour = 0`, thoả `hour >= 0` → **tính nhầm** nến của ngày hôm trước, đồng thời `_asianSessionDate != date` khiến range bị **reset** về H/L của chính nến đó.

Trong khi đó `InitializeAsianSession` (`:1000`) dùng `bar.OpenTime.Hour` — đúng. Hai đường dẫn cho ra kết quả khác nhau.

**Kịch bản hỏng**
Đáy phiên Á rơi vào nến 05:45: range theo dõi live bỏ sót đáy này → `_asianLow` cao hơn thực tế → ngưỡng sweep, `IsEntryTooExtended`, `CheckStructuralInvalidation` đều sai. Sau khi restart container, `InitializeAsianSession` tính ra `_asianLow` **khác** → bot đổi hành vi chỉ vì vừa restart.

**Đề xuất sửa**
Dùng `Bars.LastBar.OpenTime` thay cho `Server.Time` trong `TrackAsianSession`, để khớp với `InitializeAsianSession`.

---

## C-08 — Lệnh sniper staged bỏ qua sàn SL tối thiểu (AiSlMinFloor/ATR)

**Vị trí**: `cBot/AsianRangeJudasSweepBot.cs:4131-4143`
**Mức**: P1 · **Ảnh hưởng**: 15 bot Judas · điều kiện: `enableWickRetracementHunting = true` (mặc định) và giá đi xa mở nến

**Cơ chế**
`ExecuteDecision` áp sàn SL tại `:3847-3852`:
```csharp
double effectiveMinFloor = Math.Max(AiSlMinFloorPips, currentAtrPips > 0 ? Math.Round(currentAtrPips * 0.8, 0) : 200.0);
if (slPips > 0 && slPips < effectiveMinFloor) slPips = effectiveMinFloor;
```
Nhưng `ExecuteStagedMarketOrder` **tính lại** `slPips` từ `decision.new_sl_price` so với giá đã pullback (`:4131-4136`) mà **không áp lại** sàn này. Đúng lúc giá gần SL nhất thì rào chắn chống stop-hunt biến mất.

**Kịch bản hỏng**
XAUUSD: AI đề xuất SL 210p → staging kẹp lên 200p, volume tính theo 200p. Giá pullback 150p rồi sniper bắn → `slPips` tính lại chỉ còn ~60p, trong khi volume vẫn là của 200p. Rủi ro thực tế lệch, và SL nằm trong vùng nhiễu.

**Đề xuất sửa**
Trích phần tính sàn SL thành một hàm dùng chung và gọi lại trong `ExecuteStagedMarketOrder`; nếu `slPips` thay đổi thì tính lại `volume` tương ứng.

---

## C-09 — Đánh dấu BE và đóng một phần dù lệnh sửa SL thất bại

**Vị trí**: `cBot/AiAgentBot.cs:1361-1372`
**Mức**: P1 · **Ảnh hưởng**: 15 bot TMS · điều kiện: broker từ chối sửa SL

**Cơ chế**
```csharp
pos.ModifyStopLossPrice(beSl);        // ← TradeResult bị bỏ qua
_breakevenApplied.Add(pos.Id);        // ← đánh dấu đã BE bất kể kết quả
if (PartialCloseRatio > 0 ...) pos.ModifyVolume(remainingVolume);   // ← vẫn đóng một nửa
```
`_breakevenApplied` chặn thử lại (`!_breakevenApplied.Contains(pos.Id)` ở điều kiện vào). Lỗi `InvalidStopLossTakeProfit` là có thật trong hệ thống này — log `cbot-demo-demo-btcusd-all-flowrsi` ghi nhận `Modifying position PID674359496 ... FAILED with error "InvalidStopLossTakeProfit"`.

So sánh: FlowRsiBot (`:1331`) và Judas (`ProcessBreakEvenLogic`, `:1571`) đều kiểm tra `res.IsSuccessful` trước khi đánh dấu.

**Kịch bản hỏng**
Giá nhảy nhanh tới ngưỡng BE, `ModifyStopLossPrice` bị từ chối vì SL quá sát thị trường → vị thế bị **giảm nửa khối lượng** trong khi stop vẫn ở mức rủi ro ban đầu, và không bao giờ thử BE lại. Lá chắn duy nhất còn lại là giveback guard.

**Đề xuất sửa**
```csharp
var res = pos.ModifyStopLossPrice(beSl);
if (res == null || !res.IsSuccessful) { if (ShowLogs) Print($"[BE Failed] #{pos.Id}: {res?.Error}"); continue; }
_breakevenApplied.Add(pos.Id);
// ... partial close
```

---

## C-10 — Sau restart, initialSlDist lấy nhầm SL đã dời về break-even

**Vị trí**: `cBot/FlowRsiBot.cs:1303-1305`
**Mức**: P2 · **Ảnh hưởng**: các lệnh đang mở tại thời điểm restart

**Cơ chế**
`_initialSlDistances` là `Dictionary` trong RAM, mất khi restart. Fallback:
```csharp
: (pos.StopLoss.HasValue ? Math.Abs(pos.EntryPrice - pos.StopLoss.Value) / Symbol.PipSize : 20.0);
```
Với lệnh đã dời SL về BE, khoảng cách này chỉ còn ~0.5–1 pip → `currentRr = pnlPips / initialSlDist` phóng đại hàng chục lần.

**Kịch bản hỏng**
Restart khi GBPJPY đang +25p, SL tại BE+0.5p → `currentRr ≈ 50` → vượt `TrailingStopTriggerRr = 1.8` ngay tick đầu tiên → trailing stop siết ngay về `Bid − 25p` (sàn JPY) thay vì để lệnh chạy; đồng thời logic partial-close/tier-2 đánh giá trên R giả.

**Liên quan**: chính vấn đề này khuếch đại hậu quả của C-00 với 7 lệnh mở còn lại (xem OPS-01).

**Đề xuất sửa**
Ghi `_initialSlDistances` xuống `LocalStorage` của cTrader (hoặc lấy lại từ `sl_pips` đã báo cáo qua `/portfolio/report`) và khôi phục trong `OnStart`.

---

## C-11 — Kẹp volume tối thiểu bỏ qua MaxRiskPerTradeMoney

**Vị trí**: `cBot/FlowRsiBot.cs:1283-1290`
**Mức**: P2 · **Ảnh hưởng**: tài khoản nhỏ giao dịch symbol có lot tối thiểu lớn (US30, BTC, chỉ số)

**Cơ chế**
```csharp
if (normalizedUnits < Symbol.VolumeInUnitsMin) normalizedUnits = Symbol.VolumeInUnitsMin;
```
Không kiểm tra lại dollar risk sau khi nâng lên lot tối thiểu. `MaxRiskPerTradeMoney` (mặc định $50) chỉ được dùng ở bước tính `effectiveRiskAmount` phía trên.

AiAgentBot có đủ guard này (`:2124-2144`: `Hard Guardrail 2` + `Dynamic Risk Adaptation` + chặn lệnh), FlowRsiBot thì không.

**Kịch bản hỏng**
Tài khoản nhỏ, US30 với SL kỹ thuật rộng: lot tối thiểu của broker tại SL đó rủi ro > $50 → lệnh vẫn được đặt, vượt hạn mức đã cấu hình mà không có log cảnh báo nào.

**Đề xuất sửa**
Sau khi kẹp lên `VolumeInUnitsMin`, tính lại `finalRisk = normalizedUnits * slPips * Symbol.PipValue`; nếu vượt `MaxRiskPerTradeMoney` thì hoặc siết `slPips` (như AiAgentBot làm) hoặc từ chối lệnh kèm log.

---

## C-12 — Fallback XML đọc giờ ET của ForexFactory như UTC

**Vị trí**: `cBot/FlowRsiBot.cs:1885-1893` (`ParseNewsEventsFromXml`)
**Mức**: P2 · **Ảnh hưởng**: khi cả news hub lẫn JSON trực tiếp cùng lỗi (429/403 backoff)

**Cơ chế**
```csharp
if (DateTime.TryParse($"{dateStr} {timeStr}", CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal, out var parsed))
```
Feed XML của ForexFactory ghi giờ **Eastern Time không kèm offset**. `AdjustToUniversal` với chuỗi không có offset sẽ coi đó là giờ máy (container đặt TZ = UTC, đã xác minh: `/etc/timezone` = `UTC`) → mọi sự kiện bị đẩy sớm **4–5 tiếng**.

Đối chiếu: đường JSON (`ParseNewsEventsFromJson`, `:1857`) đọc trường `date` có sẵn offset (`2026-09-20T19:00:00-04:00`) nên đúng.

**Kịch bản hỏng**
NFP 08:30 ET (12:30 UTC) bị ghi thành 08:30 UTC. Cửa sổ chặn 30 phút kết thúc lúc 09:00 UTC — bot giao dịch xuyên qua tin thật lúc 12:30 mà không có rào chắn nào.

**Đề xuất sửa**
Parse với `DateTimeStyles.None` rồi chuyển đổi tường minh từ `Eastern Standard Time` sang UTC, hoặc bỏ hẳn nhánh XML và dựa vào hub + JSON (hub đã hoạt động tốt, log xác nhận).

---

## C-13 — Báo cáo đóng lệnh dùng Bid/Ask hiện tại thay vì ClosingPrice

**Vị trí**: `cBot/AiAgentBot.cs:1643`, `cBot/FlowRsiBot.cs:2040` (và `exit_time = DateTime.UtcNow` tại `:2182`)
**Mức**: P2 · **Ảnh hưởng**: mọi lệnh đóng, số liệu phân tích

**Cơ chế**
Handler `Positions.Closed` lấy giá thoát từ `Symbol.Bid/Ask` tại **thời điểm handler chạy**, không phải giá khớp thật. FlowRsiBot có xử lý riêng cho SL/TP (`:2042-2045` dùng `pos.StopLoss/TakeProfit`) nhưng các lý do đóng khác vẫn dùng giá live; AiAgentBot không xử lý gì.

Bot Judas làm đúng (`:836-846`): tra `History.FirstOrDefault(h => h.PositionId == ...)` rồi dùng `hist.ClosingPrice`.

**Kịch bản hỏng**
SL bị quét bởi một cú nhọn, giá bật lại ngay trước khi handler chạy → dashboard hiển thị giá thoát chưa từng giao dịch. Mọi thống kê pips/RR dựng trên `exit_price` đều sai.

**Đề xuất sửa**
Áp dụng cách của Judas cho cả hai bot: lấy `ClosingPrice`/`ClosingTime` từ `History` theo `PositionId`, fallback về Bid/Ask nếu không tìm thấy.

---

## C-14 — Fallback XML tải về rồi vứt bỏ, tắt news filter 6 tiếng

**Vị trí**: `cBot/AsianRangeJudasSweepBot.cs:2076-2101` (`TryFetchXmlFallback`)
**Mức**: P2 · **Ảnh hưởng**: 15 bot Judas · điều kiện: nhánh JSON lỗi

**Cơ chế**
```csharp
string xml = reader.ReadToEnd();
_lastNewsFetchTime = DateTime.UtcNow;
Print("[News Filter] XML Fallback news fetched successfully.");
```
Biến `xml` không bao giờ được parse — không có lời gọi `ParseNewsJson`/tương đương. Nhưng `_lastNewsFetchTime` vẫn được cập nhật, mà `CheckNewsEvents` (`:1882`) chỉ fetch lại khi `DateTime.UtcNow - _lastNewsFetchTime > 6 tiếng`.

**Kịch bản hỏng**
JSON lỗi → log báo "fetched successfully" (gây hiểu nhầm) → `_newsEvents` rỗng → `IsNewsPauseActive` luôn trả `false` → **news filter tắt hoàn toàn trong 6 tiếng** mà không có dấu hiệu cảnh báo.

**Đề xuất sửa**
Viết hàm `ParseNewsXml(xml)` thực sự (theo mẫu `ParseNewsEventsFromXml` của FlowRsiBot, nhưng sửa cả lỗi timezone ở C-12), hoặc bỏ nhánh này và **không** cập nhật `_lastNewsFetchTime` khi fetch thất bại để bot thử lại sau 5 phút.

---

## C-15 — Gọi HTTP đồng bộ trên luồng giao dịch trong OnBarClosed

**Vị trí**: `cBot/AsianRangeJudasSweepBot.cs:1883` → `FetchForexFactoryNews` (`:1974`)
**Mức**: P3 · **Ảnh hưởng**: 15 bot Judas · điều kiện: dashboard hoặc ForexFactory chậm

**Cơ chế**
`OnBarClosed` → `CheckNewsEvents` → `FetchForexFactoryNews` dùng `HttpWebRequest` **đồng bộ**:
- Dashboard: timeout 5 giây
- ForexFactory JSON: timeout 10 giây
- XML fallback: timeout 10 giây

Tổng cộng có thể chặn luồng cBot ~25 giây. FlowRsiBot làm đúng: `Task.Run(FetchForexFactoryNewsAsync)` trong `OnStart` (`:415`), chạy nền với vòng lặp 15 phút.

**Kịch bản hỏng**
Dashboard sập đúng lúc đóng nến → luồng bot đứng tới 25 giây: không xử lý tick, nên break-even, trailing stop, `CheckStructuralInvalidation` và `ProcessStagedOrderExecution` đều đóng băng — đúng những giây biến động mạnh nhất của nến.

**Đề xuất sửa**
Chuyển sang `HttpClient` async chạy trên background task như FlowRsiBot.

---

## Vấn đề ngoài 3 file .cs

### X-01 — `close_position` bỏ qua `ctrader_id`
**Vị trí**: `app/portfolio.py:147`
**Mức**: P2

```sql
UPDATE positions SET status='closed', ... WHERE bot_id=? AND symbol=? AND status='open' AND account_id=?
```
Không lọc theo `ctrader_id` dù cBot **có gửi** trường này trong payload. Hiện an toàn vì `MaxPositionsAllowed = 1`, nhưng sẽ đóng nhầm **tất cả** lệnh mở của cùng (bot_id, symbol) ngay khi nâng giới hạn lên > 1.

**Đề xuất**: thêm `AND ctrader_id = ?` khi payload có `ctrader_id`, fallback về logic hiện tại nếu không có.

### X-02 — Judas XAUUSD: sweep buffer 30 pip = $0.30
**Vị trí**: `app/cbot_presets.py:122`
**Mức**: P2

Preset truyền `sweepBufferPips = 30.0` cho XAUUSD. Với vàng 1 pip = $0.01 → buffer chỉ **$0.30**, quá hẹp để phân biệt sweep thật với nhiễu. Chính `AsianRangeJudasSweepBot.cs:517` có logic tự scale đề xuất **500 pip ($5.00)** cho vàng, nhưng nhánh đó chỉ chạy khi `maxAsianRangePips <= 500`, mà preset truyền 8000 → không kích hoạt.

Cùng preset cũng dùng `sweepBufferPips` cho `CheckStructuralInvalidation` (`:1127`), nên ngưỡng "phá vỡ cấu trúc quyết định" của vàng cũng chỉ là $0.30.

**Đề xuất**: nâng `sweep_buffer` của XAUUSD lên khoảng 300–500 pip, đồng bộ với logic auto-scale trong bot.

### X-03 — `breakEvenTrigger` bị bỏ qua vì bot chạy mode R:R
**Vị trí**: `app/cbot_presets.py:70`
**Mức**: P3

Preset truyền `breakEvenTrigger` (đơn vị pip) cho mọi bot Judas, nhưng `breakEvenMode` mặc định là `Risk_Reward_Ratio`, và `ProcessBreakEvenLogic` (`:1538-1560`) chỉ đọc `breakEvenTrigger` trong nhánh `Fixed_Pips`. Tham số được truyền nhưng không có tác dụng — dễ gây hiểu nhầm khi tinh chỉnh.

**Đề xuất**: hoặc truyền thêm `breakEvenMode=Fixed_Pips`, hoặc bỏ `breakEvenTrigger` khỏi preset và chỉnh `breakEvenRrTrigger`.

### X-04 — Dashboard 500: `'list object' has no attribute 'page'`
**Mức**: P2 · **Trạng thái**: chưa xác minh, xảy ra 1 lần

```
Sep 22 09:45:18  GET /demo/dashboard  500 Internal Server Error
jinja2.exceptions.UndefinedError: 'list object' has no attribute 'page'
```
Xảy ra ngay sau khi restart service. Nghi ngờ template mong đối tượng phân trang nhưng route truyền vào một `list` thuần — liên quan commit `feb765d` (paginate Recent Trades). Cần tái hiện để xác nhận là lỗi thật hay chỉ là race lúc khởi động.

---

## OPS-01 — 7 lệnh đang mở mang SL/TP sai từ trước khi vá

**Mức**: P0 · **Cần xử lý tay, tôi không tự đóng/sửa lệnh**

Bản vá C-00 chỉ áp dụng cho lệnh **mới**. Các lệnh mở trước 10:35 UTC vẫn mang SL/TP sai trên broker:

| DB id | Bot | Symbol | Side | Volume | Entry | Mở lúc (UTC) |
|---|---|---|---|---|---|---|
| 2 | audjpy-all-flowrsi | AUDJPY | Sell | 0.09 | 112.125 | 05:00 |
| 7 | ethusd-all-flowrsi | ETHUSD | Buy | 0.34 | 2737.35 | 05:45 |
| 19 | xauusd-all-flowrsi | XAUUSD | Buy | 0.01 | 4319.12 | 08:45 |
| 22 | ustec-all-flowrsi | USTEC | Buy | 0.10 | 30456 | 08:45 |
| 24 | de40-all-flowrsi | DE40 | Buy | 0.10 | 25549.9 | 08:45 |
| 27 | usdjpy-all-flowrsi | USDJPY | Sell | 0.02 | 157.15 | 09:00 |
| 33 | btcusd-all-flowrsi | BTCUSD | Sell | 0.02 | 85834.14 | 10:30 |

Ví dụ XAUUSD #19: SL broker nhận là 4293 pip = **$42.93 rủi ro** thay vì $26 như dự định.

Thêm vào đó (C-10): sau khi restart lúc 10:35, `_initialSlDistances` đã mất, nên bot lấy khoảng cách SL **sai và rất rộng** từ broker để tính R → BreakEven và Trailing Stop của 7 lệnh này gần như không bao giờ kích hoạt.

**Khuyến nghị**: sửa SL/TP thủ công trong cTrader theo mức dự định, hoặc đóng các lệnh này.

---

## Trạng thái xử lý — 2026-09-22

18/19 finding đã đóng trên nhánh `fix/cbot-review-findings`:

| Commit | Findings |
|---|---|
| `705fa74` | C-01, C-02 |
| `f2abb22` | C-03 … C-09 |
| `092d7ce` | C-10 … C-15 |
| `2b81905` | X-01, X-02 |
| `a1c5713` | X-03 |

Test: 335 passed (từ 258). Mẫu test theo PR #31 — contract ở mức source cho `.cs`
(không có .NET toolchain trong suite Python), test hành vi thật cho phần `app/`.

**Bỏ qua theo quyết định của chủ dự án**: OPS-01 và X-04.

**Chưa compile**: các file `.cs` chưa build lần nào. Đã kiểm tra cân bằng `{}`/`()`
khớp HEAD sau mỗi batch và bắt được 1 lỗi compile thật (thiếu `using System.Globalization;`
trong Judas), nhưng không thay thế được compiler.

**Lưu ý khi deploy**: `app/portfolio.py` chạy `ALTER TABLE positions ADD COLUMN ctrader_id`
lúc init — additive, nullable, an toàn chạy lại, nhưng sẽ chạm PostgreSQL production
ở lần `systemctl restart agentfx.service` đầu tiên.

---

## Phương pháp & phạm vi

**Đã kiểm tra**
- Đọc toàn bộ 3 file (8.981 dòng): tham số, vòng đời, tính tín hiệu, quản lý lệnh, giao tiếp AI, báo cáo, news filter, tick stream.
- Log 45 container (`docker logs`), lọc lỗi/exception/security alert/rejected.
- Journal `agentfx.service` từ 04:00 UTC 22/09.
- Bảng `positions` (34 dòng: 24 closed, 10 open) và đối chiếu từng lệnh với log container.
- Đối chiếu preset (`app/cbot_presets.py`) với tham số thực tế của container (`docker inspect`).
- Đối chiếu lớp bảo vệ phía server (`app/server.py`, `app/portfolio.py`) xem bot nào được bảo vệ, bot nào không.

**Chưa kiểm tra**
- Vùng DCA của bot Judas (`ProcessDCALogic`, `:1751-1866`) — mặc định `enableDCA = false`, không bot nào bật.
- Nhánh AI trực tiếp (`QueryDirectQwenApiAsync`) — mọi container chạy `UseDirectAiApi=false`.
- Logic license/expiry, UI panel, vẽ chart.
- Frontend/template (X-04 chỉ ghi nhận từ log, chưa tái hiện).
