import sqlite3
from src.db.connection import get_connection, DB_PATH

def insert_transaction(date: str, amount: float, category: str, description: str, txn_type: str) -> None:
    """Insert a new transaction into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO transactions (date, amount, category, description, type) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, description, txn_type.lower())
        )

def get_summary_data(
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    category: str = None,
    txn_type: str = None
):
    """Query aggregated summary data grouped by type and category."""
    with get_connection() as conn:
        conditions = []
        params = []

        if month:
            conditions.append("date LIKE ?")
            params.append(f"{month}%")
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        if category:
            conditions.append("LOWER(category) = LOWER(?)")
            params.append(category)
        if txn_type:
            conditions.append("LOWER(type) = LOWER(?)")
            params.append(txn_type)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT type, category, SUM(amount) as total, COUNT(*) as count FROM transactions{where_clause} GROUP BY type, category ORDER BY type, total DESC"

        return conn.execute(query, params).fetchall()

def get_transactions_data(
    category: str = None,
    txn_type: str = None,
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    min_amount: float = None,
    max_amount: float = None,
    search: str = None,
    limit: int = 50
):
    """Query transaction records matching filter criteria."""
    with get_connection() as conn:
        query = "SELECT id, date, amount, category, description, type FROM transactions"
        conditions = []
        params = []

        if category:
            conditions.append("LOWER(category) = LOWER(?)")
            params.append(category)
        if txn_type:
            conditions.append("LOWER(type) = LOWER(?)")
            params.append(txn_type)
        if month:
            conditions.append("date LIKE ?")
            params.append(f"{month}%")
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        if min_amount is not None:
            conditions.append("amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("amount <= ?")
            params.append(max_amount)
        if search:
            conditions.append("(description LIKE ? OR category LIKE ?)")
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)

        return conn.execute(query, params).fetchall()

def get_transaction_by_id(transaction_id: int):
    """Fetch a single transaction record by ID."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, date, amount, category, description, type FROM transactions WHERE id = ?",
            (transaction_id,)
        ).fetchone()

def update_transaction_data(transaction_id: int, updates_dict: dict) -> bool:
    """Update fields of a specific transaction record."""
    if not updates_dict:
        return False
    with sqlite3.connect(DB_PATH) as conn:
        set_clauses = [f"{col} = ?" for col in updates_dict.keys()]
        params = list(updates_dict.values())
        params.append(transaction_id)

        query = f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = ?"
        conn.execute(query, params)
        return True

def delete_transaction_data(transaction_id: int) -> None:
    """Delete a transaction record by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
