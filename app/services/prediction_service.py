import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import pickle
import os
from dotenv import load_dotenv
from app.modeles import Film, Prediction
from typing import List, Optional
from datetime import datetime

class PredictionService:
    """
    Service pour effectuer des prédictions sur la popularité des films.
    """

    def __init__(self):
        """
        Initialise le service de prédiction en chargeant le modèle.
        """
        load_dotenv()
        self.model_path = os.getenv("MODEL_PATH", "app/catboostmodel.pkl")

        try:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            print(f"Erreur: Le fichier modèle {self.model_path} n'a pas été trouvé.")
            self.model = None
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {str(e)}")
            self.model = None

    def prepare_data(self, film_data: dict) -> pd.DataFrame:
        """
        Prépare les données d'un film pour la prédiction.

        Args:
            film_data (dict): Données du film à prédire

        Returns:
            pd.DataFrame: DataFrame prêt pour la prédiction
        """
        # Créer un DataFrame avec les données du film
        df_prediction = pd.DataFrame([film_data])

        # Convertir la date de sortie en datetime
        df_prediction['released_date'] = pd.to_datetime(
            df_prediction['released_date'],
            format="%d/%m/%Y",
            errors='coerce'
        )

        # Ajouter les colonnes dérivées
        df_prediction["summer"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 6 and x.day >= 21) or x.month in [7, 8] or (x.month == 9 and x.day < 22)) else 0
        )
        df_prediction["automn"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 9 and x.day >= 22) or x.month in [10, 11] or (x.month == 12 and x.day < 21)) else 0
        )
        df_prediction["winter"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 12 and x.day >= 21) or x.month in [1, 2] or (x.month == 3 and x.day < 20)) else 0
        )
        df_prediction["spring"] = df_prediction["released_date"].apply(
            lambda x: 1 if ((x.month == 3 and x.day >= 21) or x.month in [4, 5] or (x.month == 6 and x.day < 21)) else 0
        )

        # Autres colonnes dérivées
        df_prediction["is_covid"] = df_prediction["released_date"].apply(
            lambda x: 1 if (
                (x >= pd.to_datetime("2020-03-17") and x <= pd.to_datetime("2020-05-11")) or
                (x >= pd.to_datetime("2020-10-30") and x <= pd.to_datetime("2020-12-15")) or
                (x >= pd.to_datetime("2021-04-03") and x <= pd.to_datetime("2021-05-03"))
            ) else 0
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

        # Colonnes pour les acteurs, réalisateurs, etc.
        # Note: Ces colonnes devraient être remplies avec des données réelles
        # Pour l'exemple, nous les initialisons à 0
        top_columns = [
            "top_actor_1", "top_actor_2", "top_actor_3", "top_director",
            "top_writer", "top_distribution", "top_actor_1_mid", "top_actor_2_mid",
            "top_actor_3_mid", "top_director_mid", "top_writer_mid", "top_distribution_mid",
            "top_pays"
        ]
        for col in top_columns:
            df_prediction[col] = 0

        # Sélection des features pour la prédiction
        features_of_interest = [
            'released_year', "country", 'category', 'classification',
            'duration_minutes', "top_actor_1", "top_actor_2", "top_actor_3",
            "top_director", 'top_writer', 'top_distribution', "top_actor_1_mid",
            "top_actor_2_mid", "top_actor_3_mid", "top_director_mid",
            'top_writer_mid', 'top_distribution_mid', 'top_pays',
            'post_streaming', 'summer_holidays', 'christmas_period', 'is_award_season',
        ]

        return df_prediction[features_of_interest]

    def predict(self, film_data: dict) -> dict:
        """
        Effectue une prédiction pour un film.

        Args:
            film_data (dict): Données du film à prédire

        Returns:
            dict: Résultat de la prédiction
        """
        if self.model is None:
            return {"error": "Le modèle n'a pas été chargé correctement."}

        try:
            # Préparer les données
            data = self.prepare_data(film_data)

            # Faire la prédiction
            prediction = np.round(self.model.predict(data), 0)[0]

            # Calculer les métriques dérivées
            daily_audience = prediction / 7  # Audience quotidienne moyenne
            cinema_entries = prediction * 0.05  # 5% des entrées totales pour notre cinéma
            confidence_score = 0.85  # Score de confiance fixe pour l'exemple
            recommended_room = 1 if cinema_entries > 100 else 2  # Salle 1 pour les films populaires
            estimated_revenue = cinema_entries * 9.5  # Prix moyen du billet à 9.5€

            return {
                "predicted_entries": int(prediction),
                "predicted_entries_cinema": int(cinema_entries),
                "predicted_daily_audience": float(daily_audience),
                "confidence_score": float(confidence_score),
                "recommended_room": int(recommended_room),
                "estimated_revenue": float(estimated_revenue),
                "prediction_date": datetime.now().strftime("%Y-%m-%d")
            }
        except Exception as e:
            return {"error": f"Erreur lors de la prédiction: {str(e)}"}

    def get_top_films(self, limit: int = 10) -> List[dict]:
        """
        Retourne les films avec les meilleures prédictions.

        Args:
            limit (int): Nombre de films à retourner

        Returns:
            List[dict]: Liste des meilleurs films
        """
        # Cette méthode devrait normalement interroger la base de données
        # Pour l'exemple, nous retournons une liste vide
        return []