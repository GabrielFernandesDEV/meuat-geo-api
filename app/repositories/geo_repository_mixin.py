from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, TypeVar, Generic, Tuple, Type
from geoalchemy2 import functions as geo_func

# Tipo genérico para os modelos
ModelType = TypeVar("ModelType")


class GeoRepositoryMixin(Generic[ModelType]):
    """
    Mixin que adiciona funcionalidades geoespaciais para models com campo de geometria.
    Implementa o padrão Mixin Pattern ou Herança Múltipla para composição de funcionalidades.
    
    Requisitos:
        - O model deve ter um atributo de geometria (padrão: 'geom')
        - O banco de dados deve ter suporte PostGIS
    """
    
    def get_by_point(
        self, 
        db: Session, 
        latitude: float, 
        longitude: float,
        page: int = 1,
        page_size: int = 10,
        geom_field_name: str = "geom"
    ) -> Tuple[List[ModelType], int]:
        """
        Busca entidades que contêm um ponto específico (latitude/longitude) com paginação
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            geom_field_name: Nome do campo de geometria (padrão: 'geom')
            
        Returns:
            Tupla contendo (lista de entidades paginadas, total de entidades encontradas)
        """
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Obtém o campo de geometria do modelo
        geom_field = getattr(self.model, geom_field_name)
        
        # Query base para buscar entidades onde a geometria contém o ponto
        query = db.query(self.model).filter(
            geo_func.ST_Contains(geom_field, ponto)
        )
        
        # Conta o total de resultados
        total = query.count()
        
        # Aplica paginação
        offset = (page - 1) * page_size
        entities = query.offset(offset).limit(page_size).all()
        
        return entities, total
    
    def get_by_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float,
        page: int = 1,
        page_size: int = 10,
        geom_field_name: str = "geom"
    ) -> Tuple[List[ModelType], int]:
        """
        Busca entidades dentro de um raio especificado em quilômetros com paginação
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto central
            longitude: Longitude do ponto central
            radius_km: Raio em quilômetros
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            geom_field_name: Nome do campo de geometria (padrão: 'geom')
            
        Returns:
            Tupla contendo (lista de entidades paginadas, total de entidades encontradas)
        """
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Converte o raio de quilômetros para metros (PostGIS usa metros)
        radius_meters = radius_km * 1000
        
        # Obtém o campo de geometria do modelo
        geom_field = getattr(self.model, geom_field_name)
        
        # Query base para buscar entidades onde a distância entre a geometria e o ponto
        # é menor ou igual ao raio especificado
        # ST_DWithin com use_spheroid=True calcula distância em metros usando esferoide
        # (mais preciso para coordenadas geográficas SRID 4326)
        query = db.query(self.model).filter(
            func.ST_DWithin(
                geom_field,
                ponto,
                radius_meters,
                True  # use_spheroid=True
            )
        )
        
        # Conta o total de resultados
        total = query.count()
        
        # Aplica paginação
        offset = (page - 1) * page_size
        entities = query.offset(offset).limit(page_size).all()
        
        return entities, total

