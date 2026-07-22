from typing import Union, List, Dict, Any, Optional
from src.utils import normalize_date
import src.db as db

def register_transaction_tools(mcp):
    """Register transaction management tools (add, get, update, delete)."""

    @mcp.tool()
    def add_transaction(
        amount: float = None,
        category_id: int = None,
        description: str = None,
        type: str = "expense",
        date: str = None,
        items: Union[List[Dict[str, Any]], Dict[str, Any]] = None,
    ) -> str:
        """
        Add one or more income or expense transactions to the budget.
        
        Supports single transaction parameters OR a batch list/dict of items in `items`.
        
        Bulk Import Workflow:
        - You can bulk import transactions without categories (`category_id` is optional).
        - After bulk logging, use `get_uncategorized_transactions` to review uncategorized transactions sorted by description.
        - Then use `update_transaction` to systematically assign category IDs to matching descriptions in bulk.

        Arguments:
        - items: Optional list of dicts (or single dict) for batch insertion. Each dict can contain:
                 {"amount": float, "category_id": int (optional), "description": str, "type": "expense"|"income", "date": "YYYY-MM-DD"}.
        - amount: Transaction monetary value (used if items is omitted).
        - category_id: Optional integer category ID from list_categories (omitting logs as 'Uncategorized').
        - description: Details or description of transaction (used if items is omitted).
        - type: Must be either 'expense' or 'income' (defaults to 'expense').
        - date: Optional transaction date formatted as YYYY-MM-DD or ISO string.
        """
        batch_items = []
        if items is not None:
            if isinstance(items, dict):
                batch_items = [items]
            elif isinstance(items, list):
                batch_items = items
        elif amount is not None and description is not None:
            batch_items = [{
                "amount": amount,
                "category_id": category_id,
                "description": description,
                "type": type,
                "date": date
            }]

        if not batch_items:
            return "No transaction data provided. Specify transaction fields or a list of items."

        if len(batch_items) == 1 and items is None:
            item = batch_items[0]
            amt = item.get("amount")
            cat_id = item.get("category_id")
            desc = item.get("description")
            t_type = item.get("type", "expense")
            t_date = item.get("date")

            validated_cat_id = None
            cat_name = "Uncategorized"
            if cat_id is not None:
                cat_record = db.get_category_by_id_or_name(cat_id)
                if not cat_record:
                    return f"Invalid category_id {cat_id}. Please use list_categories to pick a valid category ID."
                validated_cat_id = cat_record["id"]
                cat_name = cat_record["name"]

            txn_date = normalize_date(t_date)
            record = db.insert_transaction(
                date=txn_date,
                amount=amt,
                category_id=validated_cat_id,
                description=desc,
                txn_type=t_type
            )
            return f"Successfully logged {t_type} [{record['id']}] of ${amt:.2f} for {cat_name} on {txn_date}."

        successes = []
        errors = []

        for idx, item in enumerate(batch_items, 1):
            amt = item.get("amount")
            cat_id = item.get("category_id")
            desc = item.get("description")
            t_type = item.get("type", "expense")
            t_date = item.get("date")

            if amt is None or desc is None:
                errors.append(f"Item #{idx}: missing required fields ('amount' or 'description').")
                continue

            validated_cat_id = None
            cat_name = "Uncategorized"
            if cat_id is not None:
                cat_record = db.get_category_by_id_or_name(cat_id)
                if not cat_record:
                    errors.append(f"Item #{idx}: Invalid category_id {cat_id}.")
                    continue
                validated_cat_id = cat_record["id"]
                cat_name = cat_record["name"]

            txn_date = normalize_date(t_date)
            record = db.insert_transaction(
                date=txn_date,
                amount=amt,
                category_id=validated_cat_id,
                description=desc,
                txn_type=t_type
            )
            successes.append(f"[{record['id']}] {t_type.upper()} ${amt:.2f} for {cat_name} on {txn_date}")

        res_lines = []
        if successes:
            res_lines.append(f"Successfully logged {len(successes)} transaction(s):")
            for s in successes:
                res_lines.append(f"  - {s}")
        if errors:
            res_lines.append(f"Failed to log {len(errors)} transaction(s):")
            for e in errors:
                res_lines.append(f"  - {e}")

        return "\n".join(res_lines)

    @mcp.tool()
    def get_transactions(
        category_id: int = None,
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
        - category_id: Optional integer filter by category ID.
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
            category_id=category_id,
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
    def get_uncategorized_transactions(
        type: str = None,
        search: str = None,
        limit: int = 100
    ) -> str:
        """
        Get all uncategorized transactions sorted alphabetically by description.
        
        Designed for systematic categorization after bulk import: Use this tool to retrieve transactions imported without categories.
        Because results are sorted by description, similar merchant/expense descriptions are grouped together, enabling fast and consistent bulk updates via `update_transaction`.

        Arguments:
        - type: Optional filter by transaction type ('income' or 'expense').
        - search: Optional keyword search filter for description.
        - limit: Maximum number of records to return (default 100).
        """
        results = db.get_uncategorized_transactions_data(
            txn_type=type,
            search=search,
            limit=limit
        )

        if not results:
            return "No uncategorized transactions found."

        formatted_rows = []
        for row in results:
            formatted_rows.append(
                f"[{row['id']}] {row['date']} | {row['type'].upper()} | ${row['amount']:.2f} | Category: {row['category']} | {row['description']}"
            )

        return "\n".join(formatted_rows)


    @mcp.tool()
    def update_transaction(
        transaction_id: int = None,
        amount: float = None,
        category_id: int = None,
        description: str = None,
        type: str = None,
        date: str = None,
        items: Union[List[Dict[str, Any]], Dict[str, Any]] = None,
    ) -> str:
        """
        Update one or more existing transactions by ID.
        
        Supports single transaction updates OR a batch list/dict of update items in `items`.
        Use this tool to assign category_id, amount, description, type, or date.
        
        Systematic Categorization Workflow:
        - Pass a batch list in `items` containing `{"transaction_id": id, "category_id": cat_id}` to categorize multiple transactions at once.
        
        Arguments:
        - items: Optional list of update dicts. Each dict must include "transaction_id" and optional update fields.
        - transaction_id: ID of transaction to update (used if items is omitted).
        - category_id: Integer category ID from list_categories to assign a category.
        - amount: Optional new monetary amount.
        - description: Optional new description.
        - type: Optional new type ('expense' or 'income').
        - date: Optional new date (YYYY-MM-DD).
        """

        batch_items = []
        if items is not None:
            if isinstance(items, dict):
                batch_items = [items]
            elif isinstance(items, list):
                batch_items = items
        elif transaction_id is not None:
            single_item = {"transaction_id": transaction_id}
            if amount is not None: single_item["amount"] = amount
            if category_id is not None: single_item["category_id"] = category_id
            if description is not None: single_item["description"] = description
            if type is not None: single_item["type"] = type
            if date is not None: single_item["date"] = date
            batch_items = [single_item]

        if not batch_items:
            return "No transaction ID or update items provided."

        if len(batch_items) == 1 and items is None:
            t_id = batch_items[0].get("transaction_id")
            existing = db.get_transaction_by_id(t_id)
            if not existing:
                return f"Transaction with ID {t_id} not found."
            updates = {}
            if "amount" in batch_items[0] and batch_items[0]["amount"] is not None:
                updates["amount"] = batch_items[0]["amount"]
            if "category_id" in batch_items[0] and batch_items[0]["category_id"] is not None:
                cat_record = db.get_category_by_id_or_name(batch_items[0]["category_id"])
                if not cat_record:
                    return f"Invalid category_id {batch_items[0]['category_id']}. Please use list_categories to pick a valid category ID."
                updates["category_id"] = cat_record["id"]
                updates["category"] = cat_record["name"]
            if "description" in batch_items[0] and batch_items[0]["description"] is not None:
                updates["description"] = batch_items[0]["description"]
            if "type" in batch_items[0] and batch_items[0]["type"] is not None:
                updates["type"] = batch_items[0]["type"].lower()
            if "date" in batch_items[0] and batch_items[0]["date"] is not None:
                updates["date"] = normalize_date(batch_items[0]["date"])

            if not updates:
                return f"No fields provided to update for transaction ID {t_id}."

            db.update_transaction_data(t_id, updates)
            return f"Successfully updated transaction [{t_id}]."

        successes = []
        errors = []

        for idx, item in enumerate(batch_items, 1):
            t_id = item.get("transaction_id")
            if t_id is None:
                errors.append(f"Item #{idx}: missing required 'transaction_id'.")
                continue

            existing = db.get_transaction_by_id(t_id)
            if not existing:
                errors.append(f"Transaction ID {t_id} not found.")
                continue

            updates = {}
            if "amount" in item and item["amount"] is not None:
                updates["amount"] = item["amount"]
            if "category_id" in item and item["category_id"] is not None:
                cat_record = db.get_category_by_id_or_name(item["category_id"])
                if not cat_record:
                    errors.append(f"Transaction [{t_id}]: Invalid category_id {item['category_id']}.")
                    continue
                updates["category_id"] = cat_record["id"]
                updates["category"] = cat_record["name"]
            if "description" in item and item["description"] is not None:
                updates["description"] = item["description"]
            if "type" in item and item["type"] is not None:
                updates["type"] = item["type"].lower()
            if "date" in item and item["date"] is not None:
                updates["date"] = normalize_date(item["date"])

            if not updates:
                errors.append(f"Transaction [{t_id}]: No update fields provided.")
                continue

            db.update_transaction_data(t_id, updates)
            successes.append(f"Successfully updated transaction [{t_id}].")

        res_lines = []
        if successes:
            for s in successes:
                res_lines.append(s)
        if errors:
            res_lines.append(f"Failed updates ({len(errors)}):")
            for e in errors:
                res_lines.append(f"  - {e}")

        return "\n".join(res_lines)

    @mcp.tool()
    def delete_transaction(
        transaction_id: Union[int, List[int]] = None,
        transaction_ids: Union[List[int], int] = None,
    ) -> str:
        """
        Delete one or more transactions by ID.
        
        Supports a single integer ID or a list of integer IDs in `transaction_ids`.
        - transaction_ids: Integer ID or list of integer IDs to delete.
        - transaction_id: Alias for single ID deletion.
        """
        raw_ids = transaction_ids if transaction_ids is not None else transaction_id
        if raw_ids is None:
            return "No transaction ID(s) provided to delete."

        id_list = raw_ids if isinstance(raw_ids, list) else [raw_ids]

        if len(id_list) == 1 and transaction_ids is None:
            t_id = id_list[0]
            existing = db.get_transaction_by_id(t_id)
            if not existing:
                return f"Transaction with ID {t_id} not found."
            db.delete_transaction_data(t_id)
            return f"Successfully deleted transaction [{t_id}]: {existing['date']} | {existing['type'].upper()} | ${existing['amount']:.2f} | Category: {existing['category']} | {existing['description']}"

        successes = []
        errors = []

        for t_id in id_list:
            existing = db.get_transaction_by_id(t_id)
            if not existing:
                errors.append(f"Transaction with ID {t_id} not found.")
                continue

            db.delete_transaction_data(t_id)
            successes.append(f"[{t_id}] {existing['date']} | ${existing['amount']:.2f} | Category: {existing['category']} | {existing['description']}")

        res_lines = []
        if successes:
            for s in successes:
                res_lines.append(f"Successfully deleted transaction {s}")
        if errors:
            for e in errors:
                res_lines.append(e)

        return "\n".join(res_lines)
