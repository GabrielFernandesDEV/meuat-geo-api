# MeuAT Geo API

API REST geoespacial para busca de fazendas do estado de São Paulo, desenvolvida como parte do desafio técnico para a vaga de Desenvolvedor Pleno na MeuAT.

## 📋 Sobre o Projeto

O MeuAT é um CRM agrícola que trabalha com dados geoespaciais de fazendas. Esta API permite consultar fazendas do estado de São Paulo usando queries geoespaciais otimizadas, seja por código do imóvel, ponto exato ou por proximidade (raio).

### Funcionalidades Principais

- 🔍 **Busca por Código do Imóvel**: Busca fazendas pelo código único do imóvel (cod_imovel) com suporte a múltiplos resultados
- 📍 **Busca por Ponto**: Encontra fazendas que contêm um ponto específico (latitude/longitude)
- 📐 **Busca por Raio**: Encontra todas as fazendas dentro de um raio especificado em quilômetros
- 📄 **Paginação**: Todos os endpoints de busca suportam paginação para melhor performance
- 🏥 **Health Check**: Endpoint para verificar o status da API
- 📊 **Logging**: Sistema completo de logs com rotação diária
- 🗄️ **PostGIS**: Utiliza extensões geoespaciais do PostgreSQL para queries otimizadas

## 📚 Documentação Interativa

A API possui documentação interativa gerada automaticamente pelo FastAPI. Após iniciar a aplicação, acesse:

- **🔗 Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interface interativa para testar os endpoints diretamente no navegador
  - Permite fazer requisições e ver respostas em tempo real
  - Documentação completa com exemplos de requisição e resposta

> **Nota**: Certifique-se de que a API está rodando antes de acessar o link acima.

## 🚀 Tecnologias

### Backend

- **Python 3.11** - Linguagem de programação
- **FastAPI 0.104.1** - Framework web moderno e rápido com documentação automática
- **SQLAlchemy 2.0.23** - ORM para Python
- **GeoAlchemy2 0.14.2** - Extensão SQLAlchemy para dados geoespaciais
- **Pydantic 2.5.0** - Validação de dados e serialização

### Banco de Dados

- **PostgreSQL 15** - Banco de dados relacional
- **PostGIS 3.3** - Extensão para dados geoespaciais

### Processamento Geoespacial

- **GeoPandas 0.14.1** - Manipulação de dados geoespaciais
- **Shapely 2.0.2** - Operações geométricas
- **Fiona 1.9.5** - Leitura de formatos geoespaciais (Shapefile)

### Infraestrutura

- **Docker & Docker Compose** - Containerização e orquestração
- **Uvicorn** - Servidor ASGI de alta performance

### Testes

- **Pytest 7.4.3** - Framework de testes
- **HTTPX 0.25.2** - Cliente HTTP assíncrono para testes

## 📦 Pré-requisitos

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)

## 🔧 Instalação e Execução

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd meuat-geo-api
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e configure as variáveis:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
POSTGRES_USER=meuat_user
POSTGRES_PASSWORD=meuat_password
POSTGRES_DB=meuat_geo_db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
```

### 3. Execute o projeto

Com um único comando, você sobe toda a infraestrutura:

```bash
docker-compose up
```

Este comando irá:

1. ✅ Inicializar o banco de dados PostgreSQL com PostGIS
2. ✅ Executar o script de carga de dados (carrega fazendas do estado de São Paulo)
3. ✅ Iniciar a API FastAPI

A aplicação estará disponível em: `http://localhost:8000`

> **Nota**: Na primeira execução, o script de carga pode levar alguns minutos para processar todos os dados. A API só será iniciada após a conclusão da carga.

### 4. Acesse a documentação interativa

A documentação automática da API estará disponível em:

- **🔗 Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interface interativa para testar endpoints

