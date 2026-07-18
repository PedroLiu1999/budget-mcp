from sqlalchemy import select, func, and_, or_
from src.db.connection import get_session
from src.db.models import Transaction

def insert_transaction(date: str, amount: float, category: str, description: str, txn_type: str) -> None:
    """Insert a new transaction record using ORM."""
    with get_session() as session:
        txn = Transaction(
            date=date,
            amount=amount,
            category=category,
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
        stmt = select(
            Transaction.type.label("type"),
            Transaction.category.label("category"),
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        )

        filters = []
        if month:
            filters.append(Transaction.date.like(f"{month}%"))
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)
        if category:
            filters.append(func.lower(Transaction.category) == category.lower())
        if txn_type:
            filters.append(func.lower(Transaction.type) == txn_type.lower())

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.group_by(Transaction.type, Transaction.category).order_by(Transaction.type, func.sum(Transaction.amount).desc())
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
        stmt = select(Transaction)
        filters = []

        if category:
            filters.append(func.lower(Transaction.category) == category.lower())
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
            filters.append(or_(Transaction.description.like(term), Transaction.category.like(term)))

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
        for field, value in updates_dict.items():
            setattr(record, field, value)
        return True

def delete_transaction_data(transaction_id: int) -> None:
    """Delete a transaction record by ID using ORM."""
    with get_session() as session:
        record = session.get(Transaction, transaction_id)
        if record:
            session.delete(record)
