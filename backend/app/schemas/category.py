"""
カテゴリに関するAPIの入出力データ形式(スキーマ)を定義するモジュール。
DBのテーブル定義(models/category.py)とは別に、
APIとしてどんな形でデータをやり取りするかをここで定義する。
"""

from pydantic import BaseModel, ConfigDict

from app.models.transaction import TransactionType


class CategoryBase(BaseModel):
    """作成・読み取りで共通するカテゴリの項目"""

    name: str
    type: TransactionType


class CategoryCreate(CategoryBase):
    """カテゴリ新規作成時にクライアントから受け取るデータ"""

    pass


class CategoryUpdate(BaseModel):
    """カテゴリ更新時にクライアントから受け取るデータ(すべて任意項目)"""

    name: str | None = None
    type: TransactionType | None = None


class CategoryRead(CategoryBase):
    """APIがクライアントへ返すカテゴリのデータ(idを含む)"""

    model_config = ConfigDict(from_attributes=True)

    id: int