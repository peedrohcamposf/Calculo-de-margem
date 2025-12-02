from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Detalhamento das comissões aplicadas sobre o item da reserva
class ReservaItemComissaoMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_reserva_item_comissao"
    __table_args__ = (
        CheckConstraint(
            "tipo_comissao IN ('BRUTA','DSR','ENCARGO')",
            name="CK_tb_cm_margem_item_comissao_tipo",
        ),
        CheckConstraint(
            "percentual BETWEEN 0 AND 5",
            name="CK_tb_cm_margem_item_comissao_perc",
        ),
        Index(
            "IX_tb_cm_margem_item_comissao_item",
            "id_reserva_item",
        ),
        {"schema": "dbo"},
    )

    id_reserva_item_comissao = Column(BigInteger, primary_key=True)

    id_reserva_item = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_reserva_item.id_reserva_item"),
        nullable=False,
    )

    tipo_comissao = Column(String(20), nullable=False)
    percentual = Column(Numeric(9, 6), nullable=False)
    valor = Column(Numeric(18, 2), nullable=False)

    item_reserva = relationship(
        "ReservaItemMargemModel",
        back_populates="comissoes",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ReservaItemComissaoMargem("
            f"id_reserva_item_comissao={self.id_reserva_item_comissao!r}, "
            f"id_reserva_item={self.id_reserva_item!r}, "
            f"tipo_comissao={self.tipo_comissao!r}"
            f")>"
        )
