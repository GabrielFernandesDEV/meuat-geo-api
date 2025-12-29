import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from sqlalchemy.orm import Session  # type: ignore

from app.main import app
from app.infrastructure.database import get_db
from app.models.fazenda_model import Fazenda


@pytest.fixture
def mock_db():
    """
    Fixture que cria um mock da sessão do banco de dados (SQLAlchemy Session).
    
    Este mock substitui a conexão real com o banco durante os testes, permitindo
    testar a lógica de negócio sem depender de uma conexão real ao PostgreSQL/PostGIS.
    É usado em conjunto com override_get_db para injetar esse mock na aplicação.
    """
    db = Mock(spec=Session)
    return db


@pytest.fixture
def override_get_db(mock_db):
    """
    Fixture que sobrescreve a dependência get_db do FastAPI para usar um mock.
    
    Durante os testes, substitui a função get_db() real por uma versão que retorna
    o mock_db. Isso permite testar os endpoints sem necessidade de um banco de dados real.
    Após cada teste, limpa as overrides para não afetar outros testes.
    
    Args:
        mock_db: Fixture que fornece o mock da sessão do banco de dados
    """
    def _get_db():
        try:
            yield mock_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):  # noqa: F811
    """
    Fixture que cria um cliente de teste HTTP para a aplicação FastAPI.
    
    O TestClient permite fazer requisições HTTP (GET, POST, etc.) para os endpoints
    da aplicação sem precisar iniciar um servidor real. É o equivalente a usar
    requests ou httpx, mas integrado ao FastAPI.
    
    Este cliente já vem com o banco de dados mockado (através do override_get_db),
    então todos os testes que usam este cliente não precisam de banco real.
    """
    return TestClient(app)


@pytest.fixture
def sample_fazenda():
    """
    Fixture que retorna um objeto Fazenda de exemplo para uso nos testes.
    
    Cria uma instância do modelo Fazenda com dados fictícios mas realistas,
    simulando uma fazenda do estado de São Paulo. Este objeto é usado como
    retorno mockado dos repositories nos testes de endpoints.
    
    Campos importantes:
    - id: 1 (identificador único)
    - municipio: "Adamantina" (município de SP)
    - cod_estado: "SP" (código do estado)
    - geom: None (geometria mockada, seria WKBElement em produção)
    
    Returns:
        Fazenda: Objeto Fazenda com dados de exemplo
    """
    fazenda = Fazenda()
    fazenda.id = 1
    fazenda.cod_tema = "AREA_IMOVEL"
    fazenda.nom_tema = "Area do Imovel"
    fazenda.cod_imovel = "SP-3500105-279714F410E746B0B440EFAD4B0933D4"
    fazenda.mod_fiscal = 0.1912
    fazenda.num_area = 3.8239
    fazenda.ind_status = "AT"
    fazenda.ind_tipo = "IRU"
    fazenda.des_condic = "Aguardando analise"
    fazenda.municipio = "Adamantina"
    fazenda.cod_estado = "SP"
    fazenda.dat_criaca = "2025-10-09"
    fazenda.dat_atuali = "2025-10-09"
    fazenda.geom = None  # Geometria seria um objeto WKBElement em produção
    return fazenda


@pytest.fixture
def sample_fazendas_list(sample_fazenda):  # noqa: F811
    """
    Fixture que retorna uma lista com 2 fazendas de exemplo para testes.
    
    Útil para testar endpoints que retornam múltiplos resultados, como busca por
    ponto ou busca por raio. A lista contém a sample_fazenda (id=1) e uma segunda
    fazenda (id=2) com dados similares mas diferentes.
    
    Args:
        sample_fazenda: Fixture que fornece a primeira fazenda da lista
    
    Returns:
        List[Fazenda]: Lista com 2 objetos Fazenda para testes de listagens
    """
    fazenda2 = Fazenda()
    fazenda2.id = 2
    fazenda2.cod_tema = "AREA_IMOVEL"
    fazenda2.nom_tema = "Area do Imovel"
    fazenda2.cod_imovel = "SP-3500105-279714F410E746B0B440EFAD4B0933D5"
    fazenda2.mod_fiscal = 0.2000
    fazenda2.num_area = 5.0000
    fazenda2.ind_status = "AT"
    fazenda2.ind_tipo = "IRU"
    fazenda2.des_condic = "Aguardando analise"
    fazenda2.municipio = "Adamantina"
    fazenda2.cod_estado = "SP"
    fazenda2.dat_criaca = "2025-10-10"
    fazenda2.dat_atuali = "2025-10-10"
    fazenda2.geom = None
    
    return [sample_fazenda, fazenda2]

