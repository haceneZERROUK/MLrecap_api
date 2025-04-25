# Routes auth
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import text
from typing import Annotated
from app.utils import db_dependency, get_current_user, create_access_token, get_password_hash, authenticate_user
from app.modeles import Users
# from app.schemas import NewPassword


router = APIRouter()

 
    
############################
#route pour obtenir le token
############################

@router.post("/login")    # pour récupérer le token d'accès
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency) :
    """
    Authentifie un utilisateur et génère un token JWT d'accès.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulaire contenant username (email) et password.
        db (Session): Session de base de données SQLAlchemy.

    Returns:
        dict: Token d'accès JWT et son type.
            Format: {"access_token": str, "token_type": "bearer"}

    Raises:
        HTTPException:
            - 401: Si les identifiants sont incorrects
            - 404: Si l'utilisateur n'existe pas

    Note:
        Le token généré contient l'email, le nom de la banque et le rôle de l'utilisateur
    """
    user = authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if not user : 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nom d'utilisateur ou mot de passe incorrect, veuillez corriger votre saisie", headers={"WWW-Authenticate": "Bearer"})
    token_data = {
        "sub": user.email,
        "extra" : {
            "username": user.username,
                
        }
    }
    acces_token = create_access_token(data=token_data)
    return {"access_token": acces_token, "token_type": "bearer"}
