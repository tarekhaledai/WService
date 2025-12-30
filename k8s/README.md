# 🚀 Déploiement Kubernetes sur Scaleway

Ce dossier contient tous les manifests Kubernetes nécessaires pour déployer l'application WService sur **Scaleway Kubernetes Engine (Kapsule)**.

## 📋 Prérequis

1. **Compte Scaleway** avec accès à :
   - Kubernetes Engine (Kapsule)
   - Container Registry
   - Load Balancer

2. **Outils installés** :
   ```bash
   # kubectl
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
   
   # Scaleway CLI (scw)
   brew install scw
   ```

3. **Configuration Scaleway CLI** :
   ```bash
   scw init
   ```

## 🔧 Configuration

### 1. Créer le secret Kubernetes

Créez le fichier `secret.yaml` à partir de l'exemple :

```bash
cp secret.yaml.example secret.yaml
```

Éditez `secret.yaml` et remplacez les valeurs par vos secrets réels :

```yaml
stringData:
  DB_PASSWORD: "votre_mot_de_passe_securise"
```

⚠️ **Important** : Ne commitez jamais le fichier `secret.yaml` dans Git !

### 2. Configurer l'image Docker

Mettez à jour `api-deployment.yaml` avec l'URL de votre image dans Scaleway Container Registry :

```yaml
image: rg.fr-par.scw.cloud/votre-namespace/wservice-api:latest
```

## 🏗️ Construction et Push de l'Image Docker

### Option 1 : Utiliser le script fourni

```bash
./build-and-push.sh
```

### Option 2 : Commandes manuelles

```bash
# Se connecter à Scaleway Container Registry
scw registry login

# Construire l'image
docker build -t rg.fr-par.scw.cloud/votre-namespace/wservice-api:latest ./api

# Pousser l'image
docker push rg.fr-par.scw.cloud/votre-namespace/wservice-api:latest
```

## 📦 Déploiement

### Étape 1 : Se connecter au cluster Kubernetes

```bash
# Lister vos clusters
scw k8s cluster list

# Récupérer le kubeconfig
scw k8s kubeconfig install <cluster-id>
```

### Étape 2 : Appliquer les manifests dans l'ordre

```bash
# 1. Créer le namespace
kubectl apply -f namespace.yaml

# 2. Créer le ConfigMap
kubectl apply -f configmap.yaml

# 3. Créer le Secret (⚠️ après avoir édité secret.yaml)
kubectl apply -f secret.yaml

# 4. Créer le PersistentVolumeClaim pour PostgreSQL
kubectl apply -f postgres-pvc.yaml

# 5. Déployer PostgreSQL
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml

# 6. Déployer l'API
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
```

### Option : Appliquer tous les fichiers d'un coup

```bash
kubectl apply -f .
```

## 🔍 Vérification du déploiement

### Vérifier l'état des pods

```bash
kubectl get pods -n wservice
```

### Vérifier les services

```bash
kubectl get services -n wservice
```

### Voir les logs

```bash
# Logs de l'API
kubectl logs -f deployment/wservice-api -n wservice

# Logs de PostgreSQL
kubectl logs -f deployment/wservice-db -n wservice
```

### Obtenir l'URL du Load Balancer

```bash
kubectl get service wservice-api -n wservice
```

L'EXTERNAL-IP vous donnera l'URL publique de votre API.

## 🧪 Tester l'API

Une fois déployé, testez l'API :

```bash
# Récupérer l'IP externe
EXTERNAL_IP=$(kubectl get service wservice-api -n wservice -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Tester l'endpoint health
curl http://$EXTERNAL_IP/health

# Tester la connexion à la base de données
curl http://$EXTERNAL_IP/api/db/test
```

## 🔄 Mise à jour de l'application

### Mettre à jour l'image

1. Reconstruire et pousser la nouvelle image :
   ```bash
   ./build-and-push.sh
   ```

2. Redémarrer le deployment :
   ```bash
   kubectl rollout restart deployment/wservice-api -n wservice
   ```

3. Vérifier le déploiement :
   ```bash
   kubectl rollout status deployment/wservice-api -n wservice
   ```

## 🗑️ Suppression

Pour supprimer tous les ressources déployées :

```bash
kubectl delete namespace wservice
```

⚠️ **Attention** : Cela supprimera aussi le PersistentVolumeClaim et toutes les données de la base de données !

Pour conserver les données, supprimez manuellement chaque ressource sauf le PVC.

## 📊 Monitoring et Scaling

### Scale manuel

```bash
# Augmenter le nombre de réplicas de l'API
kubectl scale deployment wservice-api --replicas=3 -n wservice
```

### Autoscaling (HPA)

Pour activer l'autoscaling horizontal, créez un fichier `hpa.yaml` :

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: wservice-api-hpa
  namespace: wservice
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: wservice-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🔐 Sécurité

### Utiliser Scaleway Database pour PostgreSQL (Recommandé)

Au lieu de déployer PostgreSQL dans Kubernetes, utilisez **Scaleway Database** pour une meilleure gestion et sécurité :

1. Créer une instance PostgreSQL dans Scaleway Database
2. Mettre à jour `configmap.yaml` avec l'URL de connexion
3. Ne pas déployer `postgres-deployment.yaml` et `postgres-service.yaml`

### Secrets Management

Pour la production, considérez l'utilisation de :
- **Scaleway Secret Manager**
- **External Secrets Operator**
- **HashiCorp Vault**

## 📚 Ressources Scaleway

- [Documentation Kubernetes Engine](https://www.scaleway.com/en/docs/containers/kubernetes/)
- [Container Registry](https://www.scaleway.com/en/docs/containers/container-registry/)
- [Load Balancer](https://www.scaleway.com/en/docs/network/load-balancer/)
- [Database](https://www.scaleway.com/en/docs/databases/postgresql/)

## 🆘 Dépannage

### Les pods ne démarrent pas

```bash
# Vérifier les événements
kubectl describe pod <pod-name> -n wservice

# Vérifier les logs
kubectl logs <pod-name> -n wservice
```

### Problème de connexion à la base de données

```bash
# Vérifier que le service PostgreSQL est accessible
kubectl exec -it deployment/wservice-api -n wservice -- ping wservice-db

# Tester la connexion depuis un pod
kubectl exec -it deployment/wservice-api -n wservice -- python -c "import psycopg2; print('OK')"
```

### Image non trouvée

Vérifiez que :
1. L'image est bien poussée dans Scaleway Container Registry
2. Le cluster Kubernetes a les permissions pour accéder au registry
3. L'URL de l'image dans `api-deployment.yaml` est correcte

---

**Bon déploiement ! 🚀**

