"""
FastAPIアプリケーションのエントリーポイント。
DBテーブルの作成、各ルーターの登録、フロントエンドの静的ファイル配信を行う。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_VERSION, BASE_DIR
from app.database import Base, engine
from app.routers import categories, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリ起動時にDBのテーブルを作成する"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

app.include_router(categories.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")

# フロントエンドの静的ファイルを配信する(backend/ から見て ../frontend)
FRONTEND_DIR = BASE_DIR.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")