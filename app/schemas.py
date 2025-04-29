# Schémas Pydantic pour les formulaires de l'API
from pydantic import BaseModel, Field, EmailStr
from typing import Union


class CreateUserRequest(BaseModel):

    username: str = Field(..., description="Nom de l'utilisateur")
    email: EmailStr
    password: str = Field(..., min_length=8, description="longueur minimale de 8 caractères")
    is_admin: bool = Field(default=False, description="False par défaut")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "nom du cinema",
                "email": "mon_email@domaine.com",
                "password": "azerty12",
            }
        }        
        