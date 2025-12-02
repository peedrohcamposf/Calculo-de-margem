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


# Tipo de venda (à vista, financiada, órgão público etc.)
class TipoVendaMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_tipo_venda"
    __table_args__ = {"schema": "dbo"}

    id_tipo_venda = Column(SmallInteger, primary_key=True)
    nome = Column(String(80), nullable=False, unique=True)
    codigo_interno = Column(String(20), nullable=True)
    flag_financiado = Column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )
    flag_orgao_publico = Column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    config_dns = relationship(
        "ConfigDNMargemModel",
        back_populates="tipo_venda",
        lazy="select",
    )
    parametros_gerais = relationship(
        "ParametroGeralMargemModel",
        back_populates="tipo_venda",
        lazy="select",
    )
    reservas = relationship(
        "ReservaMargemModel",
        back_populates="tipo_venda",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<TipoVendaMargem("
            f"id_tipo_venda={self.id_tipo_venda!r}, "
            f"nome={self.nome!r}"
            f")>"
        )
