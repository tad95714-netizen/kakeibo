"""
月次集計(レポート)に関するビジネスロジックを担うモジュール。
指定期間の収支データを集計し、収入/支出の合計とカテゴリ別内訳を算出する。
"""

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.report import CategoryBreakdownItem, MonthlyReport


def get_monthly_report(db: Session, date_from: dt.date, date_to: dt.date) -> MonthlyReport:
    """指定期間内の収支を集計し、月次レポートを返す"""

    totals_stmt = (
        select(Transaction.type, func.sum(Transaction.amount))
        .where(Transaction.date >= date_from, Transaction.date <= date_to)
        .group_by(Transaction.type)
    )
    totals = dict(db.execute(totals_stmt).all())
    total_income = totals.get(TransactionType.INCOME, 0) or 0
    total_expense = totals.get(TransactionType.EXPENSE, 0) or 0

    breakdown_stmt = (
        select(
            Category.id,
            Category.name,
            Category.type,
            func.sum(Transaction.amount).label("amount"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.date >= date_from, Transaction.date <= date_to)
        .group_by(Category.id, Category.name, Category.type)
        .order_by(func.sum(Transaction.amount).desc())
    )
    category_breakdown = [
        CategoryBreakdownItem(
            category_id=row.id,
            category_name=row.name,
            type=row.type,
            amount=row.amount,
        )
        for row in db.execute(breakdown_stmt).all()
    ]

    return MonthlyReport(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        category_breakdown=category_breakdown,
    )