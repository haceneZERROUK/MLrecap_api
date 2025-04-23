# GET /predictions : Pour récupérer les prédictions de films à projeter.
# POST /predictions : Pour soumettre un film et obtenir une prédiction de fréquentation.
# GET /predictions/{film_id} : Pour récupérer les détails d'une prédiction spécifique.
# GET /predictions/top : Pour obtenir les films avec les meilleures prédictions pour la semaine.

from fastapi import APIRouter, HTTPException
from app.schemas import PredictionCreate, PredictionResponse
from app.services.prediction_service import PredictionService
from ..use_model import use_model

router = APIRouter()
prediction_service = PredictionService()



# @router.get("/predictions", response_model=list[PredictionResponse])
# async def get_predictions():
#     return await prediction_service.get_top_films()

# @router.post("/predictions", response_model=PredictionResponse)
# async def create_prediction(prediction: PredictionCreate):
#     return await prediction_service.create_prediction(prediction)


@router.get("/predictions")
def get_predictions():
    return use_model()

# @router.get("/predictions/{film_id}", response_model=PredictionResponse)
# async def get_prediction(film_id: int):
#     prediction = await prediction_service.get_prediction_by_film_id(film_id)
#     if prediction is None:
#         raise HTTPException(status_code=404, detail="Prediction not found")
#     return prediction

# @router.get("/predictions/top", response_model=list[PredictionResponse])
# async def get_top_predictions():
#     return await prediction_service.get_top_predictions()