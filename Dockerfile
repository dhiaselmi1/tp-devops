# ---- Image de base : Python officiel, variante « slim » (≈ 50 Mo au lieu de ≈ 1 Go)
FROM python:3.11-slim

# ---- Réglages Python adaptés aux conteneurs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=1.0.0
# PYTHONDONTWRITEBYTECODE : pas de fichiers .pyc inutiles dans l'image
# PYTHONUNBUFFERED       : les print/logs sortent immédiatement (visibles avec docker logs)

# ---- Répertoire de travail dans le conteneur (créé s'il n'existe pas)
WORKDIR /app

# ---- 1) Dépendances d'abord : cette couche reste en CACHE tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- 2) Code ensuite : modifier main.py ne relance PAS le long pip install
COPY . .

# ---- Sécurité : utilisateur sans privilèges, propriétaire de /app (SQLite y écrit local.db)
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# ---- Documentation du port écouté (n'ouvre rien à lui seul : c'est -p qui publie le port)
EXPOSE 8000

# ---- Commande lancée au démarrage du conteneur (forme JSON = pas de shell intermédiaire)
# 0.0.0.0 : écouter sur toutes les interfaces, sinon l'API serait injoignable depuis l'hôte
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
