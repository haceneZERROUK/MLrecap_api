# gestion des tokens
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv, find_dotenv
from passlib.context import CryptContext
from app.database import Session, db_connection
from jose import JWTError, jwt
from app.modeles import Users
from fastapi.security import OAuth2PasswordBearer



router = APIRouter(prefix="/auth", tags=["auth"])   # pour les routes d'authentification

dot_env_path = find_dotenv()
load_dotenv(dotenv_path=dot_env_path, override=True)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # pour hasher le mot de passe 
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")  # pour obtenir le token d'accès à l'API  



db_dependency = Annotated[Session, Depends(db_connection)]   # dépendance pour la connexion à la BDD

def create_access_token(data: dict, expires_delta : timedelta = None) -> str:
    """
    Crée un token JWT d'accès.

    Args:
        data (dict): Données à encoder dans le token
        expires_delta (timedelta, optional): Durée de validité personnalisée

    Returns:
        str: Token JWT encodé

    Note:
        - Utilise la SECRET_KEY et l'ALGORITHM définis
        - Durée par défaut définie par ACCESS_TOKEN_EXPIRE_MINUTES
        - Inclut automatiquement la date d'expiration
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_password_hash(password : str) -> str: 
    """
    Génère un hash bcrypt d'un mot de passe.

    Args:
        password (str): Mot de passe en clair

    Returns:
        str: Hash bcrypt du mot de passe

    Note:
        Utilise l'algorithme bcrypt avec salt automatique
    """
    return bcrypt_context.hash(password)


def authenticate_user(username: str, password: str, db: db_dependency) -> Users:
    """
    Authentifie un utilisateur par username OU email.
    """
    user = db.query(Users).filter((Users.email == username) | (Users.username == username)).first()    
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency) -> Users:
    """
    Récupère l'utilisateur actuel à partir du token JWT.

    Args:
        token (str): Token JWT à décoder
        db (Session): Session de base de données

    Returns:
        Users: Utilisateur authentifié

    Raises:
        HTTPException:
            - 401: Si le token est invalide
            - 401: Si l'utilisateur n'existe pas

    Note:
        - Vérifie la validité du token
        - Vérifie l'existence de l'utilisateur
        - Utilisé comme dépendance pour les routes protégées
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
        user = db.query(Users).filter(Users.email == username).first()
        if user is None : 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nom d'utilisateur invalide")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
