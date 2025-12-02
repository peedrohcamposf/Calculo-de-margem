from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Configuração de Desconto Negociado (DE/PARA) para cálculo de margem
class ConfigDNMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_config_dn"
    __table_args__ = (
        UniqueConstraint(
            "id_produto",
            "id_filial",
            "id_tipo_venda",
            "id_modalidade_fin_zero",
            "possui_af",
            "ano",
            "mes_zero",
            name="UQ_tb_cm_margem_config_dn_chave",
        ),
        CheckConstraint(
            "mes IS NULL OR (mes BETWEEN 1 AND 12)",
            name="CK_tb_cm_margem_config_dn_mes",
        ),
        CheckConstraint(
            "ano BETWEEN 2000 AND 2100",
            name="CK_tb_cm_margem_config_dn_ano",
        ),
        {"schema": "dbo"},
    )

    id_dn = Column(BigInteger, primary_key=True)

    id_produto = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_produto.id_produto"),
        nullable=False,
    )
    id_filial = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_filial.id_filial"),
        nullable=False,
    )
    id_tipo_venda = Column(
        SmallInteger,
        ForeignKey("dbo.tb_cm_margem_tipo_venda.id_tipo_venda"),
        nullable=False,
    )
    id_modalidade_fin = Column(
        SmallInteger,
        ForeignKey("dbo.tb_cm_margem_modalidade_financiamento.id_modalidade_fin"),
        nullable=True,
    )

    possui_af = Column(Boolean, nullable=False, server_default=text("0"))
    ano = Column(SmallInteger, nullable=False)
    mes = Column(SmallInteger, nullable=True)
    data_referencia = Column(Date, nullable=True)

    valor_dn = Column(Numeric(18, 2), nullable=False)
    origem_dado = Column(
        String(30),
        nullable=False,
        server_default=text("'PLANILHA'"),
    )

    id_modalidade_fin_zero = Column(
        Integer,
        Computed("ISNULL(CONVERT(INT, id_modalidade_fin), 0)"),
        nullable=False,
    )
    mes_zero = Column(
        SmallInteger,
        Computed("ISNULL(mes, 0)"),
        nullable=False,
    )

    produto = relationship(
        "ProdutoMargemModel",
        back_populates="config_dns",
        lazy="joined",
    )
    filial = relationship(
        "FilialMargemModel",
        back_populates="config_dns",
        lazy="joined",
    )
    tipo_venda = relationship(
        "TipoVendaMargemModel",
        back_populates="config_dns",
        lazy="joined",
    )
    modalidade = relationship(
        "ModalidadeFinanciamentoMargemModel",
        back_populates="config_dns",
        lazy="joined",
    )
    itens_reserva = relationship(
        "ReservaItemMargemModel",
        back_populates="config_dn",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<ConfigDNMargem("
            f"id_dn={self.id_dn!r}, "
            f"id_produto={self.id_produto!r}, "
            f"id_filial={self.id_filial!r}, "
            f"ano={self.ano!r}, "
            f"mes={self.mes!r}"
            f")>"
        )
