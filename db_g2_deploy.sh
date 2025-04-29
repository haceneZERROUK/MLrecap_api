#!/bin/bash

# Variables
RESOURCE_GROUP="mboumedineRG"
SERVER_NAME="groupe2server"

# Récupération des variables d'environnement
source .env

# Variables pour l'administrateur et la nouvelle base de données
ADMIN_USER=$MYSQL_USER
ADMIN_PASSWORD=$MYSQL_PASSWORD
DJANGO_PORT=$PORT

az mysql flexible-server db delete \
  --resource-group $RESOURCE_GROUP \
  --server-name $SERVER_NAME \
  --database-name $DATABASE_NAME \
  --yes


echo "Création de la base de données $DATABASE_NAME sur le serveur $SERVER_NAME..."
az mysql flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $SERVER_NAME \
  --database-name $DATABASE_NAME


# Création d'un fichier SQL temporaire pour les commandes
cat > create_api_user.sql << EOF
-- Création de l'utilisateur avec mot de passe
CREATE USER IF NOT EXISTS '$DATABASE_USERNAME'@'%' IDENTIFIED BY '$DATABASE_PASSWORD';

-- Attribution des privilèges sur la base de données
GRANT ALL PRIVILEGES ON \`$DATABASE_NAME\`.* TO '$DATABASE_USERNAME'@'%';

-- Appliquer les changements
FLUSH PRIVILEGES;
EOF

# Exécution des commandes SQL avec l'utilisateur admin Azure
mysql -h $HOST_NAME -u $MYSQL_USER -p$MYSQL_PASSWORD < create_api_user.sql

# Nettoyage
rm create_api_user.sql

echo "Base de données API et utilisateur créés avec succès !"


# GRANT ALL PRIVILEGES ON \`$DATABASE_NAME\`.* TO '$DATABASE_USERNAME'@'$DATABASE_HOST';