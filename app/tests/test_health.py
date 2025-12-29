from fastapi import status


class TestHealthEndpoint:
    """
    Classe de testes para o endpoint GET /health.
    
    O endpoint de health check é usado para verificar se a API está funcionando
    corretamente. É importante para monitoramento e health checks de infraestrutura.
    """
    
    def test_health_check_success(self, client):
        """
        Testa se o endpoint /health retorna status 200 e a resposta esperada.
        
        Verifica:
        - Status HTTP 200 (sucesso)
        - Campo "status" com valor "healthy"
        - Campo "message" com a mensagem padrão
        - Presença de ambos os campos obrigatórios
        
        Este é um teste básico que garante que o endpoint mais simples da API
        está funcionando corretamente.
        """
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "API está funcionando corretamente"
        assert "status" in data
        assert "message" in data
    
    def test_health_check_response_structure(self, client):
        """
        Testa se a estrutura e tipos da resposta do health check estão corretos.
        
        Verifica:
        - Status HTTP 200
        - Campo "status" é uma string não vazia
        - Campo "message" é uma string não vazia
        - Tipos de dados corretos (validação de schema)
        
        Este teste garante que a resposta está no formato esperado pelo schema
        Pydantic, validando tipos e presença de valores.
        """
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verifica que todos os campos esperados estão presentes
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        assert len(data["status"]) > 0
        assert len(data["message"]) > 0

