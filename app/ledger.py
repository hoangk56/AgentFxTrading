"""Account ledger: the balance the bots' trades and the user's deposits / withdrawals explain, against the broker's.

    expected = opening balance + cash movements + P&L of the positions closed since the opening
    discrepancy = broker balance - expected

The opening balance is the first balance the server logged for the account (account_balance_log, written by
AccountRegistry.upsert_from_bot on every change). Cash movements are entered on the dashboard, either by hand or by
confirming a balance change that no closed position explains: those "unexplained" changes are a deposit, a
withdrawal, or a trade whose report was lost. The daily-audit collector reads the same functions.
"""
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

# A balance change is a trade when the closes booked within this many seconds of it add up to it: the bot posts its
# close report and its 10 s ticks carry the balance, so either may reach the server first.
MATCH_SECONDS = 180
# Below this a discrepancy is rounding, not money.
TOLERANCE = 0.05
MAX_AMOUNT = 1e9
MAX_NOTE = 200


class LedgerError(ValueError):
    """Input the ledger refuses; the message is shown to the user."""


def init_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS account_cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            note TEXT,
            balance_log_id INTEGER UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cash_movements_account ON account_cash_movements(account_id)")


def parse_utc(value) -> Optional[datetime]:
    """A DB or API timestamp as aware UTC: '2026-09-24 10:10:54.15+00' (PostgreSQL), '2026-09-24 10:10:54'
    (SQLite, UTC) or ISO 8601 with 'Z'. None when empty or unparseable."""
    if not value:
        return None
    s = str(value).strip().replace("T", " ").replace("Z", "+00:00")
    if re.search(r"[+-]\d\d$", s):
        s += ":00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _db_time(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _rows(conn, sql: str, params=()) -> List[Dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def match_balance_changes(changes: List[Dict], closes: List[Dict], confirmed_ids=()) -> List[Dict]:
    """The balance changes that no closed position explains, oldest first.

    `changes` are account_balance_log rows with `_t` (parsed recorded_at), oldest first; `closes` are closed
    positions with `_t` (parsed exit_time) and `pnl`. Each change is matched with one close booked near it, or
    with all the unused closes near it together (several bots closing at the same minute). A change already
    confirmed as a cash movement (`confirmed_ids`) is not reported, and consumes no close.
    """
    used, out = set(), []
    prev_t = None
    for c in changes:
        t = c["_t"]
        if c.get("balance_before") is None:
            prev_t = t
            continue
        delta = c["balance"] - c["balance_before"]
        if c["id"] in confirmed_ids:
            prev_t = t
            continue
        lo = (prev_t or t) - timedelta(seconds=MATCH_SECONDS)
        hi = t + timedelta(seconds=MATCH_SECONDS)
        near = [p for p in closes if p["id"] not in used and lo < p["_t"] <= hi]
        tol = max(TOLERANCE, abs(delta) * 0.005)
        single = min(near, key=lambda p: abs(p["pnl"] - delta), default=None)
        if single is not None and abs(single["pnl"] - delta) <= tol:
            used.add(single["id"])
        elif near and abs(sum(p["pnl"] for p in near) - delta) <= tol:
            used.update(p["id"] for p in near)
        else:
            out.append({"log_id": c["id"], "recorded_at": _db_time(t), "balance_before": c["balance_before"],
                        "balance": c["balance"], "delta": round(delta, 2),
                        "nearby_closes": [round(p["pnl"], 2) for p in near]})
        prev_t = t
    return out


