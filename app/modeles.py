from sqlmodel import SQLModel, Field
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    role: str = Field(default="user")  # Par défaut, un utilisateur est un "user"

class Film(SQLModel, table=True):
    __tablename__ = "films"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    original_title: Optional[str] = None
    release_date: str  # Utilisez str ou date selon votre besoin
    duration: Optional[int] = None  # en minutes
    synopsis: Optional[str] = None
    budget: Optional[float] = None
    is_sequel: bool = Field(default=False)
    franchise: Optional[str] = None
    rating: Optional[str] = None  # Classification par âge
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None

    # Données sociales/marketing
    twitter_mentions: Optional[int] = None
    imdb_rating: Optional[float] = None
    metacritic_score: Optional[int] = None
    rotten_tomatoes_score: Optional[int] = None

    # Données US
    us_box_office: Optional[float] = None
    us_release_date: Optional[str] = None  # Utilisez str ou date selon votre besoin

class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    film_id: int = Field(foreign_key="films.id")
    predicted_entries: int
    predicted_entries_cinema: int
    predicted_daily_audience: float
    confidence_score: float
    recommended_room: Optional[int] = None
    estimated_revenue: float
    prediction_date: str  # Utilisez str ou date selon votre besoin