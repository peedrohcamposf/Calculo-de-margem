from decimal import Decimal, InvalidOperation


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def calcular_impostos_venda(valor_venda, icms_percent, pis_cofins_percent) -> Decimal:
    """
    Impostos Venda = (ICMS * Valor de Venda) + (PIS/COFINS * Valor de Venda)
        = Valor * ((ICMS% + PIS%)/100)
    """
    valor = _to_decimal(valor_venda)
    if not valor:
        return Decimal("0.00")

    icms = _to_decimal(icms_percent) / Decimal("100")
    pis = _to_decimal(pis_cofins_percent) / Decimal("100")

    total = valor * (icms + pis)
    return total.quantize(Decimal("0.01"))
