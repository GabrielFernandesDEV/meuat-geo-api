#!/usr/bin/env python3
"""
Script para carregar dados de Shapefile no banco PostGIS.
Mantém Polygon e MultiPolygon conforme o tipo original.
"""

import logging
import os
import threading
import time
from pathlib import Path

import fiona
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry
from tqdm_loggable.auto import tqdm

# Configura logging para INFO (necessário para tqdm-loggable)
logging.basicConfig(level=logging.INFO, format='%(message)s')


# ---------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------

def normalize_polygon_type(geom):
    """
    Mantém Polygon como Polygon e MultiPolygon como MultiPolygon.
    """
    if geom is None:
        return None

    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom

    return geom


# ---------------------------------------------------------------------
# GeoDataFrame
# ---------------------------------------------------------------------

def normalize_gdf(features, crs):
    """
    Converte features (do fiona) em GeoDataFrame usando GeoPandas.
    GeoPandas não tem leitura nativa em chunks para Shapefiles,
    então usamos fiona para ler iterativamente e GeoPandas para processar.
    """
    # GeoPandas converte features do fiona em GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)

    # CRS padrão se ausente
    if gdf.crs is None:
        gdf.set_crs(epsg=4674, inplace=True)

    # Converte para WGS84 apenas se necessário (otimização - usa to_epsg() que é mais rápido)
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    # Normaliza geometria (mantém para garantir consistência)
    gdf["geometry"] = gdf["geometry"].apply(normalize_polygon_type)

    return gdf


# ---------------------------------------------------------------------
# PostGIS
# ---------------------------------------------------------------------

def create_table(engine, gdf):
    """
    Cria a tabela fazendas com coluna GEOMETRY genérica.
    """
    gdf.head(0).to_postgis(
        name="fazendas",
        con=engine,
        if_exists="fail",
        index=False,
        dtype={"geometry": Geometry("GEOMETRY", srid=4326)},
    )

    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE fazendas ADD COLUMN id SERIAL PRIMARY KEY")
        )


def insert_batch(engine, gdf):
    """Insere um lote de dados no banco."""
    gdf.to_postgis(
        name="fazendas",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=None,  # Insere tudo de uma vez (mais rápido para lotes grandes)
    )


# ---------------------------------------------------------------------
# Processo principal
# ---------------------------------------------------------------------

def load_data(path: str, name_file: str):
    # Banco de dados
    db_user = os.getenv("POSTGRES_USER", "meuat_user")
    db_password = os.getenv("POSTGRES_PASSWORD", "meuat_password")
    db_name = os.getenv("POSTGRES_DB", "meuat_geo_db")
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    conn_str = (
        f"postgresql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    shp_file = Path(path) / name_file

    if not shp_file.exists():
        print(f"❌ Shapefile não encontrado: {shp_file}")
        return False

    engine = create_engine(conn_str)

    # Dropa tabela
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fazendas CASCADE"))

    print("📂 Lendo Shapefile em lotes...")
    start_time = time.time()

    chunk_size = 10_000
    total_loaded = 0
    table_created = False

    try:
        # fiona permite leitura iterativa (eficiente para arquivos grandes)
        # GeoPandas não tem leitura em chunks nativa para Shapefiles
        with fiona.open(shp_file) as src:
            src_crs = src.crs
            total_features = len(src)  # Conta total de features no Shapefile
            
            print(f"📊 Total de registros no Shapefile: {total_features:,}")
            print(f"📦 Processando em lotes de {chunk_size:,} registros...")

            # Barra de progresso (configurada para atualização dinâmica e rápida)
            pbar = tqdm(
                total=total_features,
                unit=" registros",
                desc="💾 Carregando",
                mininterval=0.1,  # Atualiza no mínimo a cada 0.1 segundos
                maxinterval=1.0,   # Máximo de 1 segundo entre atualizações
                smoothing=0.0,     # Sem suavização para resposta imediata
                dynamic_ncols=True # Ajusta largura dinamicamente
            )

            # Timer para atualizar o temporizador a cada segundo
            def update_timer():
                """Atualiza o temporizador do tqdm a cada segundo"""
                while not pbar.disable and pbar.n < pbar.total:
                    time.sleep(1.0)
                    pbar.refresh()  # Força atualização do temporizador
            
            timer_thread = threading.Thread(target=update_timer, daemon=True)
            timer_thread.start()

            # Processa chunks iterando diretamente sobre o arquivo
            batch = []
            processed_count = 0  # Contador de registros realmente processados (inseridos no banco)
            
            for feature in src:
                batch.append(feature)
                
                # Atualiza progresso a cada registro lido (mais dinâmico)
                pbar.update(1)
                
                # Quando o batch atinge o tamanho desejado, processa
                if len(batch) >= chunk_size:
                    batch_size = len(batch)
                    
                    # Converte features (fiona) para GeoDataFrame (GeoPandas)
                    gdf = normalize_gdf(batch, src_crs)

                    # Verifica se há duplicação de dados (gdf não deve ter mais linhas que o batch)
                    if len(gdf) != batch_size:
                        print(f"⚠️ Aviso: Batch tem {batch_size} features, mas GeoDataFrame tem {len(gdf)} linhas")
                        # Usa o tamanho do batch original para evitar inserir dados duplicados
                        gdf = gdf.head(batch_size)  # Limita ao tamanho original se houver discrepância

                    if not table_created:
                        create_table(engine, gdf)
                        table_created = True

                    # Insere no banco (aqui os dados são realmente processados)
                    insert_batch(engine, gdf)
                    processed_count += batch_size
                    total_loaded += batch_size
                    
                    # Força atualização imediata após processar (atualiza temporizador)
                    pbar.refresh()
                    
                    # Limpa o batch para o próximo lote
                    batch = []
            
            # Processa o último lote (se houver)
            if batch:
                batch_size = len(batch)
                
                # Converte features (fiona) para GeoDataFrame (GeoPandas)
                gdf = normalize_gdf(batch, src_crs)

                if len(gdf) != batch_size:
                    print(f"⚠️ Aviso: Batch tem {batch_size} features, mas GeoDataFrame tem {len(gdf)} linhas")
                    gdf = gdf.head(batch_size)

                if not table_created:
                    create_table(engine, gdf)
                    table_created = True

                # Insere no banco (aqui os dados são realmente processados)
                insert_batch(engine, gdf)
                processed_count += batch_size
                total_loaded += batch_size
                
                # Força atualização final
                pbar.refresh()

            # Fecha a barra de progresso (o timer thread vai parar automaticamente)
            pbar.close()

        # Índice espacial
        print("📊 Criando índice espacial...")
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "idx_fazendas_geometry "
                    "ON fazendas USING GIST (geometry)"
                )
            )

        elapsed = time.time() - start_time

        print(f"✅ {total_loaded:,} registros carregados")
        print(f"⏱️ Tempo total: {elapsed:.2f}s ({elapsed/60:.2f} min)")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

