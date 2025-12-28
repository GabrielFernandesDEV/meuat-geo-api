from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import List
from app.controllers.fazenda_controller import FazendaController, NOT_FOUND_RESPONSE
from app.schemas.fazenda_schema import FazendaResponse, PontoBuscaRequest
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
    response_model=List[FazendaResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar Fazendas por Ponto",
    description="Recebe coordenadas (latitude/longitude) e retorna a(s) fazenda(s) que contém aquele ponto"
)
async def buscar_fazendas_por_ponto(
    request: PontoBuscaRequest,
    db: Session = Depends(get_db)
) -> List[FazendaResponse]:
    """
    Endpoint para buscar fazendas que contêm um ponto específico
    
    Args:
        request: Objeto contendo latitude e longitude do ponto
        db: Sessão do banco de dados (injetada automaticamente)
        
    Returns:
        List[FazendaResponse]: Lista de fazendas que contêm o ponto especificado
        (pode retornar lista vazia se nenhuma fazenda contiver o ponto)
    """
    return FazendaController.get_fazendas_by_point(
        db, 
        request.latitude, 
        request.longitude
    )

