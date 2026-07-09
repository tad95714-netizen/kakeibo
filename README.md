# 家計簿アプリ (kakeibo-app)

個人で使うための家計簿(household budget)Webアプリです。PC・スマホ両方のブラウザから、同じサーバーにアクセスして日々の収支を記録できます。

## 機能

- **収支の記録**: 日付・金額・カテゴリ・メモを入力し、月ごとに一覧表示・削除ができる
- **カテゴリ管理**: 収入用/支出用のカテゴリを追加・削除できる
- **月次集計(レポート)**: 選択した月の収入合計・支出合計・収支と、カテゴリ別内訳を横棒グラフで表示

## 技術スタック

**バックエンド**
- Python 3.10以上
- FastAPI
- SQLAlchemy 2.0
- SQLite
- [uv](https://docs.astral.sh/uv/)(パッケージ管理・仮想環境)

**フロントエンド**
- HTML / CSS / JavaScript(素のまま、ビルドツール不使用)

## セットアップ

### 前提

[uv](https://docs.astral.sh/uv/) がインストールされていること。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### インストールと起動

```bash
cd kakeibo-app/backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0
```

ブラウザで `http://localhost:8000/` を開くとアプリが表示されます。

### スマホからアクセスする場合

PCと同じWi-Fiに接続した状態で、スマホのブラウザから `http://<PCのIPアドレス>:8000/` にアクセスしてください。

外出先からもアクセスしたい場合は、クラウドへのデプロイやTailscaleなどのVPNの利用を検討してください(現状はローカルネットワーク内でのアクセスを想定した構成です)。

## プロジェクト構成

```
kakeibo-app/
├── backend/
│   ├── app/
│   │   ├── main.py               # アプリのエントリーポイント(DB初期化・ルーター登録・静的配信)
│   │   ├── config.py             # 設定(DBパスなど)
│   │   ├── database.py           # DB接続・セッション管理
│   │   ├── models/               # DBテーブル定義(SQLAlchemy)
│   │   │   ├── transaction.py
│   │   │   └── category.py
│   │   ├── schemas/               # APIの入出力データ形式(Pydantic)
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   └── report.py
│   │   ├── routers/               # APIエンドポイント
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   └── reports.py
│   │   └── services/              # 集計などのビジネスロジック
│   │       └── report_service.py
│   ├── pyproject.toml
│   └── uv.lock
└── frontend/
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        ├── api.js                 # バックエンドとの通信共通処理
        ├── categories.js          # カテゴリ管理パネル(+ トースト通知の共通処理)
        ├── transactions.js        # 収支入力・一覧パネル
        ├── reports.js             # レポートパネル
        └── main.js                # タブ切り替え・起動時の初期化
```

## API一覧

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/api/categories` | カテゴリ一覧取得(`type`で絞り込み可) |
| POST | `/api/categories` | カテゴリ作成 |
| GET | `/api/categories/{id}` | カテゴリ1件取得 |
| PUT | `/api/categories/{id}` | カテゴリ更新 |
| DELETE | `/api/categories/{id}` | カテゴリ削除 |
| GET | `/api/transactions` | 収支データ一覧取得(`date_from`/`date_to`/`type`/`category_id`で絞り込み可) |
| POST | `/api/transactions` | 収支データ作成 |
| GET | `/api/transactions/{id}` | 収支データ1件取得 |
| PUT | `/api/transactions/{id}` | 収支データ更新 |
| DELETE | `/api/transactions/{id}` | 収支データ削除 |
| GET | `/api/reports/monthly?year=&month=` | 指定した年月の収支集計 |

サーバー起動中に `http://localhost:8000/docs` を開くと、Swagger UIから対話的にAPIを試せます。

## 設計方針

- **疎結合な構成**: `models`(DBテーブル定義)/ `schemas`(API入出力の型) / `routers`(エンドポイント) / `services`(集計ロジック)を分離しています。層をまたぐ変更が少なく済むよう、機能追加時は基本的に新しいファイルを追加する形で対応できます
- **フロントエンドの配色**: 日本の帳簿文化にある「黒字(収入)/赤字(支出)」の慣習をそのまま配色ルールにしています

## 現時点での制限・今後の拡張候補

- カテゴリ・収支データの「編集」はAPI(`PUT`)としては実装済みですが、画面上の編集UIはまだ無く、追加・削除のみ操作できます
- グラフ表示は簡易的な横棒表示のみです
- 複数口座への対応、レシート読み取り、予算アラート、CSVエクスポートなどは未実装です