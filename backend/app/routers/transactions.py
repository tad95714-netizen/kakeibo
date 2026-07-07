"""
収支データ(取引記録)に関するAPIの入出力データ形式(スキーマ)を定義するモジュール。
"""

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType
from app.schemas.category import CategoryRead


class TransactionBase(BaseModel):
    """作成・読み取りで共通する収支データの項目"""

    date: dt.date
    amount: int = Field(gt=0, description="金額(円)。常に正の整数で入力する")
    type: TransactionType
    memo: str | None = Field(default=None, max_length=200)


class TransactionCreate(TransactionBase):
    """収支データ新規作成時にクライアントから受け取るデータ"""

    category_id: int


class TransactionUpdate(BaseModel):
    """収支データ更新時にクライアントから受け取るデータ(すべて任意項目)"""

    date: dt.date | None = None
    amount: int | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    memo: str | None = Field(default=None, max_length=200)
    category_id: int | None = None


class TransactionRead(TransactionBase):
    """APIがクライアントへ返す収支データ(idや関連するカテゴリ情報を含む)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    category: CategoryRead
    created_at: dt.datetime