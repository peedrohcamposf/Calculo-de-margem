from __future__ import annotations

from decimal import Decimal, InvalidOperation


# Converte um valor para Decimal
def to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


# Normaliza um número no formato pt-BR para uma string em formato padrão, exemplo: "1.234,56" p/ "1234.56"
def normalizar_numero_ptbr(value) -> str:
    if value is None:
        return "0"
    if isinstance(value, (int, float, Decimal)):
        return str(value)

    s = str(value).strip()
    if not s:
        return "0"

    s = s.replace(".", "").replace(",", ".")
    return s
