from sqlalchemy.orm import Session
from typing import Optional
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

