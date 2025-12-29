from sqlalchemy import Column, Integer, Float, Text
from geoalchemy2 import Geometry
from app.infrastructure.database import Base


class Fazenda(Base):
    """
    Modelo SQLAlchemy para a tabela fazendas
    """
    __tablename__ = "fazendas"

    id = Column(Integer, primary_key=True, index=True)
    geom = Column('geom', Geometry('GEOMETRY', srid=4326), nullable=True)
    cod_tema = Column(Text, nullable=True)
    nom_tema = Column(Text, nullable=True)
    cod_imovel = Column(Text, nullable=True)
    mod_fiscal = Column(Float, nullable=True)
    num_area = Column(Float, nullable=True)
    ind_status = Column(Text, nullable=True)
    ind_tipo = Column(Text, nullable=True)
    des_condic = Column(Text, nullable=True)
    municipio = Column(Text, nullable=True)
    cod_estado = Column(Text, nullable=True)
    dat_criaca = Column(Text, nullable=True)
    dat_atuali = Column(Text, nullable=True)

