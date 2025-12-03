from __future__ import annotations

from flask_login import UserMixin
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


# Usuário autenticado via Azure AD
class UsuarioModel(TimestampMixin, UserMixin, Base):

    __tablename__ = "tb_cm_usuario"
    __table_args__ = {"schema": "dbo"}

    id_usuario = Column(Integer, primary_key=True)
    azure_oid = Column(String(64), nullable=False, unique=True)
    email_login = Column(String(254), nullable=False, unique=True)
    nome = Column(String(150), nullable=True)
    cargo = Column(String(30), nullable=False)
    ativo = Column(Boolean, nullable=False, server_default=text("1"))

    # Flask-Login
    def get_id(self) -> str:
        return str(self.id_usuario)

    def __repr__(self) -> str:
        return (
            f"<Usuario("
            f"id_usuario={self.id_usuario!r}, "
            f"email_login={self.email_login!r}"
            f")>"
        )
