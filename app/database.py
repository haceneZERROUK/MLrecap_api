# from sqlmodel import SQLModel, create_engine, text, Session
# from dotenv import load_dotenv
# import os
# from .modeles import *

# """
# Module de configuration et de gestion de la connexion à la base de données.

# Ce module gère la configuration de la base de données, supporte SQLite et MariaDB,
# et fournit une fonction de connexion pour les sessions de base de données.

# Attributes:
#     DATABASE_URL (str): URL de connexion à la base de données
#     engine: Instance du moteur SQLAlchemy pour la connexion à la base de données
# """

# load_dotenv(dotenv_path=".env")

# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./api_users.db")  # Par défaut SQLite si non défini


# engine = create_engine(DATABASE_URL)

# SQLModel.metadata.create_all(engine)  # Crée les tables dans la base de données

# def db_connection():
#     """
#     Générateur de session de base de données pour FastAPI.

#     Yields:
#         Session: Session SQLModel active pour les opérations de base de données.

#     Note:
#         - Utilise le pattern contextuel pour garantir la fermeture de la session
#         - Compatible avec le système de dépendances de FastAPI
#         - Gère automatiquement la fermeture de la session après utilisation
#         - Utilisé comme dépendance dans les routes de l'API

#     Example:
#         ```python
#         @app.get("/films")
#         def get_films(db: Session = Depends(db_connection)):
#             return db.query(Film).all()
#         ```
#     """
#     session = Session(engine)  # Ouvre une session SQLModel
#     try:
#         yield session  # Garde la session ouverte pour l'API
#     finally:
#         session.close()  # Ferme la session après utilisation

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os
from .modeles import *  # Assurez-vous d'importer tous les modèles ici

load_dotenv(dotenv_path=".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin_user:azerty@localhost:5432/api_users")  # URL de connexion PostgreSQL

engine = create_engine(DATABASE_URL)

# Crée les tables dans la base de données seulement si elles n'existent pas déjà
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
