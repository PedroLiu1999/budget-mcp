from collections import Counter
from typing import Optional

from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, DataTable, DataTableColumn, Grid, Select, SelectOption, Card, CardHeader, CardTitle, CardContent
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
        category_id: Optional[int] = None,
        type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 500,
    ) -> PrefabApp:
        """Browse spending trends over time with a category line chart, interactive category dropdown select, and category legend."""
        transactions = db.get_transactions_data(
            category_id=category_id,
            txn_type=type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        all_categories = db.get_categories_db(type_filter=type)
        category_options = [SelectOption(value="", label="All Categories")] + [
            SelectOption(value=str(c["id"]), label=f"{c['name']} ({c['type'].capitalize()})")
            for c in all_categories
        ]

        selected_category_val = str(category_id) if category_id is not None else ""

        # Aggregate amounts by date and category
        date_map = {}
        category_names = set()

        for t in sorted(transactions, key=lambda x: x["date"]):
            d = t["date"]
            cat = t["category"] or "Uncategorized"
            amt = float(t["amount"])
            category_names.add(cat)
            if d not in date_map:
                date_map[d] = {}
            date_map[d][cat] = round(date_map[d].get(cat, 0.0) + amt, 2)

        chart_data = []
        for d, cat_dict in date_map.items():
            row = {"date": d}
            row.update(cat_dict)
            chart_data.append(row)

        if not chart_data:
            chart_data = [{"date": "No Data", "Amount": 0.0}]
            series = [ChartSeries(data_key="Amount", name="No Transactions")]
        else:
            series = [
                ChartSeries(data_key=c_name, name=c_name)
                for c_name in sorted(category_names)
            ]

        with PrefabApp() as app:
            with Column(gap=4, css_class="p-6"):
                Select(
                    name="category_filter",
                    value=selected_category_val,
                    placeholder="Filter by Category",
                    children=category_options,
                )
                LineChart(
                    data=chart_data,
                    series=series,
                    x_axis="date",
                    show_legend=True,
                    show_grid=True,
                    show_dots=True,
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
