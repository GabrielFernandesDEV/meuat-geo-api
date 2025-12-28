#!/usr/bin/env python3
"""
Script para carregar dados de Shapefile no banco PostGIS.
Mantém Polygon e MultiPolygon conforme o tipo original.
"""

# Proteção contra problemas de multiprocessing no Windows
# Deve ser importado antes de outras bibliotecas que usam multiprocessing
import multiprocessing
if __name__ == "__main__":
    # Configura o método de start para evitar problemas no Windows
    multiprocessing.set_start_method('spawn', force=True)

import logging
import os
import threading
import time
from datetime import datetime
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

def convert_date_format(date_str):
    """
    Converte data do formato DD/MM/YYYY para YYYY-MM-DD.
    Retorna None se a data for inválida ou vazia.
    """
    # Verifica se é nulo ou vazio
    if date_str is None:
        return None
    
    # Converte para string e remove espaços
    date_str = str(date_str).strip()
    
    if date_str == '' or date_str.lower() in ['nan', 'none', 'null']:
        return None
    
    try:
        # Tenta converter DD/MM/YYYY para YYYY-MM-DD
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        # Se falhar, tenta outros formatos comuns
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # Se ainda falhar, retorna None (será inserido como NULL no banco)
            return None


def normalize_gdf(features, crs):
    """
    Converte features (do fiona) em GeoDataFrame usando GeoPandas.
    GeoPandas não tem leitura nativa em chunks para Shapefiles,
    então usamos fiona para ler iterativamente e GeoPandas para processar.
    """
    # GeoPandas converte features do fiona em GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)

    # Renomeia a coluna geometry para geom
    if "geometry" in gdf.columns:
        gdf = gdf.rename_geometry("geom")

    # CRS padrão se ausente
    if gdf.crs is None:
        gdf.set_crs(epsg=4674, inplace=True)

    # Converte para WGS84 apenas se necessário (otimização - usa to_epsg() que é mais rápido)
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    # Normaliza geometria (mantém para garantir consistência)
    gdf["geom"] = gdf["geom"].apply(normalize_polygon_type)

    return gdf


# ---------------------------------------------------------------------
# PostGIS
# ---------------------------------------------------------------------

def map_column_name_to_postgres_type(column_name):
    """
    Mapeia o nome da coluna para o tipo PostgreSQL.
    Retorna o tipo baseado no nome da coluna.
    """
    # Mapeamento por nome da coluna
    column_type_mapping = {
        'cod_tema': 'TEXT',
        'nom_tema': 'TEXT',
        'cod_imovel': 'TEXT',
        'mod_fiscal': 'FLOAT8',
        'num_area': 'FLOAT8',
        'ind_status': 'TEXT',
        'ind_tipo': 'TEXT',
        'des_condic': 'TEXT',
        'municipio': 'TEXT',
        'cod_estado': 'TEXT',
        'dat_criaca': 'DATE',
        'dat_atuali': 'DATE',
    }
    
    # Retorna o tipo mapeado ou TEXT como padrão
    return column_type_mapping.get(column_name.lower(), 'TEXT')


def extract_schema_from_fiona_src(src):
    """
    Extrai o schema (campos e tipos) diretamente do objeto src do fiona.
    Retorna um dicionário simples com nome da coluna: tipo PostgreSQL.
    Mapeia pelo nome da coluna.
    """
    schema = {}
    
    # Pega o schema do shapefile
    properties = src.schema.get('properties', {})
    
    for field_name, field_type in properties.items():
        # Ignora campos de geometria (já são tratados separadamente)
        if field_name.lower() not in ['geometry', 'geom']:
            # Mapeia pelo nome da coluna
            pg_type = map_column_name_to_postgres_type(field_name)
            schema[field_name] = pg_type
    
    return schema


def extract_schema_from_shapefile(shp_file):
    """
    Extrai o schema (campos e tipos) do shapefile.
    Retorna um dicionário com os campos e seus tipos PostgreSQL.
    DEPRECATED: Use extract_schema_from_fiona_src() em vez disso para evitar abrir o arquivo duas vezes.
    """
    schema = {}
    
    with fiona.open(shp_file) as src:
        schema = extract_schema_from_fiona_src(src)
    
    return schema


def create_table_from_schema(engine, schema):
    """
    Cria a tabela fazendas com base no schema (dicionário nome: tipo).
    Inclui a coluna id como SERIAL PRIMARY KEY e a coluna geom.
    """
    with engine.begin() as conn:
        # Monta a lista de colunas do schema
        columns_sql = ["id SERIAL PRIMARY KEY", "geom GEOMETRY(GEOMETRY, 4326)"]
        
        # Adiciona as colunas do schema (dicionário nome: tipo)
        for field_name, field_type in schema.items():
            columns_sql.append(f"{field_name} {field_type}")
        
        # Cria a tabela com todas as colunas de uma vez
        create_table_sql = f"""
            CREATE TABLE fazendas (
                {', '.join(columns_sql)}
            )
        """
        conn.execute(text(create_table_sql))
        
        print(f"✅ Tabela 'fazendas' criada com {len(schema)} colunas do shapefile + id + geom")


def create_table(engine, gdf):
    """
    Cria a tabela fazendas com coluna GEOMETRY genérica.
    """
    gdf.head(0).to_postgis(
        name="fazendas",
        con=engine,
        if_exists="fail",
        index=False,
        dtype={"geom": Geometry("GEOMETRY", srid=4326)},
    )

    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE fazendas ADD COLUMN id SERIAL PRIMARY KEY")
        )


def insert_batch(engine, gdf):
    """
    Insere um lote de dados no banco.
    Converte as colunas de data do formato DD/MM/YYYY para YYYY-MM-DD antes de inserir.
    """
    # Converte colunas de data para o formato aceito pelo PostgreSQL
    date_columns = ['dat_criaca', 'dat_atuali']
    for col in date_columns:
        if col in gdf.columns:
            gdf[col] = gdf[col].apply(convert_date_format)
    
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
    schema = None

    try:
        # fiona permite leitura iterativa (eficiente para arquivos grandes)
        # GeoPandas não tem leitura em chunks nativa para Shapefiles
        with fiona.open(shp_file) as src:
            src_crs = src.crs
            total_features = len(src)  # Conta total de features no Shapefile
            
            # Primeira leitura: extrai o schema do shapefile (aproveita a abertura do arquivo)
            if not table_created:
                print("🔍 Extraindo schema do shapefile...")
                schema = extract_schema_from_fiona_src(src)
                print(f"📋 Schema extraído: {len(schema)} campos encontrados")
                for field_name, field_type in schema.items():
                    print(f"   - {field_name}: {field_type}")
                
                # Cria a tabela com base no schema extraído (dicionário nome: tipo)
                create_table_from_schema(engine, schema)
                table_created = True
            
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
                    "idx_fazendas_geom "
                    "ON fazendas USING GIST (geom)"
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