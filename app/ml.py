# Modèle prédiction
import pickle
import pandas as pd
import numpy as np
from typing import Union, Dict, Any, List
from datetime import datetime
from pathlib import Path

def charger_modele(fichier_pkl: str = "catboostmodel.pkl") -> Any:
    """
    Charge le modèle CatBoost depuis un fichier pickle.

    Args:
        fichier_pkl (str): Chemin vers le fichier pickle du modèle

    Returns:
        CatBoostRegressor: Modèle CatBoost chargé

    Raises:
        FileNotFoundError: Si le fichier du modèle n'existe pas
        pickle.UnpicklingError: Si le fichier est corrompu
    """
    model_path = Path(fichier_pkl)
    if not model_path.exists():
        raise FileNotFoundError(f"Le fichier modèle {fichier_pkl} n'existe pas")
    
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def preparer_donnees(film_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Prépare les données d'un film pour la prédiction.
    
    Args:
        film_data (Dict): Dictionnaire contenant les informations du film
        
    Returns:
        pd.DataFrame: DataFrame prêt pour la prédiction
    """
    # Créer un DataFrame avec une seule ligne
    df_prediction = pd.DataFrame([film_data])
    
    # Convertir la date de sortie en datetime
    if 'released_date' in df_prediction:
        df_prediction['released_date'] = pd.to_datetime(
            df_prediction['released_date'],
            errors='coerce'
        )
        # Extraire l'année
        df_prediction['released_year'] = df_prediction['released_date'].dt.year
    
    # Créer les features de saison
    if 'released_date' in df_prediction:
        df_prediction["summer"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 6 and x.day >= 21) or x.month in [7, 8] or 
                           (x.month == 9 and x.day < 22)) else 0
        )
        df_prediction["automn"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 9 and x.day >= 22) or x.month in [10, 11] or 
                           (x.month == 12 and x.day < 21)) else 0
        )
        df_prediction["winter"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 12 and x.day >= 21) or x.month in [1, 2] or 
                           (x.month == 3 and x.day < 20)) else 0
        )
        df_prediction["spring"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 3 and x.day >= 21) or x.month in [4, 5] or 
                           (x.month == 6 and x.day < 21)) else 0
        )
        
        # Autres features temporelles
        df_prediction["is_covid"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x >= pd.to_datetime("2020-03-17") and x <= pd.to_datetime("2020-05-11")) or
                           (x >= pd.to_datetime("2020-10-30") and x <= pd.to_datetime("2020-12-15")) or
                           (x >= pd.to_datetime("2021-04-03") and x <= pd.to_datetime("2021-05-03"))) else 0
        )
        df_prediction["post_streaming"] = df_prediction["released_date"].apply(
            lambda x: 1 if x >= pd.to_datetime("2014-09-15") else 0
        )
        df_prediction["summer_holidays"] = df_prediction["released_date"].apply(
            lambda x: 1 if x.month >= 7 or (x.month <= 9 and x.day < 10) else 0
        )
        df_prediction["christmas_period"] = df_prediction["released_date"].apply(
            lambda x: 1 if (x.month == 12 and x.day >= 20) or (x.month == 1 and x.day <= 5) else 0
        )
        df_prediction["is_award_season"] = df_prediction["released_date"].apply(
            lambda x: 1 if (x.month == 2 or (x.month == 3 and x.day <= 10)) else 0
        )
    
    # Créer les features pour les acteurs, réalisateurs, etc.
    # Note: Cette partie nécessite d'avoir accès aux données d'entraînement
    # ou aux listes pré-calculées des "top" acteurs, réalisateurs, etc.
    # Pour simplifier, on peut initialiser ces colonnes à 0
    top_features = [
        "top_actor_1", "top_actor_2", "top_actor_3", "top_director",
        "top_writer", "top_distribution", "top_actor_1_mid", "top_actor_2_mid",
        "top_actor_3_mid", "top_director_mid", "top_writer_mid", "top_distribution_mid"
    ]
    
    for feature in top_features:
        df_prediction[feature] = 0
    
    # Pays populaires
    df_prediction['top_pays'] = df_prediction.country.apply(
        lambda x: 1 if x in (['France', 'Etats-Unis', 'Grande-Bretagne']) else 0
    )
    
    # Sélectionner les features nécessaires pour la prédiction
    features_of_interest = [
        'released_year', 'country', 'category', 'classification', 'duration_minutes',
        "top_actor_1", "top_actor_2", "top_actor_3", "top_director", 'top_writer',
        'top_distribution', "top_actor_1_mid", "top_actor_2_mid", "top_actor_3_mid",
        "top_director_mid", 'top_writer_mid', 'top_distribution_mid', 'top_pays',
        'post_streaming', 'summer_holidays', 'christmas_period', 'is_award_season'
    ]
    
    # S'assurer que toutes les colonnes nécessaires sont présentes
    for feature in features_of_interest:
        if feature not in df_prediction.columns:
            df_prediction[feature] = 0  # Valeur par défaut
    
    return df_prediction[features_of_interest]

def predire_entrees(model: Any, film_data: Dict[str, Any]) -> int:
    """
    Prédit le nombre d'entrées hebdomadaires pour un film.

    Args:
        model: Modèle CatBoost chargé
        film_data (Dict): Dictionnaire contenant les informations du film

    Returns:
        int: Nombre d'entrées prédites

    Note:
        Les données doivent contenir toutes les features utilisées lors de l'entraînement
    """
    # Préparer les données
    donnees_preparees = preparer_donnees(film_data)
    
    # Faire la prédiction
    prediction = model.predict(donnees_preparees)
    
    # Arrondir et convertir en entier
    return int(np.round(prediction[0], 0))

# Exemple d'utilisation
if __name__ == "__main__":
    try:
        # Charger le modèle
        model = charger_modele("catboostmodel.pkl")
        
        # Exemple de données de film
        film_test = {
            "fr_title": "Test Film",
            "original_title": "Test Film Original",
            "released_date": "2023-05-15",
            "actor_1": "Actor One",
            "actor_2": "Actor Two",
            "actor_3": "Actor Three",
            "directors": "Director Name",
            "writer": "Writer Name",
            "distribution": "Distribution Company",
            "country": "France",
            "classification": "Tous publics",
            "duration_minutes": 120,
            "category": "Action"
        }
        
        # Faire une prédiction
        entrees_predites = predire_entrees(model, film_test)
        print(f"Prédiction d'entrées hebdomadaires: {entrees_predites}")
        
        # Calculer les entrées pour le cinéma (1/2000ème)
        entrees_cinema = entrees_predites // 2000
        print(f"Entrées estimées pour le cinéma: {entrees_cinema}")
        
        # Calculer la recette estimée (10€ par entrée)
        recette_estimee = entrees_cinema * 10
        print(f"Recette estimée: {recette_estimee}€")
        
    except Exception as e:
        print(f"Erreur lors de la prédiction: {e}")