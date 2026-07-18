import asyncio
from mcp.server.fastmcp import FastMCP
import src.db as db
from src.tools import register_tools
from tests.test_tools import extract_text

def test_category_seeding_and_db_crud():
    categories = db.get_categories_db()
    assert len(categories) > 0

    # Test default categories present
    names = [c["name"] for c in categories]
    assert "Groceries" in names
    assert "Salary" in names

    # Add category
    new_cat, created = db.add_category_db("Pets", "expense", "Pet food and vet visits")
    assert created is True
    assert new_cat["name"] == "Pets"

    # Add existing category
    dup, created_dup = db.add_category_db("Pets", "expense")
    assert created_dup is False
    assert dup["id"] == new_cat["id"]

    # Update category
    updated = db.update_category_db("Pets", new_name="Pet Care", description="Updated pet care")
    assert updated is True
    fetched = db.get_category_by_id_or_name("Pet Care")
    assert fetched["name"] == "Pet Care"

    # Delete category
    deleted = db.delete_category_db("Pet Care")
    assert deleted is not None
    assert db.get_category_by_id_or_name("Pet Care") is None

def test_ensure_category_exists():
    # Pre-existing category
    groceries_name = db.ensure_category_exists("groceries", "expense")
    assert groceries_name == "Groceries"  # Canonical casing

    # New category
    new_name = db.ensure_category_exists("Crypto Investments", "income")
    assert new_name == "Crypto Investments"
    assert db.get_category_by_id_or_name("Crypto Investments") is not None

def test_category_rename_cascades_to_transactions():
    # Insert transaction under Groceries
    db.insert_transaction("2026-07-01", 50.0, "Groceries", "Milk and eggs", "expense")
    txns = db.get_transactions_data(category="Groceries")
    assert len(txns) == 1

    # Rename category Groceries -> Supermarket
    db.update_category_db("Groceries", new_name="Supermarket")

    # Check that transaction now reflects Supermarket
    new_txns = db.get_transactions_data(category="Supermarket")
    assert len(new_txns) == 1
    assert new_txns[0]["category"] == "Supermarket"

def test_category_mcp_tools():
    async def _test():
        server = FastMCP("Test Category Server")
        register_tools(server)

        # list_categories
        list_res = await server.call_tool("list_categories", {})
        text = extract_text(list_res)
        assert "📁 Category Library:" in text
        assert "Groceries" in text

        # add_category
        add_res = await server.call_tool("add_category", {
            "name": "Software",
            "type": "expense",
            "description": "Dev tools & licenses"
        })
        assert "Successfully added category" in extract_text(add_res)

        # update_category
        upd_res = await server.call_tool("update_category", {
            "category_id_or_name": "Software",
            "new_name": "Developer Software"
        })
        assert "Successfully updated category" in extract_text(upd_res)

        # delete_category
        del_res = await server.call_tool("delete_category", {
            "category_id_or_name": "Developer Software"
        })
        assert "Successfully deleted category" in extract_text(del_res)

    asyncio.run(_test())
