from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Schema de resposta do endpoint de health check
    """
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "API está funcionando corretamente"
            }
        }
