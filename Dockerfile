FROM python:3.11-slim-bookworm

# Evitar escritura de .pyc y forzar stdout a consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar los Drivers de SQL Server para Linux y dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    g++ \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get purge -y --auto-remove curl gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir la carpeta de trabajo
WORKDIR /app

# Instalar todos los paquetes de requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# Exponer el puerto de Flask interno
EXPOSE 5000

# Iniciarlo (usamos shell para que lea variables y levante SocketIO)
CMD ["python", "app.py"]
