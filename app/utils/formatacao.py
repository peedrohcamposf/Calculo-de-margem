from __future__ import annotations

from decimal import Decimal


# Formata um Decimal para o formato monetário brasileiro (1.234,56)
def formatar_brl(valor: Decimal | None) -> str | None:
    if valor is None:
        return None
    s = f"{valor:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
