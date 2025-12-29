# Testes Automatizados - MeuAT Geo API

Este diretório contém os testes automatizados para a API Geoespacial MeuAT, utilizando pytest como framework de testes.

## 📁 Estrutura de Arquivos

```
app/tests/
├── __init__.py          # Arquivo de inicialização do pacote de testes
├── conftest.py          # Fixtures compartilhadas e configurações do pytest
├── test_health.py       # Testes do endpoint GET /health
├── test_fazendas.py     # Testes dos endpoints de fazendas
└── README.md            # Este arquivo
```

## 🚀 Como Executar os Testes

### Executar todos os testes

```bash
pytest
```

### Executar com saída detalhada (verbose)

```bash
pytest -v
```

### Executar um arquivo de teste específico

```bash
# Testes de health check
pytest app/tests/test_health.py

# Testes de fazendas
pytest app/tests/test_fazendas.py
```

### Executar uma classe de testes específica

```bash
# Testes do endpoint GET /fazendas/{cod_imovel}
pytest app/tests/test_fazendas.py::TestGetFazendaByCodImovel

# Testes do endpoint POST /fazendas/busca-ponto
pytest app/tests/test_fazendas.py::TestBuscarFazendasPorPonto

# Testes do endpoint POST /fazendas/busca-raio
pytest app/tests/test_fazendas.py::TestBuscarFazendasPorRaio
```

### Executar um teste específico

```bash
pytest app/tests/test_health.py::TestHealthEndpoint::test_health_check_success
```

### Executar com cobertura de código (se tiver pytest-cov instalado)

```bash
pytest --cov=app --cov-report=html
```

## 📋 Descrição dos Testes

### `test_health.py` - Testes do Endpoint de Health Check

Testa o endpoint `GET /health` que verifica se a API está funcionando corretamente.

#### Testes Incluídos:

1. **test_health_check_success**
   - Verifica se o endpoint retorna status 200
   - Valida os campos "status" e "message" na resposta
   - Garante que a API está respondendo corretamente

2. **test_health_check_response_structure**
   - Valida a estrutura e tipos da resposta
   - Verifica que os campos são strings não vazias
   - Garante conformidade com o schema Pydantic

### `test_fazendas.py` - Testes dos Endpoints de Fazendas

#### Classe: `TestGetFazendaByCodImovel`
Testa o endpoint `GET /fazendas/{cod_imovel}` para buscar uma fazenda específica pelo código do imóvel (cod_imovel).

**Testes:**
- ✅ `test_get_fazenda_by_cod_imovel_success`: Busca bem-sucedida de fazenda existente
- ❌ `test_get_fazenda_by_cod_imovel_not_found`: Retorno 404 quando fazenda não existe

#### Classe: `TestBuscarFazendasPorPonto`
Testa o endpoint `POST /fazendas/busca-ponto` para buscar fazendas que contêm um ponto específico.

**Testes:**
- ✅ `test_buscar_fazendas_por_ponto_success`: Busca bem-sucedida com resultados
- 📄 `test_buscar_fazendas_por_ponto_empty_result`: Lista vazia quando nenhuma fazenda contém o ponto
- 📑 `test_buscar_fazendas_por_ponto_pagination`: Paginação funcionando corretamente
- 🔒 `test_buscar_fazendas_por_ponto_invalid_coordinates`: Validação de coordenadas inválidas
- 🔒 `test_buscar_fazendas_por_ponto_invalid_pagination`: Validação de parâmetros de paginação inválidos

#### Classe: `TestBuscarFazendasPorRaio`
Testa o endpoint `POST /fazendas/busca-raio` para buscar fazendas dentro de um raio específico.

**Testes:**
- ✅ `test_buscar_fazendas_por_raio_success`: Busca bem-sucedida com resultados
- 📄 `test_buscar_fazendas_por_raio_empty_result`: Lista vazia quando nenhuma fazenda está no raio
- 📑 `test_buscar_fazendas_por_raio_pagination`: Paginação funcionando corretamente
- 🔒 `test_buscar_fazendas_por_raio_invalid_coordinates`: Validação de coordenadas e raio inválidos
- 🔒 `test_buscar_fazendas_por_raio_invalid_pagination`: Validação de parâmetros de paginação inválidos

