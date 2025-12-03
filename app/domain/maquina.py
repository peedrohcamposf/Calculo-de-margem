from __future__ import annotations

from sqlalchemy import Column, Integer, Numeric, String

from .base import Base


class MaquinaModel(Base):
    __tablename__ = "tb_cm_maquinas"
    __table_args__ = {"schema": "dbo"}

    id_maquina = Column(Integer, primary_key=True)
    marca = Column(String(50), nullable=False)
    tipo = Column(String(100), nullable=False)
    modelo = Column(String(150), nullable=False)
    codigo = Column(String(10), nullable=False, unique=True)
    valor_compra = Column(Numeric(15, 2), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Maquina("
            f"id_maquina={self.id_maquina!r}, "
            f"codigo={self.codigo!r}, "
            f"modelo={self.modelo!r}"
            f")>"
        )
