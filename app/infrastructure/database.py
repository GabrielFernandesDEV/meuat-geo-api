# Importa as classes necessárias do SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

# Importa as configurações do banco de dados
from app.core.config import settings

# Monta a URL de conexão com o banco de dados
DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

# Cria o engine do SQLAlchemy com verificação de conexão
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Verifica se a conexão está ativa antes de usar
)

# Cria a fábrica de sessões do banco de dados
SessionLocal = sessionmaker(
    autocommit=False,  # Não faz commit automático
    autoflush=False,   # Não faz flush automático
    bind=engine        # Vincula ao engine criado
)

# Base para criar os modelos do banco de dados
Base = declarative_base()


# Função que retorna uma sessão do banco de dados
def get_db() -> Generator[Session, None, None]:
    """
    Dependência para obter uma sessão do banco de dados.
    Usada como dependency no FastAPI.
    
    Yields:
        Session: Sessão do banco de dados
        
    Example:
        @router.get("/exemplo")
        def exemplo(db: Session = Depends(get_db)):
            # Use db para fazer queries
            pass
    """
    # Cria uma nova sessão
    db = SessionLocal()
    try:
        # Retorna a sessão para uso
        yield db
    finally:
        # Sempre fecha a sessão após o uso
        db.close()
