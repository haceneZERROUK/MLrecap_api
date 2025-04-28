#!/bin/bash

# Récupération des variables d'environnement
source .env


# Variables
RESOURCE_GROUP=$RESOURCE_GROUP             # Nom du groupe de ressources
CONTAINER_NAME="fastapi-app-g2"            # Nom du conteneur
ACR_NAME=$ACR_NAME                         # Nom de ton Azure Container Registry
ACR_IMAGE="fastapi-app:latest"             # Nom de l'image dans le ACR
ACR_URL="$ACR_NAME.azurecr.io"             # URL du registre
CPU="1"                                    # Nombre de CPUs
MEMORY="2"                                 # Mémoire (RAM)
IP_ADDRESS="Public"                        # Type d'IP (Public ou Private)
DNS_LABEL="apiniab-test"                   # Label DNS pour l'adresse publique
OS_TYPE="Linux"                            # Type d'OS (Linux ou Windows)

# Récupération dynamique des identifiants du ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Suppression du conteneur existant
az container delete --name $CONTAINER_NAME --resource-group $RESOURCE_GROUP -y


# Déploiement du conteneur
az container create \
  --name $CONTAINER_NAME \
  --resource-group $RESOURCE_GROUP \
  --location "France Central" \
  --image $ACR_URL/$ACR_IMAGE \
  --cpu $CPU \
  --memory $MEMORY \
  --registry-login-server $ACR_URL \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --ports 8086 5432 \
  --ip-address $IP_ADDRESS \
  --os-type $OS_TYPE \
  --dns-name-label $DNS_LABEL \
  --environment-variables SECRET_KEY=$SECRET_KEY ALGORITHM=$ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES DATABASE_NAME=$DATABASE_NAME DATABASE_USERNAME=$DATABASE_USERNAME DATABASE_PASSWORD=$DATABASE_PASSWORD HOST_NAME=$HOST_NAME PORT=$PORT DATABASE_URL="$DATABASE_URL"


# Affichage des informations
echo "Le déploiement a réussi."

