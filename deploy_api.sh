#!/bin/bash
set -e  # Arrête le script si une commande échoue

# Variables
RESOURCE_GROUP="hzerroukRG"            # Nom du groupe de ressources
CONTAINER_NAME="fastapi-app-g2"                 # Nom du conteneur
ACR_NAME="hzerroukregistry"            # Nom de ton Azure Container Registry
REGION="francecentral"           # Région où tu souhaites déployer
IMAGE_NAME="fastapi-app"                   # Nom de l'image Docker
DNS_LABEL="apiniab"                 # Label DNS pour accéder au conteneur

. ./.env

echo $REGISTRY_USERNAME
echo $REGISTRY_PASSWORD


# 1. Authentification Azure (connectez-vous à votre compte Azure)
echo "Authentification Azure..."


# 4. Connexion à Azure Container Registry
echo "Connexion à Azure Container Registry..."
az acr login --name $ACR_NAME
az acr update -n $ACR_NAME --admin-enabled true
REGISTRY_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

#4.5 Suppression du container existant
echo "Deleting existing container (if any)..."
az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes

# 5. Construction de l'image Docker avec le Dockerfile
echo "Construction de l'image Docker..."
docker build -t $IMAGE_NAME .

# 6. Taguer l'image Docker pour Azure Container Registry
echo "Taguer l'image Docker pour Azure Container Registry..."
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

echo "Pousser l'image vers Azure Container Registry..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

# 8. Déploiement du conteneur sur Azure Container Instances
echo "Déploiement du conteneur sur Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $ACR_NAME.azurecr.io/$IMAGE_NAME:latest \
    --dns-name-label $DNS_LABEL\
    --cpu 1 \
    --memory 3.5 \
    --ip-address public \
    --ports 8086 \
    --environment-variables SECRET_KEY=$SECRET_KEY DATABASE_URL=$DATABASE_URL ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES ALGORITHM=$ALGORITHM MODEL_PATH=$MODEL_PATH \
    --registry-login-server $ACR_NAME.azurecr.io \
    --registry-username $REGISTRY_USERNAME \
    --registry-password $REGISTRY_PASSWORD \
    --os-type Linux


# 9. Afficher l'URL du conteneur
CONTAINER_IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" -o tsv)
echo "Le conteneur est déployé. Vous pouvez y accéder à l'adresse suivante : http://$CONTAINER_IP:8086"