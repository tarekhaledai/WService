# 🐳 Orchestration de Dev avec Docker Compose

Ce projet est un exercice guidé pour apprendre Docker Compose avec une application complète (API + Base de données persistante).

## 📚 Concepts Clés

### 1. **Services**
Un service est un conteneur Docker défini dans `docker-compose.yml`. Dans ce projet :
- **`api`** : Service de l'application Python/Flask
- **`db`** : Service de la base de données PostgreSQL

Chaque service peut avoir sa propre configuration (ports, volumes, variables d'environnement, etc.).

### 2. **Réseaux Virtuels**
Les réseaux permettent aux conteneurs de communiquer entre eux. Ici :
- **`wservice-network`** : Réseau bridge qui connecte l'API et la base de données
- Les services peuvent se référencer par leur nom (ex: `db` pour accéder à la base de données)

### 3. **Volumes**
Les volumes permettent de persister les données et de partager des fichiers :
- **`db-data`** : Volume persistant pour les données PostgreSQL (survit au redémarrage)
- **`./api:/app`** : Volume de montage pour le développement (hot-reload)

### 4. **Secrets (.env)**
Le fichier `.env` contient les variables d'environnement sensibles :
- Mots de passe de la base de données
- Ports de configuration
- Variables d'environnement

⚠️ **Important** : Le fichier `.env` ne doit jamais être commité dans Git (déjà dans `.gitignore`).

## 🚀 Commandes Essentielles

### Démarrer les services
```bash
docker-compose up
```
Démarre tous les services en mode attaché (logs visibles dans le terminal).

```bash
docker-compose up -d
```
Démarre tous les services en mode détaché (en arrière-plan).

### Arrêter les services
```bash
docker-compose down
```
Arrête et supprime les conteneurs, mais **conserve les volumes** (données persistantes).

```bash
docker-compose down -v
```
Arrête les conteneurs et **supprime aussi les volumes** (⚠️ supprime les données).

### Voir les logs
```bash
docker-compose logs
```
Affiche tous les logs de tous les services.

```bash
docker-compose logs -f
```
Affiche les logs en temps réel (follow mode).

```bash
docker-compose logs api
```
Affiche uniquement les logs du service `api`.

```bash
docker-compose logs db
```
Affiche uniquement les logs du service `db`.

### Autres commandes utiles
```bash
# Voir l'état des services
docker-compose ps

# Reconstruire les images
docker-compose build

# Reconstruire et redémarrer
docker-compose up --build

# Exécuter une commande dans un conteneur
docker-compose exec api sh
docker-compose exec db psql -U postgres -d wservice_db

# Redémarrer un service spécifique
docker-compose restart api
```

## 📋 Structure du Projet

```
WService/
├── docker-compose.yml      # Configuration Docker Compose
├── .env                    # Variables d'environnement (secrets)
├── .env.example           # Exemple de configuration
├── .gitignore             # Fichiers à ignorer par Git
├── README.md              # Ce fichier
└── api/                   # Application API
    ├── Dockerfile         # Image Docker de l'API
    ├── requirements.txt   # Dépendances Python
    ├── app.py            # Application Flask
    └── .dockerignore      # Fichiers à ignorer lors du build
```

## 🎯 Exercice Guidé

### Étape 1 : Configuration initiale

1. **Créer le fichier `.env`** (si pas déjà fait) :
   ```bash
   cp .env.example .env
   ```
   Puis éditez `.env` et modifiez le mot de passe de la base de données.

### Étape 2 : Démarrer l'application

```bash
docker-compose up --build
```

Cette commande va :
- Construire l'image de l'API
- Télécharger l'image PostgreSQL
- Créer le réseau `wservice-network`
- Créer le volume `db-data`
- Démarrer les deux services

### Étape 3 : Tester l'application

Une fois les services démarrés, testez les endpoints :

```bash
# Vérifier que l'API fonctionne
curl http://localhost:3000/health

# Tester la connexion à la base de données
curl http://localhost:3000/api/db/test

# Initialiser la table users
curl -X POST http://localhost:3000/api/db/init

# Créer un utilisateur
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Lister les utilisateurs
curl http://localhost:3000/api/users
```

### Étape 4 : Observer les logs

Dans un autre terminal :
```bash
docker-compose logs -f
```

### Étape 5 : Vérifier la persistance

1. Arrêtez les services : `docker-compose down`
2. Redémarrez : `docker-compose up -d`
3. Vérifiez que les données sont toujours là : `curl http://localhost:3000/api/users`

Les données persistent grâce au volume `db-data` !

## 🔍 Analyse du docker-compose.yml

### Section `services`
- **`api`** : Service de l'application
  - `build` : Construit l'image depuis `./api/Dockerfile`
  - `ports` : Expose le port 3000
  - `environment` : Variables d'environnement (depuis `.env`)
  - `volumes` : Montage pour le développement
  - `depends_on` : Attend que `db` soit prêt
  - `networks` : Connecté au réseau `wservice-network`

- **`db`** : Service de la base de données
  - `image` : Utilise l'image PostgreSQL officielle
  - `volumes` : Volume persistant pour les données
  - `healthcheck` : Vérifie que PostgreSQL est prêt

### Section `networks`
Définit le réseau virtuel `wservice-network` de type bridge.

### Section `volumes`
Définit le volume persistant `db-data` pour stocker les données PostgreSQL.

## 🛠️ Dépannage

### Les services ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs

# Vérifier que les ports ne sont pas déjà utilisés
lsof -i :3000
lsof -i :5432
```

### Reconstruire depuis zéro
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Accéder à la base de données directement
```bash
docker-compose exec db psql -U postgres -d wservice_db
```

## 📖 Ressources

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices Docker Compose](https://docs.docker.com/compose/production/)

## ✅ Checklist de compréhension

- [ ] Comprendre le concept de services
- [ ] Comprendre les réseaux virtuels
- [ ] Comprendre les volumes persistants
- [ ] Savoir utiliser les commandes `up`, `down`, `logs`
- [ ] Comprendre l'utilisation du fichier `.env`
- [ ] Savoir tester l'application
- [ ] Vérifier la persistance des données

---

**Bon apprentissage ! 🎓**

