from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Fluxo financeiro do item (entrada e parcelas, valores presentes e custos)
class ReservaItemFluxoMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_reserva_item_fluxo"
    __table_args__ = (
        CheckConstraint(
            "tipo_parcela IN (1, 2)",
            name="CK_tb_cm_margem_fluxo_tipo_parcela",
        ),
        CheckConstraint(
            "percentual_base BETWEEN 0 AND 1",
            name="CK_tb_cm_margem_fluxo_percentual_base",
        ),
        Index(
            "IX_tb_cm_margem_fluxo_item",
            "id_reserva_item",
            "numero_parcela",
        ),
        {"schema": "dbo"},
    )

    id_reserva_item_fluxo = Column(BigInteger, primary_key=True)

    id_reserva_item = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_reserva_item.id_reserva_item"),
        nullable=False,
    )

    # 1=entrada e 2=parcela
    tipo_parcela = Column(SmallInteger, nullable=False)
    # 0 para entrada
    numero_parcela = Column(SmallInteger, nullable=False)
    prazo_dias = Column(Integer, nullable=False)

    percentual_base = Column(Numeric(9, 6), nullable=False)
    valor_nominal = Column(Numeric(18, 2), nullable=False)
    taxa_efetiva = Column(Numeric(9, 6), nullable=False)
    valor_presente = Column(Numeric(18, 2), nullable=False)
    custo_financeiro = Column(Numeric(18, 2), nullable=False)

    item_reserva = relationship(
        "ReservaItemMargemModel",
        back_populates="fluxos",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ReservaItemFluxoMargem("
            f"id_reserva_item_fluxo={self.id_reserva_item_fluxo!r}, "
            f"id_reserva_item={self.id_reserva_item!r}, "
            f"numero_parcela={self.numero_parcela!r}"
            f")>"
        )
