import pytest
import src.db.connection as connection
import src.db.transactions as db_txns
from src.db import init_db

@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    """Use an isolated temporary SQLite database for each test function."""
    db_file = str(tmp_path / "test_budget.db")
    monkeypatch.setattr(connection, "DB_PATH", db_file)
    monkeypatch.setattr(db_txns, "DB_PATH", db_file)
    init_db()
    yield db_file
