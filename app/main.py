from fastapi import FastAPI

app = FastAPI(
    title="MeuAT Geo API",
    description="API REST para busca de fazendas por localização geográfica",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à MeuAT Geo API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API"""
    return {"status": "ok"}

