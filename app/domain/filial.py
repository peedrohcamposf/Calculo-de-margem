from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Filial vinculada a reservas, vendedores e parâmetros
class FilialMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_filial"
    __table_args__ = (
        Index("IX_tb_cm_margem_filial_nome_ci", "nome_ci"),
        {"schema": "dbo"},
    )

    id_filial = Column(Integer, primary_key=True)
    codigo_sap = Column(String(10), nullable=False, unique=True)
    nome = Column(String(120), nullable=False)
    nome_ci = Column(
        String(120),
        Computed("UPPER(nome) COLLATE Latin1_General_CI_AI"),
        nullable=False,
    )
    uf = Column(String(2), nullable=True)
    cidade = Column(String(100), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    # Relacionamentos
    vendedores = relationship(
        "VendedorMargemModel",
        back_populates="filial",
        lazy="select",
    )
    reservas = relationship(
        "ReservaMargemModel",
        back_populates="filial",
        lazy="select",
    )
    config_dns = relationship(
        "ConfigDNMargemModel",
        back_populates="filial",
        lazy="select",
    )
    parametros_gerais = relationship(
        "ParametroGeralMargemModel",
        back_populates="filial",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<FilialMargem("
            f"id_filial={self.id_filial!r}, "
            f"codigo_sap={self.codigo_sap!r}, "
            f"nome={self.nome!r}"
            f")>"
        )
