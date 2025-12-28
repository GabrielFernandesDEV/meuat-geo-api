from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Schema padrão para respostas de erro
    """
    detail: str = Field(..., description="Mensagem de erro detalhada")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Fazenda com ID 0 não encontrada"
            }
        }
    }

