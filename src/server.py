from mcp.server.fastmcp import FastMCP
import sqlite3
from datetime import datetime

# Initialize the server
mcp = FastMCP("Personal Budget Server")

def init_db():
    """Ensure the SQLite database and transactions table exist."""
    with sqlite3.connect("budget.db") as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                type TEXT
            )
        ''')

@mcp.tool()
def add_transaction(amount: float, category: str, description: str, type: str = "expense", date: str = None) -> str:
    """
    Add a new income or expense transaction to the budget.
    - type: Must be either 'expense' or 'income' (defaults to 'expense').
    - date: Optional transaction date formatted as YYYY-MM-DD or ISO string (defaults to current date if omitted).
    """
    txn_date = datetime.now().strftime("%Y-%m-%d")
    if date:
        date_str = date.strip()
        if len(date_str) >= 10 and date_str[4] in ('-', '/') and date_str[7] in ('-', '/'):
            txn_date = date_str[:10].replace('/', '-')
        else:
            try:
                txn_date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
            except Exception:
                txn_date = date_str

    with sqlite3.connect("budget.db") as conn:
        conn.execute(
            "INSERT INTO transactions (date, amount, category, description, type) VALUES (?, ?, ?, ?, ?)",
            (txn_date, amount, category, description, type.lower())
        )
    return f"Successfully logged {type} of ${amount:.2f} for {category} on {txn_date}."

@mcp.tool()
def get_summary(
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    category: str = None,
    type: str = None,
    by_category: bool = False
) -> str:
    """
    Get a summary of expenses, income, and net balance with flexible filtering and optional category breakdown.
    - month: Filter by month (YYYY-MM).
    - start_date: Filter starting from date (YYYY-MM-DD).
    - end_date: Filter ending at date (YYYY-MM-DD).
    - category: Filter by specific category (case-insensitive).
    - type: Filter by transaction type ('expense' or 'income').
    - by_category: Set to True to include detailed category breakdown.
    """
    with sqlite3.connect("budget.db") as conn:
        conn.row_factory = sqlite3.Row
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
        if type:
            conditions.append("LOWER(type) = LOWER(?)")
            params.append(type)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT type, category, SUM(amount) as total, COUNT(*) as count FROM transactions{where_clause} GROUP BY type, category ORDER BY type, total DESC"

        results = conn.execute(query, params).fetchall()

    if not results or all(row['total'] is None for row in results):
        return "No transactions found matching the specified summary criteria."

    total_income = 0.0
    total_expense = 0.0
    income_categories = []
    expense_categories = []

    for row in results:
        t_type = (row['type'] or '').lower()
        cat = row['category']
        amt = row['total'] or 0.0
        cnt = row['count']

        if t_type == 'income':
            total_income += amt
            income_categories.append(f"  - {cat}: ${amt:.2f} ({cnt} transaction{'s' if cnt > 1 else ''})")
        elif t_type == 'expense':
            total_expense += amt
            expense_categories.append(f"  - {cat}: ${amt:.2f} ({cnt} transaction{'s' if cnt > 1 else ''})")

    period_str = ""
    if month:
        period_str = f" for {month}"
    elif start_date and end_date:
        period_str = f" from {start_date} to {end_date}"
    elif start_date:
        period_str = f" from {start_date}"
    elif end_date:
        period_str = f" up to {end_date}"

    output = [f"--- Financial Summary{period_str} ---"]

    if by_category:
        if income_categories:
            output.append("\nIncome Breakdown:")
            output.extend(income_categories)
        if expense_categories:
            output.append("\nExpense Breakdown:")
            output.extend(expense_categories)
        output.append("")

    output.append(f"Total Income:  ${total_income:.2f}")
    output.append(f"Total Expense: ${total_expense:.2f}")

    net = total_income - total_expense
    sign = "+" if net >= 0 else "-"
    output.append(f"Net Balance:   {sign}${abs(net):.2f}")

    return "\n".join(output)

@mcp.tool()
def get_transactions(
    category: str = None,
    type: str = None,
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    min_amount: float = None,
    max_amount: float = None,
    search: str = None,
    limit: int = 50
) -> str:
    """
    Get transactions based on specified filter criteria.
    - category: Filter by category (case-insensitive).
    - type: Filter by type ('income' or 'expense').
    - month: Filter by month formatted as YYYY-MM.
    - start_date: Filter transactions on or after YYYY-MM-DD.
    - end_date: Filter transactions on or before YYYY-MM-DD.
    - min_amount: Filter transactions with amount >= min_amount.
    - max_amount: Filter transactions with amount <= max_amount.
    - search: Keyword search matching description or category.
    - limit: Maximum number of records to return (default 50).
    """
    with sqlite3.connect("budget.db") as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT id, date, amount, category, description, type FROM transactions"
        conditions = []
        params = []

        if category:
            conditions.append("LOWER(category) = LOWER(?)")
            params.append(category)
        if type:
            conditions.append("LOWER(type) = LOWER(?)")
            params.append(type)
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

        results = conn.execute(query, params).fetchall()

    if not results:
        return "No transactions found matching the specified filters."

    formatted_rows = []
    for row in results:
        formatted_rows.append(
            f"[{row['id']}] {row['date']} | {row['type'].upper()} | ${row['amount']:.2f} | Category: {row['category']} | {row['description']}"
        )

    return "\n".join(formatted_rows)

if __name__ == "__main__":
    init_db()
    # Runs over stdio by default, the standard transport for local MCP tools
    mcp.run()