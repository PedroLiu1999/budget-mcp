from collections import Counter
from typing import Optional

from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, DataTable, DataTableColumn, Grid
from prefab_ui.components.charts import PieChart

import src.db as db


def register_app_tools(mcp):
    """Register interactive UI application tools."""

    @mcp.tool(app=True)
    def transaction_directory(
        month: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> PrefabApp:
        """Browse the transaction directory with an interactive data table and category pie chart."""
        transactions = db.get_transactions_data(
            month=month,
            txn_type=type,
            limit=limit,
        )

        category_counts = [
            {"category": category, "count": count}
            for category, count in Counter(
                t.get("category") or "Uncategorized" for t in transactions
            ).items()
        ]

        if not category_counts:
            category_counts = [{"category": "No Data", "count": 0}]

        with PrefabApp() as app:
            with Column(gap=4, css_class="p-6"):
                with Grid(columns=[1, 2], gap=4):
                    PieChart(
                        data=category_counts,
                        data_key="count",
                        name_key="category",
                        show_legend=True,
                    )
                    DataTable(
                        columns=[
                            DataTableColumn(key="date", header="Date", sortable=True),
                            DataTableColumn(key="type", header="Type", sortable=True),
                            DataTableColumn(key="category", header="Category", sortable=True),
                            DataTableColumn(key="amount", header="Amount", sortable=True),
                            DataTableColumn(key="description", header="Description", sortable=True),
                        ],
                        rows=transactions,
                        search=True,
                    )

        return app
