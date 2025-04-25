# GET /predictions : Pour récupérer les prédictions de films à projeter.
# POST /predictions : Pour soumettre un film et obtenir une prédiction de fréquentation.
# GET /predictions/{film_id} : Pour récupérer les détails d'une prédiction spécifique.
# GET /predictions/top : Pour obtenir les films avec les meilleures prédictions pour la semaine.

from fastapi import APIRouter, Depends
from typing import Annotated
from ..use_model import use_model
from app.utils import get_current_user

router = APIRouter()


@router.post("/predictions")
def get_predictions(data: list[dict],current_user: Annotated[str, Depends(get_current_user)]):
    return use_model(data)

