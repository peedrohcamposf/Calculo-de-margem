from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Modalidade de financiamento utilizada em reservas de margem
class ModalidadeFinanciamentoMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_modalidade_financiamento"
    __table_args__ = {"schema": "dbo"}

    id_modalidade_fin = Column(SmallInteger, primary_key=True)
    nome = Column(String(80), nullable=False, unique=True)
    codigo_interno = Column(String(20), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    config_dns = relationship(
        "ConfigDNMargemModel",
        back_populates="modalidade",
        lazy="select",
    )
    parametros_gerais = relationship(
        "ParametroGeralMargemModel",
        back_populates="modalidade",
        lazy="select",
    )
    reservas = relationship(
        "ReservaMargemModel",
        back_populates="modalidade",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<ModalidadeFinMargem("
            f"id_modalidade_fin={self.id_modalidade_fin!r}, "
            f"nome={self.nome!r}"
            f")>"
        )
