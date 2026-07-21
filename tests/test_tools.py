import asyncio
from fastmcp import FastMCP
from src.tools import register_tools
import src.db as db

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
        shop_cat = db.get_category_by_id_or_name("Shopping")

        # Test invalid category_id
        bad_res = await server.call_tool("add_transaction", {
            "amount": 10.0,
            "category_id": 99999,
            "description": "Bad cat"
        })
        assert "Invalid category_id 99999" in extract_text(bad_res)

        # Call add_transaction with valid category_id
        res1 = await server.call_tool("add_transaction", {
            "amount": 75.50,
            "category_id": shop_cat["id"],
            "description": "New shoes",
            "type": "expense",
            "date": "2026-07-10"
        })
        assert "Successfully logged expense [1] of $75.50 for Shopping on 2026-07-10." in extract_text(res1)

        # Call get_transactions filtering by category_id
        res2 = await server.call_tool("get_transactions", {"category_id": shop_cat["id"]})
        assert "[1] 2026-07-10 | EXPENSE | $75.50 | Category: Shopping | New shoes" in extract_text(res2)

    asyncio.run(_test())

def test_tools_get_summary():
    async def _test():
        server = get_test_server()
        salary_cat = db.get_category_by_id_or_name("Salary")
        rent_cat = db.get_category_by_id_or_name("Housing & Rent")

        await server.call_tool("add_transaction", {
            "amount": 2000.0,
            "category_id": salary_cat["id"],
            "description": "Monthly pay",
            "type": "income",
            "date": "2026-07-01"
        })
        await server.call_tool("add_transaction", {
            "amount": 500.0,
            "category_id": rent_cat["id"],
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
        assert "Housing & Rent: $500.00" in text_cat

    asyncio.run(_test())

def test_tools_update_and_delete_transaction():
    async def _test():
        server = get_test_server()
        food_cat = db.get_category_by_id_or_name("Food & Dining")
        shop_cat = db.get_category_by_id_or_name("Shopping")

        await server.call_tool("add_transaction", {
            "amount": 10.0,
            "category_id": food_cat["id"],
            "description": "Espresso",
            "type": "expense"
        })

        # Update
        update_res = await server.call_tool("update_transaction", {
            "transaction_id": 1,
            "amount": 12.50,
            "category_id": shop_cat["id"]
        })
        assert "Successfully updated transaction [1]." in extract_text(update_res)

        # Delete
        delete_res = await server.call_tool("delete_transaction", {"transaction_id": 1})
        assert "Successfully deleted transaction [1]" in extract_text(delete_res)

        # Non-existent delete
        del_missing = await server.call_tool("delete_transaction", {"transaction_id": 999})
        assert "Transaction with ID 999 not found." in extract_text(del_missing)

    asyncio.run(_test())

def test_auto_init_db_on_register(tmp_path):
    """Verify that calling register_tools initializes the database without requiring init_db to be called manually."""
    from sqlalchemy import create_engine
    test_engine = create_engine(f"sqlite:///{tmp_path}/auto_init.db", echo=False)
    db.set_engine(test_engine)
    
    server = FastMCP("Auto Init Test Server")
    register_tools(server)
    
    cat = db.get_category_by_id_or_name("Groceries")
    assert cat is not None
    assert cat["name"] == "Groceries"

