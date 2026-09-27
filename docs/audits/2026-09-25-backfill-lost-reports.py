"""Bù sổ 3 lệnh chạy ngoài sổ (báo cáo open bị rơi) vào bảng positions của Postgres production.

Cách chạy, từ repo local. Script được pipe qua stdin, không copy file nào lên VPS:

    # 1. Kiểm tra (mặc định, chỉ đọc): in các dòng sẽ thêm, EXPLAIN câu INSERT, ledger trước/sau
    ssh forge@204.168.144.232 'cd /home/forge/AgentFxTrading && .venv/bin/python -' \
        < docs/audits/2026-09-25-backfill-lost-reports.py

    # 2. Ghi thật (một transaction)
    ssh forge@204.168.144.232 'cd /home/forge/AgentFxTrading && .venv/bin/python - --apply' \
        < docs/audits/2026-09-25-backfill-lost-reports.py

Chạy lại không sao: ctrader_id đã có dòng trong DB thì bỏ qua.

Nguồn dữ liệu (quét log json của cả 45 container, từ 23/09 02:29 UTC, so với positions theo ctrader_id):
- Container nào cũng có dòng cTrader "SUCCEEDED, Position PID…", ngay sau đó là
  "Failed to report position open", và không có dòng DB nào mang ctrader_id đó.
- pnl là số bot báo khi đóng lệnh. Server đã bỏ qua báo cáo đóng đó
  ("Close position ignored … ctrader_id=…" trong logs/agent_2026-09-24.log).
- Sau khi bù, ledger (balance − Σpnl) của demo-10115236 phải về đúng 2000,00.
  Trước khi bù là 2008,60 = 2000 + (−11,62 − 1,91 + 22,13).
"""
import sys

import psycopg2
from dotenv import dotenv_values

APPLY = "--apply" in sys.argv[1:]
ACCOUNT = "demo-10115236"
DEPOSIT = 2000.00

# Thời gian là UTC. Giá lấy từ log bot. Riêng EURJPY là ước tính, đánh dấu "~".
ROWS = [
    # us30-all-flowrsi, 14:15 VN. [Order Executed] Buy 0.10 lots at 51404.8, SL 51290.13571,
    # TP 51571.24643. Đóng 15:13:48 VN, PnL −11.62. US30: pnl = Δgiá × lot (khớp với id 82 và 90),
    # nên giá ra = 51404.8 − 116.2 = 51288.6, thấp hơn SL 1.5 điểm: chạm SL.
    dict(ctrader_id=675558107, bot_id="cbot-demo-demo-us30-all-flowrsi", symbol="US30", side="Buy",
         volume=0.1, entry_price=51404.8, sl_pips=1151.6, tp_pips=1659.5,
         sl_price=51290.13571, tp_price=51571.24643,
         entry_time="2026-09-24 07:15:14+00", exit_time="2026-09-24 08:13:48+00",
         exit_price=51288.6, pnl=-11.62,
         close_reason="StopLoss (recovered: open report lost)"),
    # eurjpy-london (AiAgentBot), 14:45 VN. Sell 1000 units, SL 28.6p, TP 38.1p. Không có SL
    # modify, không có dòng "Closing position" của bot. Đóng 16:00:35 VN, PnL −1.91: chạm SL.
    # Bot này không log giá vào. ~180.210 là giá eurjpy-all-flowrsi khớp Sell 6 s trước đó
    # (id 66). Mức SL/TP tính từ số pip. Giá ra ~ = giá vào + 0.292, tức −1.85 $ gross + 0.06 $
    # commission, quy đổi USDJPY ≈ 157.9.
    # Giá chính xác xem trong cTrader History, position 675569508.
    dict(ctrader_id=675569508, bot_id="cbot-demo-demo-eurjpy-london", symbol="EURJPY", side="Sell",
         volume=0.01, entry_price=180.210, sl_pips=28.6, tp_pips=38.1,
         sl_price=180.496, tp_price=179.829,
         entry_time="2026-09-24 07:45:37+00", exit_time="2026-09-24 09:00:35+00",
         exit_price=180.502, pnl=-1.91,
         close_reason="StopLoss (recovered: open report lost, est. prices)"),
    # us30-all-flowrsi, 23:15 VN. [Order Executed] Buy 0.10 lots at 51222.7, SL 51066.03214,
    # TP 51442.90179. Break-even rồi trailing: SL 51280.83, TP 51439.4 (lần modify cuối, 16:16:52 UTC).
    # Đóng 23:17:29 VN, PnL +22.13 → giá ra = 51222.7 + 221.3 = 51444.0, cao hơn TP: chạm TP.
    # Lệnh này đóng 15 phút trước khi server có bản tự bù sổ (PR #52) khởi động lại lúc 16:32 UTC.
    dict(ctrader_id=675864311, bot_id="cbot-demo-demo-us30-all-flowrsi", symbol="US30", side="Buy",
         volume=0.1, entry_price=51222.7, sl_pips=1601.7, tp_pips=2167.0,
         sl_price=51280.83, tp_price=51439.4,
         entry_time="2026-09-24 16:15:12+00", exit_time="2026-09-24 16:17:29+00",
         exit_price=51444.0, pnl=22.13,
         close_reason="TakeProfit (recovered: open report lost)"),
]

