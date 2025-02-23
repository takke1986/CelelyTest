# Shopping Calculator

Django と Celery を使用した買い物リスト計算アプリケーション

## 機能

- 商品名と価格の登録
- 商品の削除
- 合計金額の自動計算（小数点以下切り捨て）
- 計算履歴の表示

## 技術スタック

- Python 3.11
- Django 5.0.4
- Celery 5.4.0
- Redis
- Bootstrap 5

## セットアップ

1. 依存関係のインストール:

```bash
pip install django celery redis
```

2. Redis サーバーの起動:

```bash
brew services start redis
```

3. データベースのセットアップ:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Celery ワーカーの起動:

```bash
celery -A shopping_calculator worker -l info
```

5. 開発サーバーの起動:

```bash
python manage.py runserver
```

## アプリケーション構成

## データモデル

### ShoppingItem

- name: 商品名（CharField）
- price: 価格（DecimalField, 小数点以下 1 桁）
- created_at: 作成日時（DateTimeField）

### CalculationResult

- total_amount: 合計金額（DecimalField, 小数点以下切り捨て）
- calculated_at: 計算日時（DateTimeField）
- status: 状態（CharField）

## 使用方法

1. ブラウザで http://127.0.0.1:8000 にアクセス
2. 商品名と価格を入力して追加
3. 必要に応じて商品を削除
4. 合計金額が自動的に計算されます

## メンテナンス

古い計算結果の削除:

```bash
python manage.py cleanup_results
```

## エラーハンドリング

- 価格入力の制限（小数点以下 1 桁まで）
- 削除時の確認機能
- 計算エラーの通知
- Redis 接続エラーの処理

## 開発モード

- DEBUG=True: 同期的に動作
- DEBUG=False: 非同期処理（Celery 使用）

## 注意事項

- 価格は小数点以下 1 桁まで入力可能
- 合計金額は小数点以下切り捨て
- 開発環境では DEBUG=True で同期的に動作

## ライセンス

MIT License

## 作者

takashitakeuchi

## 貢献方法

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題や提案がある場合は、Issue を作成してください。
