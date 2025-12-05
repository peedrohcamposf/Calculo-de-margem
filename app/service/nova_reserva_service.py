from decimal import Decimal, InvalidOperation
from typing import Optional


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def calcular_impostos_venda(
    valor_venda,
    icms_percent,
    pis_cofins_percent,
) -> Decimal:
    """
    Impostos Venda = (ICMS * Valor de Venda) + (PIS/COFINS * Valor de Venda)
        = Valor * ((ICMS% + PIS%)/100)
    """
    base = _to_decimal(valor_venda)
    icms = _to_decimal(icms_percent) / Decimal("100")
    pis = _to_decimal(pis_cofins_percent) / Decimal("100")

    total = base * (icms + pis)
    return total.quantize(Decimal("0.01"))


def calcular_impostos_compra(
    valor_maquina,
    icms_pis_percent,
    pis_cofins_percent,
) -> Optional[Decimal]:
    """
    Impostos Compra = (ICMS + PIS/COFINS * Valor da Máquina) + (PIS/COFINS * Valor da Máquina)
        = Valor * ((ICMS% + PIS%)/100)
    """

    if valor_maquina is None:
        return None

    base = _to_decimal(valor_maquina)
    if base == 0:
        return None

    icms_pis = base * (_to_decimal(icms_pis_percent) / Decimal("100"))
    pis = base * (_to_decimal(pis_cofins_percent) / Decimal("100"))

    total = (icms_pis + pis).quantize(Decimal("0.01"))
    return total
