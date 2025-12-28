from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.repositories.fazenda_repository import FazendaRepository
from app.schemas.fazenda_schema import FazendaResponse

# Respostas de erro para documentação
NOT_FOUND_RESPONSE = {
    404: {
        "description": "Fazenda não encontrada",
        "content": {
            "application/json": {
                "example": {"detail": "Fazenda com ID 0 não encontrada"}
            }
        }
    }
}


class FazendaController:
    """
    Controller responsável pela lógica de negócio relacionada a Fazendas
    """
    
    @staticmethod
    def get_fazenda_by_id(db: Session, fazenda_id: int) -> FazendaResponse:
        """
        Busca uma fazenda pelo ID
        
        Args:
            db: Sessão do banco de dados
            fazenda_id: ID da fazenda a ser buscada
            
        Returns:
            FazendaResponse: Dados da fazenda encontrada
            
        Raises:
            HTTPException: 
                - 404: Se a fazenda não for encontrada
                - 500: Em caso de erro interno do servidor
        """
        try:
            # Busca a fazenda no repositório
            fazenda = FazendaRepository.get_by_id(db, fazenda_id)
            
            # Verifica se a fazenda foi encontrada
            if not fazenda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Fazenda com ID {fazenda_id} não encontrada"
                )
            
            # Converte o model para o schema de resposta usando from_attributes
            return FazendaResponse.model_validate(fazenda)
            
        except HTTPException:
            # Re-lança HTTPException (404, etc) para que o FastAPI trate corretamente
            raise
        except Exception as e:
            # Trata erros inesperados
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar fazenda: {str(e)}"
            )
    
    @staticmethod
    def get_fazendas_by_point(db: Session, latitude: float, longitude: float) -> List[FazendaResponse]:
        """
        Busca fazendas que contêm um ponto específico (latitude/longitude)
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            
        Returns:
            List[FazendaResponse]: Lista de fazendas que contêm o ponto
            
        Raises:
            HTTPException: 
                - 500: Em caso de erro interno do servidor
        """
        try:
            # Busca as fazendas no repositório
            fazendas = FazendaRepository.get_by_point(db, latitude, longitude)
            
            # Converte os models para os schemas de resposta
            return [FazendaResponse.model_validate(fazenda) for fazenda in fazendas]
            
        except Exception as e:
            # Trata erros inesperados
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar fazendas por ponto: {str(e)}"
            )

