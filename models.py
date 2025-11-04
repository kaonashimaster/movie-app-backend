from sqlalchemy import Column, Integer, String, Boolean # type: ignore
from database import Base

class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    is_favorite = Column(Boolean, default=True)