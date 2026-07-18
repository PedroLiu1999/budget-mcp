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
def add_transaction(amount: float, category: str, description: str, type: str = "expense") -> str:
    """
    Add a new income or expense transaction to the budget.
    type must be either 'expense' or 'income'.
    """
    with sqlite3.connect("budget.db") as conn:
        conn.execute(
            "INSERT INTO transactions (date, amount, category, description, type) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d"), amount, category, description, type.lower())
        )
    return f"Successfully logged {type} of ${amount:.2f} for {category}."

@mcp.tool()
def get_summary(month: str = None) -> str:
    """
    Get a summary of expenses and income. 
    Optionally pass a month formatted as YYYY-MM to filter.
    """
    with sqlite3.connect("budget.db") as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT type, SUM(amount) as total FROM transactions"
        params = []
        if month:
            query += " WHERE date LIKE ?"
            params.append(f"{month}%")
        query += " GROUP BY type"
        
        results = conn.execute(query, params).fetchall()
        
    if not results or all(row['total'] is None for row in results):
        return "No transactions found for the specified period."
        
    return "\n".join(f"{row['type'].capitalize()}: ${row['total']:.2f}" for row in results if row['total'] is not None)

if __name__ == "__main__":
    init_db()
    # Runs over stdio by default, the standard transport for local MCP tools
    mcp.run()