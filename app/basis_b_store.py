"""Tables of the basis B demo (docs/basis-b-demo.md): the daily universe, one row per signal / paper trade, one row per
hourly run. Times are epoch milliseconds (UTC) for bar hours and ISO strings for wall-clock stamps."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from app.db import get_db_connection

TRADE_COLUMNS = (
    "symbol", "spot", "factor", "rank", "signal_ms", "entry_ms", "b_h", "m_h", "d_bp",
    "perp_open_in", "spot_open_in", "perp_vwap_in", "spot_vwap_in", "perp_fill_in", "spot_fill_in",
    "perp_spread_bp_in", "spot_spread_bp_in", "entry_at", "notional",
    "borrowable", "inventory", "inventory_usd", "rate_hourly_in", "max_borrowable", "fillable", "borrow_note",
    "status", "exit_ms", "exit_reason", "perp_open_out", "spot_open_out", "perp_vwap_out", "spot_vwap_out",
    "exit_at", "funding", "rates_json", "net_registered", "net_book", "fund_part", "price_part",
)


def init_schema(db_target=None) -> None:
    conn = get_db_connection(db_target)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS basis_b_universe (
                day_ms BIGINT NOT NULL,
                symbol TEXT NOT NULL,
                spot TEXT NOT NULL,
                factor REAL NOT NULL,
                rank INTEGER NOT NULL,
                PRIMARY KEY (day_ms, symbol)
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS basis_b_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                spot TEXT NOT NULL,
                factor REAL NOT NULL,
                rank INTEGER NOT NULL,
                signal_ms BIGINT NOT NULL,
                entry_ms BIGINT NOT NULL,
                b_h REAL NOT NULL,
                m_h REAL NOT NULL,
                d_bp REAL NOT NULL,
                perp_open_in REAL,
                spot_open_in REAL,
                perp_vwap_in REAL,
                spot_vwap_in REAL,
                perp_fill_in REAL,
                spot_fill_in REAL,
                perp_spread_bp_in REAL,
                spot_spread_bp_in REAL,
                entry_at TEXT NOT NULL,
                notional REAL NOT NULL,
                borrowable INTEGER,
                inventory REAL,
                inventory_usd REAL,
                rate_hourly_in REAL,
                max_borrowable REAL,
                fillable INTEGER,
                borrow_note TEXT,
                status TEXT NOT NULL,
                exit_ms BIGINT,
                exit_reason TEXT,
                perp_open_out REAL,
                spot_open_out REAL,
                perp_vwap_out REAL,
                spot_vwap_out REAL,
                exit_at TEXT,
                funding REAL,
                rates_json TEXT,
                net_registered REAL,
                net_book REAL,
                fund_part REAL,
                price_part REAL,
                UNIQUE (symbol, entry_ms)
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS basis_b_runs (
                hour_ms BIGINT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                coins INTEGER,
                signals INTEGER,
                exits INTEGER,
                has_secret INTEGER,
                error TEXT
            )""")
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------------------------------------------- universe

def save_universe(day_ms: int, rows: List[Dict[str, Any]], db_target=None) -> None:
    conn = get_db_connection(db_target)
    try:
        conn.execute("DELETE FROM basis_b_universe WHERE day_ms = ?", (day_ms,))
        for r in rows:
            conn.execute("INSERT INTO basis_b_universe (day_ms, symbol, spot, factor, rank) VALUES (?,?,?,?,?)",
                         (day_ms, r["symbol"], r["spot"], r["factor"], r["rank"]))
        conn.commit()
    finally:
        conn.close()


def load_universe(day_ms: int, db_target=None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_target)
    try:
        return [dict(r) for r in conn.execute(
            "SELECT symbol, spot, factor, rank FROM basis_b_universe WHERE day_ms = ? ORDER BY rank",
            (day_ms,)).fetchall()]
    finally:
        conn.close()


# ------------------------------------------------------------------------------------------------------------- trades

def insert_trade(row: Dict[str, Any], db_target=None) -> None:
    cols = [c for c in TRADE_COLUMNS if c in row]
    conn = get_db_connection(db_target)
    try:
        conn.execute(f"INSERT INTO basis_b_trades ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})",
                     tuple(row[c] for c in cols))
        conn.commit()
    finally:
        conn.close()


def update_trade(trade_id: int, fields: Dict[str, Any], db_target=None) -> None:
    cols = [c for c in fields if c in TRADE_COLUMNS]
    if not cols:
        return
    conn = get_db_connection(db_target)
    try:
        conn.execute(f"UPDATE basis_b_trades SET {', '.join(c + ' = ?' for c in cols)} WHERE id = ?",
                     tuple(fields[c] for c in cols) + (trade_id,))
        conn.commit()
    finally:
        conn.close()


def load_trades(status: Optional[str] = None, db_target=None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_target)
    try:
        if status:
            rows = conn.execute("SELECT * FROM basis_b_trades WHERE status = ? ORDER BY entry_ms, id", (status,))
        else:
            rows = conn.execute("SELECT * FROM basis_b_trades ORDER BY entry_ms, id")
        out = [dict(r) for r in rows.fetchall()]
    finally:
        conn.close()
    for r in out:
        r["rates"] = json.loads(r["rates_json"]) if r.get("rates_json") else []
    return out


# --------------------------------------------------------------------------------------------------------------- runs

def run_started(hour_ms: int, started_at: str, db_target=None) -> bool:
    """Claim the run of this hour; False if a run already finished it (cron fires several times an hour)."""
    conn = get_db_connection(db_target)
    try:
        row = conn.execute("SELECT finished_at FROM basis_b_runs WHERE hour_ms = ?", (hour_ms,)).fetchone()
        if row is not None and row["finished_at"]:
            return False
        if row is None:
            conn.execute("INSERT INTO basis_b_runs (hour_ms, started_at) VALUES (?, ?)", (hour_ms, started_at))
        else:
            conn.execute("UPDATE basis_b_runs SET started_at = ?, error = NULL WHERE hour_ms = ?",
                         (started_at, hour_ms))
        conn.commit()
        return True
    finally:
        conn.close()


def run_finished(hour_ms: int, finished_at: Optional[str], coins: int, signals: int, exits: int, has_secret: bool,
                 error: Optional[str] = None, db_target=None) -> None:
    conn = get_db_connection(db_target)
    try:
        conn.execute("UPDATE basis_b_runs SET finished_at = ?, coins = ?, signals = ?, exits = ?, has_secret = ?,"
                     " error = ? WHERE hour_ms = ?",
                     (finished_at, coins, signals, exits, int(has_secret), error, hour_ms))
        conn.commit()
    finally:
        conn.close()


def last_runs(limit: int = 1, db_target=None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_target)
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM basis_b_runs ORDER BY hour_ms DESC LIMIT ?", (limit,)).fetchall()]
    finally:
        conn.close()
