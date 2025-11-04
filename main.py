from fastapi import FastAPI # type: ignore
import models #設計図
from database import engine #接続道具
import uvicorn # type: ignore
import requests # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from sqlalchemy.orm import Session # type: ignore
import schemas
from database import SessionLocal
from fastapi import Depends # type: ignore
from fastapi import HTTPException # type: ignore

# .envファイルから環境変数を読み込む
load_dotenv()

app = FastAPI()

# データベースセッションを取得するための依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# データベースのテーブルを作成します
#models.Base.metadataは、models.pyで定義した設計図の集まりです
#.create_all(bind=engine)は、その設計図に基づいて実際のテーブルをデータベースに作成する命令です
models.Base.metadata.create_all(bind=engine)

# CORS設定
origins = [
    "http://localhost:5173",
]

# app（あなたのサーバー）に、新しい警備システムを追加します
app.add_middleware(
    # 警備システムの種類は「CORS警備員」です
    CORSMiddleware,
    
    # 【許可する訪問者のリスト】
    # "http://localhost:5173" という住所から来た人だけ通してOKです
    allow_origins=origins,
    
    # 【身分証の確認】
    # もし訪問者が身分証（クッキーなど）を持っていたら、それも確認してOKです
    allow_credentials=True,
    
    # 【許可する行動のリスト】
    # 訪問者が「見せてください(GET)」や「これを預かってください(POST)」など、
    # どんな行動(*)をしようとしても、すべて許可してOKです
    allow_methods=["*"],
    
    # 【許可する持ち物のリスト】
    # 訪問者がどんな書類(*)を持っていても、すべて許可してOKです
    allow_headers=["*"],
)

@app.get("/movies")
async def get_movies():
    # 環境変数からアクセストークンを安全に取得
    accessToken = os.getenv("TMDB_ACCESS_TOKEN")
    
    if not accessToken:
        return {"error": "Access token not found"}

    url = "https://api.themoviedb.org/3/movie/popular"
    
    # APIリクエストのヘッダーとパラメータを設定
    # ここで、アクセストークンを使って認証情報をヘッダーに追加します
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {accessToken}"
    }
    
    #追加の要望
    params = {
        "language": "ja-JP",
        "page": 1
    }

    try:
        #先ほど設定したヘッダーとパラメータを使って、
        #API(TMDB)にリクエストを送ります
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()  # エラーがあれば例外を発生させる
        data = r.json() #TMDBからの返事をJSON形式で受け取ります
        # その中から「results」という部分を取り出します
        # もし「results」がなければ、空のリストを使います
        movies = data.get("results", [])
        return movies
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

#今回はデータを取得(GET)するのではなく、作成(POST)するので、@app.postを使用
@app.post("/favorites")
async def create_favorite_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    # 受け取ったデータを使って、データベースに保存するモデルを作成
    db_movie = models.FavoriteMovie(movie_id=movie.movie_id, title=movie.title)
    
    # データベースに「追加して」とお願いする（まだ保存はされない）
    db.add(db_movie)
    # 変更をデータベースに「確定（コミット）」する（ここで初めて保存される）
    db.commit()
    # 最新の状態をdb_movieに反映させる
    db.refresh(db_movie)
    
    return db_movie

@app.get("/favorites")
async def get_favorite_movies(db: Session = Depends(get_db)):
    # データベースからすべてのお気に入り映画を取得
    favorite_movies = db.query(models.FavoriteMovie).all()
    return favorite_movies

@app.delete("/favorites/{movie_id}")
async def cdelete_favorite_movie(movie_id: int, db: Session = Depends(get_db)):
    # 指定されたmovie_idのお気に入り映画をデータベースから削除
    db_movie = db.query(models.FavoriteMovie).filter(models.FavoriteMovie.movie_id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Favorite movie not found")
    
    # 3. 映画が見つかったら、削除して変更を保存
    db.delete(db_movie)
    db.commit()
    
    # 4. 成功したことを伝える
    return {"message": "Favorite movie deleted successfully"}