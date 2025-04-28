#!/bin/bash

# Récupération des variables d'environnement
source .env

# Variables
RESOURCE_GROUP=$RESOURCE_GROUP
SERVER_NAME=$DB_SERVER_NAME


# Variables pour l'administrateur et la nouvelle base de données
ADMIN_USER=$POSTGRES_USER
ADMIN_PASSWORD=$POSTGRES_PASSWORD
API_DB_NAME=$DATABASE_NAME
API_USER=$DATABASE_USERNAME
API_PASSWORD=$DATABASE_PASSWORD

# Créer la nouvelle base de données
echo "Création de la base de données $API_DB_NAME sur le serveur $SERVER_NAME..."
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $SERVER_NAME \
  --database-name $API_DB_NAME

# Création d'un fichier SQL temporaire pour les commandes
cat > create_api_user.sql << EOF
-- Création de l'utilisateur avec mot de passe
CREATE USER "$API_USER" WITH PASSWORD '$API_PASSWORD';

-- Attribution des privilèges sur la base de données
GRANT ALL PRIVILEGES ON DATABASE "$API_DB_NAME" TO "$API_USER";

-- Se connecter à la nouvelle base de données
\c $API_DB_NAME

-- Accorder les privilèges au niveau du schéma
GRANT ALL PRIVILEGES ON SCHEMA public TO "$API_USER";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "$API_USER";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO "$API_USER";

-- Accorder les privilèges sur les séquences existantes
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO "$API_USER";

-- Pour les futures séquences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO "$API_USER";

-- Supprimer la table users si elle existe déjà
DROP TABLE IF EXISTS users;

-- Créer la table users selon le modèle SQLModel
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);
EOF

# Exécution des commandes SQL avec l'utilisateur admin
PGPASSWORD=$ADMIN_PASSWORD psql \
  -h $HOST_NAME \
  -U $ADMIN_USER \
  -d postgres \
  -f create_api_user.sql

# Nettoyage
rm create_api_user.sql

echo "Base de données API et utilisateur créés avec succès !"
echo "URL de connexion pour l'API : postgresql://$API_USER:$API_PASSWORD@$HOST_NAME:$PORT/$API_DB_NAME"
