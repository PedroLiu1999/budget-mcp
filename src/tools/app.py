from collections import Counter
from typing import Optional

from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, DataTable, DataTableColumn, Grid
from prefab_ui.components.charts import PieChart, LineChart, ChartSeries

import src.db as db


def register_app_tools(mcp):
    """Register interactive UI application tools."""

    @mcp.tool(app=True)
    def budget_dashboard(
        month: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> PrefabApp:
        """Browse the interactive budget dashboard with a category breakdown chart and transaction data table."""
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

    @mcp.tool(app=True)
    def spending_trends(
        type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 500,
    ) -> PrefabApp:
        """Browse spending trends over time grouped by year-month with a line chart and transaction data table."""
        transactions = db.get_transactions_data(
            txn_type=type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        # Aggregate amounts by year-month and category
        month_map = {}
        category_names = set()

        for t in sorted(transactions, key=lambda x: x["date"]):
            month = t["date"][:7] if t.get("date") else "Unknown"
            cat = t.get("category") or "Uncategorized"
            amt = float(t.get("amount", 0.0))
            category_names.add(cat)
            if month not in month_map:
                month_map[month] = {}
            month_map[month][cat] = round(month_map[month].get(cat, 0.0) + amt, 2)

        chart_data = []
        for m, cat_dict in month_map.items():
            row = {"month": m}
            row.update(cat_dict)
            chart_data.append(row)

        if not chart_data:
            chart_data = [{"month": "No Data", "Amount": 0.0}]
            series = [ChartSeries(data_key="Amount", name="No Transactions")]
        else:
            series = [
                ChartSeries(data_key=c_name, name=c_name)
                for c_name in sorted(category_names)
            ]

        with PrefabApp() as app:
            with Column(gap=4, css_class="p-6"):
                LineChart(
                    data=chart_data,
                    series=series,
                    x_axis="month",
                    show_legend=True,
                    show_grid=True,
                    show_dots=False,
                    show_tooltip=True,
                    height=320,
                )
                DataTable(
                    columns=[
                        DataTableColumn(key="date", header="Date", sortable=True),
                        DataTableColumn(key="type", header="Type", sortable=True),
                        DataTableColumn(key="category", header="Category", sortable=True),
                        DataTableColumn(key="amount", header="Amount ($)", sortable=True),
                        DataTableColumn(key="description", header="Description", sortable=True),
                    ],
                    rows=transactions,
                    search=True,
                )

        return app

