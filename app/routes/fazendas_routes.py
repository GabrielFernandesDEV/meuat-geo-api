from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.controllers.fazenda_controller import FazendaController, NOT_FOUND_RESPONSE
from app.schemas.fazenda_schema import FazendaResponse, PontoBuscaRequest, RaioBuscaRequest, PaginatedResponse
from app.infrastructure.database import get_db
from typing import List

router = APIRouter(
    prefix="/fazendas",
    tags=["fazendas"]
)



@router.get(
    "/{cod_imovel}",
    response_model=PaginatedResponse[FazendaResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar Fazendas por Código do Imóvel",
    description="Retorna os dados de todas as fazendas com o código do imóvel especificado (cod_imovel). Pode retornar múltiplos resultados. "
                "Parâmetros de paginação podem ser passados via query params: page e page_size.",
    responses=NOT_FOUND_RESPONSE
)
async def get_fazenda_by_cod_imovel(
    cod_imovel: str = Path(..., min_length=1, description="Código do imóvel da fazenda (cod_imovel)"),
    page: int = Query(1, gt=0, description="Número da página (padrão: 1)"),
    page_size: int = Query(10, gt=0, le=100, description="Quantidade de itens por página (padrão: 10, máximo: 100)"),
    db: Session = Depends(get_db)
) -> PaginatedResponse[FazendaResponse]:
    """
    Endpoint para buscar fazendas pelo código do imóvel (cod_imovel) com paginação
    
    Args:
        cod_imovel: Código do imóvel da fazenda a ser buscada
        page: Número da página (query param, padrão: 1)
        page_size: Tamanho da página (query param, padrão: 10, máximo: 100)
        db: Sessão do banco de dados (injetada automaticamente)
        
    Returns:
        PaginatedResponse[FazendaResponse]: Resposta paginada com fazendas encontradas (pode conter múltiplos itens)
        
    Raises:
        HTTPException: 404 se nenhuma fazenda for encontrada
        
    Example:
        GET /fazendas/SP-3500105-279714F410E746B0B440EFAD4B0933D4?page=1&page_size=10
    """
    return FazendaController.get_fazenda_by_cod_imovel(db, cod_imovel, page, page_size)


@router.post(
    "/busca-ponto",
    response_model=PaginatedResponse[FazendaResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar Fazendas por Ponto",
    description="Recebe coordenadas (latitude/longitude) no body e retorna a(s) fazenda(s) que contém aquele ponto. "
                "Parâmetros de paginação podem ser passados via query params: page e page_size."
)
async def buscar_fazendas_por_ponto(
    request: PontoBuscaRequest,
    page: int = Query(1, gt=0, description="Número da página (padrão: 1)"),
    page_size: int = Query(10, gt=0, le=100, description="Quantidade de itens por página (padrão: 10, máximo: 100)"),
    db: Session = Depends(get_db)
) -> PaginatedResponse[FazendaResponse]:
    """
    Endpoint para buscar fazendas que contêm um ponto específico com paginação
    
    Args:
        request: Objeto contendo latitude e longitude do ponto (no body)
        page: Número da página (query param, padrão: 1)
        page_size: Tamanho da página (query param, padrão: 10, máximo: 100)
        db: Sessão do banco de dados (injetada automaticamente)
        
    Returns:
        PaginatedResponse[FazendaResponse]: Resposta paginada com fazendas que contêm o ponto especificado
        (pode retornar lista vazia se nenhuma fazenda contiver o ponto)
        
    Example:
        POST /fazendas/busca-ponto?page=1&page_size=10
        Body: {"latitude": -23.5505, "longitude": -46.6333}
    """
    return FazendaController.get_fazendas_by_point(
        db, 
        request.latitude, 
        request.longitude,
        page,
        page_size
    )


@router.post(
    "/busca-raio",
    response_model=PaginatedResponse[FazendaResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar Fazendas por Raio",
    description="Recebe coordenadas (latitude/longitude) e raio em quilômetros no body, retorna todas as fazendas dentro desse raio. "
                "Parâmetros de paginação podem ser passados via query params: page e page_size."
)
async def buscar_fazendas_por_raio(
    request: RaioBuscaRequest,
    page: int = Query(1, gt=0, description="Número da página (padrão: 1)"),
    page_size: int = Query(10, gt=0, le=100, description="Quantidade de itens por página (padrão: 10, máximo: 100)"),
    db: Session = Depends(get_db)
) -> PaginatedResponse[FazendaResponse]:
    """
    Endpoint para buscar fazendas dentro de um raio específico com paginação
    
    Args:
        request: Objeto contendo latitude, longitude do ponto central e raio em quilômetros (no body)
        page: Número da página (query param, padrão: 1)
        page_size: Tamanho da página (query param, padrão: 10, máximo: 100)
        db: Sessão do banco de dados (injetada automaticamente)
        
    Returns:
        PaginatedResponse[FazendaResponse]: Resposta paginada com fazendas dentro do raio especificado
        (pode retornar lista vazia se nenhuma fazenda estiver dentro do raio)
        
    Example:
        POST /fazendas/busca-raio?page=1&page_size=10
        Body: {"latitude": -23.5505, "longitude": -46.6333, "raio_km": 50}
    """
    return FazendaController.get_fazendas_by_radius(
        db,
        request.latitude,
        request.longitude,
        request.raio_km,
        page,
        page_size
    )

