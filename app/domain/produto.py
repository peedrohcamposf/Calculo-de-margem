from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Computed,
    Index,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Produto / modelo SAP envolvido na composição de margem
class ProdutoMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_produto"
    __table_args__ = (
        Index("IX_tb_cm_margem_produto_desc_ci", "descricao_ci"),
        {"schema": "dbo"},
    )

    id_produto = Column(BigInteger, primary_key=True)
    codigo_sap = Column(String(40), nullable=False, unique=True)
    descricao = Column(String(200), nullable=False)
    descricao_ci = Column(
        String(200),
        Computed("UPPER(descricao) COLLATE Latin1_General_CI_AI"),
        nullable=False,
    )
    sigla_modelo = Column(String(50), nullable=True)
    familia = Column(String(80), nullable=True)
    tipo_produto = Column(String(50), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    config_dns = relationship(
        "ConfigDNMargemModel",
        back_populates="produto",
        lazy="select",
    )
    itens_reserva = relationship(
        "ReservaItemMargemModel",
        back_populates="produto",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<ProdutoMargem("
            f"id_produto={self.id_produto!r}, "
            f"codigo_sap={self.codigo_sap!r}, "
            f"descricao={self.descricao!r}"
            f")>"
        )
