# Point d'entrée de l'application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import route_admin, route_auth, route_prediction


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
app.include_router(route_auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(route_prediction.router, tags=["Prédictions"])
app.include_router(route_admin.router, prefix="/admin", tags=["Administration"])

# Route racine
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API de prédiction de popularité des films",
        "documentation": "/docs",
        "routes": {
            "prédictions": "/predictions",
            "administration": "/admin",
            "authentification": "/auth"
        }
    }