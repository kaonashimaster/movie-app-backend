from pydantic import BaseModel # type: ignore

# Reactアプリから受け取るデータの形を定義
#「お気に入り映画を登録する際には、movie_id（数値）とtitle（文字列）の2つの情報を送ってくださいね」というルールを定義
class MovieCreate(BaseModel):
    movie_id: int
    title: str