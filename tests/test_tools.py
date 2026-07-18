import asyncio
from mcp.server.fastmcp import FastMCP
from src.tools import register_tools

def get_test_server():
    server = FastMCP("Test Budget Server")
    register_tools(server)
    return server

def extract_text(res):
    """Extract text output from FastMCP call_tool result."""
    if isinstance(res, (list, tuple)) and len(res) > 0:
        elem = res[0]
        if isinstance(elem, (list, tuple)) and len(elem) > 0:
            return getattr(elem[0], "text", str(elem[0]))
        return getattr(elem, "text", str(elem))
    return str(res)

def test_tools_add_and_get_transactions():
    async def _test():
        server = get_test_server()

        # Call add_transaction
        res1 = await server.call_tool("add_transaction", {
            "amount": 75.50,
            "category": "Shopping",
            "description": "New shoes",
            "type": "expense",
            "date": "2026-07-10"
        })
        assert "Successfully logged expense of $75.50 for Shopping on 2026-07-10." in extract_text(res1)

        # Call get_transactions
        res2 = await server.call_tool("get_transactions", {"category": "Shopping"})
        assert "[1] 2026-07-10 | EXPENSE | $75.50 | Category: Shopping | New shoes" in extract_text(res2)

    asyncio.run(_test())

def test_tools_get_summary():
    async def _test():
        server = get_test_server()

        await server.call_tool("add_transaction", {
            "amount": 2000.0,
            "category": "Salary",
            "description": "Monthly pay",
            "type": "income",
            "date": "2026-07-01"
        })
        await server.call_tool("add_transaction", {
            "amount": 500.0,
            "category": "Rent",
            "description": "Apartment rent",
            "type": "expense",
            "date": "2026-07-02"
        })

        # Summary default
        summary_res = await server.call_tool("get_summary", {"month": "2026-07"})
        text = extract_text(summary_res)
        assert "Total Income:  $2000.00" in text
        assert "Total Expense: $500.00" in text
        assert "Net Balance:   +$1500.00" in text

        # Summary with category breakdown
        summary_cat_res = await server.call_tool("get_summary", {"month": "2026-07", "by_category": True})
        text_cat = extract_text(summary_cat_res)
        assert "Income Breakdown:" in text_cat
        assert "Expense Breakdown:" in text_cat
        assert "Rent: $500.00" in text_cat

    asyncio.run(_test())

def test_tools_update_and_delete_transaction():
    async def _test():
        server = get_test_server()

        await server.call_tool("add_transaction", {
            "amount": 10.0,
            "category": "Coffee",
            "description": "Espresso",
            "type": "expense"
        })

        # Update
        update_res = await server.call_tool("update_transaction", {
            "transaction_id": 1,
            "amount": 12.50,
            "category": "Drinks"
        })
        assert "Successfully updated transaction [1]." in extract_text(update_res)

        # Delete
        delete_res = await server.call_tool("delete_transaction", {"transaction_id": 1})
        assert "Successfully deleted transaction [1]" in extract_text(delete_res)

        # Non-existent delete
        del_missing = await server.call_tool("delete_transaction", {"transaction_id": 999})
        assert "Transaction with ID 999 not found." in extract_text(del_missing)

    asyncio.run(_test())
