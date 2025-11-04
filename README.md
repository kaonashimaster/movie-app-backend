映画推薦アプリ (バックエンド)

これは、ReactとFastAPIで構築する映画推薦Webアプリケーションのバックエンド（サーバーサイド）リポジトリです。

主な機能

GET /movies: TMDBから「人気映画」のリストを取得して返します。

GET /favorites: データベースから「お気に入り映画」のリストを返します。

POST /favorites: 映画を「お気に入り」としてデータベースに保存します。

DELETE /favorites/{movie_id}: 映画を「お気に入り」から削除します。

使用技術

Python

FastAPI

SQLAlchemy (SQLite)

TMDB API

dotenv (環境変数管理)
