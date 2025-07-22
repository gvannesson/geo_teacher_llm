FROM python:3.12-slim

# Installer git et uv
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Créer dossier de travail
WORKDIR /app

# Copier les fichiers de dépendances en premier pour cache
COPY pyproject.toml .
COPY uv.lock .

# Installer les dépendances système avec uv
RUN uv pip install --system --no-deps .

# Copier le reste du projet
COPY . .

# Exposer le port Chainlit
EXPOSE 8000

# Commande de démarrage
CMD ["chainlit", "run", "geo_teacher_chainlit/app.py", "--host", "0.0.0.0", "--port", "8000"]
