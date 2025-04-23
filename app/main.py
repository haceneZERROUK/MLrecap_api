# Point d'entrée de l'application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import route_admin, route_auth, route_prediction

"""
Point d'entrée principal de l'API de prédiction de popularité des films.

Ce module initialise l'application FastAPI et configure les routes
pour l'authentification, l'administration et la gestion des prédictions de films.

Application Properties:
    title: "API de Prédiction de Films"
    description: "API pour prédire la popularité des films pour le cinéma 'New is always better'"
    version: "0.1"

Routes incluses:
    - /api/v1/predictions: Gestion des prédictions de films
    - /api/v1/admin: Administration des utilisateurs
    - /api/v1/auth: Authentification et gestion des tokens

Note:
    L'API utilise FastAPI pour:
    - Documentation automatique (Swagger UI sur /docs)
    - Validation des données avec Pydantic
    - Gestion des routes avec APIRouter
    - Support asynchrone natif
"""

# Créer l'application FastAPI
app = FastAPI(
    title="API de Prédiction de Films",
    description="API pour prédire la popularité des films pour le cinéma 'New is always better'",
    version="0.1"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(route_prediction.router, prefix="/api/v1/predictions", tags=["Prédictions"])
app.include_router(route_admin.router, prefix="/api/v1/admin", tags=["Administration"])
app.include_router(route_auth.router, prefix="/api/v1/auth", tags=["Authentification"])

# Route racine
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API de prédiction de popularité des films",
        "documentation": "/docs",
        "routes": {
            "prédictions": "/api/v1/predictions",
            "administration": "/api/v1/admin",
            "authentification": "/api/v1/auth"
        }
    }