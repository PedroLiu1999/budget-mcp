import pytest
from sqlalchemy import create_engine
from src.db.connection import set_engine, init_db

@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """Use an isolated temporary SQLite database for each test function."""
    db_file = str(tmp_path / "test_budget.db")
    test_engine = create_engine(f"sqlite:///{db_file}", echo=False)
    set_engine(test_engine)
    init_db()
    yield db_file
