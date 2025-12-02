from __future__ import annotations

from sqlalchemy import Column, DateTime, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Campos padrões baseados em sysutcdatetime()
class TimestampMixin:

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )  # O banco de dados define no insert
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
        onupdate=text("SYSUTCDATETIME()"),
    )  # O banco de dados define no insert e o ORM atualiza no update
