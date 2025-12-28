-- Habilita a extensão PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verifica se PostGIS foi instalado corretamente
SELECT PostGIS_Version();






