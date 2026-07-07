"""
カテゴリ(収支の分類)のテーブル定義。
「食費」「交通費」「給与」のように、取引を分類するためのラベルを表す。
"""

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.transaction import TransactionType

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Category(Base):
    """収支を分類するためのカテゴリを表すテーブル(例: 食費、交通費、給与)"""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", "type", name="uq_category_name_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")