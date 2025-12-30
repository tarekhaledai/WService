#!/bin/bash

# Script pour construire et pousser l'image Docker vers Scaleway Container Registry
# Usage: ./build-and-push.sh [tag]

set -e

# Configuration
REGISTRY="rg.fr-par.scw.cloud"
NAMESPACE="your-namespace"  # ⚠️ Remplacez par votre namespace Scaleway
IMAGE_NAME="wservice-api"
TAG="${1:-latest}"
FULL_IMAGE="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${TAG}"

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Construction et push de l'image Docker${NC}"
echo -e "${BLUE}Image: ${FULL_IMAGE}${NC}"
echo ""

# Vérifier que scw est installé
if ! command -v scw &> /dev/null; then
    echo -e "${YELLOW}⚠️  Scaleway CLI (scw) n'est pas installé${NC}"
    echo "Installez-le avec: brew install scw"
    exit 1
fi

# Vérifier que docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker n'est pas installé${NC}"
    exit 1
fi

# Se connecter à Scaleway Container Registry
echo -e "${BLUE}🔐 Connexion à Scaleway Container Registry...${NC}"
scw registry login || {
    echo -e "${YELLOW}⚠️  Échec de la connexion. Vérifiez votre configuration avec 'scw init'${NC}"
    exit 1
}

# Construire l'image
echo -e "${BLUE}🔨 Construction de l'image Docker...${NC}"
cd "$(dirname "$0")/.."
docker build -t "${FULL_IMAGE}" ./api

# Pousser l'image
echo -e "${BLUE}📤 Push de l'image vers Scaleway Container Registry...${NC}"
docker push "${FULL_IMAGE}"

echo ""
echo -e "${GREEN}✅ Image poussée avec succès: ${FULL_IMAGE}${NC}"
echo ""
echo -e "${BLUE}📝 N'oubliez pas de mettre à jour api-deployment.yaml avec cette image:${NC}"
echo -e "   image: ${FULL_IMAGE}"

