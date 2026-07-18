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
    deleted, err = db.delete_category_db("Pet Care")
    assert err is None
    assert deleted is not None
    assert db.get_category_by_id_or_name("Pet Care") is None

def test_ensure_category_exists():
    # Pre-existing category by name
    groceries_cat = db.ensure_category_exists("groceries", "expense")
    assert groceries_cat["name"] == "Groceries"  # Canonical casing

    # Pre-existing category by ID
    cat_id = groceries_cat["id"]
    by_id_cat = db.ensure_category_exists(cat_id, "expense")
    assert by_id_cat["id"] == cat_id
    assert by_id_cat["name"] == "Groceries"

    # New category
    new_cat = db.ensure_category_exists("Crypto Investments", "income")
    assert new_cat["name"] == "Crypto Investments"
    assert db.get_category_by_id_or_name("Crypto Investments") is not None

def test_category_rename_cascades_to_transactions():
    groc_cat = db.get_category_by_id_or_name("Groceries")
    # Insert transaction under Groceries
    db.insert_transaction("2026-07-01", 50.0, groc_cat["id"], "Milk and eggs", "expense")
    txns = db.get_transactions_data(category_id=groc_cat["id"])
    assert len(txns) == 1

    # Rename category Groceries -> Supermarket
    db.update_category_db(groc_cat["id"], new_name="Supermarket")

    # Check that transaction now reflects Supermarket
    new_txns = db.get_transactions_data(category_id=groc_cat["id"])
    assert len(new_txns) == 1
    assert new_txns[0]["category"] == "Supermarket"

def test_category_by_id_in_transactions():
    util_cat = db.get_category_by_id_or_name("Utilities")
    cat_id = util_cat["id"]

    # Insert transaction using category ID
    db.insert_transaction("2026-07-05", 25.0, cat_id, "Electricity", "expense")

    # Get transactions by category ID
    txns = db.get_transactions_data(category_id=cat_id)
    assert len(txns) == 1
    assert txns[0]["category"] == "Utilities"
    assert txns[0]["category_id"] == cat_id

def test_delete_category_denies_if_linked_transactions():
    temp_cat, _ = db.add_category_db("Temporary Cat", "expense")
    shopping_cat = db.get_category_by_id_or_name("Shopping")

    txn = db.insert_transaction("2026-07-01", 33.0, temp_cat["id"], "Temp item", "expense")

    # Attempt deletion without reassign_to target -> Denied
    del_data, err = db.delete_category_db(temp_cat["id"])
    assert del_data is None
    assert "Cannot delete category" in err

    # Perform deletion with valid reassign_to target -> Succeeded
    del_data, err2 = db.delete_category_db(temp_cat["id"], reassign_to_id_or_name=shopping_cat["id"])
    assert err2 is None
    assert del_data["reassigned_transactions_count"] == 1
    assert del_data["reassigned_to"] == "Shopping"

    # Verify transaction reassignment
    updated_txn = db.get_transaction_by_id(txn["id"])
    assert updated_txn["category_id"] == shopping_cat["id"]
    assert updated_txn["category"] == "Shopping"

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
