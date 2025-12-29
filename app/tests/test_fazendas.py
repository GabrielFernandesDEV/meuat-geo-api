from unittest.mock import patch
from fastapi import status


class TestGetFazendaById:
    """
    Classe de testes para o endpoint GET /fazendas/{id}.
    
    Este endpoint busca uma fazenda específica pelo seu ID. Testa casos de sucesso,
    falha (404) e validação de parâmetros inválidos.
    """
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_id')
    def test_get_fazenda_by_id_success(self, mock_get_by_id, client, sample_fazenda, mock_db):
        """
        Testa busca bem-sucedida de uma fazenda existente pelo ID.
        
        Cenário: Fazenda com ID=1 existe no banco de dados.
        
        Verifica:
        - Status HTTP 200 (sucesso)
        - Retorno de todos os campos esperados da fazenda
        - Valores corretos nos campos principais (id, cod_tema, municipio, etc.)
        - Chamada correta do repository com o ID fornecido
        
        Este é o caso feliz (happy path) do endpoint de busca por ID.
        """
        # Configura os mocks
        mock_get_by_id.return_value = sample_fazenda
        
        # Faz a requisição
        response = client.get("/fazendas/1")
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["cod_tema"] == "AREA_IMOVEL"
        assert data["nom_tema"] == "Area do Imovel"
        assert data["municipio"] == "Adamantina"
        assert data["cod_estado"] == "SP"
        
        # Verifica que o método do repository foi chamado corretamente
        mock_get_by_id.assert_called_once()
        call_args = mock_get_by_id.call_args[0]
        assert call_args[1] == 1  # fazenda_id
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_id')
    def test_get_fazenda_by_id_not_found(self, mock_get_by_id, client, mock_db):
        """
        Testa o comportamento quando uma fazenda não existe no banco de dados.
        
        Cenário: Fazenda com ID=999 não existe no banco.
        
        Verifica:
        - Status HTTP 404 (Not Found)
        - Mensagem de erro apropriada indicando que a fazenda não foi encontrada
        - Presença do campo "detail" na resposta de erro
        
        Este teste garante que a API retorna o código HTTP correto quando
        um recurso não existe, seguindo as convenções REST.
        """
        # Configura os mocks
        mock_get_by_id.return_value = None
        
        # Faz a requisição
        response = client.get("/fazendas/999")
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "não encontrada" in data["detail"].lower()
    
    def test_get_fazenda_by_id_invalid_id(self, client):
        """
        Testa a validação de parâmetros de rota inválidos.
        
        Cenários testados:
        - ID = 0 (deve ser > 0 conforme validação do Path)
        - ID = -1 (valores negativos não são permitidos)
        
        Verifica:
        - Status HTTP 422 (Unprocessable Entity) para ambos os casos
        - Validação do Pydantic/FastAPI rejeitando valores inválidos
        
        Este teste garante que a API valida corretamente os parâmetros
        de entrada antes de processar a requisição.
        """
        # Testa com ID zero
        response = client.get("/fazendas/0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Testa com ID negativo
        response = client.get("/fazendas/-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestBuscarFazendasPorPonto:
    """
    Classe de testes para o endpoint POST /fazendas/busca-ponto.
    
    Este endpoint recebe coordenadas (latitude/longitude) e retorna todas as
    fazendas cuja geometria contém aquele ponto. Testa casos de sucesso, lista
    vazia, paginação e validações de entrada.
    """
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_point')
    def test_buscar_fazendas_por_ponto_success(self, mock_get_by_point, 
                                                 client, sample_fazendas_list, mock_db):
        """
        Testa busca bem-sucedida de fazendas que contêm um ponto específico.
        
        Cenário: Existem 2 fazendas que contêm o ponto (-23.5505, -46.6333).
        
        Verifica:
        - Status HTTP 200 (sucesso)
        - Estrutura de resposta paginada correta (items, total, page, etc.)
        - Total de 2 fazendas encontradas
        - Paginação funcionando (page=1, page_size=10, total_pages=1)
        - Lista items contém 2 fazendas com IDs 1 e 2
        - Chamada correta do repository com coordenadas e parâmetros de paginação
        
        Este é o caso feliz do endpoint, testando o fluxo completo com resultados.
        """
        # Configura os mocks
        mock_get_by_point.return_value = (sample_fazendas_list, 2)
        
        # Dados da requisição
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        
        # Faz a requisição
        response = client.post("/fazendas/busca-ponto?page=1&page_size=10", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == 1
        assert data["items"][1]["id"] == 2
        
        # Verifica que o método do repository foi chamado corretamente
        mock_get_by_point.assert_called_once()
        call_args = mock_get_by_point.call_args[0]
        assert call_args[1] == -23.5505  # latitude
        assert call_args[2] == -46.6333  # longitude
        assert call_args[3] == 1  # page
        assert call_args[4] == 10  # page_size
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_point')
    def test_buscar_fazendas_por_ponto_empty_result(self, mock_get_by_point, 
                                                      client, mock_db):
        """
        Testa o comportamento quando nenhuma fazenda contém o ponto fornecido.
        
        Cenário: Nenhuma fazenda contém o ponto (-50.0, -50.0) (coordenadas
        fora da área coberta pelos dados, por exemplo).
        
        Verifica:
        - Status HTTP 200 (sucesso - lista vazia é um resultado válido)
        - Total = 0 (nenhuma fazenda encontrada)
        - Lista items vazia
        - total_pages = 0
        - Estrutura de paginação mantida mesmo com resultados vazios
        
        Este teste garante que a API lida corretamente com casos onde não há
        resultados, retornando uma estrutura válida mas vazia.
        """
        # Configura os mocks
        mock_get_by_point.return_value = ([], 0)
        
        # Dados da requisição
        payload = {
            "latitude": -50.0,
            "longitude": -50.0
        }
        
        # Faz a requisição
        response = client.post("/fazendas/busca-ponto", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0
        assert len(data["items"]) == 0
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_point')
    def test_buscar_fazendas_por_ponto_pagination(self, mock_get_by_point, 
                                                    client, sample_fazendas_list, mock_db):
        """
        Testa se a paginação está funcionando corretamente.
        
        Cenário: Existem 2 fazendas no total, solicitando página 2 com page_size=1.
        
        Verifica:
        - Status HTTP 200
        - page = 2 (página solicitada)
        - page_size = 1 (tamanho da página solicitado)
        - total = 2 (total de registros)
        - total_pages = 2 (2 páginas no total)
        - Repository chamado com os parâmetros de paginação corretos (page=2, page_size=1)
        
        Este teste garante que os parâmetros de paginação são corretamente
        passados para o repository e refletidos na resposta.
        """
        # Configura os mocks - retorna apenas uma fazenda na página 2
        mock_get_by_point.return_value = ([sample_fazendas_list[0]], 2)
        
        # Dados da requisição
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        
        # Faz a requisição com paginação
        response = client.post("/fazendas/busca-ponto?page=2&page_size=1", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 1
        assert data["total"] == 2
        assert data["total_pages"] == 2
        
        # Verifica que o método do repository foi chamado com os parâmetros corretos
        mock_get_by_point.assert_called_once()
        call_args = mock_get_by_point.call_args[0]
        assert call_args[3] == 2  # page
        assert call_args[4] == 1  # page_size
    
    def test_buscar_fazendas_por_ponto_invalid_coordinates(self, client):
        """
        Testa a validação de coordenadas geográficas inválidas.
        
        Cenários testados:
        - Latitude = 91.0 (fora do intervalo válido -90 a 90)
        - Longitude = 181.0 (fora do intervalo válido -180 a 180)
        - Body vazio (campos obrigatórios faltando)
        
        Verifica:
        - Status HTTP 422 (Unprocessable Entity) para todos os casos
        - Validação do Pydantic rejeitando valores fora dos intervalos permitidos
        
        Este teste garante que coordenadas inválidas são rejeitadas antes
        de processar a requisição, evitando erros no processamento geoespacial.
        """
        # Latitude fora do intervalo válido
        payload = {
            "latitude": 91.0,  # Deve ser entre -90 e 90
            "longitude": -46.6333
        }
        response = client.post("/fazendas/busca-ponto", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Longitude fora do intervalo válido
        payload = {
            "latitude": -23.5505,
            "longitude": 181.0  # Deve ser entre -180 e 180
        }
        response = client.post("/fazendas/busca-ponto", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Dados faltando
        response = client.post("/fazendas/busca-ponto", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_buscar_fazendas_por_ponto_invalid_pagination(self, client):
        """
        Testa a validação de parâmetros de paginação inválidos.
        
        Cenários testados:
        - page = 0 (deve ser > 0)
        - page_size = 101 (excede o máximo permitido de 100)
        - page_size = 0 (deve ser > 0)
        
        Verifica:
        - Status HTTP 422 (Unprocessable Entity) para todos os casos
        - Validação do FastAPI Query rejeitando valores fora dos limites
        
        Este teste garante que os parâmetros de paginação são validados
        corretamente, prevenindo comportamentos inesperados ou problemas
        de performance com page_size muito grande.
        """
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        
        # Page inválida (zero ou negativo)
        response = client.post("/fazendas/busca-ponto?page=0", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Page_size muito grande (maior que 100)
        response = client.post("/fazendas/busca-ponto?page_size=101", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Page_size inválido (zero ou negativo)
        response = client.post("/fazendas/busca-ponto?page_size=0", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestBuscarFazendasPorRaio:
    """
    Classe de testes para o endpoint POST /fazendas/busca-raio.
    
    Este endpoint recebe coordenadas (latitude/longitude) e um raio em quilômetros,
    retornando todas as fazendas cuja geometria está dentro desse raio do ponto
    central. Testa casos de sucesso, lista vazia, paginação e validações.
    """
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_radius')
    def test_buscar_fazendas_por_raio_success(self, mock_get_by_radius, 
                                               client, sample_fazendas_list, mock_db):
        """
        Testa busca bem-sucedida de fazendas dentro de um raio específico.
        
        Cenário: Existem 2 fazendas dentro do raio de 50km do ponto (-23.5505, -46.6333).
        
        Verifica:
        - Status HTTP 200 (sucesso)
        - Estrutura de resposta paginada correta
        - Total de 2 fazendas encontradas
        - Paginação funcionando corretamente
        - Chamada correta do repository com coordenadas, raio e parâmetros de paginação
        - Lista items contém as 2 fazendas esperadas
        
        Este é o caso feliz do endpoint de busca por raio, testando o fluxo completo.
        """
        # Configura os mocks
        mock_get_by_radius.return_value = (sample_fazendas_list, 2)
        
        # Dados da requisição
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "raio_km": 50.0
        }
        
        # Faz a requisição
        response = client.post("/fazendas/busca-raio?page=1&page_size=10", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1
        assert len(data["items"]) == 2
        
        # Verifica que o método do repository foi chamado corretamente
        mock_get_by_radius.assert_called_once()
        call_args = mock_get_by_radius.call_args[0]
        assert call_args[1] == -23.5505  # latitude
        assert call_args[2] == -46.6333  # longitude
        assert call_args[3] == 50.0  # raio_km
        assert call_args[4] == 1  # page
        assert call_args[5] == 10  # page_size
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_radius')
    def test_buscar_fazendas_por_raio_empty_result(self, mock_get_by_radius, 
                                                     client, mock_db):
        """
        Testa o comportamento quando nenhuma fazenda está dentro do raio fornecido.
        
        Cenário: Nenhuma fazenda está dentro de 1km do ponto (-50.0, -50.0).
        
        Verifica:
        - Status HTTP 200 (sucesso - lista vazia é um resultado válido)
        - Total = 0 (nenhuma fazenda encontrada)
        - Lista items vazia
        - total_pages = 0
        - Estrutura de paginação mantida mesmo sem resultados
        
        Este teste garante que a API retorna uma resposta válida mesmo quando
        não há fazendas no raio especificado, importante para casos onde o
        usuário busca em áreas não cobertas pelos dados.
        """
        # Configura os mocks
        mock_get_by_radius.return_value = ([], 0)
        
        # Dados da requisição
        payload = {
            "latitude": -50.0,
            "longitude": -50.0,
            "raio_km": 1.0
        }
        
        # Faz a requisição
        response = client.post("/fazendas/busca-raio", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0
        assert len(data["items"]) == 0
    
    @patch('app.controllers.fazenda_controller.FazendaRepository.get_by_radius')
    def test_buscar_fazendas_por_raio_pagination(self, mock_get_by_radius, 
                                                   client, sample_fazendas_list, mock_db):
        """
        Testa se a paginação funciona corretamente na busca por raio.
        
        Cenário: Existem 2 fazendas no total dentro do raio, solicitando página 2
        com page_size=1.
        
        Verifica:
        - Status HTTP 200
        - Parâmetros de paginação corretos na resposta (page=2, page_size=1)
        - Total e total_pages calculados corretamente
        - Repository chamado com os parâmetros de paginação corretos
        
        Este teste garante que a paginação funciona da mesma forma em todos
        os endpoints de busca, mantendo consistência na API.
        """
        # Configura os mocks - retorna apenas uma fazenda na página 2
        mock_get_by_radius.return_value = ([sample_fazendas_list[0]], 2)
        
        # Dados da requisição
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "raio_km": 50.0
        }
        
        # Faz a requisição com paginação
        response = client.post("/fazendas/busca-raio?page=2&page_size=1", json=payload)
        
        # Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 1
        assert data["total"] == 2
        assert data["total_pages"] == 2
        
        # Verifica que o método do repository foi chamado com os parâmetros corretos
        mock_get_by_radius.assert_called_once()
        call_args = mock_get_by_radius.call_args[0]
        assert call_args[4] == 2  # page
        assert call_args[5] == 1  # page_size
    
    def test_buscar_fazendas_por_raio_invalid_coordinates(self, client):
        """
        Testa a validação de coordenadas geográficas e raio inválidos.
        
        Cenários testados:
        - Latitude = 91.0 (fora do intervalo -90 a 90)
        - Longitude = 181.0 (fora do intervalo -180 a 180)
        - raio_km = 0 (deve ser > 0)
        - raio_km = -10 (valores negativos não permitidos)
        - Body vazio (campos obrigatórios faltando)
        
        Verifica:
        - Status HTTP 422 (Unprocessable Entity) para todos os casos
        - Validação do Pydantic rejeitando valores inválidos
        
        Este teste garante que todos os parâmetros de entrada são validados
        antes do processamento, especialmente o raio que deve ser positivo
        para fazer sentido em uma busca geoespacial.
        """
        # Latitude fora do intervalo válido
        payload = {
            "latitude": 91.0,
            "longitude": -46.6333,
            "raio_km": 50.0
        }
        response = client.post("/fazendas/busca-raio", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Longitude fora do intervalo válido
        payload = {
            "latitude": -23.5505,
            "longitude": 181.0,
            "raio_km": 50.0
        }
        response = client.post("/fazendas/busca-raio", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Raio inválido (zero ou negativo)
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "raio_km": 0
        }
        response = client.post("/fazendas/busca-raio", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "raio_km": -10
        }
        response = client.post("/fazendas/busca-raio", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Dados faltando
        response = client.post("/fazendas/busca-raio", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_buscar_fazendas_por_raio_invalid_pagination(self, client):
        """
        Testa a validação de parâmetros de paginação inválidos na busca por raio.
        
        Cenários testados:
        - page = 0 (deve ser > 0)
        - page_size = 101 (excede o máximo de 100)
        - page_size = 0 (deve ser > 0)
        
        Verifica:
        - Status HTTP 422 (Unprocessable Entity) para todos os casos
        - Validação do FastAPI Query funcionando corretamente
        
        Este teste garante consistência nas validações de paginação entre
        todos os endpoints que suportam paginação, mantendo o mesmo comportamento.
        """
        payload = {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "raio_km": 50.0
        }
        
        # Page inválida (zero ou negativo)
        response = client.post("/fazendas/busca-raio?page=0", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Page_size muito grande (maior que 100)
        response = client.post("/fazendas/busca-raio?page_size=101", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Page_size inválido (zero ou negativo)
        response = client.post("/fazendas/busca-raio?page_size=0", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

