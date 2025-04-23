# Schémas Pydantic pour les formulaires de l'API
from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import Optional, List
from datetime import date, datetime

"""
Module définissant les schémas Pydantic pour la validation des données d'entrée de l'API.

Ce module contient les modèles de validation pour les demandes de prédictions de films,
la création et mise à jour d'utilisateurs, et le changement de mot de passe.
"""

# Schémas pour les utilisateurs
class CreateUserRequest(BaseModel):
    """
    Schéma de validation pour la création d'un nouvel utilisateur.

    Attributes:
        nom (str): Nom de l'utilisateur
        email (EmailStr): Adresse email valide
        password (str): Mot de passe (minimum 8 caractères)
    """
    nom: str = Field(..., description="Nom de l'utilisateur")
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe (min. 8 caractères)")

    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Jean Dupont",
                "email": "jean.dupont@cinema.fr",
                "password": "MotDePasse123"
            }
        }


class UpdateUserRequest(BaseModel):
    """
    Schéma pour la mise à jour d'un utilisateur.

    Attributes:
        nom (Optional[str]): Nouveau nom
        email (Optional[EmailStr]): Nouvelle adresse email
        password (Optional[str]): Nouveau mot de passe
        role (Optional[str]): Nouveau rôle
    """
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = None


class NewPassword(BaseModel):
    """
    Schéma de validation pour le changement de mot de passe.

    Attributes:
        new_password (str): Nouveau mot de passe (minimum 8 caractères)
        confirm_password (str): Confirmation du nouveau mot de passe
    """
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe (min. 8 caractères)")
    confirm_password: str = Field(..., min_length=8, description="Confirmation du mot de passe")

    class Config:
        json_schema_extra = {
            "example": {
                "new_password": "NouveauMotDePasse123",
                "confirm_password": "NouveauMotDePasse123",
            }
        }


# Schémas pour les films et prédictions
class FilmBase(BaseModel):
    """
    Schéma de base pour les informations d'un film.

    Attributes:
        fr_title (str): Titre français du film
        original_title (str): Titre original du film
        released_date (date): Date de sortie du film
        casting (str): Casting du film (acteurs principaux)
        director (str): Réalisateur du film
        writer (str): Scénariste du film
        distribution (str): Distributeur du film
        country (str): Pays d'origine du film
        classification (str): Classification du film (tous publics, -12 ans, etc.)
        duration (str): Durée du film
        categories (str): Catégories/genres du film
        synopsis (str): Synopsis du film
        allocine_url (str): URL de la page Allociné du film
        image_url (str): URL de l'image/affiche du film
    """
    fr_title: str = Field(..., description="Titre français du film")
    original_title: str = Field(..., description="Titre original du film")
    released_date: date = Field(..., description="Date de sortie du film")
    casting: str = Field(..., description="Casting du film (acteurs principaux)")
    director: str = Field(..., description="Réalisateur du film")
    writer: str = Field(..., description="Scénariste du film")
    distribution: str = Field(..., description="Distributeur du film")
    country: str = Field(..., description="Pays d'origine du film")
    classification: str = Field(..., description="Classification du film (tous publics, -12 ans, etc.)")
    duration: str = Field(..., description="Durée du film")
    categories: str = Field(..., description="Catégories/genres du film")
    synopsis: str = Field(..., description="Synopsis du film")
    allocine_url: str = Field(..., description="URL de la page Allociné du film")
    image_url: str = Field(..., description="URL de l'image/affiche du film")


class FilmCreate(FilmBase):
    """
    Schéma pour la création d'un nouveau film.
    """
    pass


class FilmResponse(FilmBase):
    """
    Schéma de réponse pour un film.

    Attributes:
        id (int): ID du film
        weekly_entrances_pred (int): Prédiction du nombre d'entrées hebdomadaires
        programmed (bool): Indique si le film est programmé
        programmation_start_date (Optional[date]): Date de début de programmation
        programmation_end_date (Optional[date]): Date de fin de programmation
    """
    id: int
    weekly_entrances_pred: int
    programmed: bool = False
    programmation_start_date: Optional[date] = None
    programmation_end_date: Optional[date] = None

    class Config:
        orm_mode = True


class PredictionCreate(BaseModel):
    """
    Schéma pour la création d'une prédiction.

    Attributes:
        film_id (int): ID du film pour lequel faire une prédiction
        semaine (date): Semaine pour laquelle la prédiction est faite
    """
    film_id: int = Field(..., description="ID du film pour lequel faire une prédiction")
    semaine: date = Field(..., description="Semaine pour laquelle la prédiction est faite")

    class Config:
        json_schema_extra = {
            "example": {
                "film_id": 1,
                "semaine": "2023-04-19"
            }
        }