COLS = ("bot_id", "symbol", "side", "volume", "initial_volume", "entry_price", "sl_pips", "tp_pips",
        "sl_price", "tp_price", "entry_time", "exit_time", "exit_price", "pnl", "status",
        "account_id", "ctrader_id", "close_reason")
# NOT EXISTS: an toàn cả khi server vừa tự bù dòng đó giữa lúc kiểm tra và lúc ghi.
INSERT = (f"INSERT INTO positions ({', '.join(COLS)}) "
          f"SELECT {', '.join(['%s'] * len(COLS))} "
          f"WHERE NOT EXISTS (SELECT 1 FROM positions WHERE account_id = %s AND ctrader_id = %s)")


def values(r):
    row = dict(r, initial_volume=r["volume"], status="closed", account_id=ACCOUNT)
    return [row[c] for c in COLS] + [ACCOUNT, r["ctrader_id"]]


def ledger(cur):
    cur.execute("SELECT last_balance FROM accounts WHERE account_id = %s", (ACCOUNT,))
    balance = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(pnl), 0), COUNT(*) FROM positions WHERE account_id = %s", (ACCOUNT,))
    total, count = cur.fetchone()
    return float(balance), round(float(total), 2), count


url = dotenv_values(".env").get("DATABASE_URL") or ""  # không in ra
if not url.startswith("postgres"):
    sys.exit("ABORT: .env không có DATABASE_URL Postgres. Hãy chạy trong /home/forge/AgentFxTrading")
conn = psycopg2.connect(url)
conn.set_session(readonly=not APPLY)
cur = conn.cursor()
cur.execute("SET TIME ZONE 'UTC'")

cur.execute("SELECT ctrader_id, id, status, pnl FROM positions WHERE ctrader_id = ANY(%s)",
            ([r["ctrader_id"] for r in ROWS],))
existing = {row[0]: row[1:] for row in cur.fetchall()}
todo = [r for r in ROWS if r["ctrader_id"] not in existing]
for cid, (rid, status, pnl) in existing.items():
    print(f"Bỏ qua #{cid}: đã có dòng id={rid} ({status}, pnl={pnl})")

balance, total, count = ledger(cur)
add = round(sum(r["pnl"] for r in todo), 2)
print(f"Ledger trước: balance {balance:.2f} − Σpnl {total:.2f} ({count} dòng) = {balance - total:.2f}")
print(f"Sẽ thêm {len(todo)} dòng, Σpnl {add:+.2f} → ledger sau = {balance - total - add:.2f} (mong đợi {DEPOSIT:.2f})")
for r in todo:
    print(f"  #{r['ctrader_id']} {r['bot_id']} {r['symbol']} {r['side']} {r['volume']} "
          f"@ {r['entry_price']} → {r['exit_price']} pnl {r['pnl']:+.2f} | {r['close_reason']}")

if not todo:
    print("Không còn gì để bù.")
    sys.exit(0)

if not APPLY:
    # EXPLAIN kiểm tra câu INSERT (cột, kiểu dữ liệu) mà không ghi gì, chạy được trong session read-only.
    for r in todo:
        cur.execute("EXPLAIN " + INSERT, values(r))
        cur.fetchall()
    conn.rollback()
    print("DRY RUN: câu INSERT hợp lệ, chưa ghi gì. Thêm --apply để ghi.")
    sys.exit(0)

try:
    inserted = 0
    for r in todo:
        cur.execute(INSERT, values(r))
        inserted += cur.rowcount
    conn.commit()
except Exception:
    conn.rollback()
    raise
balance, total, count = ledger(cur)
drift = round(balance - total - DEPOSIT, 2)
print(f"ĐÃ GHI {inserted} dòng. Ledger sau: {balance:.2f} − {total:.2f} ({count} dòng) = {balance - total:.2f}"
      + ("  OK" if abs(drift) < 0.01 else f"  CẢNH BÁO: lệch {drift:+.2f} so với {DEPOSIT:.2f}"))
