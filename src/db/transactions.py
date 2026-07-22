from sqlalchemy import select, func, and_, or_
from src.db.connection import get_session
from src.db.models import Transaction, Category

def insert_transaction(date: str, amount: float, category_id: int = None, description: str = "", txn_type: str = "expense") -> dict:
    """Insert a new transaction record linking category_id via ORM and return the created record."""
    from src.db.categories import get_category_by_id_or_name
    cat_record = get_category_by_id_or_name(category_id) if category_id is not None else None
    cat_name = cat_record["name"] if cat_record else None

    with get_session() as session:
        txn = Transaction(
            date=date,
            amount=amount,
            category_id=cat_record["id"] if cat_record else None,
            category=cat_name,
            description=description,
            type=txn_type.lower()
        )
        session.add(txn)
        session.flush()
        record_dict = txn.to_dict()
    return record_dict

def get_uncategorized_transactions_data(
    txn_type: str = None,
    search: str = None,
    limit: int = 100
):
    """Query transactions that are uncategorized (category_id is NULL or category is 'Uncategorized'), sorted by description."""
    with get_session() as session:
        stmt = select(Transaction).outerjoin(Category)
        filters = [
            or_(
                Transaction.category_id.is_(None),
                Transaction.category == "Uncategorized",
                Transaction.category.is_(None)
            )
        ]

        if txn_type:
            filters.append(func.lower(Transaction.type) == txn_type.lower())
        if search:
            term = f"%{search}%"
            filters.append(Transaction.description.like(term))

        stmt = stmt.where(and_(*filters)).order_by(Transaction.description.asc(), Transaction.id.asc()).limit(limit)
        records = session.scalars(stmt).all()

        return [record.to_dict() for record in records]


def get_summary_data(
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    category_id: int = None,
    txn_type: str = None
):
    """Query aggregated summary data grouped by type and category using ORM."""
    with get_session() as session:
        cat_name_expr = func.coalesce(Category.name, Transaction.category, "Uncategorized")
        stmt = select(
            Transaction.type.label("type"),
            cat_name_expr.label("category"),
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).outerjoin(Category)

        filters = []
        if month:
            filters.append(Transaction.date.like(f"{month}%"))
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)
        if category_id is not None:
            filters.append(or_(Transaction.category_id == category_id, Category.id == category_id))
        if txn_type:
            filters.append(func.lower(Transaction.type) == txn_type.lower())

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.group_by(Transaction.type, cat_name_expr).order_by(Transaction.type, func.sum(Transaction.amount).desc())
        results = session.execute(stmt).all()

        return [
            {
                "type": row.type,
                "category": row.category,
                "total": row.total,
                "count": row.count
            }
            for row in results
        ]

def get_transactions_data(
    category_id: int = None,
    txn_type: str = None,
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    min_amount: float = None,
    max_amount: float = None,
    search: str = None,
    limit: int = 50
):
    """Query transaction records matching filter criteria using ORM."""
    with get_session() as session:
        stmt = select(Transaction).outerjoin(Category)
        filters = []

        if category_id is not None:
            filters.append(or_(Transaction.category_id == category_id, Category.id == category_id))

        if txn_type:
            filters.append(func.lower(Transaction.type) == txn_type.lower())
        if month:
            filters.append(Transaction.date.like(f"{month}%"))
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)
        if min_amount is not None:
            filters.append(Transaction.amount >= min_amount)
        if max_amount is not None:
            filters.append(Transaction.amount <= max_amount)
        if search:
            term = f"%{search}%"
            filters.append(or_(
                Transaction.description.like(term),
                Transaction.category.like(term),
                Category.name.like(term)
            ))

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit)
        records = session.scalars(stmt).all()

        return [record.to_dict() for record in records]

def get_transaction_by_id(transaction_id: int):
    """Fetch a single transaction record by ID using ORM."""
    with get_session() as session:
        record = session.get(Transaction, transaction_id)
        return record.to_dict() if record else None

def update_transaction_data(transaction_id: int, updates_dict: dict) -> bool:
    """Update fields of a specific transaction record using ORM."""
    if not updates_dict:
        return False
    with get_session() as session:
        record = session.get(Transaction, transaction_id)
        if not record:
            return False

        if "category_id" in updates_dict or "category" in updates_dict:
            cat_input = updates_dict.get("category_id") or updates_dict.get("category")
            from src.db.categories import get_category_by_id_or_name
            cat_info = get_category_by_id_or_name(cat_input)
            if cat_info:
                record.category_id = cat_info["id"]
                record.category = cat_info["name"]

        for field, value in updates_dict.items():
            if field in ("category", "category_id"):
                continue
            setattr(record, field, value)
        return True

def delete_transaction_data(transaction_id: int) -> None:
    """Delete a transaction record by ID using ORM."""
    with get_session() as session:
        record = session.get(Transaction, transaction_id)
        if record:
            session.delete(record)
