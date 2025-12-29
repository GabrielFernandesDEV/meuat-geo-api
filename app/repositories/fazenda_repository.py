from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.models.fazenda_model import Fazenda
from app.repositories.base_repository import BaseRepository
from app.repositories.geo_repository_mixin import GeoRepositoryMixin


class FazendaRepository(BaseRepository[Fazenda], GeoRepositoryMixin[Fazenda]):
    """
    Repository responsável pelas operações de banco de dados relacionadas a Fazendas.
    
    Herda funcionalidades de:
    - BaseRepository: métodos genéricos (get_by_id)
    - GeoRepositoryMixin: métodos geoespaciais com paginação (get_by_point, get_by_radius)
    """
    
    def __init__(self):
        """
        Inicializa o repository com o modelo Fazenda
        """
        BaseRepository.__init__(self, Fazenda)
    
    # Métodos disponíveis através das classes base:
    # - get_by_id(db, fazenda_id) -> Optional[Fazenda] (de BaseRepository)
    # - get_by_point(db, latitude, longitude, page=1, page_size=10) -> Tuple[List[Fazenda], int] (de GeoRepositoryMixin)
    # - get_by_radius(db, latitude, longitude, raio_km, page=1, page_size=10) -> Tuple[List[Fazenda], int] (de GeoRepositoryMixin)
    
    # Métodos estáticos mantidos para compatibilidade com código existente
    @staticmethod
    def get_by_id(db: Session, fazenda_id: int) -> Optional[Fazenda]:
        """
        Busca uma fazenda pelo ID (método estático para compatibilidade)
        
        Args:
            db: Sessão do banco de dados
            fazenda_id: ID da fazenda a ser buscada
            
        Returns:
            Fazenda se encontrada, None caso contrário
        """
        return db.query(Fazenda).filter(Fazenda.id == fazenda_id).first()
    
    @staticmethod
    def get_by_point(db: Session, latitude: float, longitude: float, page: int = 1, page_size: int = 10) -> Tuple[List[Fazenda], int]:
        """
        Busca fazendas que contêm um ponto específico (latitude/longitude) com paginação
        (método estático para compatibilidade)
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            
        Returns:
            Tupla contendo (lista de fazendas paginadas, total de fazendas encontradas)
        """
        repository = FazendaRepository()
        # Chama diretamente o método do mixin para evitar recursão
        return GeoRepositoryMixin.get_by_point(repository, db, latitude, longitude, page, page_size)
    
    @staticmethod
    def get_by_radius(db: Session, latitude: float, longitude: float, raio_km: float, page: int = 1, page_size: int = 10) -> Tuple[List[Fazenda], int]:
        """
        Busca fazendas dentro de um raio específico a partir de um ponto central com paginação
        (método estático para compatibilidade)
        
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
        repository = FazendaRepository()
        # Chama diretamente o método do mixin para evitar recursão
        return GeoRepositoryMixin.get_by_radius(repository, db, latitude, longitude, raio_km, page, page_size)

