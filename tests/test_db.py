import src.db as db

def test_db_insert_and_get_transactions():
    food_cat = db.get_category_by_id_or_name("Groceries")
    salary_cat = db.get_category_by_id_or_name("Salary")

    db.insert_transaction("2026-07-01", 100.0, food_cat["id"], "Groceries", "expense")
    db.insert_transaction("2026-07-02", 2000.0, salary_cat["id"], "Paycheck", "income")

    rows = db.get_transactions_data()
    assert len(rows) == 2

    # Query with filters by category_id
    food_rows = db.get_transactions_data(category_id=food_cat["id"])
    assert len(food_rows) == 1
    assert food_rows[0]["amount"] == 100.0
    assert food_rows[0]["category"] == "Groceries"
    assert food_rows[0]["type"] == "expense"

    income_rows = db.get_transactions_data(txn_type="income")
    assert len(income_rows) == 1
    assert income_rows[0]["amount"] == 2000.0

def test_db_filters_search_date_amount():
    food_cat = db.get_category_by_id_or_name("Food & Dining")
    util_cat = db.get_category_by_id_or_name("Utilities")

    db.insert_transaction("2026-06-10", 15.0, food_cat["id"], "McDonalds lunch", "expense")
    db.insert_transaction("2026-06-15", 45.0, food_cat["id"], "Dinner party", "expense")
    db.insert_transaction("2026-07-01", 150.0, util_cat["id"], "Electricity bill", "expense")

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
    salary_cat = db.get_category_by_id_or_name("Salary")
    groc_cat = db.get_category_by_id_or_name("Groceries")

    db.insert_transaction("2026-07-01", 3000.0, salary_cat["id"], "Monthly pay", "income")
    db.insert_transaction("2026-07-05", 50.0, groc_cat["id"], "Supermarket", "expense")
    db.insert_transaction("2026-07-10", 30.0, groc_cat["id"], "Snacks", "expense")

    summary_rows = db.get_summary_data(month="2026-07")
    assert len(summary_rows) == 2

    cat_totals = {r["category"]: r["total"] for r in summary_rows}
    assert cat_totals["Salary"] == 3000.0
    assert cat_totals["Groceries"] == 80.0

def test_db_update_and_delete():
    misc_cat = db.get_category_by_id_or_name("Miscellaneous")
    shop_cat = db.get_category_by_id_or_name("Shopping")

    db.insert_transaction("2026-07-01", 20.0, misc_cat["id"], "Item 1", "expense")
    rows = db.get_transactions_data()
    txn_id = rows[0]["id"]

    # Update
    updated = db.update_transaction_data(txn_id, {"amount": 25.0, "category_id": shop_cat["id"]})
    assert updated is True

    record = db.get_transaction_by_id(txn_id)
    assert record["amount"] == 25.0
    assert record["category"] == "Shopping"

    # Delete
    db.delete_transaction_data(txn_id)
    assert db.get_transaction_by_id(txn_id) is None
