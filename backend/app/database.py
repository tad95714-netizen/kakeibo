"""
データベースへの接続を管理するモジュール。
SQLAlchemyのエンジン・セッション・Baseクラスをここで定義し、
models/ 配下の各テーブル定義や、routers/ 配下のAPI処理から利用する。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# SQLiteへの接続エンジンを作成
# check_same_thread=False は、FastAPIが複数スレッドから同じ接続を
# 使う可能性があるSQLite特有の制約に対応するための設定
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# DBセッションを作るためのファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """各テーブルのモデルクラスが継承する基底クラス"""

    pass


def get_db():
    """
    FastAPIの依存性注入(Depends)で使うためのDBセッション生成関数。
    リクエストごとにセッションを作り、処理が終わったら必ずクローズする。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()