class PredictionResponse(BaseModel):
    """
    Schéma de réponse pour une prédiction.

    Attributes:
        id (int): ID de la prédiction
        film_id (int): ID du film
        fr_title (str): Titre français du film
        weekly_entrances_pred (int): Nombre d'entrées prédites au niveau national
        entrees_cinema (int): Nombre d'entrées prédites pour le cinéma (1/2000ème)
        recette_estimee (float): Recette estimée pour le cinéma
        date_prediction (datetime): Date à laquelle la prédiction a été faite
        released_date (date): Date de sortie du film
    """
    id: int
    film_id: int
    fr_title: str
    weekly_entrances_pred: int
    entrees_cinema: int
    recette_estimee: float
    date_prediction: datetime
    released_date: date

    @validator('entrees_cinema', always=True)
    def calculate_entrees_cinema(cls, v, values):
        """Calcule les entrées du cinéma (1/2000ème des entrées nationales)."""
        if 'weekly_entrances_pred' in values:
            return values['weekly_entrances_pred'] // 2000
        return v

    @validator('recette_estimee', always=True)
    def calculate_recette(cls, v, values):
        """Calcule la recette estimée (entrées cinéma * 10€)."""
        if 'entrees_cinema' in values:
            return values['entrees_cinema'] * 10.0
        return v

    class Config:
        orm_mode = True


class PredictionDetail(PredictionResponse):
    """
    Schéma détaillé d'une prédiction incluant des informations supplémentaires.

    Attributes:
        entrees_reelles (Optional[int]): Nombre réel d'entrées (si disponible)
        precision (Optional[float]): Précision de la prédiction en pourcentage
        original_title (str): Titre original du film
        duration (str): Durée du film
        categories (str): Catégories/genres du film
        director (str): Réalisateur du film
        casting (str): Casting du film
        synopsis (str): Synopsis du film
        country (str): Pays d'origine du film
        image_url (str): URL de l'image/affiche du film
        programmed (bool): Indique si le film est programmé
    """
    entrees_reelles: Optional[int] = None
    precision: Optional[float] = None
    original_title: str
    duration: str
    categories: str
    director: str
    casting: str
    synopsis: str
    country: str
    image_url: str
    programmed: bool

    @validator('precision', always=True)
    def calculate_precision(cls, v, values):
        """Calcule la précision si les entrées réelles sont disponibles."""
        if 'entrees_reelles' in values and values['entrees_reelles'] and 'weekly_entrances_pred' in values:
            predites = values['weekly_entrances_pred']
            reelles = values['entrees_reelles']
            if reelles > 0:
                return 100 - min(100, abs(predites - reelles) / reelles * 100)
        return v


# Schéma pour les recommandations de salles
class SalleRecommendation(BaseModel):
    """
    Schéma pour les recommandations de films par salle.

    Attributes:
        salle_id (int): ID de la salle
        capacite (int): Capacité de la salle
        film_id (int): ID du film recommandé
        fr_title (str): Titre français du film
        entrees_estimees (int): Nombre d'entrées estimées
        recette_estimee (float): Recette estimée
        taux_occupation (float): Taux d'occupation estimé de la salle
        image_url (str): URL de l'image/affiche du film
    """
    salle_id: int
    capacite: int
    film_id: int
    fr_title: str
    entrees_estimees: int
    recette_estimee: float
    taux_occupation: float
    image_url: str

    class Config:
        orm_mode = True


class ProgrammationRequest(BaseModel):
    """
    Schéma pour programmer un film dans une salle.

    Attributes:
        film_id (int): ID du film à programmer
        salle_id (int): ID de la salle
        date_debut (date): Date de début de programmation
        date_fin (date): Date de fin de programmation
    """
    film_id: int
    salle_id: int
    date_debut: date
    date_fin: date

    class Config:
        json_schema_extra = {
            "example": {
                "film_id": 1,
                "salle_id": 1,
                "date_debut": "2023-04-19",
                "date_fin": "2023-04-25"
            }
        }


class RecettesHebdomadaires(BaseModel):
    """
    Schéma pour les recettes hebdomadaires.

    Attributes:
        semaine (date): Semaine concernée
        chiffre_affaires (float): Chiffre d'affaires total
        charges (float): Charges fixes
        benefice (float): Bénéfice (CA - charges)
        taux_occupation_moyen (float): Taux d'occupation moyen des salles
        croissance_semaine (Optional[float]): Taux de croissance par rapport à la semaine précédente
        croissance_mois (Optional[float]): Taux de croissance par rapport au mois précédent
    """
    semaine: date
    chiffre_affaires: float
    charges: float = 4900.0  # Charges fixes hebdomadaires
    benefice: float
    taux_occupation_moyen: float
    croissance_semaine: Optional[float] = None
    croissance_mois: Optional[float] = None

    @validator('benefice', always=True)
    def calculate_benefice(cls, v, values):
        """Calcule le bénéfice à partir du CA et des charges."""
        if 'chiffre_affaires' in values and 'charges' in values:
            return values['chiffre_affaires'] - values['charges']
        return v

    class Config:
        orm_mode = True