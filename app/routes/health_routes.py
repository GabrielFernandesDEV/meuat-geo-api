from fastapi import APIRouter
from app.controllers.health_controller import HealthController
from app.schemas.health_schema import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Endpoint para verificar o status de saúde da API"
)
async def health_check() -> HealthResponse:
    """
    Endpoint de health check para verificar o status da API
    
    Returns:
        HealthResponse: Status e mensagem da API
    """
    return HealthController.get_health()
