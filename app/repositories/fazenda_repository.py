from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
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
    def get_by_point(db: Session, latitude: float, longitude: float) -> List[Fazenda]:
        """
        Busca fazendas que contêm um ponto específico (latitude/longitude)
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            
        Returns:
            Lista de fazendas que contêm o ponto
        """
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Busca fazendas onde a geometria contém o ponto
        # ST_Contains retorna True se a geometria da fazenda contém o ponto
        fazendas = db.query(Fazenda).filter(
            geo_func.ST_Contains(Fazenda.geom, ponto)
        ).all()
        
        return fazendas

