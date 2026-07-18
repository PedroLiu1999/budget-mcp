from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "type": self.type
        }

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
