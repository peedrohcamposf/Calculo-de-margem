from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Banco financiador associado às reservas financiadas
class BancoFinanciadorMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_banco_financiador"
    __table_args__ = (
        Index(
            "UQ_tb_cm_margem_banco_financiador_nome",
            "nome",
            unique=True,
        ),
        {"schema": "dbo"},
    )

    id_banco_financiador = Column(Integer, primary_key=True)
    codigo_sap = Column(String(10), nullable=True)
    nome = Column(String(120), nullable=False)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    reservas = relationship(
        "ReservaMargemModel",
        back_populates="banco_financiador",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<BancoFinanciadorMargem("
            f"id_banco_financiador={self.id_banco_financiador!r}, "
            f"nome={self.nome!r}"
            f")>"
        )
