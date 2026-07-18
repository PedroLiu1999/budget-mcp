import src.db as db

def test_db_insert_and_get_transactions():
    db.insert_transaction("2026-07-01", 100.0, "Food", "Groceries", "expense")
    db.insert_transaction("2026-07-02", 2000.0, "Salary", "Paycheck", "income")

    rows = db.get_transactions_data()
    assert len(rows) == 2

    # Query with filters
    food_rows = db.get_transactions_data(category="Food")
    assert len(food_rows) == 1
    assert food_rows[0]["amount"] == 100.0
    assert food_rows[0]["type"] == "expense"

    income_rows = db.get_transactions_data(txn_type="income")
    assert len(income_rows) == 1
    assert income_rows[0]["amount"] == 2000.0

def test_db_filters_search_date_amount():
    db.insert_transaction("2026-06-10", 15.0, "Dining", "McDonalds lunch", "expense")
    db.insert_transaction("2026-06-15", 45.0, "Dining", "Dinner party", "expense")
    db.insert_transaction("2026-07-01", 150.0, "Utilities", "Electricity bill", "expense")

    # Search term
    search_rows = db.get_transactions_data(search="McDonalds")
    assert len(search_rows) == 1
    assert search_rows[0]["description"] == "McDonalds lunch"

    # Date range
    june_rows = db.get_transactions_data(month="2026-06")
    assert len(june_rows) == 2

    # Amount range
    large_rows = db.get_transactions_data(min_amount=100.0)
    assert len(large_rows) == 1
    assert large_rows[0]["amount"] == 150.0

def test_db_summary_data():
    db.insert_transaction("2026-07-01", 3000.0, "Salary", "Monthly pay", "income")
    db.insert_transaction("2026-07-05", 50.0, "Groceries", "Supermarket", "expense")
    db.insert_transaction("2026-07-10", 30.0, "Groceries", "Snacks", "expense")

    summary_rows = db.get_summary_data(month="2026-07")
    assert len(summary_rows) == 2  # Salary and Groceries

    cat_totals = {r["category"]: r["total"] for r in summary_rows}
    assert cat_totals["Salary"] == 3000.0
    assert cat_totals["Groceries"] == 80.0

def test_db_update_and_delete():
    db.insert_transaction("2026-07-01", 20.0, "Misc", "Item 1", "expense")
    rows = db.get_transactions_data()
    txn_id = rows[0]["id"]

    # Update
    updated = db.update_transaction_data(txn_id, {"amount": 25.0, "category": "UpdatedMisc"})
    assert updated is True

    record = db.get_transaction_by_id(txn_id)
    assert record["amount"] == 25.0
    assert record["category"] == "UpdatedMisc"

    # Delete
    db.delete_transaction_data(txn_id)
    assert db.get_transaction_by_id(txn_id) is None
