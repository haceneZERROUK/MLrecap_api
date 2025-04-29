FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install essential system dependencies, including ODBC and MySQL support
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    libodbc1 \
    gpg \
    dirmngr \
    libgomp1 \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18 for SQL Server
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Vérifie l'installation ODBC
RUN odbcinst -q -d

# Crée un utilisateur non privilégié
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copier les dépendances Python
COPY requirements.txt .

# Installer les dépendances - avec désactivation du cache pour éviter les problèmes
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir mysql-connector-python==8.2.0  # Installer explicitement mysql-connector-python

# Copier le code source
COPY . .

COPY .env /app

# Vérifier l'installation du module mysql pour le débogage
RUN python -c "import mysql.connector; print('MySQL Connector installé avec succès')"

# Utiliser l'utilisateur non privilégié
USER appuser

# Exposer le port utilisé par l'app
EXPOSE 8086

# CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8086"]
ENTRYPOINT ["./entrypoint.sh"]