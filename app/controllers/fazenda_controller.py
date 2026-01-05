from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from math import ceil
from app.repositories.fazenda_repository import FazendaRepository
from app.schemas.fazenda_schema import FazendaResponse, PaginatedResponse
from typing import List

# Respostas de erro para documentação
NOT_FOUND_RESPONSE = {
    404: {
        "description": "Fazenda não encontrada",
        "content": {
            "application/json": {
                "example": {"detail": "Fazenda com código SP-3500105-279714F410E746B0B440EFAD4B0933D4 não encontrada"}
            }
        }
    }
}


class FazendaController:
    """
    Controller responsável pela lógica de negócio relacionada a Fazendas
    """
    
    @staticmethod
    def get_fazenda_by_cod_imovel(db: Session, cod_imovel: str) -> List[FazendaResponse]:
        """
        Busca todas as fazendas pelo cod_imovel (pode retornar múltiplos resultados)
        
        Args:
            db: Sessão do banco de dados
            cod_imovel: Código do imóvel da fazenda a ser buscada
            
        Returns:
            List[FazendaResponse]: Lista de fazendas encontradas (pode estar vazia ou conter múltiplos itens)
            
        Raises:
            HTTPException: 
                - 404: Se nenhuma fazenda for encontrada
                - 500: Em caso de erro interno do servidor
        """
        try:
            # Busca todas as fazendas no repositório (pode retornar múltiplos)
            fazendas = FazendaRepository.get_by_cod_imovel(db, cod_imovel)
            
            # Verifica se alguma fazenda foi encontrada
            if not fazendas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Fazenda com código {cod_imovel} não encontrada"
                )
            
            # Converte os models para os schemas de resposta
            return [FazendaResponse.model_validate(fazenda) for fazenda in fazendas]
            
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
    def get_fazenda_by_id(db: Session, fazenda_id: int) -> FazendaResponse:
        """
        Busca uma fazenda pelo ID
        DEPRECATED: Use get_fazenda_by_cod_imovel() em vez disso.
        
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
    def get_fazendas_by_point(db: Session, latitude: float, longitude: float, page: int = 1, page_size: int = 10) -> PaginatedResponse[FazendaResponse]:
        """
        Busca fazendas que contêm um ponto específico (latitude/longitude) com paginação
        
        Args:
            db: Sessão do banco de dados
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            page: Número da página (padrão: 1)
            page_size: Tamanho da página (padrão: 10)
            
        Returns:
            PaginatedResponse[FazendaResponse]: Resposta paginada com fazendas que contêm o ponto
            
        Raises:
            HTTPException: 
                - 500: Em caso de erro interno do servidor
        """
        try:
            # Busca as fazendas no repositório com paginação
            fazendas, total = FazendaRepository.get_by_point(db, latitude, longitude, page, page_size)
            
            # Converte os models para os schemas de resposta
            items = [FazendaResponse.model_validate(fazenda) for fazenda in fazendas]
            
            # Calcula o total de páginas
            total_pages = ceil(total / page_size) if total > 0 else 0
            
            # Retorna a resposta paginada
            return PaginatedResponse[FazendaResponse](
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            # Trata erros inesperados
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar fazendas por ponto: {str(e)}"
            )
    
    @staticmethod
    def get_fazendas_by_radius(db: Session, latitude: float, longitude: float, raio_km: float, page: int = 1, page_size: int = 10) -> PaginatedResponse[FazendaResponse]:
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
            PaginatedResponse[FazendaResponse]: Resposta paginada com fazendas dentro do raio especificado
            
        Raises:
            HTTPException: 
                - 500: Em caso de erro interno do servidor
        """
        try:
            # Busca as fazendas no repositório com paginação
            fazendas, total = FazendaRepository.get_by_radius(db, latitude, longitude, raio_km, page, page_size)
            
            # Converte os models para os schemas de resposta
            items = [FazendaResponse.model_validate(fazenda) for fazenda in fazendas]
            
            # Calcula o total de páginas
            total_pages = ceil(total / page_size) if total > 0 else 0
            
            # Retorna a resposta paginada
            return PaginatedResponse[FazendaResponse](
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            # Trata erros inesperados
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar fazendas por raio: {str(e)}"
            )

