from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Parâmetros gerais (impostos, comissões, taxas etc.) aplicados ao cálculo de margem
class ParametroGeralMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_parametro_geral"
    __table_args__ = (
        Index(
            "IX_tb_cm_margem_param_geral_codigo",
            "codigo",
            "id_filial",
            "id_tipo_venda",
            "id_modalidade_fin",
            "data_inicio",
        ),
        {"schema": "dbo"},
    )

    id_parametro = Column(Integer, primary_key=True)
    codigo = Column(String(50), nullable=False)
    descricao = Column(String(200), nullable=True)
    valor_decimal = Column(Numeric(18, 6), nullable=True)
    valor_texto = Column(String(200), nullable=True)

    id_filial = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_filial.id_filial"),
        nullable=True,
    )
    id_tipo_venda = Column(
        SmallInteger,
        ForeignKey("dbo.tb_cm_margem_tipo_venda.id_tipo_venda"),
        nullable=True,
    )
    id_modalidade_fin = Column(
        SmallInteger,
        ForeignKey("dbo.tb_cm_margem_modalidade_financiamento.id_modalidade_fin"),
        nullable=True,
    )

    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=True)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    filial = relationship(
        "FilialMargemModel",
        back_populates="parametros_gerais",
        lazy="joined",
    )
    tipo_venda = relationship(
        "TipoVendaMargemModel",
        back_populates="parametros_gerais",
        lazy="joined",
    )
    modalidade = relationship(
        "ModalidadeFinanciamentoMargemModel",
        back_populates="parametros_gerais",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ParametroGeralMargem("
            f"id_parametro={self.id_parametro!r}, "
            f"codigo={self.codigo!r}"
            f")>"
        )
