FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    # Compilador C necessário para compilar extensões Python (psycopg2, geopandas, etc)
    gcc \
    g++ \
    # Bibliotecas de desenvolvimento PostgreSQL (necessário para compilar psycopg2)
    libpq-dev \
    # Bibliotecas GDAL para processar dados geoespaciais (usado pelo GeoPandas/Fiona)
    libgdal-dev \
    # Ferramentas GDAL de linha de comando
    gdal-bin \
    # Bibliotecas PROJ para sistemas de coordenadas e projeções geoespaciais
    libproj-dev \
    proj-data \
    # Bibliotecas GEOS para operações geométricas espaciais
    libgeos-dev \
    # Biblioteca para índices espaciais (melhora performance de queries geoespaciais)
    libspatialindex-dev \
    # Parser XML necessário para Fiona (leitura de Shapefiles)
    libexpat1 \
    libexpat1-dev \
    # Bibliotecas adicionais para GDAL/Fiona
    libxml2-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Configura variáveis de ambiente para GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH

# Atualiza pip, setuptools e wheel
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código (será sobrescrito pelo volume, mas necessário para o build)
COPY . .
