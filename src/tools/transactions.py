from src.utils import normalize_date
import src.db as db

def register_transaction_tools(mcp):
    """Register transaction management tools (add, get, update, delete)."""

    @mcp.tool()
    def add_transaction(amount: float, category: str, description: str, type: str = "expense", date: str = None) -> str:
        """
        Add a new income or expense transaction to the budget.
        - amount: Transaction monetary value.
        - category: Category name or ID (matches established categories from list_categories, or registers a new category if needed).
        - description: Details or description of transaction.
        - type: Must be either 'expense' or 'income' (defaults to 'expense').
        - date: Optional transaction date formatted as YYYY-MM-DD or ISO string (defaults to current date if omitted).
        """
        txn_date = normalize_date(date)
        cat_info = db.ensure_category_exists(category, type_val=type)
        db.insert_transaction(
            date=txn_date,
            amount=amount,
            category=cat_info["id"],
            description=description,
            txn_type=type
        )
        return f"Successfully logged {type} of ${amount:.2f} for {cat_info['name']} on {txn_date}."

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
        - category: Filter by category name or ID (case-insensitive).
        - type: Filter by type ('income' or 'expense').
        - month: Filter by month formatted as YYYY-MM.
        - start_date: Filter transactions on or after YYYY-MM-DD.
        - end_date: Filter transactions on or before YYYY-MM-DD.
        - min_amount: Filter transactions with amount >= min_amount.
        - max_amount: Filter transactions with amount <= max_amount.
        - search: Keyword search matching description or category.
        - limit: Maximum number of records to return (default 50).
        """
        results = db.get_transactions_data(
            category=category,
            txn_type=type,
            month=month,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            limit=limit
        )

        if not results:
            return "No transactions found matching the specified filters."

        formatted_rows = []
        for row in results:
            formatted_rows.append(
                f"[{row['id']}] {row['date']} | {row['type'].upper()} | ${row['amount']:.2f} | Category: {row['category']} | {row['description']}"
            )

        return "\n".join(formatted_rows)

    @mcp.tool()
    def update_transaction(
        transaction_id: int,
        amount: float = None,
        category: str = None,
        description: str = None,
        type: str = None,
        date: str = None
    ) -> str:
        """
        Update an existing transaction by ID.
        - transaction_id: ID of transaction to update (required).
        - amount: New transaction amount.
        - category: New category name or ID.
        - description: New description.
        - type: New type ('expense' or 'income').
        - date: New date ('YYYY-MM-DD' or ISO format string).
        """
        existing = db.get_transaction_by_id(transaction_id)
        if not existing:
            return f"Transaction with ID {transaction_id} not found."

        updates = {}
        if amount is not None:
            updates["amount"] = amount
        if category is not None:
            cat_info = db.ensure_category_exists(category, type_val=type or existing['type'])
            updates["category_id"] = cat_info["id"]
            updates["category"] = cat_info["name"]
        if description is not None:
            updates["description"] = description
        if type is not None:
            updates["type"] = type.lower()
        if date is not None:
            updates["date"] = normalize_date(date)

        if not updates:
            return f"No fields provided to update for transaction ID {transaction_id}."

        db.update_transaction_data(transaction_id, updates)
        return f"Successfully updated transaction [{transaction_id}]."

    @mcp.tool()
    def delete_transaction(transaction_id: int) -> str:
        """
        Delete a transaction by ID.
        - transaction_id: ID of transaction to delete (required).
        """
        existing = db.get_transaction_by_id(transaction_id)
        if not existing:
            return f"Transaction with ID {transaction_id} not found."

        db.delete_transaction_data(transaction_id)
        return f"Successfully deleted transaction [{transaction_id}]: {existing['date']} | {existing['type'].upper()} | ${existing['amount']:.2f} | Category: {existing['category']} | {existing['description']}"
