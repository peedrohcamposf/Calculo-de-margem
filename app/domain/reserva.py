from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
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


# Cabeçalho da reserva de margem (negociação principal)
class ReservaMargemModel(TimestampMixin, Base):

    __tablename__ = "tb_cm_margem_reserva"
    __table_args__ = (
        Index(
            "IX_tb_cm_margem_reserva_cliente",
            "id_cliente",
            "data_reserva",
        ),
        Index(
            "IX_tb_cm_margem_reserva_filial",
            "id_filial",
            "data_reserva",
        ),
        {"schema": "dbo"},
    )

    id_reserva = Column(BigInteger, primary_key=True)
    codigo_reserva = Column(String(30), nullable=True)

    id_cliente = Column(
        BigInteger,
        ForeignKey("dbo.tb_cm_margem_cliente.id_cliente"),
        nullable=False,
    )
    id_filial = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_filial.id_filial"),
        nullable=False,
    )
    id_vendedor = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_vendedor.id_vendedor"),
        nullable=True,
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
    id_banco_financiador = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_banco_financiador.id_banco_financiador"),
        nullable=True,
    )

    possui_af = Column(Boolean, nullable=False, server_default=text("0"))
    data_reserva = Column(DateTime, nullable=False)
    previsao_entrega = Column(Date, nullable=True)

    taxa_juros_mensal_padrao = Column(Numeric(9, 6), nullable=True)
    observacoes = Column(String(1000), nullable=True)

    # 1=rascunho, 2=calculada, etc.
    status_reserva = Column(
        SmallInteger,
        nullable=False,
        server_default=text("1"),
    )

    criado_por = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_usuario.id_usuario"),
        nullable=True,
    )
    atualizado_por = Column(
        Integer,
        ForeignKey("dbo.tb_cm_margem_usuario.id_usuario"),
        nullable=True,
    )

    cliente = relationship(
        "ClienteMargemModel",
        back_populates="reservas",
        lazy="joined",
    )
    filial = relationship(
        "FilialMargemModel",
        back_populates="reservas",
        lazy="joined",
    )
    vendedor = relationship(
        "VendedorMargemModel",
        back_populates="reservas",
        lazy="joined",
    )
    tipo_venda = relationship(
        "TipoVendaMargemModel",
        back_populates="reservas",
        lazy="joined",
    )
    modalidade = relationship(
        "ModalidadeFinanciamentoMargemModel",
        back_populates="reservas",
        lazy="joined",
    )
    banco_financiador = relationship(
        "BancoFinanciadorMargemModel",
        back_populates="reservas",
        lazy="joined",
    )

    usuario_criador = relationship(
        "UsuarioMargemModel",
        foreign_keys=[criado_por],
        back_populates="reservas_criadas",
        lazy="joined",
    )
    usuario_atualizador = relationship(
        "UsuarioMargemModel",
        foreign_keys=[atualizado_por],
        back_populates="reservas_atualizadas",
        lazy="joined",
    )

    itens = relationship(
        "ReservaItemMargemModel",
        back_populates="reserva",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ReservaMargem("
            f"id_reserva={self.id_reserva!r}, "
            f"codigo_reserva={self.codigo_reserva!r}"
            f")>"
        )
