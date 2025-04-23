# Routes admin
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import CreateUserRequest, UpdateUserRequest
from app.utils import db_dependency, bcrypt_context, get_current_user
from app.modeles import User
from typing import Annotated, List

router = APIRouter(prefix="/admin", tags=["admin"])  # pour les routes d'administration

@router.get("/users", response_model=List[dict])  # Obtenir la liste des utilisateurs
async def get_users(db: db_dependency, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Récupère la liste de tous les utilisateurs de l'application.

    Args:
        db (Session): Session de base de données SQLAlchemy.
        current_user (User): Utilisateur actuellement authentifié.

    Returns:
        list: Liste des utilisateurs sous forme de dictionnaires.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les droits d'administration.

    Note:
        - Nécessite des droits d'administration
        - Retourne tous les champs de la table users
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit : droits d'administration requis.")

    users = db.query(User).all()
    return users

@router.post("/users")  # Créer un utilisateur
async def create_user(create_user_request: CreateUserRequest, db: db_dependency, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Crée un nouvel utilisateur dans le système.

    Args:
        create_user_request (CreateUserRequest): Données du nouvel utilisateur.
        db (Session): Session de base de données SQLAlchemy.
        current_user (User): Utilisateur actuellement authentifié.

    Returns:
        dict: Message de confirmation avec le nom de l'utilisateur créé.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les droits d'administration.

    Note:
        - Nécessite des droits d'administration
        - Le mot de passe est automatiquement hashé avant stockage
        - CreateUserRequest doit contenir :
            - nom (str)
            - email (str)
            - password (str)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit : droits d'administration requis.")

    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà.")

    create_user_model = User(
        nom=create_user_request.nom,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role="user"  # Par défaut, les nouveaux utilisateurs ont le rôle "user"
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"message": f"Utilisateur {create_user_request.nom} créé avec succès.", "id": create_user_model.id}

@router.put("/users/{user_id}")  # Mettre à jour un utilisateur
async def update_user(
    user_id: int,
    update_user_request: UpdateUserRequest,
    db: db_dependency,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Met à jour les informations d'un utilisateur existant.

    Args:
        user_id (int): ID de l'utilisateur à mettre à jour.
        update_user_request (UpdateUserRequest): Nouvelles données de l'utilisateur.
        db (Session): Session de base de données SQLAlchemy.
        current_user (User): Utilisateur actuellement authentifié.

    Returns:
        dict: Message de confirmation.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les droits d'administration ou si l'utilisateur n'existe pas.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit : droits d'administration requis.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    # Mise à jour des champs si fournis
    if update_user_request.nom:
        user.nom = update_user_request.nom
    if update_user_request.email:
        # Vérifier si le nouvel email n'est pas déjà utilisé par un autre utilisateur
        existing_user = db.query(User).filter(User.email == update_user_request.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé par un autre utilisateur.")
        user.email = update_user_request.email
    if update_user_request.password:
        user.hashed_password = bcrypt_context.hash(update_user_request.password)
    if update_user_request.role:
        user.role = update_user_request.role

    db.commit()
    return {"message": f"Utilisateur {user_id} mis à jour avec succès."}

@router.delete("/users/{user_id}")  # Supprimer un utilisateur
async def delete_user(
    user_id: int,
    db: db_dependency,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Supprime un utilisateur du système.

    Args:
        user_id (int): ID de l'utilisateur à supprimer.
        db (Session): Session de base de données SQLAlchemy.
        current_user (User): Utilisateur actuellement authentifié.

    Returns:
        dict: Message de confirmation.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les droits d'administration ou si l'utilisateur n'existe pas.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit : droits d'administration requis.")

    # Empêcher la suppression de son propre compte
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user_id} supprimé avec succès."}

@router.get("/users/{user_id}")  # Obtenir les détails d'un utilisateur spécifique
async def get_user(
    user_id: int,
    db: db_dependency,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Récupère les détails d'un utilisateur spécifique.

    Args:
        user_id (int): ID de l'utilisateur à récupérer.
        db (Session): Session de base de données SQLAlchemy.
        current_user (User): Utilisateur actuellement authentifié.

    Returns:
        dict: Détails de l'utilisateur.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les droits d'administration ou si l'utilisateur n'existe pas.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit : droits d'administration requis.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    return user