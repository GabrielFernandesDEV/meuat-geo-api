from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.controllers.fazenda_controller import FazendaController, NOT_FOUND_RESPONSE
from app.schemas.fazenda_schema import FazendaResponse, PontoBuscaRequest, RaioBuscaRequest, PaginatedResponse
from app.infrastructure.database import get_db

router = APIRouter(
    prefix="/fazendas",
    tags=["fazendas"]
)



@router.get(
    "/{id}",
    response_model=FazendaResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar Fazenda por ID",
    description="Retorna os dados de uma fazenda específica pelo ID",
    responses=NOT_FOUND_RESPONSE
)
async def get_fazenda_by_id(
    id: int = Path(..., gt=0, description="ID da fazenda (deve ser um número inteiro positivo)"),
    db: Session = Depends(get_db)
) -> FazendaResponse:
    """
    Endpoint para buscar uma fazenda pelo ID
    
    Args:
        id: ID da fazenda a ser buscada
        db: Sessão do banco de dados (injetada automaticamente)
        
    Returns:
        FazendaResponse: Dados da fazenda encontrada
        
    Raises:
        HTTPException: 404 se a fazenda não for encontrada
    """
    return FazendaController.get_fazenda_by_id(db, id)


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

