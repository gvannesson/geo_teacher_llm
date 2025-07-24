FROM python:3.12-slim

# Installer git et curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"


# Créer dossier de travail
WORKDIR /app

# Copier les fichiers de dépendances en premier pour cache
COPY pyproject.toml uv.lock README.md ./
RUN uv venv && uv sync

RUN uv add sentencepiece>=0.2.0
# Installer les dépendances système avec uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential gcc python3-dev cmake \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Copier le reste du projet
COPY . .

# Exposer le port Chainlit
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=7860
EXPOSE 7860

ENV PYTHONPATH=/app

# Commande de démarrage
CMD ["uv", "run","chainlit", "run", "geo_teacher_chainlit/app.py", "--host", "0.0.0.0", "--port", "7860"]

