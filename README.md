@ -1,174 +0,0 @@

# MeuAT Geo API

API REST para busca de fazendas por localização geográfica no estado de São Paulo, desenvolvida como parte do desafio técnico para a vaga de Desenvolvedor Pleno na MeuAT.

## 📋 Sobre o Projeto

O MeuAT é um CRM agrícola que trabalha com dados geoespaciais de fazendas. Esta API permite consultar fazendas do estado de São Paulo usando queries geoespaciais, seja por ponto exato ou por proximidade.

## 🚀 Tecnologias

- **Python 3.10+**
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **PostGIS** - Extensão para dados geoespaciais
- **Docker & Docker Compose** - Containerização e orquestração

## 📦 Pré-requisitos

- Docker
- Docker Compose

## 🔧 Instalação e Execução

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd meuat-geo-api
```

### 2. Execute o projeto

Com um único comando, você sobe toda a infraestrutura:

```bash
docker-compose up
```

A aplicação estará disponível em: `http://localhost:8000`

O script de seed é executado automaticamente na primeira inicialização, carregando os dados das fazendas do estado de São Paulo.

### 3. Acesse a documentação interativa

A documentação automática da API (Swagger) estará disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints da API

### 1. GET /fazendas/

Retorna os dados de uma fazenda específica pelo ID (CAR).

**Exemplo de requisição:**

```bash
GET http://localhost:8000/fazendas/123456
```

**Resposta:**

```json
{
  "id": "123456",
  "nome": "Fazenda Exemplo",
  "geometria": {...},
  ...
}
```

### 2. POST /fazendas/busca-ponto

Recebe coordenadas (latitude/longitude) e retorna a(s) fazenda(s) que contém aquele ponto.

**Exemplo de requisição:**

```bash
POST http://localhost:8000/fazendas/busca-ponto
Content-Type: application/json

{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### 3. POST /fazendas/busca-raio

Recebe coordenadas + raio em quilômetros e retorna todas as fazendas dentro desse raio.

**Exemplo de requisição:**

```bash
POST http://localhost:8000/fazendas/busca-raio
Content-Type: application/json

{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "raio_km": 50
}
```

## 🏗️ Estrutura do Projeto

```
meuat-geo-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI
│   ├── models/              # Modelos de dados
│   ├── schemas/             # Schemas Pydantic
│   ├── routes/              # Endpoints da API
│   ├── database.py          # Configuração do banco
│   └── seed.py              # Script de seed
├── data/                    # Dados GeoJSON
├── docker-compose.yml       # Configuração Docker
├── Dockerfile               # Imagem da aplicação
├── requirements.txt         # Dependências Python
└── README.md
```

## 🗄️ Banco de Dados

O projeto utiliza PostgreSQL com a extensão PostGIS habilitada para realizar queries geoespaciais eficientes:

- **ST_Contains**: Verifica se um ponto está dentro de um polígono
- **ST_DWithin**: Busca geometrias dentro de um raio especificado

## 🧪 Testes

Para executar os testes:

```bash
docker-compose exec api pytest
```

## 📝 Observações

- Os dados das fazendas são carregados automaticamente via script de seed ao iniciar o container pela primeira vez
- O banco de dados persiste os dados em volumes do Docker
- Todos os logs são exibidos no console durante a execução

## 🔍 Desenvolvimento

### Acessar o shell do container

```bash
docker-compose exec api bash
```

### Visualizar logs

```bash
docker-compose logs -f api
```

### Parar os containers

```bash
docker-compose down
```

### Reconstruir os containers

```bash
docker-compose up --build
```

## 📄 Licença

Este projeto foi desenvolvido como parte do processo seletivo para a vaga de Desenvolvedor Pleno na MeuAT.

## 👤 Autor

Desenvolvido como parte do desafio técnico MeuAT.