**Legenda:**
- ✅ = Caso de sucesso (happy path)
- ❌ = Caso de erro (404, etc.)
- 📄 = Caso sem resultados
- 📑 = Teste de funcionalidade (paginação)
- 🔒 = Teste de validação

## 🔧 Fixtures (conftest.py)

As fixtures são configurações reutilizáveis que preparam o ambiente para os testes:

### `mock_db`
Cria um mock da sessão do banco de dados (SQLAlchemy Session). Substitui a conexão real durante os testes, permitindo testar a lógica sem depender do PostgreSQL/PostGIS.

### `override_get_db`
Sobrescreve a dependência `get_db` do FastAPI para usar o mock do banco. Isso permite testar endpoints sem necessidade de banco real.

### `client`
Cria um cliente HTTP de teste (TestClient) para fazer requisições aos endpoints da API sem iniciar um servidor real.

### `sample_fazenda`
Retorna um objeto `Fazenda` de exemplo com dados fictícios mas realistas, usado como retorno mockado dos repositories.

### `sample_fazendas_list`
Retorna uma lista com 2 fazendas de exemplo, útil para testar endpoints que retornam múltiplos resultados.

## 🎯 Estratégia de Testes

### Mocking
Os testes utilizam **mocks** para isolar a lógica de negócio:
- O banco de dados é mockado através de `mock_db`
- Os métodos dos repositories são mockados usando `@patch`
- Isso permite testar apenas a lógica dos controllers e rotas

### Cobertura de Testes
Os testes cobrem:
- ✅ **Casos de sucesso**: Fluxo principal funcionando corretamente
- ❌ **Casos de erro**: Tratamento de erros (404, validações)
- 🔒 **Validações**: Parâmetros inválidos são rejeitados
- 📑 **Funcionalidades**: Paginação, estrutura de resposta

### Endpoints Testados
- ✅ `GET /health` - Health check
- ✅ `GET /fazendas/{cod_imovel}` - Buscar fazenda por código do imóvel
- ✅ `POST /fazendas/busca-ponto` - Buscar fazendas por ponto
- ✅ `POST /fazendas/busca-raio` - Buscar fazendas por raio

## 📊 Estatísticas dos Testes

Total de testes: **13**

- Testes de Health: 2
- Testes de Fazendas por Código do Imóvel: 2
- Testes de Busca por Ponto: 5
- Testes de Busca por Raio: 5

## 🔍 Validações Testadas

### Validações de Parâmetros
- Código do imóvel (cod_imovel) não pode ser vazio
- Coordenadas fora dos intervalos válidos são rejeitadas
  - Latitude: deve estar entre -90 e 90
  - Longitude: deve estar entre -180 e 180
- Raio deve ser maior que zero
- Parâmetros de paginação validados
  - Page deve ser > 0
  - Page_size deve ser entre 1 e 100

### Validações de Resposta
- Estrutura de resposta paginada correta
- Tipos de dados corretos nos campos
- Códigos HTTP apropriados (200, 404, 422)
- Mensagens de erro apropriadas

## 💡 Dicas

### Executar testes em modo watch (se tiver pytest-watch instalado)

```bash
ptw
```

### Ver apenas os testes que falharam

```bash
pytest --lf  # last failed
```

### Parar no primeiro erro

```bash
pytest -x
```

### Mostrar prints/logs durante os testes

```bash
pytest -s
```

## 📝 Notas Importantes

1. **Não requer banco de dados real**: Os testes usam mocks, então não é necessário ter o PostgreSQL/PostGIS rodando
2. **Testes isolados**: Cada teste é independente e pode ser executado isoladamente
3. **Fast execution**: Como não há I/O real, os testes são muito rápidos
4. **Documentação**: Cada teste tem docstrings detalhadas explicando o que está sendo testado

## 🔗 Referências

- [Documentação do Pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

