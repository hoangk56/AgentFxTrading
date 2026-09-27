"""Account ledger: the balance the bots' trades and the user's deposits / withdrawals explain, against the broker's.

    expected = 0 + cash movements + P&L of every closed position of the account
    discrepancy = broker balance - expected

The ledger starts from 0. The broker balance is the last one the server logged (account_balance_log, written by
AccountRegistry.upsert_from_bot on every change). Cash movements are entered on the dashboard, either by hand or by
confirming a balance change that no closed position explains: those "unexplained" changes are a deposit, a
withdrawal, or a trade whose report was lost. The first balance the server logged is a change from 0: the closes
booked before it explain a part, the rest is money deposited before the server kept a log. The daily-audit collector
reads the same functions.
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
    positions with `_t` (parsed exit_time) and `pnl`, oldest first. Each change is matched with one close booked
    near it, or with all the unused closes near it together (several bots closing at the same minute). A change
    already confirmed as a cash movement (`confirmed_ids`) is not reported, and consumes no close.

    The first change (no balance before it) goes from 0: every close booked up to it explains a part, and what they
    leave is reported (`opening`). A close is reported before the tick that carries its balance, so the closes
    booked after the first balance belong to the next changes.
    """
    used, out = set(), []
    prev_t = None
    for c in changes:
        t = c["_t"]
        if c.get("balance_before") is None:
            earlier = [p for p in closes if p["id"] not in used and p["_t"] <= t]
            used.update(p["id"] for p in earlier)
            earlier_pnl = sum(p["pnl"] for p in earlier)
            rest = c["balance"] - earlier_pnl
            if c["id"] not in confirmed_ids and abs(rest) > TOLERANCE:
                out.append({"log_id": c["id"], "recorded_at": _db_time(t), "balance_before": 0.0,
                            "balance": c["balance"], "delta": round(rest, 2), "nearby_closes": [], "opening": True,
                            "earlier_closes": len(earlier), "earlier_pnl": round(earlier_pnl, 2)})
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
                        "nearby_closes": [round(p["pnl"], 2) for p in near], "opening": False})
        prev_t = t
    return out


def _changes_and_closes(conn, account_id: str):
    """The account's balance log and closed positions, parsed and oldest first."""
    changes = _rows(conn, "SELECT id, recorded_at, balance_before, balance FROM account_balance_log "
                          "WHERE account_id = ? ORDER BY id", (account_id,))
    for c in changes:
        c["_t"] = parse_utc(c["recorded_at"])
    closes = _rows(conn, "SELECT id, exit_time, pnl FROM positions WHERE account_id = ? AND status = 'closed' "
                         "AND pnl IS NOT NULL", (account_id,))
    for p in closes:
        p["_t"] = parse_utc(p["exit_time"])
    return [c for c in changes if c["_t"]], sorted((p for p in closes if p["_t"]), key=lambda p: p["_t"])


def account_ledger(conn, account: Dict) -> Dict:
    """The ledger of one account (a row of `accounts`)."""
    account_id = account["account_id"]
    changes, closes = _changes_and_closes(conn, account_id)
    movements = _rows(conn, "SELECT id, occurred_at, amount, note, balance_log_id FROM account_cash_movements "
                            "WHERE account_id = ? ORDER BY occurred_at, id", (account_id,))
    deposits = sum(m["amount"] for m in movements if m["amount"] > 0)
    withdrawals = -sum(m["amount"] for m in movements if m["amount"] < 0)
    closed_pnl = sum(p["pnl"] for p in closes)
    expected = deposits - withdrawals + closed_pnl
    result = {
        "account_id": account_id, "label": account.get("label"), "account_type": account.get("account_type"),
        "account_number": account.get("account_number"),
        "deposits": round(deposits, 2), "withdrawals": round(withdrawals, 2),
        "closed_pnl": round(closed_pnl, 2), "closed_trades": len(closes), "expected_balance": round(expected, 2),
        "broker_balance": None, "broker_balance_at": None, "discrepancy": None, "balanced": None,
        "movements": movements, "unexplained": [],
    }
    if not changes:
        return result

    broker = changes[-1]["balance"]
    discrepancy = broker - expected
    confirmed = {m["balance_log_id"] for m in movements if m["balance_log_id"] is not None}
    result.update(
        broker_balance=round(broker, 2), broker_balance_at=_db_time(changes[-1]["_t"]),
        discrepancy=round(discrepancy, 2), balanced=abs(discrepancy) <= TOLERANCE,
        unexplained=match_balance_changes(changes, closes, confirmed),
    )
    return result


def ledgers(conn, accounts: List[Dict]) -> List[Dict]:
    return [account_ledger(conn, a) for a in accounts]


def add_movement(conn, account_id: str, amount, occurred_at=None, note: Optional[str] = None,
                 balance_log_id: Optional[int] = None) -> int:
    """Record a deposit (amount > 0) or a withdrawal (< 0). With `balance_log_id` the movement confirms that
    balance change: its time is taken from the log, its amount is what no close explains (the whole change, or for
    the first balance what the earlier closes leave), and the change leaves the unexplained list."""
    note = (note or "").strip()
    if len(note) > MAX_NOTE or any(ch in note for ch in "\r\n\x00"):
        raise LedgerError(f"Note: at most {MAX_NOTE} characters on one line")
    if balance_log_id is not None:
        log = _rows(conn, "SELECT id, account_id, recorded_at, balance_before, balance FROM account_balance_log "
                          "WHERE id = ?", (balance_log_id,))
        if not log or log[0]["account_id"] != account_id:
            raise LedgerError("That balance change does not belong to this account")
        if _rows(conn, "SELECT id FROM account_cash_movements WHERE balance_log_id = ?", (balance_log_id,)):
            raise LedgerError("That balance change is already recorded")
        changes, closes = _changes_and_closes(conn, account_id)
        confirmed = {r["balance_log_id"] for r in _rows(
            conn, "SELECT balance_log_id FROM account_cash_movements WHERE account_id = ? "
                  "AND balance_log_id IS NOT NULL", (account_id,))}
        entry = next((u for u in match_balance_changes(changes, closes, confirmed) if u["log_id"] == balance_log_id),
                     None)
        if entry is None:
            raise LedgerError("The closed trades explain that balance change: it is not a deposit or a withdrawal")
        amount = entry["delta"]
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
