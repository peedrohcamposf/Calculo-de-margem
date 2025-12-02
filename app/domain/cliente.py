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


# Cliente utilizado nas reservas de margem
class ClienteMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_cliente"
    __table_args__ = (
        Index("IX_tb_cm_margem_cliente_razao_ci", "razao_social_ci"),
        Index("IX_tb_cm_margem_cliente_email_low", "email"),
        {"schema": "dbo"},
    )

    id_cliente = Column(BigInteger, primary_key=True)
    codigo_sap = Column(String(20), nullable=False, unique=True)
    razao_social = Column(String(200), nullable=False)
    razao_social_ci = Column(
        String(200),
        Computed("UPPER(razao_social) COLLATE Latin1_General_CI_AI"),
        nullable=False,
    )
    cnpj = Column(String(20), nullable=True)
    inscricao_estadual = Column(String(30), nullable=True)
    email = Column(String(254), nullable=True)
    telefone = Column(String(30), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    # Relacionamentos
    reservas = relationship(
        "ReservaMargemModel",
        back_populates="cliente",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<ClienteMargem("
            f"id_cliente={self.id_cliente!r}, "
            f"codigo_sap={self.codigo_sap!r}, "
            f"razao_social={self.razao_social!r}"
            f")>"
        )
