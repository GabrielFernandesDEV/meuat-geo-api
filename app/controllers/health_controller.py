from app.schemas.health_schema import HealthResponse


class HealthController:
    """
    Controller responsável pela lógica de negócio do health check
    """
    
    @staticmethod
    def get_health() -> HealthResponse:
        """
        Retorna o status de saúde da API
        
        Returns:
            HealthResponse: Objeto com status e mensagem da API
        """
        return HealthResponse(
            status="healthy",
            message="API está funcionando corretamente"
        )
