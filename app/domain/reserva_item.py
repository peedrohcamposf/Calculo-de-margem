from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Item da reserva com todos os componentes de custo, impostos e margem
class ReservaItemMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_reserva_item"
    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="CK_tb_cm_margem_reserva_item_qtd",
        ),
        CheckConstraint(
            """
            impostos_venda_percent BETWEEN 0 AND 1 AND
            impostos_compra_percent_icms_piscofins BETWEEN 0 AND 1 AND
            impostos_compra_percent_piscofins BETWEEN 0 AND 1 AND
            perc_credito_impostos_frete BETWEEN 0 AND 1 AND
            perc_pdi_garantia BETWEEN 0 AND 1 AND
            margem_bruta_percent BETWEEN -1 AND 5 AND
            margem_contrib_percent BETWEEN -1 AND 5
            """,
            name="CK_tb_cm_margem_reserva_item_perc",
        ),
        Index(
            "IX_tb_cm_margem_reserva_item_reserva",
            "id_reserva",
        ),
        {"schema": "dbo"},
    )

    id_reserva_item = Column(BigInteger, primary_key=True)

    id_reserva = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_reserva.id_reserva"),
        nullable=False,
    )
    id_produto = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_produto.id_produto"),
        nullable=False,
    )
    id_dn = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_config_dn.id_dn"),
        nullable=True,
    )

    quantidade = Column(Integer, nullable=False, server_default=text("1"))

    valor_venda_unitario = Column(Numeric(18, 2), nullable=False)
    valor_venda_total = Column(
        Numeric(18, 2),
        Computed("valor_venda_unitario * quantidade"),
        nullable=False,
    )

    valor_dn_unitario = Column(Numeric(18, 2), nullable=False)
    valor_dn_total = Column(
        Numeric(18, 2),
        Computed("valor_dn_unitario * quantidade"),
        nullable=False,
    )

    impostos_venda_percent = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )
    impostos_venda_valor = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    impostos_compra_percent_icms_piscofins = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )
    impostos_compra_percent_piscofins = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )
    impostos_compra_valor_total = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    valor_opcionais = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    valor_mao_obra = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    custo_frete_compra = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    perc_credito_impostos_frete = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )
    valor_credito_impostos_frete = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    custo_contrato_manutencao = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    perc_pdi_garantia = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )
    valor_pdi_garantia = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    frete_venda = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    custo_financeiro_total = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    valor_carta_fianca = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    valor_cortesia = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    comissao_total = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    margem_bruta_valor = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    margem_bruta_percent = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )

    margem_contrib_valor = Column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    margem_contrib_percent = Column(
        Numeric(9, 6),
        nullable=False,
        server_default=text("0"),
    )

    reserva = relationship(
        "ReservaMargemModel",
        back_populates="itens",
        lazy="joined",
    )
    produto = relationship(
        "ProdutoMargemModel",
        back_populates="itens_reserva",
        lazy="joined",
    )
    config_dn = relationship(
        "ConfigDNMargemModel",
        back_populates="itens_reserva",
        lazy="joined",
    )
    opcionais = relationship(
        "ReservaItemOpcionalMargemModel",
        back_populates="item_reserva",
        lazy="select",
        cascade="all, delete-orphan",
    )
    fluxos = relationship(
        "ReservaItemFluxoMargemModel",
        back_populates="item_reserva",
        lazy="select",
        cascade="all, delete-orphan",
    )
    comissoes = relationship(
        "ReservaItemComissaoMargemModel",
        back_populates="item_reserva",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ReservaItemMargem("
            f"id_reserva_item={self.id_reserva_item!r}, "
            f"id_reserva={self.id_reserva!r}"
            f")>"
        )
