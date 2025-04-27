import psycopg2
import os

# Charge la chaîne de connexion depuis l'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # Essayer de se connecter à la base de données
    connection = psycopg2.connect(DATABASE_URL)
    print("Connexion réussie!")
except Exception as e:
    # Si une erreur se produit, afficher l'erreur
    print(f"Erreur de connexion: {e}")
    connection = None  # Définir connection comme None en cas d'échec

# Vérifier si la connexion a réussi
if connection:
    print("La connexion a réussi et la variable 'connection' est définie.")
    connection.close()  # Fermer la connexion si elle est ouverte
else:
    print("La connexion a échoué, la variable 'connection' n'est pas définie.")
