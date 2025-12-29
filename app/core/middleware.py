import logging
import time
import sys
from datetime import datetime
from pathlib import Path
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configurar logging para arquivo e console
logger = logging.getLogger("middleware_logger")
logger.setLevel(logging.INFO)

# Evitar duplicação de handlers
if not logger.handlers:
    # Formato das mensagens
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    # Criar nome do arquivo com data no padrão PostgreSQL (app-YYYY-MM-DD.log)
    log_dir = Path("logs/api")
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_filename = log_dir / f"app-{today}.log"
    
    # Handler para arquivo com data no nome
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Evitar duplicação de logs
    logger.propagate = False


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturar detalhes da requisição
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        full_url = f"{url}?{query_params}" if query_params else url
        
        # Log da requisição
        logger.info(f"Request: {method} {full_url} from {client_ip}")
        
        # Medir tempo de processamento
        start_time = time.time()
        
        # Processar a requisição
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Obter informações detalhadas da rota processada
        route_info = {
            "path": url,
            "endpoint": "unknown",
            "handler": "unknown"
        }
        
        if hasattr(request, 'scope'):
            # Tentar obter informações da rota
            route = request.scope.get('route')
            if route:
                route_info["path"] = getattr(route, 'path', url)
                route_info["endpoint"] = getattr(route, 'name', 'unknown')
                
                # Tentar obter informações do handler
                if 'endpoint' in request.scope:
                    endpoint = request.scope['endpoint']
                    if hasattr(endpoint, '__name__'):
                        route_info["handler"] = endpoint.__name__
                    elif hasattr(endpoint, '__qualname__'):
                        route_info["handler"] = endpoint.__qualname__
                    elif hasattr(endpoint, '__module__'):
                        route_info["handler"] = f"{endpoint.__module__}.{getattr(endpoint, '__name__', 'unknown')}"
        
        # Log da resposta com informações completas do que foi processado
        status_code = response.status_code
        
        # Usar ERRO para códigos de erro (>= 400), INFO para sucesso
        log_message = (
            f"Response: {method} {full_url} returned {status_code} to {client_ip} | "
            f"Endpoint: {route_info['endpoint']} | "
            f"Handler: {route_info['handler']} | "
            f"Path: {route_info['path']} | "
            f"ProcessTime: {process_time:.4f}s"
        )
        
        if status_code >= 400:
            logger.error(log_message)
        else:
            logger.info(log_message)
        
        return response

