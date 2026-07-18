import src.db as db

def register_summary_tools(mcp):
    """Register financial summary tools."""

    @mcp.tool()
    def get_summary(
        month: str = None,
        start_date: str = None,
        end_date: str = None,
        category_id: int = None,
        type: str = None,
        by_category: bool = False
    ) -> str:
        """
        Get a summary of expenses, income, and net balance with flexible filtering and optional category breakdown.
        - month: Filter by month (YYYY-MM).
        - start_date: Filter starting from date (YYYY-MM-DD).
        - end_date: Filter ending at date (YYYY-MM-DD).
        - category_id: Optional integer category ID filter from list_categories.
        - type: Filter by transaction type ('expense' or 'income').
        - by_category: Set to True to include detailed category breakdown.
        """
        results = db.get_summary_data(
            month=month,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            txn_type=type
        )

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
