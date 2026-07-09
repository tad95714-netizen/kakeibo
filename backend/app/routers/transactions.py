"""
収支データ管理APIのエンドポイントを定義するモジュール。
一覧取得・作成・取得・更新・削除の基本的なCRUD操作を提供する。
"""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _get_category_or_404(db: Session, category_id: int) -> Category:
    """指定したIDのカテゴリを取得する。存在しない場合は404エラー"""
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="指定されたカテゴリが見つかりません")
    return category


def _validate_type_matches_category(transaction_type: TransactionType, category: Category) -> None:
    """取引の種別とカテゴリの種別が一致しているかを確認する"""
    if category.type != transaction_type:
        raise HTTPException(
            status_code=400,
            detail="取引の種別(収入/支出)とカテゴリの種別が一致しません",
        )


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    type: TransactionType | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    収支データの一覧を取得する。
    date_from/date_to で期間、type/category_id で絞り込みができる。
    """
    stmt = select(Transaction).options(joinedload(Transaction.category))
    if date_from is not None:
        stmt = stmt.where(Transaction.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Transaction.date <= date_to)
    if type is not None:
        stmt = stmt.where(Transaction.type == type)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc())
    return db.scalars(stmt).unique().all()


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """新しい収支データを作成する"""
    category = _get_category_or_404(db, transaction.category_id)
    _validate_type_matches_category(transaction.type, category)

    db_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        type=transaction.type,
        memo=transaction.memo,
        category_id=transaction.category_id,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """指定したIDの収支データを1件取得する"""
    db_transaction = db.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="収支データが見つかりません")
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)
):
    """指定したIDの収支データを更新する(部分更新に対応)"""
    db_transaction = db.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="収支データが見つかりません")

    update_data = transaction.model_dump(exclude_unset=True)

    # 種別 or カテゴリを変更する場合は、整合性を確認する
    if "type" in update_data or "category_id" in update_data:
        new_type = update_data.get("type", db_transaction.type)
        new_category_id = update_data.get("category_id", db_transaction.category_id)
        category = _get_category_or_404(db, new_category_id)
        _validate_type_matches_category(new_type, category)

    for field, value in update_data.items():
        setattr(db_transaction, field, value)

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """指定したIDの収支データを削除する"""
    db_transaction = db.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="収支データが見つかりません")
    db.delete(db_transaction)
    db.commit()