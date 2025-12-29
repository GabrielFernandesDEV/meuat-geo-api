from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """
    Schema de resposta do endpoint de health check
    """
    status: str
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "message": "API está funcionando corretamente"
            }
        }
    )
