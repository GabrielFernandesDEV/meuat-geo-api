from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import date


class FazendaResponse(BaseModel):
    """
    Schema de resposta para uma fazenda no formato tradicional
    """
    id: int
    cod_tema: Optional[str] = None
    nom_tema: Optional[str] = None
    cod_imovel: Optional[str] = None
    mod_fiscal: Optional[float] = None
    num_area: Optional[float] = None
    ind_status: Optional[str] = None
    ind_tipo: Optional[str] = None
    des_condic: Optional[str] = None
    municipio: Optional[str] = None
    cod_estado: Optional[str] = None
    dat_criaca: Optional[str] = None
    dat_atuali: Optional[str] = None

    @field_validator('dat_criaca', 'dat_atuali', mode='before')
    @classmethod
    def convert_date_to_string(cls, v):
        """Converte date para string se necessário"""
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return str(v) if v else None

    model_config = {
        "from_attributes": True,  # Permite criar a partir de objetos SQLAlchemy
        "json_schema_extra": {
            "example": {
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
        }
    }


class FazendaFeatureResponse(BaseModel):
    """
    Schema de resposta para uma fazenda no formato GeoJSON Feature
    """
    type: str = Field(default="Feature", description="Tipo do objeto GeoJSON")
    geometry: Dict[str, Any] = Field(..., description="Geometria em formato GeoJSON")
    properties: Dict[str, Any] = Field(..., description="Propriedades da fazenda")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-51.074144648, -21.708854973], [-51.072451456, -21.708112303], [-51.071743304, -21.709722639], [-51.073568396, -21.710490759], [-51.074144648, -21.708854973]]]
                },
                "properties": {
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
            }
        }
    }


class PontoBuscaRequest(BaseModel):
    """
    Schema de request para busca de fazendas por ponto (coordenadas)
    """
    latitude: float = Field(..., ge=-90, le=90, description="Latitude do ponto (entre -90 e 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude do ponto (entre -180 e 180)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -23.5505,
                "longitude": -46.6333
            }
        }
    }


class RaioBuscaRequest(BaseModel):
    """
    Schema de request para busca de fazendas por raio (coordenadas + raio em quilômetros)
    """
    latitude: float = Field(..., ge=-90, le=90, description="Latitude do ponto central (entre -90 e 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude do ponto central (entre -180 e 180)")
    raio_km: float = Field(..., gt=0, description="Raio de busca em quilômetros (deve ser maior que 0)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -23.5505,
                "longitude": -46.6333,
                "raio_km": 50
            }
        }
    }