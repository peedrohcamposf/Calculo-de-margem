from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Vendedor responsável pelas negociações de margem
class VendedorMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_vendedor"
    __table_args__ = (
        Index("IX_tb_cm_margem_vendedor_nome_ci", "nome_ci"),
        Index("IX_tb_cm_margem_vendedor_email_low", "email"),
        {"schema": "dbo"},
    )

    id_vendedor = Column(Integer, primary_key=True)
    codigo_sap = Column(String(20), nullable=False, unique=True)
    nome = Column(String(150), nullable=False)
    nome_ci = Column(
        String(150),
        Computed("UPPER(nome) COLLATE Latin1_General_CI_AI"),
        nullable=False,
    )
    email = Column(String(254), nullable=True)

    id_filial = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_filial.id_filial"),
        nullable=True,
    )

    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    filial = relationship(
        "FilialMargemModel",
        back_populates="vendedores",
        lazy="joined",
    )
    usuarios = relationship(
        "UsuarioMargemModel",
        back_populates="vendedor",
        lazy="select",
    )
    reservas = relationship(
        "ReservaMargemModel",
        back_populates="vendedor",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<VendedorMargem("
            f"id_vendedor={self.id_vendedor!r}, "
            f"codigo_sap={self.codigo_sap!r}, "
            f"nome={self.nome!r}"
            f")>"
        )
