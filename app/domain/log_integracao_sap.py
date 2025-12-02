from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
    text,
)

from .base import Base


class LogIntegracaoSapMargemModel(Base):

    __tablename__ = "tb_cm_margem_log_integracao_sap"
    __table_args__ = {"schema": "dbo"}

    id_log_integracao = Column(BigInteger, primary_key=True)
    sistema_origem = Column(String(50), nullable=False)
    tipo_registro = Column(String(50), nullable=False)
    chave_externa = Column(String(100), nullable=False)
    data_execucao = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )
    sucesso = Column(Boolean, nullable=False)
    mensagem_erro = Column(String, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<LogIntegracaoSapMargem("
            f"id_log_integracao={self.id_log_integracao!r}, "
            f"sistema_origem={self.sistema_origem!r}, "
            f"tipo_registro={self.tipo_registro!r}"
            f")>"
        )
