from sqlalchemy.orm import Session
from typing import Optional, TypeVar, Generic, Type

# Tipo genérico para os modelos
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Repository base genérico com métodos comuns para qualquer model.
    Implementa o padrão Generic Repository Pattern.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Args:
            model: Classe do modelo SQLAlchemy
        """
        self.model = model
    
    def get_by_id(self, db: Session, entity_id: int) -> Optional[ModelType]:
        """
        Busca uma entidade pelo ID
        
        Args:
            db: Sessão do banco de dados
            entity_id: ID da entidade a ser buscada
            
        Returns:
            Entidade se encontrada, None caso contrário
        """
        return db.query(self.model).filter(self.model.id == entity_id).first()

