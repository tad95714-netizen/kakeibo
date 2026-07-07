"""
アプリケーション全体の設定を管理するモジュール。
データベースの保存場所やアプリ名など、変更されうる値をここに集約することで、
他のファイルを直接書き換えずに設定を変更できるようにする。
"""

from pathlib import Path

# このファイル(config.py)から見て backend/ フォルダを指す
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLiteデータベースファイルの保存場所(backend/kakeibo.db)
DATABASE_PATH = BASE_DIR / "kakeibo.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# アプリケーションの基本情報
APP_NAME = "家計簿アプリ"
APP_VERSION = "0.1.0"