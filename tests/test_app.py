import asyncio
from fastmcp import FastMCP
from src.tools import register_tools
from prefab_ui.app import PrefabApp
import src.db as db


def test_budget_dashboard_tool():
    async def _test():
        server = FastMCP("Test Budget Server")
        register_tools(server)

        shop_cat = db.get_category_by_id_or_name("Shopping")
        food_cat = db.get_category_by_id_or_name("Food & Dining")

        await server.call_tool("add_transaction", {
            "amount": 45.0,
            "category_id": shop_cat["id"],
            "description": "Test Shopping",
            "type": "expense",
            "date": "2026-07-15"
        })
        await server.call_tool("add_transaction", {
            "amount": 15.0,
            "category_id": food_cat["id"],
            "description": "Test Lunch",
            "type": "expense",
            "date": "2026-07-16"
        })

        res = await server.call_tool("budget_dashboard", {})
        assert res is not None

    asyncio.run(_test())