> Veja também a seção [📚 Documentação Interativa](#-documentação-interativa) acima para mais detalhes.

## 📡 Endpoints da API

### 1. Health Check

#### `GET /health`

Verifica o status de saúde da API.

**Resposta:**

```json
{
  "status": "healthy",
  "message": "API está funcionando corretamente"
}
```

---

### 2. Buscar Fazendas por Código do Imóvel

#### `GET /fazendas/{cod_imovel}`

Retorna todas as fazendas com o código do imóvel especificado. Pode retornar múltiplos resultados.

**Parâmetros de Path:**

- `cod_imovel` (string, obrigatório): Código do imóvel da fazenda

**Parâmetros de Query (opcionais):**

- `page` (int, padrão: 1, mínimo: 1): Número da página
- `page_size` (int, padrão: 10, mínimo: 1, máximo: 100): Quantidade de itens por página

**Exemplo de requisição:**

```bash
GET http://localhost:8000/fazendas/SP-3500105-279714F410E746B0B440EFAD4B0933D4?page=1&page_size=10
```

**Resposta (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "cod_tema": "AREA_IMOVEL",
      "nom_tema": "Area do Imovel",
      "cod_imovel": "SP-3500105-279714F410E746B0B440EFAD4B0933D4",
      "mod_fiscal": 0.1912,
      "num_area": 3.8239,
      "ind_status": "AT",
      "ind_tipo": "IRU",
      "des_condic": "Aguardando analise",
      "municipio": "Adamantina",
      "cod_estado": "SP",
      "dat_criaca": "2025-10-09",
      "dat_atuali": "2025-10-09"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Resposta de Erro (404 Not Found):**

```json
{
  "detail": "Fazenda com código SP-3500105-279714F410E746B0B440EFAD4B0933D4 não encontrada"
}
```

---

### 3. Buscar Fazendas por Ponto

#### `POST /fazendas/busca-ponto`

Recebe coordenadas (latitude/longitude) no body e retorna a(s) fazenda(s) que contém aquele ponto.

**Parâmetros de Query (opcionais):**

- `page` (int, padrão: 1, mínimo: 1): Número da página
- `page_size` (int, padrão: 10, mínimo: 1, máximo: 100): Quantidade de itens por página

**Body (JSON):**

```json
{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Validações:**

- `latitude`: Deve estar entre -90 e 90
- `longitude`: Deve estar entre -180 e 180

**Exemplo de requisição:**

```bash
POST http://localhost:8000/fazendas/busca-ponto?page=1&page_size=10
Content-Type: application/json

{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Resposta (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "cod_tema": "AREA_IMOVEL",
      "nom_tema": "Area do Imovel",
      "cod_imovel": "SP-3500105-279714F410E746B0B440EFAD4B0933D4",
      "mod_fiscal": 0.1912,
      "num_area": 3.8239,
      "ind_status": "AT",
      "ind_tipo": "IRU",
      "des_condic": "Aguardando analise",
      "municipio": "Adamantina",
      "cod_estado": "SP",
      "dat_criaca": "2025-10-09",
      "dat_atuali": "2025-10-09"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

> **Nota**: Se nenhuma fazenda contiver o ponto especificado, a resposta terá `items: []` e `total: 0`.

---

### 4. Buscar Fazendas por Raio

#### `POST /fazendas/busca-raio`

Recebe coordenadas (latitude/longitude) e raio em quilômetros no body, retorna todas as fazendas dentro desse raio.

**Parâmetros de Query (opcionais):**

- `page` (int, padrão: 1, mínimo: 1): Número da página
- `page_size` (int, padrão: 10, mínimo: 1, máximo: 100): Quantidade de itens por página

**Body (JSON):**

```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "raio_km": 50
}
```

**Validações:**

- `latitude`: Deve estar entre -90 e 90
- `longitude`: Deve estar entre -180 e 180
- `raio_km`: Deve ser maior que 0 e menor que 20000 km

**Exemplo de requisição:**

```bash
POST http://localhost:8000/fazendas/busca-raio?page=1&page_size=10
Content-Type: application/json

{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "raio_km": 50
}
```

**Resposta (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "cod_tema": "AREA_IMOVEL",
      "nom_tema": "Area do Imovel",
      "cod_imovel": "SP-3500105-279714F410E746B0B440EFAD4B0933D4",
      "mod_fiscal": 0.1912,
      "num_area": 3.8239,
      "ind_status": "AT",
      "ind_tipo": "IRU",
      "des_condic": "Aguardando analise",
      "municipio": "Adamantina",
      "cod_estado": "SP",
      "dat_criaca": "2025-10-09",
      "dat_atuali": "2025-10-09"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 10,
  "total_pages": 15
}
```

> **Nota**: Se nenhuma fazenda estiver dentro do raio especificado, a resposta terá `items: []` e `total: 0`.

---

## 🏗️ Estrutura do Projeto

```
meuat-geo-api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Aplicação FastAPI principal
│   ├── controllers/                 # Camada de controle (lógica de negócio)
│   │   ├── fazenda_controller.py    # Controller de fazendas
│   │   └── health_controller.py     # Controller de health check
│   ├── core/                        # Configurações e utilitários centrais
│   │   ├── config.py                # Configurações da aplicação
│   │   ├── exception_handlers.py    # Handlers de exceções customizados
│   │   └── middleware.py            # Middleware de logging
│   ├── infrastructure/              # Infraestrutura (banco de dados)
│   │   └── database.py              # Configuração do SQLAlchemy
│   ├── models/                      # Modelos SQLAlchemy (ORM)
│   │   └── fazenda_model.py         # Modelo da tabela fazendas
│   ├── repositories/                # Camada de repositório (acesso a dados)
│   │   ├── base_repository.py       # Repository base genérico
│   │   ├── fazenda_repository.py    # Repository de fazendas
│   │   └── geo_repository_mixin.py  # Mixin com métodos geoespaciais
│   ├── routes/                      # Rotas da API
│   │   ├── fazendas_routes.py       # Rotas de fazendas
│   │   └── health_routes.py         # Rotas de health check
│   ├── schemas/                     # Schemas Pydantic (validação/serialização)
│   │   ├── error_schema.py          # Schema de erros
│   │   ├── fazenda_schema.py        # Schemas de fazenda
│   │   └── health_schema.py          # Schema de health check
│   └── tests/                       # Testes automatizados
│       ├── conftest.py              # Configuração do pytest
│       ├── test_fazendas.py         # Testes de fazendas
│       └── test_health.py           # Testes de health check
├── data/                            # Dados geoespaciais (Shapefiles)
├── docs/                            # Documentação adicional
├── init-scripts/                    # Scripts de inicialização do PostgreSQL
│   ├── 01-init-postgis.sql         # Script para habilitar PostGIS
│   └── pg_hba.conf                  # Configuração de autenticação
├── logs/                            # Logs da aplicação
│   ├── api/                         # Logs da API (rotação diária)
│   └── postgresql/                  # Logs do PostgreSQL
├── scripts_carga/                   # Scripts de carga de dados
│   ├── download_data.py             # Download de dados
│   ├── load_data.py                 # Carregamento no banco
│   └── main.py                      # Script principal de carga
├── docker-compose.yml               # Configuração Docker Compose
├── Dockerfile                       # Imagem Docker da aplicação
├── env.example                      # Exemplo de variáveis de ambiente
├── requirements.txt                 # Dependências Python
└── README.md                        # Este arquivo
```

## 🗄️ Banco de Dados

### Estrutura

O projeto utiliza PostgreSQL 15 com a extensão PostGIS 3.3 habilitada para realizar queries geoespaciais eficientes.

### Tabela `fazendas`

A tabela principal contém os seguintes campos:

| Campo          | Tipo                      | Descrição                                                           |
| -------------- | ------------------------- | --------------------------------------------------------------------- |
| `id`         | INTEGER                   | Chave primária                                                       |
| `geom`       | GEOMETRY(GEOMETRY, 4326)  | Geometria em formato PostGIS (SRID 4326 - WGS84)                      |
| `geog`       | GEOGRAPHY(GEOMETRY, 4326) | Geografia em formato PostGIS (otimizado para cálculos de distância) |
| `cod_tema`   | TEXT                      | Código do tema                                                       |
| `nom_tema`   | TEXT                      | Nome do tema                                                          |
| `cod_imovel` | TEXT                      | Código único do imóvel                                             |
| `mod_fiscal` | FLOAT                     | Módulo fiscal                                                        |
| `num_area`   | FLOAT                     | Número da área                                                      |
| `ind_status` | TEXT                      | Indicador de status                                                   |
| `ind_tipo`   | TEXT                      | Indicador de tipo                                                     |
| `des_condic` | TEXT                      | Descrição da condição                                             |
| `municipio`  | TEXT                      | Município                                                            |
| `cod_estado` | TEXT                      | Código do estado                                                     |
| `dat_criaca` | TEXT                      | Data de criação                                                     |
| `dat_atuali` | TEXT                      | Data de atualização                                                 |

### Índices Geoespaciais

O banco de dados utiliza índices espaciais do PostGIS para otimizar as queries:

- **Índice GIST** na coluna `geom` para buscas por ponto (`ST_Contains`)
- **Índice GIST** na coluna `geog` para buscas por raio (`ST_DWithin`)

### Funções PostGIS Utilizadas

- **`ST_Contains(geom, ponto)`**: Verifica se uma geometria contém um ponto
- **`ST_DWithin(geog, ponto, raio)`**: Busca geometrias dentro de um raio especificado (usa cálculo esferoidal)
- **`ST_MakePoint(longitude, latitude)`**: Cria um ponto a partir de coordenadas
- **`ST_SetSRID(geom, 4326)`**: Define o sistema de referência espacial (WGS84)

### Otimizações

A busca por raio utiliza uma estratégia de dois filtros para melhor performance:

1. **Filtro rápido (bounding box)**: Usa o operador `&&` com índices espaciais para uma primeira filtragem
2. **Filtro preciso**: Usa `ST_DWithin` com a coluna `geog` (geography) para cálculo esferoidal preciso

## 🧪 Testes

### Executar Testes

Para executar os testes dentro do container:

```bash
docker-compose exec api pytest
```

### Executar Testes com Cobertura

```bash
docker-compose exec api pytest --cov=app --cov-report=html
```

### Executar Testes Específicos

```bash
docker-compose exec api pytest app/tests/test_fazendas.py
```

## 📝 Logging

O projeto possui um sistema completo de logging:

### Logs da API

- **Localização**: `logs/api/app-YYYY-MM-DD.log`
- **Rotação**: Diária (um arquivo por dia)
- **Nível**: INFO
- **Formato**: `%(asctime)s - %(levelname)s - %(message)s`

### Logs do PostgreSQL

- **Localização**: `logs/postgresql/postgresql-YYYY-MM-DD.log`
- **Rotação**: Diária
- **Configuração**: Logs de conexões, desconexões, erros e warnings

### Informações Registradas

Cada requisição registra:

- Método HTTP e URL completa
- IP do cliente
- Código de status da resposta
- Tempo de processamento
- Endpoint e handler processados

## 🔍 Desenvolvimento

### Acessar o Shell do Container

```bash
docker-compose exec api bash
```

### Visualizar Logs em Tempo Real

**Logs da API:**

```bash
docker-compose logs -f api
```

**Logs do Banco de Dados:**

```bash
docker-compose logs -f db
```

**Todos os logs:**

```bash
docker-compose logs -f
```

### Parar os Containers

```bash
docker-compose down
```

### Parar e Remover Volumes (limpar dados)

```bash
docker-compose down -v
```

### Reconstruir os Containers

```bash
docker-compose up --build
```

### Recarregar Dados

Para recarregar os dados no banco:

```bash
docker-compose up carga
```

### Acessar o Banco de Dados

```bash
docker-compose exec db psql -U meuat_user -d meuat_geo_db
```

## 🎯 Arquitetura

O projeto segue uma arquitetura em camadas:

### Camadas

1. **Routes** (`app/routes/`): Define os endpoints da API e validações de entrada
2. **Controllers** (`app/controllers/`): Contém a lógica de negócio
3. **Repositories** (`app/repositories/`): Abstrai o acesso aos dados
4. **Models** (`app/models/`): Define a estrutura das tabelas (ORM)
5. **Schemas** (`app/schemas/`): Define a validação e serialização de dados (Pydantic)

### Padrões de Design

- **Repository Pattern**: Abstração do acesso a dados
- **Generic Repository**: Repository base genérico reutilizável
- **Mixin Pattern**: Composição de funcionalidades geoespaciais
- **Dependency Injection**: Uso do sistema de dependências do FastAPI

## 🔒 Segurança

- Validação de entrada com Pydantic
- Sanitização de parâmetros de query
- Tratamento de erros padronizado
- Logs de segurança (tentativas de acesso, erros)

## 📊 Performance

### Otimizações Implementadas

1. **Índices Espaciais**: Uso de índices GIST do PostGIS
2. **Paginação**: Todos os endpoints de busca suportam paginação
3. **Otimização de Count**: Evita count desnecessário na primeira página quando há poucos resultados
4. **Bounding Box**: Filtro rápido antes do cálculo preciso de distância
5. **Geography Type**: Uso da coluna `geog` para cálculos de distância esferoidais precisos

### Limites

- `page_size` máximo: 100 itens por página
- `raio_km` máximo: 20000 km (aproximadamente metade da circunferência da Terra)

## 🐛 Troubleshooting

### API não inicia

Verifique se o banco de dados está saudável:

```bash
docker-compose ps
docker-compose logs db
```

### Erro de conexão com banco

Verifique as variáveis de ambiente no arquivo `.env`:

```bash
cat .env
```

### Dados não carregam

Verifique os logs do container de carga:

```bash
docker-compose logs carga
```

### Porta já em uso

Altere a porta no `docker-compose.yml` ou no arquivo `.env`:

```yaml
ports:
  - "${API_PORT:-8000}:8000"
```

## 📄 Licença

Este projeto foi desenvolvido como parte do processo seletivo para a vaga de Desenvolvedor Pleno na MeuAT.

## 👤 Autor

Desenvolvido como parte do desafio técnico MeuAT.
