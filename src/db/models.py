from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String, default="expense")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description
        }

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)

    category_rel: Mapped[Optional[Category]] = relationship("Category")

    def to_dict(self):
        cat_name = self.category_rel.name if self.category_rel else (self.category or "Uncategorized")
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "category_id": self.category_id,
            "category": cat_name,
            "description": self.description,
            "type": self.type
        }
