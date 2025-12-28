from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Tuple
from geoalchemy2 import functions as geo_func
from app.models.fazenda_model import Fazenda


class FazendaRepository:
    """
    Repository responsável pelas operações de banco de dados relacionadas a Fazendas
    """
    
    @staticmethod
    def get_by_id(db: Session, fazenda_id: int) -> Optional[Fazenda]:
        """
        Busca uma fazenda pelo ID
        
        Args:
            db: Sessão do banco de dados
            fazenda_id: ID da fazenda a ser buscada
            
        Returns:
            Fazenda se encontrada, None caso contrário
        """
        fazenda = db.query(Fazenda).filter(Fazenda.id == fazenda_id).first()
        return fazenda
    
    @staticmethod
    def get_by_point(db: Session, latitude: float, longitude: float, page: int = 1, page_size: int = 10) -> Tuple[List[Fazenda], int]:
        """
        Busca fazendas que contêm um ponto específico (latitude/longitude) com paginação
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            
        Returns:
            Tupla contendo (lista de fazendas paginadas, total de fazendas encontradas)
        """
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Query base para buscar fazendas onde a geometria contém o ponto
        query = db.query(Fazenda).filter(
            geo_func.ST_Contains(Fazenda.geom, ponto)
        )
        
        # Conta o total de resultados
        total = query.count()
        
        # Aplica paginação
        offset = (page - 1) * page_size
        fazendas = query.offset(offset).limit(page_size).all()
        
        return fazendas, total
    
    @staticmethod
    def get_by_radius(db: Session, latitude: float, longitude: float, raio_km: float, page: int = 1, page_size: int = 10) -> Tuple[List[Fazenda], int]:
        """
        Busca fazendas dentro de um raio específico a partir de um ponto central com paginação
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto central
            longitude: Longitude do ponto central
            raio_km: Raio de busca em quilômetros
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            
        Returns:
            Tupla contendo (lista de fazendas paginadas, total de fazendas encontradas)
        """
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Converte o raio de quilômetros para metros
        raio_metros = raio_km * 1000
        
        # Query base para buscar fazendas onde a distância entre a geometria da fazenda e o ponto
        # é menor ou igual ao raio especificado
        # ST_DWithin com use_spheroid=True calcula distância em metros usando esferoide
        # (mais preciso para coordenadas geográficas SRID 4326)
        query = db.query(Fazenda).filter(
            func.ST_DWithin(
                Fazenda.geom,
                ponto,
                raio_metros,
                True
            )
        )
        
        # Conta o total de resultados
        total = query.count()
        
        # Aplica paginação
        offset = (page - 1) * page_size
        fazendas = query.offset(offset).limit(page_size).all()
        
        return fazendas, total

