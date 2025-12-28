from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.routes import health_router, fazendas_router
from app.core.exception_handlers import validation_exception_handler
import uvicorn

app = FastAPI(
    title="MeuAT Geo API",
    description="API Geoespacial para MeuAT",
    version="1.0.0"
)

# Registra exception handlers customizados
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Registra as rotas
app.include_router(health_router)
app.include_router(fazendas_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )