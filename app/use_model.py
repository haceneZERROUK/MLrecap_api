import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, cv, Pool
import pickle
import sklearn
import json
import os
from dotenv import load_dotenv
import pyodbc

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
driver = os.getenv('DB_DRIVER')

conn_str = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'PORT=1433;'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

try:
    # Connexion à la base de données
    conn = pyodbc.connect(conn_str)
    print("Connexion réussie à la base SQL Azure")

    # Lire la table 'movies' directement dans un DataFrame pandas
    query = "SELECT * FROM movies"
    df = pd.read_sql_query(query, conn)


except Exception as e:
    print("Erreur de connexion :", e)

# Charger les données JSON dans un DataFrame
df_prediction = pd.read_json('app/new_film.json')
df_2 = df_prediction.copy()  # Si tu as besoin d'une copie distincte
# Groupement des acteurs 1, 2, 3 , scénaristes, réalisateurs, et distributeurs qui font plus de 500k entrées
# + ajout d'un groupe "mid" entre 250k et 500k

def use_model():
   
# Acteur 1
    df_actor_1 = df.groupby('actor_1')['weekly_entrances'].mean().reset_index()
    df_actor_1_mid = df_actor_1[(df_actor_1['weekly_entrances'] < 500001) & (df_actor_1['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_1 = df_actor_1[df_actor_1['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Acteur 2
    df_actor_2 = df.groupby('actor_2')['weekly_entrances'].mean().reset_index()
    df_actor_2_mid = df_actor_2[(df_actor_2['weekly_entrances'] < 500001) & (df_actor_2['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_2 = df_actor_2[df_actor_2['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Acteur 3
    df_actor_3 = df.groupby('actor_3')['weekly_entrances'].mean().reset_index()
    df_actor_3_mid = df_actor_3[(df_actor_3['weekly_entrances'] < 500001) & (df_actor_3['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_3 = df_actor_3[df_actor_3['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Réalisateurs
    df_director = df.groupby('directors')['weekly_entrances'].mean().reset_index()
    df_director_mid = df_director[(df_director['weekly_entrances'] < 500001) & (df_director['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_director = df_director[df_director['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Scénaristes
    df_writer = df.groupby('writer')['weekly_entrances'].mean().reset_index()
    df_writer_mid = df_writer[(df_writer['weekly_entrances'] < 500001) & (df_writer['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_writer = df_writer[df_writer['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Distributeurs
    df_distribution = df.groupby('distribution')['weekly_entrances'].mean().reset_index()
    df_distribution_mid = df_distribution[(df_distribution['weekly_entrances'] < 500001) & (df_distribution['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_distribution = df_distribution[df_distribution['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)


    # Création des colonnes "top" et "top_mid" pour les différents groupes

    df_prediction['top_actor_1'] = df_prediction['actor_1'].apply(lambda x: 1 if x in df_actor_1['actor_1'].to_list() else 0)
    df_prediction['top_actor_1_mid'] = df_prediction['actor_1'].apply(lambda x: 1 if x in df_actor_1_mid['actor_1'].to_list() else 0)

    df_prediction['top_actor_2'] = df_prediction['actor_2'].apply(lambda x: 1 if x in df_actor_2['actor_2'].to_list() else 0)
    df_prediction['top_actor_2_mid'] = df_prediction['actor_2'].apply(lambda x: 1 if x in df_actor_2_mid['actor_2'].to_list() else 0)

    df_prediction['top_actor_3'] = df_prediction['actor_3'].apply(lambda x: 1 if x in df_actor_3['actor_3'].to_list() else 0)
    df_prediction['top_actor_3_mid'] = df_prediction['actor_3'].apply(lambda x: 1 if x in df_actor_3_mid['actor_3'].to_list() else 0)

    df_prediction['top_director'] = df_prediction['directors'].apply(lambda x: 1 if x in df_director['directors'].to_list() else 0)
    df_prediction['top_director_mid'] = df_prediction['directors'].apply(lambda x: 1 if x in df_director_mid['directors'].to_list() else 0)

    df_prediction['top_writer'] = df_prediction['writer'].apply(lambda x: 1 if x in df_writer['writer'].to_list() else 0)
    df_prediction['top_writer_mid'] = df_prediction['writer'].apply(lambda x: 1 if x in df_writer_mid['writer'].to_list() else 0)

    df_prediction['top_distribution'] = df_prediction['distribution'].apply(lambda x: 1 if x in df_distribution['distribution'].to_list() else 0)
    df_prediction['top_distribution_mid'] = df_prediction['distribution'].apply(lambda x: 1 if x in df_distribution_mid['distribution'].to_list() else 0)



    df_prediction['top_pays'] = df_prediction.country.apply(lambda x : 1 if x in (['France','Etats-Unis','Grande-Bretagne']) else 0)

    df_prediction['released_date'] = pd.to_datetime(
        df_prediction['released_date'],
        format="%d/%m/%Y",
        errors='coerce'  # Optionnel : mettra NaT si une date est mal formée
    )

    df_prediction["summer"] = df_prediction["released_date"].apply(lambda x: 1 if ((x.month == 6 and x.day >= 21) or x.month in [7, 8] or (x.month == 9 and x.day < 22)) else 0)
    df_prediction["automn"] = df_prediction["released_date"].apply(lambda x: 1 if ((x.month == 9 and x.day >= 22) or x.month in [10, 11] or (x.month == 12 and x.day < 21)) else 0)
    df_prediction["winter"] = df_prediction["released_date"].apply(lambda x: 1 if ((x.month == 12 and x.day >= 21) or x.month in [1, 2] or (x.month == 3 and x.day < 20)) else 0)
    df_prediction["spring"] = df_prediction["released_date"].apply(lambda x: 1 if ((x.month == 3 and x.day >= 21) or x.month in [4, 5] or (x.month == 6 and x.day < 21)) else 0)

    df_prediction["is_covid"] = df_prediction["released_date"].apply(lambda x: 1 if (
        (x >= pd.to_datetime("2020-03-17") and x <= pd.to_datetime("2020-05-11")) or
        (x >= pd.to_datetime("2020-10-30") and x <= pd.to_datetime("2020-12-15")) or
        (x >= pd.to_datetime("2021-04-03") and x <= pd.to_datetime("2021-05-03"))
    ) else 0)

    df_prediction["post_streaming"] = df_prediction["released_date"].apply(lambda x: 1 if x >= pd.to_datetime("2014-09-15") else 0)

    df_prediction["summer_holidays"] = df_prediction["released_date"].apply(lambda x: 1 if x.month >= 7 or (x.month <= 9 and x.day < 10) else 0)

    df_prediction["christmas_period"] = df_prediction["released_date"].apply(lambda x: 1 if (x.month == 12 and x.day >= 20) or (x.month == 1 and x.day <= 5) else 0)

    df_prediction["is_award_season"] = df_prediction["released_date"].apply(lambda x: 1 if (x.month == 2 or (x.month == 3 and x.day <= 10)) else 0)


    #Selection des features du df_prediciton pour la prediction

    features_of_interest = [
        'released_year',
        "country",
        'category',
        'classification',
        'duration_minutes',
        "top_actor_1",
        "top_actor_2",
        "top_actor_3",
        "top_director",
        'top_writer',
        'top_distribution',
        "top_actor_1_mid",
        "top_actor_2_mid",
        "top_actor_3_mid",
        "top_director_mid",
        'top_writer_mid',
        'top_distribution_mid',
        'top_pays',
        'post_streaming',
        'summer_holidays',
        'christmas_period',
        'is_award_season',

    ]


    numerical_column = [

        'released_year',
        "duration_minutes",

    ]


    ordinal_column = [
        "top_actor_1",
        "top_actor_2",
        "top_actor_3",
        "top_director",
        'top_writer',
        "top_actor_1_mid",
        "top_actor_2_mid",
        "top_actor_3_mid",
        "top_director_mid",
        'top_writer_mid',
        'top_distribution_mid',
        'top_distribution',
        'top_pays',
        'post_streaming',
        'summer_holidays',
        'christmas_period',
        'is_award_season',
    ]

    categorical_column = [
        "country",
        'category',
        'classification',

    ]


    data, numerical_data,categorical_data = (
        df_prediction[features_of_interest],
        df_prediction[numerical_column],
        df_prediction[categorical_column]
    )

    with open("app/catboostmodel.pkl", "rb") as f:
        modele = pickle.load(f)


    result = np.round(modele.predict(data),0)


    df_2['prediction'] = result

    # df_prediction.sort_values(by = 'prediction', ascending=False).head(10).to_json('top_movies.json')
    # movies_list = df_2.sort_values(by = 'prediction', ascending=False).head(10).to_dict()
    movies_list = df_2.sort_values(by='prediction', ascending=False).head(10).to_dict(orient='records')

    # return movies_list
    return {"movies": movies_list}
  