def account_ledger(conn, account: Dict) -> Dict:
    """The ledger of one account (a row of `accounts`)."""
    account_id = account["account_id"]
    changes = _rows(conn, "SELECT id, recorded_at, balance_before, balance FROM account_balance_log "
                          "WHERE account_id = ? ORDER BY id", (account_id,))
    for c in changes:
        c["_t"] = parse_utc(c["recorded_at"])
    changes = [c for c in changes if c["_t"]]
    movements = _rows(conn, "SELECT id, occurred_at, amount, note, balance_log_id FROM account_cash_movements "
                            "WHERE account_id = ? ORDER BY occurred_at, id", (account_id,))
    result = {
        "account_id": account_id, "label": account.get("label"), "account_type": account.get("account_type"),
        "account_number": account.get("account_number"),
        "opening_balance": None, "opening_at": None, "deposits": 0.0, "withdrawals": 0.0, "closed_pnl": 0.0,
        "closed_trades": 0, "expected_balance": None, "broker_balance": None, "broker_balance_at": None,
        "discrepancy": None, "balanced": None, "movements": [], "unexplained": [],
    }
    if not changes:
        result["movements"] = [dict(m, counted=False) for m in movements]
        return result

    opening = changes[0]
    opening_t = opening["_t"]
    closes = _rows(conn, "SELECT id, exit_time, pnl FROM positions WHERE account_id = ? AND status = 'closed' "
                         "AND pnl IS NOT NULL", (account_id,))
    for p in closes:
        p["_t"] = parse_utc(p["exit_time"])
    closes = sorted((p for p in closes if p["_t"] and p["_t"] > opening_t), key=lambda p: p["_t"])

    counted = []
    for m in movements:
        m_t = parse_utc(m["occurred_at"])
        m["counted"] = bool(m_t and m_t >= opening_t)
        if m["counted"]:
            counted.append(m["amount"])
    deposits = sum(a for a in counted if a > 0)
    withdrawals = -sum(a for a in counted if a < 0)
    closed_pnl = sum(p["pnl"] for p in closes)
    expected = opening["balance"] + deposits - withdrawals + closed_pnl
    broker = changes[-1]["balance"]
    discrepancy = broker - expected
    confirmed = {m["balance_log_id"] for m in movements if m["balance_log_id"] is not None}
    result.update(
        opening_balance=round(opening["balance"], 2), opening_at=_db_time(opening_t),
        deposits=round(deposits, 2), withdrawals=round(withdrawals, 2),
        closed_pnl=round(closed_pnl, 2), closed_trades=len(closes),
        expected_balance=round(expected, 2), broker_balance=round(broker, 2),
        broker_balance_at=_db_time(changes[-1]["_t"]),
        discrepancy=round(discrepancy, 2), balanced=abs(discrepancy) <= TOLERANCE,
        movements=movements, unexplained=match_balance_changes(changes, closes, confirmed),
    )
    return result


def ledgers(conn, accounts: List[Dict]) -> List[Dict]:
    return [account_ledger(conn, a) for a in accounts]


def add_movement(conn, account_id: str, amount, occurred_at=None, note: Optional[str] = None,
                 balance_log_id: Optional[int] = None) -> int:
    """Record a deposit (amount > 0) or a withdrawal (< 0). With `balance_log_id` the movement confirms that
    balance change: its time and amount are taken from the log and the change leaves the unexplained list."""
    note = (note or "").strip()
    if len(note) > MAX_NOTE or any(ch in note for ch in "\r\n\x00"):
        raise LedgerError(f"Note: at most {MAX_NOTE} characters on one line")
    if balance_log_id is not None:
        log = _rows(conn, "SELECT id, account_id, recorded_at, balance_before, balance FROM account_balance_log "
                          "WHERE id = ?", (balance_log_id,))
        if not log or log[0]["account_id"] != account_id:
            raise LedgerError("That balance change does not belong to this account")
        if log[0]["balance_before"] is None:
            raise LedgerError("The first balance of an account is its opening balance, not a movement")
        if _rows(conn, "SELECT id FROM account_cash_movements WHERE balance_log_id = ?", (balance_log_id,)):
            raise LedgerError("That balance change is already recorded")
        amount = round(log[0]["balance"] - log[0]["balance_before"], 2)
        when = parse_utc(log[0]["recorded_at"])
    else:
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise LedgerError("Amount: expected a number")
        if not math.isfinite(amount) or amount == 0 or abs(amount) >= MAX_AMOUNT:
            raise LedgerError("Amount: a non-zero number (positive = deposit, negative = withdrawal)")
        amount = round(amount, 2)
        when = parse_utc(occurred_at) if occurred_at else datetime.now(timezone.utc)
        if when is None:
            raise LedgerError("Time: expected an ISO date and time")
        if when > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise LedgerError("Time: a movement cannot be in the future")
    row = conn.execute("INSERT INTO account_cash_movements (account_id, occurred_at, amount, note, balance_log_id) "
                       "VALUES (?, ?, ?, ?, ?) RETURNING id",
                       (account_id, _db_time(when), amount, note or None, balance_log_id)).fetchone()
    conn.commit()
    return int(row[0])


def delete_movement(conn, movement_id: int) -> bool:
    deleted = conn.execute("DELETE FROM account_cash_movements WHERE id = ?", (movement_id,)).rowcount > 0
    conn.commit()
    return deleted
