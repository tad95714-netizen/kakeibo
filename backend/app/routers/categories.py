"""
カテゴリ管理APIのエンドポイントを定義するモジュール。
一覧取得・作成・取得・更新・削除の基本的なCRUD操作を提供する。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.transaction import TransactionType
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    type: TransactionType | None = None,
    db: Session = Depends(get_db),
):
    """カテゴリの一覧を取得する。typeを指定すると収入用/支出用で絞り込める"""
    stmt = select(Category)
    if type is not None:
        stmt = stmt.where(Category.type == type)
    stmt = stmt.order_by(Category.id)
    return db.scalars(stmt).all()


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """新しいカテゴリを作成する"""
    db_category = Category(name=category.name, type=category.type)
    db.add(db_category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="同じ名前・種別のカテゴリが既に存在します"
        )
    db.refresh(db_category)
    return db_category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """指定したIDのカテゴリを1件取得する"""
    db_category = db.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
    return db_category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)
):
    """指定したIDのカテゴリを更新する(部分更新に対応)"""
    db_category = db.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")

    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="同じ名前・種別のカテゴリが既に存在します"
        )
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """指定したIDのカテゴリを削除する"""
    db_category = db.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
    db.delete(db_category)
    db.commit()