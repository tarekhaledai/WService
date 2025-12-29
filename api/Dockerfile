FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour psycopg2
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port
EXPOSE 3000

# Commande par défaut (peut être surchargée dans docker-compose.yml)
CMD ["python", "app.py"]
