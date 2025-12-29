# Test de connexion à la base de données
echo "Test de connexion à la base de données"
curl http://localhost:3000/api/db/test

# Initialiser la table users
echo "Initialisation de la table users"
curl -X POST http://localhost:3000/api/db/init

# Créer un utilisateur
echo "Création d'un utilisateur"
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com"}'

# Lister les utilisateurs
echo "Lister les utilisateurs"
curl http://localhost:3000/api/users