from sqlalchemy import select, func, or_
from src.db.connection import get_session
from src.db.models import Category

DEFAULT_CATEGORIES = [
    # Expenses
    {"name": "Food & Dining", "type": "expense", "description": "Meals, snacks, and dining out"},
    {"name": "Groceries", "type": "expense", "description": "Supermarket and food grocery shopping"},
    {"name": "Housing & Rent", "type": "expense", "description": "Rent, mortgage, and home maintenance"},
    {"name": "Utilities", "type": "expense", "description": "Electricity, water, gas, internet, and phone bills"},
    {"name": "Transportation", "type": "expense", "description": "Fuel, public transit, taxi, and car maintenance"},
    {"name": "Entertainment", "type": "expense", "description": "Movies, games, events, and hobbies"},
    {"name": "Shopping", "type": "expense", "description": "Clothing, electronics, household items, and personal items"},
    {"name": "Healthcare", "type": "expense", "description": "Medical expenses, prescriptions, and insurance"},
    {"name": "Subscriptions", "type": "expense", "description": "Recurring software, streaming, and membership fees"},
    {"name": "Miscellaneous", "type": "expense", "description": "General uncategorized expenses"},
    # Income
    {"name": "Salary", "type": "income", "description": "Regular employment paychecks and wages"},
    {"name": "Freelance", "type": "income", "description": "Contract work, consulting, and side gigs"},
    {"name": "Investments", "type": "income", "description": "Dividends, interest, and capital gains"},
    {"name": "Gifts", "type": "income", "description": "Monetary gifts and bonuses"},
    {"name": "Other Income", "type": "income", "description": "Other miscellaneous income sources"}
]

def seed_default_categories() -> None:
    """Seed initial standard categories if the category table is empty."""
    with get_session() as session:
        existing_count = session.scalar(select(func.count(Category.id)))
        if existing_count == 0:
            for cat_data in DEFAULT_CATEGORIES:
                cat = Category(
                    name=cat_data["name"],
                    type=cat_data["type"],
                    description=cat_data["description"]
                )
                session.add(cat)

def get_categories_db(type_filter: str = None):
    """Query active categories, optionally filtered by 'expense' or 'income'."""
    with get_session() as session:
        stmt = select(Category)
        if type_filter:
            stmt = stmt.where(func.lower(Category.type) == type_filter.lower())
        stmt = stmt.order_by(Category.type, Category.name)
        records = session.scalars(stmt).all()
        return [record.to_dict() for record in records]

def get_category_by_id_or_name(id_or_name):
    """Look up category by integer ID or case-insensitive string name."""
    with get_session() as session:
        if str(id_or_name).isdigit():
            record = session.get(Category, int(id_or_name))
            if record:
                return record.to_dict()
        
        stmt = select(Category).where(func.lower(Category.name) == str(id_or_name).lower())
        record = session.scalars(stmt).first()
        return record.to_dict() if record else None

def add_category_db(name: str, type_val: str = "expense", description: str = None):
    """Add a new category if it does not already exist."""
    existing = get_category_by_id_or_name(name)
    if existing:
        return existing, False

    with get_session() as session:
        cat = Category(
            name=name.strip(),
            type=type_val.lower(),
            description=description.strip() if description else None
        )
        session.add(cat)
        session.flush()
        result = cat.to_dict()
    return result, True

def update_category_db(id_or_name, new_name: str = None, type_val: str = None, description: str = None) -> bool:
    """Update an existing category's properties and propagate name updates to transactions."""
    with get_session() as session:
        record = None
        if str(id_or_name).isdigit():
            record = session.get(Category, int(id_or_name))
        if not record:
            stmt = select(Category).where(func.lower(Category.name) == str(id_or_name).lower())
            record = session.scalars(stmt).first()

        if not record:
            return False

        old_name = record.name
        if new_name is not None and new_name.strip() != old_name:
            clean_new_name = new_name.strip()
            record.name = clean_new_name
            # Cascade category name update to existing transaction records
            from src.db.models import Transaction
            stmt_txns = select(Transaction).where(func.lower(Transaction.category) == old_name.lower())
            txns = session.scalars(stmt_txns).all()
            for t in txns:
                t.category = clean_new_name

        if type_val is not None:
            record.type = type_val.lower()
        if description is not None:
            record.description = description.strip()
        return True

def delete_category_db(id_or_name) -> dict | None:
    """Delete a category by ID or name."""
    with get_session() as session:
        record = None
        if str(id_or_name).isdigit():
            record = session.get(Category, int(id_or_name))
        if not record:
            stmt = select(Category).where(func.lower(Category.name) == str(id_or_name).lower())
            record = session.scalars(stmt).first()

        if not record:
            return None

        data = record.to_dict()
        session.delete(record)
        return data

def ensure_category_exists(name: str, type_val: str = "expense") -> str:
    """
    Ensure category is registered. Returns canonical category name string.
    If category doesn't exist, it is automatically added.
    """
    existing = get_category_by_id_or_name(name)
    if existing:
        return existing["name"]
    new_cat, _ = add_category_db(name=name, type_val=type_val)
    return new_cat["name"]
