from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import and_, text
from typing import List, TypeVar, Generic, Tuple

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
    
    def _validate_radius(self, radius_km: float):
        """Valida se o raio é positivo"""
        if radius_km <= 0:
            raise ValueError("Raio deve ser maior que zero")
        if radius_km > 20000:  # Aproximadamente metade da circunferência da Terra
            raise ValueError("Raio muito grande (máximo: 20000 km)")
    
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
            func.ST_Contains(geom_field, ponto)
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
        # Valida o raio antes de processar
        self._validate_radius(radius_km)
        
        # Converte o raio de quilômetros para metros (PostGIS usa metros)
        radius_meters = radius_km * 1000
        
        # Cria um ponto PostGIS a partir das coordenadas (SRID 4326 = WGS84)
        ponto = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326
        )
        
        # Obtém o campo de geometria do modelo
        geom_field = getattr(self.model, geom_field_name)
        
        # Obtém o nome da tabela para referenciar a coluna corretamente
        table_name = self.model.__table__.name
        
        # Cria expressão SQL para o bounding box usando operador && (otimização rápida)
        # Cria um buffer em geography e converte para geometry para usar com &&
        bbox_sql = text(
            f"{table_name}.{geom_field_name} && "
            f"ST_Envelope(ST_Buffer(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)::geometry)"
        )
        
        # Query otimizada com dois filtros:
        # 1. Operador && (bounding box) - filtro rápido que usa índices espaciais
        #    Performance: cost=24285.38..24285.39 rows=1 width=8 (COM &&)
        # 2. ST_DWithin - filtro preciso com cálculo esferoidal usando geography
        #    Performance: cost=315962.09..315962.10 rows=1 width=8 (SEM &&)
        query = db.query(self.model).filter(
            and_(
                bbox_sql.bindparams(lon=longitude, lat=latitude, radius=radius_meters),
                func.ST_DWithin(
                    geom_field,
                    ponto,
                    radius_meters,
                    True  # use_spheroid=True
                )
            )
        )
        
        # Conta o total de resultados
        total = query.count()
        
        # Aplica paginação
        offset = (page - 1) * page_size
        entities = query.offset(offset).limit(page_size).all()
        
        return entities, total