from sqlmodel import SQLModel, create_engine, text, Session
from dotenv import load_dotenv
import os
from .modeles import *

"""
Module de configuration et de gestion de la connexion à la base de données.

Ce module gère la configuration de la base de données, supporte SQLite et MariaDB,
et fournit une fonction de connexion pour les sessions de base de données.

Attributes:
    DATABASE_URL (str): URL de connexion à la base de données
    engine: Instance du moteur SQLAlchemy pour la connexion à la base de données
"""

load_dotenv(dotenv_path="./app/.env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # Par défaut SQLite si non défini

# Vérifier si on utilise MariaDB pour créer la base de données si nécessaire
if "mariadb" in DATABASE_URL:
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", None)
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", None)
    DB_NAME = "film_popularity"  # Nom de la base de données pour le projet

    # Moteur pour créer la BDD
    temp_engine = create_engine(f"mariadb+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@localhost:3306/")

    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conn.execute(text("FLUSH PRIVILEGES"))
    temp_engine.dispose()

    DATABASE_URL = f"mariadb+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@localhost:3306/{DB_NAME}"  # BDD définitive sous MariaDB

sqlite_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=sqlite_args)

SQLModel.metadata.create_all(engine)  # Crée les tables dans la base de données

def db_connection():
    """
    Générateur de session de base de données pour FastAPI.

    Yields:
        Session: Session SQLModel active pour les opérations de base de données.

    Note:
        - Utilise le pattern contextuel pour garantir la fermeture de la session
        - Compatible avec le système de dépendances de FastAPI
        - Gère automatiquement la fermeture de la session après utilisation
        - Utilisé comme dépendance dans les routes de l'API

    Example:
        ```python
        @app.get("/films")
        def get_films(db: Session = Depends(db_connection)):
            return db.query(Film).all()
        ```
    """
    session = Session(engine)  # Ouvre une session SQLModel
    try:
        yield session  # Garde la session ouverte pour l'API
    finally:
        session.close()  # Ferme la session après utilisation