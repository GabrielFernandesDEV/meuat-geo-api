from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers.fazenda_controller import FazendaController, NOT_FOUND_RESPONSE
from app.schemas.fazenda_schema import FazendaResponse
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
    id: int,
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

