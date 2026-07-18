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
    def add_category(name: str, type: str = "expense", description: str = None) -> str:
        """
        Create a new category in the category library.
        - name: Unique category name (required).
        - type: Category type ('expense' or 'income', defaults to 'expense').
        - description: Optional description explaining what belongs in this category.
        """
        result, created = db.add_category_db(name=name, type_val=type, description=description)
        if not created:
            return f"Category '{result['name']}' already exists (ID: {result['id']}, Type: {result['type']})."

        return f"Successfully added category [{result['id']}] '{result['name']}' ({result['type'].upper()})."

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
    def delete_category(category_id_or_name: str) -> str:
        """
        Delete a category from the library.
        - category_id_or_name: ID or name of category to delete (required).
        """
        deleted = db.delete_category_db(category_id_or_name)
        if not deleted:
            return f"Category '{category_id_or_name}' not found."

        return f"Successfully deleted category [{deleted['id']}] '{deleted['name']}' ({deleted['type'].upper()})."
