from typing import Union, List, Dict, Any, Optional
import src.db as db

def register_category_tools(mcp):
    """Register category management tools (list, add, update, delete)."""

    @mcp.tool()
    def list_categories(type: str = None) -> str:
        """
        List established categories available for transactions.
        - type: Optional filter by 'expense' or 'income'.
        Use this tool to see standard existing categories before creating new ones.
        """
        categories = db.get_categories_db(type_filter=type)
        if not categories:
            return "No categories found."

        expenses = [c for c in categories if c['type'].lower() == 'expense']
        incomes = [c for c in categories if c['type'].lower() == 'income']
        other = [c for c in categories if c['type'].lower() not in ('expense', 'income')]

        output = ["📁 Category Library:"]

        if expenses:
            output.append("\nEXPENSE CATEGORIES:")
            for c in expenses:
                desc = f" - {c['description']}" if c['description'] else ""
                output.append(f"  [{c['id']}] {c['name']}{desc}")

        if incomes:
            output.append("\nINCOME CATEGORIES:")
            for c in incomes:
                desc = f" - {c['description']}" if c['description'] else ""
                output.append(f"  [{c['id']}] {c['name']}{desc}")

        if other:
            output.append("\nOTHER CATEGORIES:")
            for c in other:
                desc = f" - {c['description']}" if c['description'] else ""
                output.append(f"  [{c['id']}] {c['name']} ({c['type']}){desc}")

        return "\n".join(output)

    @mcp.tool()
    def add_category(
        name: str = None,
        type: str = "expense",
        description: str = None,
        items: Union[List[Dict[str, Any]], Dict[str, Any]] = None,
    ) -> str:
        """
        Create one or more categories in the category library.
        
        Supports single category parameters OR a batch list/dict of items in `items`.
        - items: Optional list of dicts. Each dict can contain: {"name": str, "type": "expense"|"income", "description": str}.
        - name: Unique category name (used if items is omitted).
        - type: Category type ('expense' or 'income', defaults to 'expense').
        - description: Optional description explaining what belongs in this category.
        """
        batch_items = []
        if items is not None:
            if isinstance(items, dict):
                batch_items = [items]
            elif isinstance(items, list):
                batch_items = items
        elif name is not None:
            batch_items = [{
                "name": name,
                "type": type,
                "description": description
            }]

        if not batch_items:
            return "No category data provided. Specify name/type or a list of items."

        if len(batch_items) == 1 and items is None:
            c_name = batch_items[0].get("name")
            c_type = batch_items[0].get("type", "expense")
            c_desc = batch_items[0].get("description")
            if not c_name:
                return "No category name provided."
            result, created = db.add_category_db(name=c_name, type_val=c_type, description=c_desc)
            if not created:
                return f"Category '{result['name']}' already exists (ID: {result['id']}, Type: {result['type']})."
            return f"Successfully added category [{result['id']}] '{result['name']}' ({result['type'].upper()})."

        successes = []
        errors = []

        for idx, item in enumerate(batch_items, 1):
            c_name = item.get("name")
            c_type = item.get("type", "expense")
            c_desc = item.get("description")

            if not c_name:
                errors.append(f"Item #{idx}: missing required category 'name'.")
                continue

            result, created = db.add_category_db(name=c_name, type_val=c_type, description=c_desc)
            if not created:
                errors.append(f"Category '{result['name']}' already exists (ID: {result['id']}).")
            else:
                successes.append(f"[{result['id']}] '{result['name']}' ({result['type'].upper()})")

        res_lines = []
        if successes:
            res_lines.append(f"Successfully added {len(successes)} category(ies):")
            for s in successes:
                res_lines.append(f"  - {s}")
        if errors:
            for e in errors:
                res_lines.append(f"  - {e}")

        return "\n".join(res_lines)

    @mcp.tool()
    def update_category(
        category_id_or_name: str,
        new_name: str = None,
        type: str = None,
        description: str = None
    ) -> str:
        """
        Update an existing category's name, type, or description.
        - category_id_or_name: ID or current name of the category to update (required).
        - new_name: Optional new category name.
        - type: Optional new type ('expense' or 'income').
        - description: Optional new description string.
        """
        existing = db.get_category_by_id_or_name(category_id_or_name)
        if not existing:
            return f"Category '{category_id_or_name}' not found."

        if new_name is None and type is None and description is None:
            return f"No update fields provided for category '{existing['name']}'."

        success = db.update_category_db(
            id_or_name=category_id_or_name,
            new_name=new_name,
            type_val=type,
            description=description
        )

        if not success:
            return f"Failed to update category '{category_id_or_name}'."

        return f"Successfully updated category [{existing['id']}] '{existing['name']}'."

    @mcp.tool()
    def delete_category(
        category_id_or_name: Union[str, int, List[Union[str, int]]] = None,
        category_ids_or_names: Union[List[Union[str, int]], str, int] = None,
        reassign_to_category_id: int = None
    ) -> str:
        """
        Delete one or more categories from the library.
        
        Supports a single category ID/name or a list of category IDs/names in `category_ids_or_names`.
        - category_ids_or_names: ID/name or list of IDs/names to delete.
        - category_id_or_name: Alias for single category deletion.
        - reassign_to_category_id: Target category ID to reassign linked transactions to.
        """
        raw_items = category_ids_or_names if category_ids_or_names is not None else category_id_or_name
        if raw_items is None:
            return "No category ID(s) or name(s) provided to delete."

        item_list = raw_items if isinstance(raw_items, list) else [raw_items]

        if len(item_list) == 1 and category_ids_or_names is None:
            deleted, err = db.delete_category_db(item_list[0], reassign_to_id_or_name=reassign_to_category_id)
            if err:
                return err
            msg = f"Successfully deleted category [{deleted['id']}] '{deleted['name']}' ({deleted['type'].upper()})."
            if deleted.get("reassigned_transactions_count", 0) > 0:
                msg += f" Reassigned {deleted['reassigned_transactions_count']} transaction(s) to '{deleted['reassigned_to']}'."
            return msg

        successes = []
        errors = []

        for item in item_list:
            deleted, err = db.delete_category_db(item, reassign_to_id_or_name=reassign_to_category_id)
            if err:
                errors.append(err)
            else:
                msg = f"[{deleted['id']}] '{deleted['name']}' ({deleted['type'].upper()})"
                if deleted.get("reassigned_transactions_count", 0) > 0:
                    msg += f" (reassigned {deleted['reassigned_transactions_count']} transaction(s) to '{deleted['reassigned_to']}')"
                successes.append(msg)

        res_lines = []
        if successes:
            for s in successes:
                res_lines.append(f"Successfully deleted category {s}.")
        if errors:
            for e in errors:
                res_lines.append(e)

        return "\n".join(res_lines)
