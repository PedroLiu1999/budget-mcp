from sqlalchemy import select, func, and_, or_
from src.db.connection import get_session
from src.db.models import Transaction, Category

def insert_transaction(date: str, amount: float, category: str, description: str, txn_type: str) -> None:
    """Insert a new transaction record linking category_id via ORM."""
    from src.db.categories import ensure_category_exists
    cat_data = ensure_category_exists(category, type_val=txn_type)
    with get_session() as session:
        txn = Transaction(
            date=date,
            amount=amount,
            category_id=cat_data["id"],
            category=cat_data["name"],
            description=description,
            type=txn_type.lower()
        )
        session.add(txn)

def get_summary_data(
    month: str = None,
    start_date: str = None,
    end_date: str = None,
    category: str = None,
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
        if category:
            cat_str = str(category).lower()
            if cat_str.isdigit():
                filters.append(or_(Transaction.category_id == int(category), Category.id == int(category)))
            else:
                filters.append(or_(func.lower(Category.name) == cat_str, func.lower(Transaction.category) == cat_str))
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
    category: str = None,
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

        if category:
            cat_str = str(category).lower()
            if cat_str.isdigit():
                filters.append(or_(Transaction.category_id == int(category), Category.id == int(category)))
            else:
                filters.append(or_(func.lower(Category.name) == cat_str, func.lower(Transaction.category) == cat_str))

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

        if "category" in updates_dict or "category_id" in updates_dict:
            cat_input = updates_dict.get("category") or updates_dict.get("category_id")
            from src.db.categories import ensure_category_exists
            cat_info = ensure_category_exists(cat_input, type_val=record.type)
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
