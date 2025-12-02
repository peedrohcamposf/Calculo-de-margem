from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    Computed,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Serviços / opcionais vinculados ao item da reserva
class ReservaItemOpcionalMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_reserva_item_opcional"
    __table_args__ = (
        Index(
            "IX_tb_cm_margem_reserva_item_opc_item",
            "id_reserva_item",
        ),
        {"schema": "dbo"},
    )

    id_reserva_item_opcional = Column(BigInteger, primary_key=True)

    id_reserva_item = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_reserva_item.id_reserva_item"),
        nullable=False,
    )

    descricao = Column(String(200), nullable=False)
    horas = Column(Numeric(9, 2), nullable=True)
    quantidade = Column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )
    custo_unitario = Column(Numeric(18, 2), nullable=False)

    valor_total = Column(
        Numeric(18, 2),
        Computed("custo_unitario * quantidade"),
        nullable=False,
    )

    item_reserva = relationship(
        "ReservaItemMargemModel",
        back_populates="opcionais",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ReservaItemOpcionalMargem("
            f"id_reserva_item_opcional={self.id_reserva_item_opcional!r}, "
            f"id_reserva_item={self.id_reserva_item!r}"
            f")>"
        )
