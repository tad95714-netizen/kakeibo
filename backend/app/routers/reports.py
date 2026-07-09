"""
月次集計(レポート)APIのエンドポイントを定義するモジュール。
"""

import calendar
import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.report import MonthlyReport
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    """指定した年月の収支集計(収入合計・支出合計・収支・カテゴリ別内訳)を取得する"""
    date_from = dt.date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    date_to = dt.date(year, month, last_day)

    return report_service.get_monthly_report(db, date_from, date_to)