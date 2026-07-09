"""
月次集計(レポート)に関するAPIの出力データ形式(スキーマ)を定義するモジュール。
"""

from pydantic import BaseModel

from app.models.transaction import TransactionType


class CategoryBreakdownItem(BaseModel):
    """カテゴリ別の集計1件分"""

    category_id: int
    category_name: str
    type: TransactionType
    amount: int


class MonthlyReport(BaseModel):
    """指定した月の収支集計結果"""

    total_income: int
    total_expense: int
    balance: int
    category_breakdown: list[CategoryBreakdownItem]