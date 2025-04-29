from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv, find_dotenv
import os
from app.modeles import Users


dotenv_path = find_dotenv()
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./api_users.db") 

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

def db_connection():
    """
    Génère une session de base de données pour FastAPI
    """
    session = Session(engine)  # Ouvre une session SQLModel
    try:
        yield session  # Garde la session ouverte pour l'API
    finally:
        session.close()  # Ferme la session après utilisation
