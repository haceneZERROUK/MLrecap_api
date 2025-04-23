# Routes auth
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.utils import db_dependency, get_current_user, create_access_token, get_password_hash, authenticate_user
from app.modeles import User
from app.schemas import NewPassword

router = APIRouter(prefix="/auth", tags=["auth"])

############################
# Route pour obtenir le token
############################

@router.post("/login")  # pour récupérer le token d'accès
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
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
        Le token généré contient l'email, le nom et le rôle de l'utilisateur.
    """
    user = authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le compte n'est pas activé ! Veuillez activer votre compte avant de vous connecter",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = {
        "sub": user.email,
        "extra": {
            "nom": user.nom,  # Changé de nom_banque à nom
            "role": user.role
        }
    }
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}

##############################
# Route pour activer le compte
##############################

@router.post("/activation/{email}")
def activation(email: str, password_form: NewPassword, db: db_dependency):
    """
    Active le compte d'un utilisateur et définit son mot de passe sans authentification.

    Args:
        email (str): Email de l'utilisateur à activer
        password_form (NewPassword): Formulaire contenant le nouveau mot de passe et sa confirmation
        db (Session): Session de base de données SQLAlchemy

    Returns:
        dict: Message de confirmation d'activation du compte

    Raises:
        HTTPException:
            - 404: Si l'utilisateur n'est pas trouvé
            - 400: Si le compte est déjà activé
            - 400: Si les mots de passe ne correspondent pas

    Note:
        - Ne nécessite pas d'authentification
        - Accessible via l'URL /activation/{email}
        - Le nouveau mot de passe est hashé avant stockage
    """
    # Utiliser l'ORM au lieu de SQL brut
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé dans la base de données"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le compte est déjà activé"
        )

    if password_form.new_password != password_form.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )

    # Mettre à jour l'utilisateur avec l'ORM
    user.hashed_password = get_password_hash(password_form.new_password)
    user.is_active = True
    db.commit()

    return {"message": "Le compte a été activé avec succès"}

##############################
# Route pour changer le mot de passe
##############################

@router.post("/change-password")
def change_password(
    password_form: NewPassword,
    db: db_dependency,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Permet à un utilisateur connecté de changer son mot de passe.

    Args:
        password_form (NewPassword): Formulaire contenant le nouveau mot de passe et sa confirmation
        db (Session): Session de base de données SQLAlchemy
        current_user (User): Utilisateur actuellement authentifié

    Returns:
        dict: Message de confirmation du changement de mot de passe

    Raises:
        HTTPException:
            - 400: Si les mots de passe ne correspondent pas

    Note:
        - Nécessite une authentification
        - Le nouveau mot de passe est hashé avant stockage
    """
    if password_form.new_password != password_form.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )

    current_user.hashed_password = get_password_hash(password_form.new_password)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}