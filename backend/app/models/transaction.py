"""
収支データ(取引記録)のテーブル定義。
1件の収入または支出を1レコードとして保存する。
"""

import datetime as dt
import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.category import Category


class TransactionType(str, enum.Enum):
    """収支の種別"""

    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """収支の記録を表すテーブル。1件の収入または支出を1レコードとして保存する"""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column()
    amount: Mapped[int] = mapped_column()
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    memo: Mapped[str | None] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[dt.datetime] = mapped_column(server_default=func.now())

    category: Mapped["Category"] = relationship(back_populates="transactions")